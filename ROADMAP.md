# CRACKWATCH — Dual Platform Architecture

## THE VISION
Two apps. One mission. Complete transparency.

```
                    CRACKWATCH ECOSYSTEM
    ┌─────────────────────────────────────────────┐
    │                                             │
    │   📱 PUBLIC APP          🏛️ GOVERNMENT APP   │
    │   (Citizens)             (Authorities)       │
    │                                             │
    │   Report damage    ←→    Detect & Analyze   │
    │   Track repairs    ←→    Prioritize & Plan  │
    │   Hold accountable ←→    Execute & Report   │
    │                                             │
    └──────────────┬──────────────┬───────────────┘
                   │              │
                   ▼              ▼
              ┌────────────────────────┐
              │   SHARED BACKEND API   │
              │   FastAPI + YOLOv8     │
              │   PostgreSQL + Redis   │
              └────────────────────────┘
```

---

## APP 1: 🏛️ GOVERNMENT COMMAND CENTER (Web Dashboard)
**What we already built** — enhanced further.

### Who uses it?
- Municipal engineers
- PWD (Public Works Department) officers
- Government inspectors
- City administration

### Features
| Feature | Status | Description |
|---------|--------|-------------|
| AI Damage Detection | ✅ DONE | Upload image → YOLOv8 detects cracks/potholes |
| Severity Scoring | ✅ DONE | Composite score with explainable AI |
| Cost Estimation (₹) | ✅ DONE | Repair method, time, crew, INR cost |
| Priority Ranking | ✅ DONE | Urgency-based "what to fix first" |
| Repair Plan Generator | ✅ DONE | One-click daily action plan |
| Before vs After Cost | ✅ DONE | Fix now vs ignore comparison |
| Export Report | ✅ DONE | Printable HTML report |
| Dashboard Analytics | ✅ DONE | Charts, trends, severity distribution |
| Geo-tagged Map | 🔨 TODO | Map view of all reported damage |
| Batch Processing | 🔨 TODO | Upload multiple images at once |
| Historical Tracking | 🔨 TODO | Track damage over time |
| Contractor Assignment | 💡 FUTURE | Assign repair crews to locations |

### Data Flow
```
Inspector uploads image
    → AI detects damage (D00, D10, D20, D40, spalling, leak, corrosion)
    → Severity scored (0-100)
    → Cost estimated (₹ INR)
    → Priority ranked
    → Appears on command center dashboard
    → Repair plan generated
    → Report exported for action
```

---

## APP 2: 📱 PUBLIC TRANSPARENCY APP (Mobile APK)
**The killer feature that wins the hackathon.**

### Who uses it?
- Citizens / commuters
- Journalists
- NGOs / activists
- Anyone affected by bad roads

### Core Screens

#### 1. 🗺️ LIVE POTHOLE MAP (Home Screen)
```
┌────────────────────────────────┐
│  🗺️ [FULL SCREEN MAP]          │
│                                │
│     📍 Red pin = Unfixed       │
│     📍 Orange pin = In progress│
│     📍 Green pin = Fixed       │
│                                │
│  ┌──────────────────────┐      │
│  │ 🔍 Search location   │      │
│  └──────────────────────┘      │
│                                │
│  [Filter: All | Critical | New]│
│                                │
│  ┌──────────────────────────┐  │
│  │ Nearest: Pothole 2.3km ↗ │  │
│  │ Reported 3 days ago       │  │
│  │ Status: NOT FIXED ❌      │  │
│  └──────────────────────────┘  │
│                                │
│     [ 📸 REPORT DAMAGE ]       │
│     (Big floating button)      │
└────────────────────────────────┘
```

#### 2. 📸 REPORT DAMAGE (Camera Screen)
```
User flow:
1. Tap "Report Damage" button
2. Camera opens → take photo of pothole/crack
3. AI auto-detects damage type + severity
4. GPS auto-captures location
5. User adds optional description
6. Submit → appears on public map instantly
7. Government dashboard gets notified
```

