<div align="center">

# 🛣️ CRACK**WATCH**

### *AI-Powered Smart Infrastructure Command Center*

---

*Built in 48 hours. Deployable to 1 billion people.*

</div>

---

## 🎯 The 30-Second Pitch

> Last year in Maharashtra alone, **3,275 people died** because of potholes on Indian roads.
> **73% of reported potholes are never fixed.** ₹33,000 crore is spent annually on road repairs, but manual inspection is slow, expensive, and dangerous.
>
> **CRACKWATCH** doesn't just detect damage — it **predicts when it will fail, estimates the repair cost, submits the report to authorities, and publicly ranks every contractor by negligence**.
>
> Citizens report via the PWA — or WhatsApp — in under 3 seconds.
> Governments see the report on an inspector's map with AI-analyzed severity, cost, and a priority queue.
> The public sees every unfixed pothole and which contractor is responsible.
>
> **Detecting a pothole doesn't fix it. A watched government does.**

---

## 🏆 What Makes This Groundbreaking

<table>
<tr>
<td width="33%" align="center">

### 💬 WhatsApp Bot
**Zero app install needed.**
500M Indian WhatsApp users can report damage *right now*, no learning curve, no app store, no login.

</td>
<td width="33%" align="center">

### 🤖 3-Model AI Pipeline
**Fully offline, 757ms per image.**
YOLOv8s-RDD + CrackSeg + OpenCV running in parallel. Zero cloud bills. Works when internet drops.

</td>
<td width="33%" align="center">

### 🔥 Wall of Shame
**Contractor accountability, publicly ranked.**
Every unfixed report compounds their negligence score. Politicians don't want to be at the top.

</td>
</tr>
<tr>
<td width="33%" align="center">

### 🔮 Predictive Engine
**"This road fails in 18 days."**
Monsoon-adjusted damage progression model. Shows cost delta if repair delayed.

</td>
<td width="33%" align="center">

### 🛡️ 5-Layer Fraud Detection
**No selfies reach the inspector.**
Image authenticity + GPS validation + content relevance + duplicate detection + rate limiting.

</td>
<td width="33%" align="center">

