const BACKEND_URL = "http://localhost:8000";

if (window.lucide) lucide.createIcons();

if (window.gsap && window.ScrollTrigger) {
  gsap.registerPlugin(ScrollTrigger);
}

async function fetchLiveWeatherForLocation(city, state) {
  const defaultCity = city || "Nashik";
  const defaultState = state || "Maharashtra";

  try {
    const geoResp = await fetch(
      `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(defaultCity)}&count=1&country=IN&language=en`
    );
    const geoData = await geoResp.json();

    if (geoData.results && geoData.results.length > 0) {
      const { latitude, longitude, name, admin1 } = geoData.results[0];
      const locationName = `${name}, ${admin1 || defaultState}`;

      const weatherResp = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,apparent_temperature&hourly=precipitation_probability&forecast_days=1`
      );
      const weatherData = await weatherResp.json();
      const current = weatherData.current;
      const rainChance = weatherData.hourly?.precipitation_probability[0] || 15;

      updateWeatherUI(
        Math.round(current.temperature_2m),
        current.relative_humidity_2m,
        Math.round(current.wind_speed_10m),
        rainChance,
        Math.round(current.apparent_temperature),
        current.precipitation > 0 ? "Rainy conditions" : "Partly Cloudy / Clear",
        locationName
      );
      return;
    }
  } catch (err) {
    console.warn("Weather API fetch failed, applying fallbacks:", err);
  }

  updateWeatherUI(29, 78, 12, 20, 31, "Partly Cloudy · Humid", `${defaultCity}, ${defaultState}`);
}

function updateWeatherUI(temp, humidity, wind, rain, feelsLike, condition, location) {
  const liveTempEl = document.getElementById('liveTemp');
  if (liveTempEl) liveTempEl.textContent = `${temp}°C`;

  const condEl = document.getElementById('liveWeatherCondition');
  if (condEl) condEl.textContent = condition;

  const humEl = document.getElementById('liveHumidity');
  if (humEl) humEl.textContent = `${humidity}%`;

  const windEl = document.getElementById('liveWind');
  if (windEl) windEl.textContent = `${wind} km/h`;

  const rainEl = document.getElementById('liveRain');
  if (rainEl) rainEl.textContent = `${rain}%`;

  const feelsEl = document.getElementById('liveFeelsLike');
  if (feelsEl) feelsEl.textContent = `${feelsLike}°C`;

  const locLabel = document.getElementById('weatherLocationLabel');
  if (locLabel) locLabel.textContent = `LIVE WEATHER FOR ${location.toUpperCase()}`;

  const pills = document.querySelectorAll('.top-pill');
  if (pills.length >= 2) {
    pills[0].innerHTML = `<i data-lucide="map-pin"></i> ${location}`;
    pills[1].innerHTML = `<i data-lucide="thermometer"></i> ${temp}°C · Live`;
  }

  if (window.lucide) lucide.createIcons();
}

const particleContainer = document.getElementById('particlesContainer');
if (particleContainer) {
  for (let i = 0; i < 8; i++) {
    const p = document.createElement('div');
    p.className = 'leaf-sprite';
    p.style.left = (Math.random() * 90 + 5) + '%';
    p.style.top = (Math.random() * 80 + 10) + '%';
    p.style.animationDelay = (Math.random() * 8) + 's';
    p.style.animationDuration = (12 + Math.random() * 6) + 's';
    particleContainer.appendChild(p);
  }
}

const mainPane = document.getElementById('mainContentPane');
const scrollFill = document.getElementById('scrollProgressFill');
if (mainPane && scrollFill) {
  mainPane.addEventListener('scroll', () => {
    const totalScroll = mainPane.scrollHeight - mainPane.clientHeight;
    if (totalScroll > 0) {
      scrollFill.style.width = (mainPane.scrollTop / totalScroll) * 100 + '%';
    }
  });
}

const navItems = document.querySelectorAll('.nav-item');
const pageSections = document.querySelectorAll('.page-section');

function scrollToSection(targetId) {
  navItems.forEach(item => {
    item.classList.toggle('active', item.dataset.target === targetId);
  });
  pageSections.forEach(sec => {
    sec.classList.toggle('active', sec.id === `page-${targetId}`);
  });
  if (mainPane) mainPane.scrollTop = 0;
  if (window.ScrollTrigger) ScrollTrigger.refresh();
}

navItems.forEach(item => {
  item.addEventListener('click', () => scrollToSection(item.dataset.target));
});

const journeyStages = [
  { step: "STEP 1 OF 4 — GERMINATION & SOIL SEED", title: "Seedling Root Establishment", desc: "The model tracks soil moisture (34%) and root radicle emergence in early growth." },
  { step: "STEP 2 OF 4 — VEGETATIVE LEAF EXPANSION", title: "Stem & Canopy Architecture", desc: "Leaves unfold cleanly. Spectral reflection values match healthy chlorophyll density." },
  { step: "STEP 3 OF 4 — PATHOGEN LESION EMERGENCE", title: "Early Blight Spore Detection", desc: "Fungal conidia spores settle on mid-canopy leaves during high humidity (>75%)." },
  { step: "STEP 4 OF 4 — DIAGNOSTIC SCAN ASSEMBLY", title: "High-Confidence Diagnosis", desc: "Scanning overlay confirms Northern Leaf Blight with 94.6% confidence." }
];

const botanicalTrack = document.getElementById('botanicalTrack');
if (botanicalTrack && mainPane && window.ScrollTrigger) {
  ScrollTrigger.create({
    trigger: botanicalTrack,
    scroller: mainPane,
    start: "top top+=20",
    end: "bottom bottom",
    scrub: 0.5,
    onUpdate: (self) => {
      const p = self.progress;
      const stageIdx = Math.min(3, Math.floor(p * 4));
      const stage = journeyStages[stageIdx];
      
      const stepInd = document.getElementById('stepIndicator');
      if (stepInd) stepInd.innerHTML = `<i data-lucide="sparkles" style="width:14px;"></i> ${stage.step}`;
      
      const lbl = document.getElementById('journeyStageLabel');
      if (lbl) lbl.textContent = stage.step;
      const ttl = document.getElementById('journeyStageTitle');
      if (ttl) ttl.textContent = stage.title;
      const dsc = document.getElementById('journeyStageDesc');
      if (dsc) dsc.textContent = stage.desc;

      gsap.to('#svgRoots', { opacity: 0.2 + p * 0.8, duration: 0.1 });
      gsap.to('#svgStem', { strokeDashoffset: (1 - Math.min(1, p * 2)) * 300, duration: 0.1 });
      gsap.to('#svgLeaves', { opacity: Math.min(1, Math.max(0, (p - 0.25) * 4)), duration: 0.1 });
      gsap.to('#svgCorn', { opacity: Math.min(1, Math.max(0, (p - 0.5) * 4)), duration: 0.1 });
      gsap.to('#svgScanOverlay', { opacity: Math.min(1, Math.max(0, (p - 0.75) * 4)), duration: 0.1 });
      gsap.to('#svgLaserLine', { y: Math.sin(p * 20) * 80 + 90, duration: 0.1 });
      
      if (window.lucide) lucide.createIcons();
    }
  });
}

const explainerCards = document.querySelectorAll('.explainer-trigger-card');
const explainerPillStep = document.getElementById('explainerPillStep');
const explainerPillTitle = document.getElementById('explainerPillTitle');
const explainerPillDesc = document.getElementById('explainerPillDesc');

if (window.ScrollTrigger) {
  explainerCards.forEach(card => {
    ScrollTrigger.create({
      trigger: card,
      scroller: mainPane,
      start: "top center",
      end: "bottom center",
      onEnter: () => updateExplainer(card),
      onEnterBack: () => updateExplainer(card)
    });
  });
}

function updateExplainer(card) {
  if (explainerPillStep) explainerPillStep.textContent = `FINDING ${card.dataset.step} OF 3`;
  if (explainerPillTitle) explainerPillTitle.textContent = card.dataset.title;
  if (explainerPillDesc) explainerPillDesc.textContent = card.dataset.desc;
}

document.querySelectorAll('.tilt-card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    card.style.transform = `perspective(800px) rotateX(${(-y / rect.height) * 8}deg) rotateY(${(x / rect.width) * 8}deg) translateY(-4px)`;
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = `perspective(800px) rotateX(0deg) rotateY(0deg) translateY(0px)`;
  });
});

const detectionForm = document.getElementById('detectionForm');
const leafFileInput = document.getElementById('leafFileInput');
const cityInput = document.getElementById('cityInput');
const stateInput = document.getElementById('stateInput');
const imagePreviewBox = document.getElementById('imagePreviewBox');
const imagePreviewEl = document.getElementById('imagePreviewEl');
const liveStatusText = document.getElementById('liveStatusText');
const resultSummaryCard = document.getElementById('resultSummaryCard');

if (cityInput && stateInput) {
  cityInput.addEventListener('change', () => {
    fetchLiveWeatherForLocation(cityInput.value.trim(), stateInput.value.trim());
  });
  stateInput.addEventListener('change', () => {
    fetchLiveWeatherForLocation(cityInput.value.trim(), stateInput.value.trim());
  });
}

if (leafFileInput) {
  leafFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        imagePreviewEl.src = ev.target.result;
        imagePreviewBox.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  });
}

if (detectionForm) {
  detectionForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const file = leafFileInput.files[0];
    const city = (cityInput && cityInput.value.trim()) || "Nashik";
    const state = (stateInput && stateInput.value.trim()) || "Maharashtra";

    if (!file) {
      alert("Please upload or drop a leaf image file first.");
      return;
    }

    resultSummaryCard.style.display = "none";
    liveStatusText.innerHTML = "⚙️ <i>Connecting to backend server...</i>";

    fetchLiveWeatherForLocation(city, state);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("city", city);
    formData.append("state", state);

    try {
      const response = await fetch(`${BACKEND_URL}/analyze/stream`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`API Error (${response.status}): ${errText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);
            handleStreamEvent(event);
          } catch (err) {
            console.warn("Parsing chunk failed:", line);
          }
        }
      }
    } catch (err) {
      liveStatusText.innerHTML = `<span style="color:var(--error);">Analysis Failed: ${err.message}</span>`;
    }
  });
}

