# WeatherGPT

**Problem Statement:** AI-Based Conversational AI for Weather Forecasting, Alerts, and Climate Information
**Sponsor:** Ministry of Earth Sciences (MoES)
**Theme:** Disaster Management

This is a minimal, working starting point — a chat-style web app that pulls live weather
data and answers questions about it. It is intentionally simple so your team can focus
hackathon time on the parts that actually differentiate your solution.

## What's included

```
weathergpt/
├── backend/
│   ├── app.py            # Flask API: geocoding + weather fetch + reply generation
│   └── requirements.txt
├── frontend/
│   └── index.html        # Single-page chat UI, no build step needed
└── README.md
```

## Quick start

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Then open `frontend/index.html` directly in a browser (or serve it with any static
server). Enter a city name and a question, and it'll fetch live weather from
Open-Meteo (free, no API key required) and reply.

## What this starter does NOT do yet (your work during the hackathon)

1. **Real conversational AI.** `generate_reply()` in `app.py` is currently
   rule-based. Swap it for a call to an LLM (Claude API, OpenAI, or an
   open-weight model like Llama/Mistral) so it can:
   - Handle free-form questions ("will it rain during my commute tomorrow?")
   - Support Indian regional languages
   - Remember conversation context across turns

2. **Real alerting logic tied to IMD thresholds.** Right now there's a
   placeholder rain-probability check. A real "early warning" system should
   use official IMD alert criteria (heatwave, cyclone, heavy rainfall
   thresholds by district).

3. **Hyperlocal / district-level data.** Open-Meteo is a good free stand-in,
   but MoES/IMD problem statements typically expect integration with their
   own APIs or datasets — check the official portal for what's provided.

4. **Voice input/output** — a nice differentiator for accessibility
   (many target users may not read comfortably). Consider Web Speech API
   for a quick win.

5. **Persistence** — save user's preferred locations, alert subscriptions,
   or forecast history (SQLite is plenty for a hackathon demo).

## Suggested 36-hour build order

1. Get the current scaffold running end-to-end (30 min)
2. Wire in an LLM for natural responses (2–3 hrs)
3. Add multilingual support — even 2–3 Indian languages is a strong demo (3–4 hrs)
4. Build out proper alert logic + push notification mock (3–4 hrs)
5. Polish UI, add voice input, prepare demo script (remaining time)
