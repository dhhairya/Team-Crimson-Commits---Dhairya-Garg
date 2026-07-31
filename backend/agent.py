"""Stage 2: a hand-rolled ReAct loop over OpenRouter tool calling."""

import json

from llm import AGENT_MODEL, chat, parse_json
from prompts import AGENT_PROMPT
from tools import TOOL_SCHEMAS, TOOLS


def describe(name, args):
    """Turn a tool call into something a farmer can read while they wait."""
    if name == "get_weather":
        return f"Checking live weather for {args.get('city', 'your location')}..."
    if name == "web_search":
        return f"Searching trusted agricultural sources: \"{args.get('query', '')}\""
    return f"Running {name}..."


def stream_agent(diagnosis, city, state, max_steps=8):
    """Run the ReAct loop, yielding progress events as it goes.

    Yields {"type": "status"|"tool"} events while working, then one {"type": "result"} event.
    max_steps counts model turns, not tool calls: the model may fire several tools in one turn,
    read the results, and then decide to search again. It only stops when it returns no tool
    calls and a parseable JSON answer.
    """
    messages = [
        {"role": "system", "content": AGENT_PROMPT},
        {
            "role": "user",
            "content": (
                f"Leaf diagnosis: {json.dumps(diagnosis)}\n"
                f"Farmer location: {city}, {state}, India.\n"
                "Check the weather there and give me the treatment plan."
            ),
        },
    ]
    trace = []

    for step in range(1, max_steps + 1):
        print(f"[agent] turn {step}/{max_steps}", flush=True)
        yield {"type": "status", "message": "Thinking about the treatment plan..."}
        msg = chat(messages, AGENT_MODEL, tools=TOOL_SCHEMAS)
        messages.append(msg)

        calls = msg.get("tool_calls")
        if not calls:
            answer = parse_json(msg.get("content"))
            if answer:
                yield {"type": "result", "answer": answer, "trace": trace}
                return
            messages.append({"role": "user", "content": "Return only the final JSON object."})
            continue

        for call in calls:
            name = call["function"]["name"]
            args = json.loads(call["function"]["arguments"] or "{}")
            print(f"[tool] {name}({args})", flush=True)
            yield {"type": "status", "message": describe(name, args)}
            try:
                result = TOOLS[name](**args)
            except Exception as exc:  # a failed tool should not kill the demo
                result = {"error": str(exc)}
            trace.append({"tool": name, "args": args, "result": result})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": json.dumps(result)[:8000],
                }
            )

    # Out of steps: force an answer with the tools taken away.
    yield {"type": "status", "message": "Finalising the recommendation..."}
    messages.append({"role": "user", "content": "Stop searching. Give the final JSON now."})
    answer = parse_json(chat(messages, AGENT_MODEL).get("content"))
    yield {
        "type": "result",
        "answer": answer or {"error": "The agent could not produce a recommendation."},
        "trace": trace,
    }


def run_agent(diagnosis, city, state, max_steps=8):
    """Non-streaming wrapper: drain the generator and return the final result."""
    for event in stream_agent(diagnosis, city, state, max_steps):
        if event["type"] == "result":
            return {"answer": event["answer"], "trace": event["trace"]}
    return {"answer": {"error": "The agent produced no result."}, "trace": []}