function handleStreamEvent(event) {
  if (event.type === "status") {
    liveStatusText.innerHTML = `⚙️ ${event.message}`;
  } else if (event.type === "diagnosis") {
    const diag = event.data;
    liveStatusText.innerHTML = `🔬 <b>Diagnosis Complete:</b> Identified <b>${diag.disease_identified}</b> on <b>${diag.crop_type}</b> (${diag.severity_percent}% leaf area affected)`;
  } else if (event.type === "result") {
    const rec = event.answer;
    
    resultSummaryCard.style.display = "block";
    
    const banner = document.getElementById("resultStatusBanner");
    banner.textContent = rec.diagnostic_summary || rec.disease || "Analysis Complete";
    
    if (rec.ui_status_color === "RED") banner.className = "badge badge-err";
    else if (rec.ui_status_color === "YELLOW") banner.className = "badge badge-warn";
    else banner.className = "badge badge-ok";

    document.getElementById("resultDiseaseTitle").textContent = rec.disease || "Unknown Disease";
    document.getElementById("resultSummaryDesc").textContent = rec.safety_notes || "";
    document.getElementById("resChemical").textContent = rec.chemical || "-";
    document.getElementById("resDosage").textContent = rec.dosage || "-";
    document.getElementById("resSprayNow").textContent = rec.spray_now ? "YES" : "NO";
    document.getElementById("resWindow").textContent = rec.best_spray_window || "-";

    liveStatusText.innerHTML = "✅ <b>Analysis Complete!</b> Live treatment plan generated.";
  } else if (event.type === "error") {
    liveStatusText.innerHTML = `<span style="color:var(--error);">Error: ${event.message}</span>`;
  }
}

function toggleAssistant() {
  const shell = document.getElementById('appShell');
  const text = document.getElementById('assistantToggleText');
  if (shell) {
    shell.classList.toggle('assistant-collapsed');
    if (text) text.textContent = shell.classList.contains('assistant-collapsed') ? 'Show Assistant' : 'Hide Assistant';
  }
}

const assistantToggleBtn = document.getElementById('assistantToggleBtn');
if (assistantToggleBtn) assistantToggleBtn.addEventListener('click', toggleAssistant);

function askAssistant(q) {
  const body = document.getElementById('chatBody');
  if (!body) return;
  body.innerHTML += `<div class="msg user">${q}</div>`;
  body.scrollTop = body.scrollHeight;

  setTimeout(() => {
    let reply = "I've logged your query. Based on current field conditions, applying recommended triazole fungicide within 5 days offers an 82% resolution probability.";
    body.innerHTML += `<div class="msg bot">${reply}</div>`;
    body.scrollTop = body.scrollHeight;
  }, 700);
}

function sendMessage() {
  const input = document.getElementById('chatInput');
  if (input && input.value.trim()) {
    askAssistant(input.value.trim());
    input.value = '';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  fetchLiveWeatherForLocation("Nashik", "Maharashtra");
});