### 🎮 Gamification Engine
**Citizens compete to fix their city.**
XP, Civic Coins, 13 badges, daily streaks, AI Challenge game, Pothole Hunter leaderboard.

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                          CRACKWATCH ECOSYSTEM                           │
│                                                                          │
│   ┌──────────────┐     ┌──────────────┐     ┌────────────────┐          │
│   │  Govt App    │     │  Citizen PWA │     │  WhatsApp Bot  │          │
│   │  React+Vite  │     │  React+Vite  │     │  (Twilio)      │          │
│   │  Port 5173   │     │  Port 5175   │     │  +14155238886  │          │
│   │  HTTPS       │     │  Phone-frame │     │  join code     │          │
│   └──────┬───────┘     └──────┬───────┘     └────────┬───────┘          │
│          │                    │                      │                   │
│          └──────────┬─────────┴──────────┬───────────┘                   │
│                     ▼                    ▼                               │
│            ┌───────────────┐    ┌───────────────┐                        │
│            │ HTTPS :8000   │    │ HTTP :8001    │                        │
│            │ Frontend API  │    │ ngrok tunnel  │                        │
│            └───────┬───────┘    └───────┬───────┘                        │
│                    │                    │                                │
│                    └──────────┬─────────┘                                │
│                               │                                          │
│                       ┌───────▼────────┐                                 │
│                       │   FastAPI      │                                 │
│                       │   (single app) │                                 │
│                       └───────┬────────┘                                 │
│                               │                                          │
│  ┌──────┬──────┬──────┬──────┼──────┬──────┬──────┬──────┐              │
│  ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼              │
│ YOLO  Crack  OpenCV Severity Cost  Fraud Predict Gamify Analytics       │
│ RDD   Seg    CV     Engine   INR   5-lyr X-days  XP/Lvl Wall of Shame   │
│                                                                          │
│                       ┌──────────────┐                                   │
│                       │ shared_store │ ← cross-process state sync        │
│                       │    .json     │                                   │
│                       └──────────────┘                                   │
└────────────────────────────────────────────────────────────────────────┘
```

**Dual-backend design:**
- **Port 8000 HTTPS** — serves frontends (mobile camera/GPS requires secure context)
- **Port 8001 HTTP** — receives Twilio WhatsApp webhooks via ngrok
- **Shared state** via `shared_store.json` (merge-on-read/write)

---

## ✨ Complete Feature List

### 🏛️ Government Command Center (Web Dashboard)

| Feature | What It Does |
|---------|--------------|
| 🤖 **AI Damage Detection** | Upload an image → 3-model pipeline detects 10+ damage types in 757ms |
| 📏 **Severity Scoring** | 0-100 composite score based on damage area × confidence × type weight |
| 💰 **Cost Estimation** | INR estimates calibrated to CPWD 2023 Mumbai rates + repair method + crew size |
| 📋 **Repair Plan Generator** | Priority-ranked daily action plan for inspectors |
| 🗺️ **Reports Map** | Interactive Leaflet map with admin controls (mark fixed/in-progress) |
| 🎥 **Video + Live Camera** | Frame-by-frame video analysis + live camera detection |
| 🔮 **Predictive Analytics** | "This road fails in X days" with monsoon acceleration (2.5× Jun-Sep) |
| 🔥 **Wall of Shame** | 6+ contractors ranked by negligence score |
| ⚠️ **Priority Queue** | Top 5 urgent repairs with total cost projection |
| 🏥 **City Health Score** | 0-100 rating per city with trend indicators |
| 🔄 **Before/After** | Upload 2 images → AI computes improvement % |
| 📊 **Smart Heatmap** | Geo-intensity visualization of damage severity |
| 🛡️ **Fraud Controls** | Toggle 5-layer fraud detection on/off |

### 📱 Public Citizen App (PWA)

| Feature | What It Does |
|---------|--------------|
| 🗺️ **Live Pothole Map** | Real-time pins color-coded by status (unfixed/in-progress/fixed) |
| 📸 **Photo + GPS Reporting** | Tap → photo → AI classifies → auto-GPS → submit in 3 taps |
| ⬆️ **Upvote System** | Citizens vote which potholes matter most → priority re-rank |
| 🧭 **Pothole-Aware Navigation** | OSRM routing with safety scores, hazard markers, "Avoid Potholes" toggle |
| 🏆 **Pothole Hunter Leaderboard** | Top citizens by XP — gold/silver/bronze podium |
| 🎖️ **13 Achievement Badges** | First Report → Road Warrior → City Saver → AI Master |
| 💰 **Civic Coins** | Virtual currency earned from reports + verifications |
| 🔥 **Daily/Weekly Streaks** | Bonus XP multipliers for consistent reporting |
| 🧠 **AI Challenge Game** | Guess damage type from scenario description (+50 XP correct) |
| 📊 **Transparency Dashboard** | Government performance score + fix rate + cost total |
| 💬 **WhatsApp Integration** | Report directly from WhatsApp, no PWA needed |
| 📱 **Phone-Frame Desktop** | Mobile-first design looks like a phone on desktop |

### 💬 WhatsApp Bot (Twilio)

| Feature | What It Does |
|---------|--------------|
| 🚀 **Zero-Install Reporting** | Send photo → get AI analysis in 3 seconds |
| 🔄 **Two-Step Conversation** | Stateful flow: photo first, then location share |
| 📍 **Native Location Share** | Uses WhatsApp's native location picker for accurate GPS |
| 🤖 **AI Reply** | Damage type + severity + cost + gamification rewards |
| 🛡️ **No-Damage Guard** | Clean photos rejected with tips (not auto-approved) |
| ⏱️ **15-min Session Expiry** | Prevents stale photo + fresh location mismatch |
| 🎮 **Gamification in Chat** | XP, coins, new badge notifications in reply message |

---

## 🧰 Tech Stack

<table>
<tr>
<td valign="top" width="50%">

### 🎯 AI / ML
- **YOLOv8s-RDD** — Road damage detection (72.6% mAP)
- **YOLOv8s-CrackSeg** — Building/wall crack segmentation (85%+)
- **OpenCV** — Supplementary CV (leaks, rust, spalling, moiré)
- **Ultralytics** — Inference framework
- **RDD2022 Dataset** — 4.8K Indian road images

### ⚙️ Backend
- **Python 3.12+**
- **FastAPI 0.115** — Async ASGI framework
- **Uvicorn 0.30** — ASGI server with HTTPS
- **Pillow** — Image decoding + EXIF extraction
- **httpx** — Async HTTP client
- **python-dotenv** — Credentials management
- **Twilio SDK 9.3** — WhatsApp integration
- **JWT** — Stateless auth (PyJWT)

</td>
<td valign="top" width="50%">

### 🎨 Frontend (Govt Dashboard)
- **React 19** + **Vite 8**
- **Tailwind CSS v4** (via `@tailwindcss/vite`)
- **shadcn/ui** component primitives
- **Framer Motion** — Animations
- **Recharts** — Analytics charts
- **Leaflet** + **react-leaflet-cluster** — Maps
- **Lucide React** — Icons
- **Space Grotesk + Geist** — Typography

### 📱 Frontend (Public PWA)
- **React 19** + **Vite 8**
- **Leaflet Routing Machine** (OSRM) — Pothole-aware nav
- **Framer Motion** — Phone-frame animations
- Progressive Web App (installable)

### 🔌 Integrations
- **Twilio WhatsApp Sandbox** — Messaging platform
- **ngrok** — HTTPS tunnel for webhooks
- **OpenStreetMap / Nominatim** — Geocoding (free)
- **OSRM** — Free routing engine

</td>
</tr>
</table>

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **Git**
- (Optional) **ngrok** for WhatsApp webhook
- (Optional) **Twilio account** (free trial) for WhatsApp

### 1. Clone the Repo

```bash
git clone https://github.com/gragznotkool/CrackWatch.git
cd CrackWatch
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
# Govt Dashboard
cd ..
npm install