#### 3. 📊 TRANSPARENCY DASHBOARD
```
┌────────────────────────────────┐
│  Government Performance Score  │
│         ██████░░░░ 62%         │
│                                │
│  ┌──────┐ ┌──────┐ ┌──────┐   │
│  │ 847  │ │ 523  │ │ 324  │   │
│  │Total │ │Fixed │ │Pending│   │
│  │Report│ │  ✅  │ │  ⏳  │   │
│  └──────┘ └──────┘ └──────┘   │
│                                │
│  Average Fix Time: 12.3 days   │
│  Fastest Fix: 2 days           │
│  Longest Pending: 89 days ⚠️   │
│                                │
│  📈 Monthly Trend              │
│  ▁▃▅▇█▇▅▃▁ (reports)          │
│  ▁▂▃▅▇█▇▅▃ (fixes)            │
│                                │
│  🏆 Ward Rankings              │
│  #1 Ward A — 89% fixed        │
│  #2 Ward B — 76% fixed        │
│  #3 Ward C — 45% fixed ⚠️     │
│                                │
│  [ Share Stats 📤 ]            │
└────────────────────────────────┘
```

#### 4. 📋 MY REPORTS (Profile)
```
- List of all reports by this user
- Status tracking (Submitted → Acknowledged → In Progress → Fixed)
- Push notifications when status changes
- "Upvote" existing reports (more votes = higher priority)
```

### Why This Wins
```
Normal team:  "We detect potholes"
You:          "We detect potholes AND 
               hold the government accountable 
               with public transparency data"
```

---

## TECHNICAL ARCHITECTURE

```
┌─────────────┐     ┌─────────────┐
│  📱 Public   │     │  🏛️ Govt    │
│  React Native│     │  React Web  │
│  (APK/iOS)  │     │  (Dashboard)│
└──────┬──────┘     └──────┬──────┘
       │                    │
       └────────┬───────────┘
                │
         ┌──────▼──────┐
         │  FastAPI     │
         │  Backend     │
         │              │
         │ /detect      │  ← AI inference (Roboflow/YOLO)
         │ /report      │  ← Public damage reports
         │ /reports/map │  ← Geo data for map
         │ /stats/govt  │  ← Govt performance metrics  
         │ /repair-plan │  ← Priority + cost
         │ /alerts      │  ← Push notifications
         └──────┬──────┘
                │
         ┌──────▼──────┐
         │  Database    │
         │  PostgreSQL  │
         │  + PostGIS   │  ← Geo queries
         │  + Redis     │  ← Caching + real-time
         └─────────────┘
```

### Tech Stack
| Component | Technology | Why |
|-----------|-----------|-----|
| Public App | React Native + Expo | Cross-platform APK + iOS |
| Govt Dashboard | React + Vite + Tailwind | Already built |
| Backend | FastAPI (Python) | Already built |
| AI Model | YOLOv8/YOLO26 via Roboflow | Already trained |
| Database | PostgreSQL + PostGIS | Geo queries for map |
| Maps | Google Maps API / Leaflet | Pin visualization |
| Push Notifications | Firebase Cloud Messaging | Status updates |
| File Storage | Cloudinary / S3 | Image uploads |
| Hosting | Vercel (web) + Railway (API) | Free tier |

---

## 48-HOUR HACKATHON PLAN

### What to demo tomorrow (MUST HAVE):
1. ✅ Government dashboard with real AI detection
2. ✅ Cost estimation + repair plan
3. ✅ Explainable AI
4. 🔨 Public app mockup/prototype (can be Figma or basic React Native)
5. 🔨 Map with reported damage pins
6. 🔨 Transparency stats (even with mock data)

### What to show as "roadmap" in presentation:
- Mobile APK for citizens
- Real-time government accountability
- Ward-level performance rankings
- Push notification system
- Integration with existing 311/grievance systems

---

## PRESENTATION HOOK

> "Every year, Indian municipalities spend ₹33,000 crore on road repairs.
> Yet 73% of potholes are never fixed.
> 
> We built TWO systems:
> One that tells the government WHAT to fix.
> One that tells the PUBLIC what they HAVEN'T fixed.
> 
> Transparency drives accountability.
> Accountability drives action.
> Action saves lives."

---

## JUDGE-WINNING DIFFERENTIATOR

| What others do | What you do |
|---------------|-------------|
| Detect damage | Detect + Estimate cost + Prioritize |
| Show results | Generate actionable repair plans |
| Dashboard only | Dashboard + Public transparency app |
| Tech demo | Government-ready product |
| "AI accuracy" | "Saves ₹2 lakh per road if fixed early" |
| One-way system | Two-way: govt ↔ citizens accountability loop |