# Public PWA
cd public-app
npm install
cd ..
```

### 4. (Optional) Generate SSL Certs for Mobile Testing

```bash
# Using mkcert (recommended)
mkcert -install
mkcert -cert-file certs/cert.pem -key-file certs/key.pem localhost 127.0.0.1 <your-lan-ip>

# Copy to backend too (for the API)
cp certs/cert.pem backend/cert.pem
cp certs/key.pem backend/key.pem
```

### 5. Configure Environment

```bash
# crackwatch/.env
VITE_API_URL=https://<your-lan-ip>:8000

# public-app/.env
VITE_API_URL=https://<your-lan-ip>:8000

# backend/.env  (for WhatsApp)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

### 6. Run Everything

```bash
# Terminal 1 — Backend (HTTPS, for frontend)
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 \
  --ssl-keyfile key.pem --ssl-certfile cert.pem

# Terminal 2 — Backend (HTTP, for WhatsApp via ngrok)
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001

# Terminal 3 — Govt Dashboard
npm run dev                # → https://<your-ip>:5173

# Terminal 4 — Public PWA
cd public-app
npm run dev                # → https://<your-ip>:5175

# Terminal 5 — ngrok (for WhatsApp)
ngrok http http://localhost:8001
# Copy the https://*.ngrok-free.app URL to Twilio Sandbox webhook
```

### 7. (Optional) Seed Demo Data

```bash
# 20 reports from real images across Mumbai + Navi Mumbai
cd backend
PYTHONIOENCODING=utf-8 python seed_from_images.py

# 10 gamification demo users
curl -k -X POST https://localhost:8000/gamification/seed-demo
```

---

## 🔐 Demo Credentials

| Role | Username | Password | What You Get |
|------|----------|----------|--------------|
| 🏛️ Government Inspector | `admin` | `admin123` | Full govt dashboard + admin controls |
| 🏛️ Municipal Officer | `inspector` | `inspect123` | Same as admin, different name |
| 🏛️ NHAI Engineer | `engineer` | `eng123` | Same as admin, different name |
| 📱 Demo Citizen | `saud` | `123` | Pre-seeded profile: Lv.6, 3200 XP, 10 badges, 21-day streak, #1 leaderboard |
| 📱 Anonymous Citizen | *any name* | *blank* | Fresh account, starts at 0 XP |

---

## 📖 API Reference

### Authentication
```
POST /auth/login              Government or citizen login → JWT
POST /auth/register           Anonymous citizen registration
GET  /auth/me                 Verify token
```

### Detection
```
POST /detect                  Image upload → full AI pipeline
POST /detect/video            Video frame-by-frame analysis
POST /detect/frame            Single base64 frame (live camera)
GET  /sectors                 Available detection sectors
```

### Citizen Reports
```
POST /public/report                Submit citizen report (photo + GPS)
GET  /public/reports/map           Lightweight map pins
GET  /public/reports/map/detail    Full reports with images
GET  /public/reports/{id}          Single report
POST /public/reports/{id}/upvote   Upvote a report
```

### Admin
```
GET  /admin/reports/map            Govt reports with admin fields
PATCH /admin/reports/{id}/status   Change status (submitted/in_progress/fixed)
GET  /admin/settings               Read system settings
PATCH /admin/settings              Toggle fraud detection
POST /admin/reports/seed-demo      Seed demo reports
```

### Advanced Analytics
```
GET /analytics/wall-of-shame       Contractor leaderboard
GET /analytics/heatmap             Geo-intensity points
GET /analytics/priority-queue      Top 5 urgent repairs
GET /analytics/city-health         Per-city health scores
GET /analytics/forecast            Predictive maintenance forecast
POST /analytics/before-after       Compare before/after images
```

### Gamification
```
GET  /gamification/leaderboard           Top 20 XP holders
GET  /gamification/profile/{user_id}     Full user profile
GET  /gamification/challenges/{user_id}  Daily quests
POST /gamification/verify                Community vote on report
GET  /gamification/ai-challenge          Random scenario
POST /gamification/ai-challenge/answer   Submit guess
GET  /gamification/achievements          All badges
POST /gamification/seed-demo             Seed 10 demo users
```

### WhatsApp
```
POST /whatsapp/webhook          Twilio incoming-message handler
```

### Repair Plan
```
POST /repair-plan/generate      Priority-ranked daily plan
GET  /repair-plan/explain/{id}  Explainable AI breakdown
```

---

## 💬 WhatsApp Bot Setup

### 1. Twilio Sandbox (Free)

1. Sign up at https://www.twilio.com/try-twilio (free, no credit card)
2. Navigate to **Messaging → Try it out → Send a WhatsApp message**
3. Note your **sandbox number** (`+1 415 523 8886`) and **join code**

### 2. Configure Webhook

1. Run `ngrok http http://localhost:8001` — copy the forwarding URL
2. In Twilio Sandbox → **Sandbox settings**:
   - **When a message comes in:** `https://your-ngrok.ngrok-free.app/whatsapp/webhook`
   - **Method:** HTTP POST
   - Save

### 3. Opt In Any Phone

From any WhatsApp:
```
join your-sandbox-code
```
to `+1 415 523 8886`

### 4. Report Damage via WhatsApp

1. Send a photo of damage
2. Bot replies: *"📸 Got your photo! Now tap 📎 → Location → Send current location"*
3. Share your location via WhatsApp's attachment menu
4. Bot replies with AI analysis, cost, repair method, XP earned

---

## 🎯 Key Design Decisions

<details>
<summary><b>Why local YOLO, not cloud inference?</b></summary>

Zero cloud bills. Sub-second latency. Works offline. Critical for rural India where connectivity is inconsistent. Municipalities can deploy on a ₹30K laptop with no recurring costs.
</details>

<details>
<summary><b>Why two uvicorn processes (HTTPS + HTTP)?</b></summary>

Frontend requires HTTPS for mobile camera/GPS (browser security). ngrok free tier can't verify self-signed upstream TLS, so Twilio webhooks need plain HTTP. Solved with a shared `shared_store.json` for cross-process state.
</details>

<details>
<summary><b>Why WhatsApp instead of another chat platform?</b></summary>

500M+ monthly active users in India. Zero install friction. Works on feature phones via WhatsApp Lite. Citizens already know how to send photos. No "why should I install your app?" barrier.
</details>

<details>
<summary><b>Why YOLOv8 and not newer models like YOLOv11?</b></summary>

YOLOv8s-RDD has pre-trained weights on RDD2022 (4.8K Indian road images). A newer architecture without domain-specific training scores ~14 percentage points lower on Indian damage. "Newer ≠ better" when domain data matters.
</details>

<details>
<summary><b>Why in-memory state instead of PostgreSQL?</b></summary>

Hackathon velocity. Every feature ships in 30 minutes because there's no migration overhead. `shared_store.json` adds persistence + cross-process sync. Production would use PostgreSQL + PostGIS for geo-queries.
</details>

<details>
<summary><b>Why rule-based cost estimation, not ML?</b></summary>

Explainability. Inspectors need to defend budget allocations. A rule-based engine calibrated to CPWD 2023 rates gives line-item accountability. ML would be a black box no government will approve.
</details>

---

## 📊 Performance Metrics

| Metric | Value | Context |
|--------|-------|---------|
| YOLO inference time | **~500ms** | CPU only, no GPU |
| Full pipeline latency | **~757ms** | YOLO + CrackSeg + OpenCV + annotation |
| WhatsApp round-trip | **~3 seconds** | User's photo → bot reply |
| Reports on map load | **~50ms** | 20 reports with base64 images |
| Fraud check time | **~200ms** | Mostly Laplacian + FFT |
| Memory footprint | **~1.2 GB** | Per uvicorn process (YOLO weights) |
| Inference accuracy | **72.6% mAP** | YOLOv8s-RDD on RDD2022 test set |

---

## 🎯 Roadmap

### ✅ Shipped (v1.0.0 → v3.6.2)
- Core AI pipeline (3 models)
- Dual-platform (Govt + Citizen)
- WhatsApp integration with stateful conversations
- Gamification (13 badges, leaderboard, AI challenge)
- 5-layer fraud detection
- Predictive maintenance engine
- Wall of Shame with 6 contractors
- Pothole-aware navigation
- Demo-ready seed data (20 reports across Mumbai + Navi Mumbai)
- 15-slide presentation deck

### 🚧 Post-Hackathon (Backlog)
- PostgreSQL + PostGIS migration
- Real WhatsApp Business API (no sandbox join code)
- Mobile native apps (React Native)
- Offline-first sync queue
- Multi-language (Hindi, Marathi)
- UPI-based citizen crowdfunding ("fund this fix")
- WebSocket real-time map updates
- AR live-scan camera overlay
- Voice note transcription (Whisper)
- Municipal ERP integration (SAP, custom CPGRAMS bridges)

---

## 🛡️ Security Notes

### Hackathon-Safe Compromises
- Passwords are plaintext in `auth.py` (would be bcrypt-hashed in prod)
- JWT secret is hardcoded (would be env var + rotation)
- CORS = `allow_origins=["*"]` (would be scoped to known frontends)
- Rate limiting is in-memory (would need Redis for multi-worker)

### Actually Production-Safe
- ✅ XML escaping in TwiML replies
- ✅ Fraud detection resilient to hostile users
- ✅ Image authenticity resists screenshot attacks (moiré detection)
- ✅ GPS bounds check rejects out-of-India coords
- ✅ `.env`, `.pem`, and `shared_store.json` are gitignored
- ✅ JWT tokens expire in 24h

---

## 📚 Version History

See [CHANGELOG.md](./CHANGELOG.md) — every release documented with bullet points.

Highlights:
- **v1.0.0** — Production release, dual platform
- **v1.4.0** — 5-layer fraud detection
- **v2.0.0** — Smart navigation with pothole avoidance
- **v2.2.0** — Predictive maintenance engine
- **v3.0.0** — Full gamification (12 features)
- **v3.3.0** — `saud/123` demo account
- **v3.4.0** — No-damage rejection
- **v3.5.0** — WhatsApp bot
- **v3.5.2** — Stateful WhatsApp two-step flow (photo + location)
- **v3.6.0** — Presentation rebuild with groundbreaking features
- **v3.6.1** — 20 AI-detected real-image reports across Mumbai
- **v3.6.2** — Wall of Shame with 6 contractors

---


### The One Line That Wins

> **"Detecting a pothole doesn't fix it. A watched government does."**

---

---

## 📜 License

MIT — Feel free to fork, adapt, and deploy to your own municipality. Open-source infrastructure accountability should be a public good.

---

## 🙏 Acknowledgments

- **RDD2022 Dataset** — Pre-trained YOLO weights
- **HuggingFace** — Model hosting
- **Twilio** — WhatsApp Sandbox (free tier)
- **OpenStreetMap + OSRM** — Free mapping infrastructure
- **Ultralytics** — YOLOv8 inference framework

- Every pothole that inspired this build. May you never trip another commuter.

---

<div align="center">



*If this helped your city, a ⭐ on GitHub means the world.*

[⬆ back to top](#-crackwatch)

</div>
