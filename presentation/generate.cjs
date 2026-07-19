const pptxgen = require("pptxgenjs");
const pptx = new pptxgen();

// ── Sovereign Intelligence Theme ──
const BG = "0E0E10";
const BG_CARD = "1C1B1D";
const BG_CARD_LIGHT = "26252A";
const EMERALD = "4EDEA3";
const EMERALD_DEEP = "10B981";
const CYAN = "5DE6FF";
const VIOLET = "A78BFA";
const AMBER = "FFA94D";
const RED = "FF6B6B";
const GOLD = "FFD76B";
const WHITE = "E5E1E4";
const MUTED = "BBCABF";
const DIM = "7A7872";
const BORDER = "2A2A2C";

pptx.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 inches
pptx.author = "Saud Satopay";
pptx.company = "NIRMAN Hackathon 2026";
pptx.subject = "AI Infrastructure Damage Detection";
pptx.title = "CRACKWATCH — Smart Infrastructure Command Center";

pptx.defineSlideMaster({
  title: "DARK_MASTER",
  background: { color: BG },
  objects: [
    { rect: { x: 0, y: 0, w: "100%", h: 0.08, fill: { color: EMERALD } } },
    { text: { text: "CRACKWATCH", options: { x: 11.8, y: 7.1, w: 1.5, h: 0.3, color: DIM, fontSize: 9, fontFace: "Calibri", bold: true, align: "right" } } },
  ],
});

// Helper: create a card with border
function card(slide, x, y, w, h, fill = BG_CARD) {
  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h,
    fill: { color: fill },
    line: { color: BORDER, width: 1 },
    rectRadius: 0.12,
  });
}

// Helper: slide title + emerald underline
function title(slide, text, sub) {
  slide.addText(text, {
    x: 0.6, y: 0.45, w: 12.1, h: 0.7,
    color: WHITE, fontSize: 34, bold: true, fontFace: "Calibri",
  });
  if (sub) {
    slide.addText(sub, {
      x: 0.6, y: 1.15, w: 12.1, h: 0.4,
      color: MUTED, fontSize: 14, fontFace: "Calibri",
    });
  }
}

// Helper: tag label
function tag(slide, x, y, text, color) {
  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x, y, w: 1.4, h: 0.3,
    fill: { color: color, transparency: 87 },
    line: { color: color, width: 0.75 },
    rectRadius: 0.08,
  });
  slide.addText(text, {
    x, y, w: 1.4, h: 0.3,
    color, fontSize: 9, bold: true, fontFace: "Calibri", align: "center", charSpacing: 1,
  });
}

// ════════════════════════════════════════════════
// SLIDE 1: Title
// ════════════════════════════════════════════════
let slide = pptx.addSlide({ masterName: "DARK_MASTER" });

// Background accent glow
slide.addShape(pptx.shapes.OVAL, {
  x: 9, y: -2, w: 6, h: 6,
  fill: { color: EMERALD, transparency: 92 }, line: { color: EMERALD, transparency: 100 },
});
slide.addShape(pptx.shapes.OVAL, {
  x: -2, y: 5, w: 5, h: 5,
  fill: { color: CYAN, transparency: 94 }, line: { color: CYAN, transparency: 100 },
});

// Tag
slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
  x: 0.8, y: 1.2, w: 2.4, h: 0.4, fill: { color: EMERALD, transparency: 91 }, line: { color: EMERALD, width: 1 }, rectRadius: 0.2,
});
slide.addText("🏆 NIRMAN HACKATHON 2026", {
  x: 0.8, y: 1.2, w: 2.4, h: 0.4, color: EMERALD, fontSize: 10, bold: true, fontFace: "Calibri", align: "center", charSpacing: 1,
});

// Logo text
slide.addText(
  [
    { text: "CRACK", options: { color: WHITE, fontSize: 96, bold: true, fontFace: "Calibri" } },
    { text: "WATCH", options: { color: EMERALD, fontSize: 96, bold: true, fontFace: "Calibri" } },
  ],
  { x: 0.6, y: 1.9, w: 12, h: 1.6 }
);

// Subtitle
slide.addText("AI-Powered Smart Infrastructure Command Center", {
  x: 0.8, y: 3.6, w: 11, h: 0.6, color: MUTED, fontSize: 24, fontFace: "Calibri",
});

// Tagline
slide.addText("Detect damage before it becomes disaster.", {
  x: 0.8, y: 4.3, w: 11, h: 0.5,
  color: EMERALD, fontSize: 18, italic: true, fontFace: "Calibri",
});

// Feature pills
const pills = [
  "🏛️ Govt Dashboard", "📱 Citizen PWA", "💬 WhatsApp Bot",
  "🤖 3 AI Models", "🏆 Gamified", "🛡️ Fraud-Proof",
];
pills.forEach((p, i) => {
  const col = i % 3;
  const row = Math.floor(i / 3);
  const x = 0.8 + col * 2.3;
  const y = 5.3 + row * 0.55;
  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x, y, w: 2.1, h: 0.45, fill: { color: BG_CARD }, line: { color: BORDER, width: 1 }, rectRadius: 0.1,
  });
  slide.addText(p, { x, y, w: 2.1, h: 0.45, color: WHITE, fontSize: 10, bold: true, fontFace: "Calibri", align: "center" });
});

// Footer
slide.addText("Saud Satopay  •  Amity University Mumbai  •  April 15-17, 2026  •  Problem Statement #4", {
  x: 0.6, y: 6.8, w: 12.1, h: 0.3, color: DIM, fontSize: 11, fontFace: "Calibri",
});

// ════════════════════════════════════════════════
// SLIDE 2: The Problem
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "The Problem",
  "India has 6.4 million km of roads. Manual inspection is slow, expensive, and dangerous.");

slide.addText("Every year, thousands of accidents happen due to undetected road damage.", {
  x: 0.6, y: 1.55, w: 12.1, h: 0.4, color: DIM, fontSize: 13, italic: true, fontFace: "Calibri",
});

// Stats grid — 4 cards
const problemStats = [
  { num: "₹33,000 Cr", label: "Annual road repair budget", color: AMBER, icon: "💰" },
  { num: "73%", label: "Potholes never fixed", color: RED, icon: "⚠️" },
  { num: "11,000+", label: "Deaths from road damage / yr", color: RED, icon: "☠️" },
  { num: "30+ days", label: "Avg complaint resolution", color: AMBER, icon: "⏱️" },
];
problemStats.forEach((s, i) => {
  const x = 0.6 + i * 3.1;
  card(slide, x, 2.3, 2.9, 2.3);
  slide.addText(s.icon, { x: x + 0.3, y: 2.5, w: 0.7, h: 0.5, fontSize: 28, align: "left" });
  slide.addText(s.num, { x, y: 3.0, w: 2.9, h: 0.7, color: s.color, fontSize: 30, bold: true, fontFace: "Calibri", align: "center" });
  slide.addText(s.label, { x: x + 0.15, y: 3.8, w: 2.6, h: 0.6, color: MUTED, fontSize: 12, fontFace: "Calibri", align: "center" });
});

// Hook quote
card(slide, 0.6, 5.0, 12.1, 1.8, "0D2319");
slide.addText("“What if AI could detect these issues, estimate cost, AND hold the government accountable — all before a single accident happens?”", {
  x: 1.0, y: 5.1, w: 11.3, h: 1.6, color: EMERALD, fontSize: 20, bold: true, italic: true, fontFace: "Calibri", align: "center", valign: "middle",
});

// ════════════════════════════════════════════════
// SLIDE 3: Our Solution
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "Our Solution: CRACKWATCH",
  "Not just detection — a full accountability loop from citizen to city hall.");

// 4 pillar cards in a row
const pillars = [
  { icon: "🤖", h: "AI Detection", d: "3-model pipeline detects 10+ damage types in 757ms. Fully offline.", color: EMERALD },
  { icon: "💰", h: "Cost Engine", d: "INR estimates, repair methods, crew requirements, urgency tags.", color: CYAN },
  { icon: "🔮", h: "Predictive", d: "'This road fails in X days' with monsoon acceleration factor.", color: AMBER },
  { icon: "🏆", h: "Gamified", d: "Citizens earn XP, coins, badges — compete to fix their city.", color: GOLD },
];
pillars.forEach((p, i) => {
  const x = 0.6 + i * 3.1;
  card(slide, x, 1.9, 2.9, 2.8);
  slide.addText(p.icon, { x: x + 0.3, y: 2.05, w: 0.7, h: 0.7, fontSize: 32, align: "left" });
  slide.addText(p.h, { x: x + 0.3, y: 2.8, w: 2.5, h: 0.5, color: p.color, fontSize: 18, bold: true, fontFace: "Calibri" });
  slide.addText(p.d, { x: x + 0.3, y: 3.3, w: 2.5, h: 1.3, color: MUTED, fontSize: 12, fontFace: "Calibri", lineSpacingMultiple: 1.3 });
});

// Bottom differentiator
card(slide, 0.6, 5.0, 12.1, 1.9);
slide.addText("What makes us different", {
  x: 1.0, y: 5.15, w: 11, h: 0.4, color: DIM, fontSize: 12, bold: true, fontFace: "Calibri", charSpacing: 2,
});
slide.addText([
  { text: "Others say: ", options: { color: DIM, fontSize: 16, fontFace: "Calibri" } },
  { text: '"We detect potholes."', options: { color: MUTED, fontSize: 16, italic: true, fontFace: "Calibri" } },
], { x: 1.0, y: 5.55, w: 11, h: 0.45 });
slide.addText([
  { text: "We say: ", options: { color: EMERALD, fontSize: 18, bold: true, fontFace: "Calibri" } },
  { text: '"We tell governments EXACTLY what to fix tomorrow, at what cost, and make sure they don\'t ignore it."', options: { color: WHITE, fontSize: 18, bold: true, fontFace: "Calibri" } },
], { x: 1.0, y: 6.05, w: 11, h: 0.75 });

// ════════════════════════════════════════════════
// SLIDE 4: Dual Platform Architecture
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "Dual Platform Architecture",
  "Two apps. One backend. A complete citizen ↔ government accountability loop.");

// Left: Govt App
card(slide, 0.6, 1.9, 5.9, 4.5);
slide.addText("🏛️", { x: 0.9, y: 2.1, w: 0.7, h: 0.6, fontSize: 32, align: "left" });
slide.addText("GOVERNMENT APP", { x: 1.7, y: 2.1, w: 4.5, h: 0.35, color: EMERALD, fontSize: 11, bold: true, fontFace: "Calibri", charSpacing: 2 });
slide.addText("Command Center", { x: 1.7, y: 2.45, w: 4.5, h: 0.45, color: WHITE, fontSize: 22, bold: true, fontFace: "Calibri" });
slide.addText("React + Vite web dashboard for inspectors & PWD officers.", {
  x: 0.9, y: 3.1, w: 5.3, h: 0.4, color: MUTED, fontSize: 12, fontFace: "Calibri",
});
const govFeatures = [
  "• AI damage detection & severity scoring",
  "• INR cost estimation + repair methods",
  "• Priority-ranked action plans",
  "• Reports map with admin controls",
  "• Video & live camera inference",
  "• Predictive maintenance forecasts",
  "• Wall of Shame (contractor accountability)",
];
govFeatures.forEach((f, i) => {
  slide.addText(f, { x: 0.9, y: 3.55 + i * 0.35, w: 5.3, h: 0.3, color: WHITE, fontSize: 12, fontFace: "Calibri" });
});

// Right: Citizen App
card(slide, 6.8, 1.9, 5.9, 4.5);
slide.addText("📱", { x: 7.1, y: 2.1, w: 0.7, h: 0.6, fontSize: 32, align: "left" });
slide.addText("CITIZEN APP", { x: 7.9, y: 2.1, w: 4.5, h: 0.35, color: CYAN, fontSize: 11, bold: true, fontFace: "Calibri", charSpacing: 2 });
slide.addText("Public PWA + WhatsApp", { x: 7.9, y: 2.45, w: 4.5, h: 0.45, color: WHITE, fontSize: 22, bold: true, fontFace: "Calibri" });
slide.addText("Phone-shaped PWA + WhatsApp bot — no install needed.", {
  x: 7.1, y: 3.1, w: 5.3, h: 0.4, color: MUTED, fontSize: 12, fontFace: "Calibri",
});
const citFeatures = [
  "• Photo + GPS damage reporting",
  "• Live pothole map (7 unfixed, 3 fixed…)",
  "• Pothole-aware navigation",
  "• Pothole Hunter leaderboard",
  "• Civic Coins + 13 achievement badges",
  "• AI Challenge game (+50 XP)",
  "• WhatsApp reporting (500M users)",
];
citFeatures.forEach((f, i) => {
  slide.addText(f, { x: 7.1, y: 3.55 + i * 0.35, w: 5.3, h: 0.3, color: WHITE, fontSize: 12, fontFace: "Calibri" });
});

// Bottom: shared infra
card(slide, 0.6, 6.55, 12.1, 0.65);
slide.addText("⚙️  Shared FastAPI Backend  •  YOLOv8 AI Pipeline  •  JWT Auth  •  Twilio WhatsApp  •  Fully Offline", {
  x: 0.6, y: 6.55, w: 12.1, h: 0.65, color: EMERALD, fontSize: 13, bold: true, fontFace: "Calibri", align: "center", valign: "middle",
});

// ════════════════════════════════════════════════
// SLIDE 5: 🆕 WhatsApp Bot — SHOWSTOPPER
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "WhatsApp Bot  💬  Zero App Install",
  "Citizens report damage via WhatsApp — the platform they already have.");

// NEW tag
tag(slide, 11.1, 0.55, "⭐ NEW", GOLD);

// Left: the why
card(slide, 0.6, 1.7, 5.9, 5.1);
slide.addText("Why this is groundbreaking", {
  x: 0.9, y: 1.9, w: 5.3, h: 0.4, color: EMERALD, fontSize: 11, bold: true, fontFace: "Calibri", charSpacing: 2,
});
slide.addText("500,000,000", {
  x: 0.9, y: 2.4, w: 5.3, h: 0.9, color: WHITE, fontSize: 44, bold: true, fontFace: "Calibri",
});
slide.addText("WhatsApp users in India can report damage right now.", {
  x: 0.9, y: 3.3, w: 5.3, h: 0.5, color: MUTED, fontSize: 14, fontFace: "Calibri",
});

const bullets = [
  { k: "❌ No", v: "App store install" },
  { k: "❌ No", v: "Account signup, no password" },
  { k: "❌ No", v: "Learning curve — it's already WhatsApp" },
  { k: "✅", v: "Works on any phone (even feature phones)" },
  { k: "✅", v: "Native location share for GPS accuracy" },
];
bullets.forEach((b, i) => {
  slide.addText([
    { text: b.k + "  ", options: { color: b.k.startsWith("❌") ? RED : EMERALD, fontSize: 13, bold: true, fontFace: "Calibri" } },
    { text: b.v, options: { color: WHITE, fontSize: 13, fontFace: "Calibri" } },
  ], { x: 0.9, y: 4.0 + i * 0.45, w: 5.3, h: 0.4 });
});

slide.addText("Powered by Twilio + FastAPI webhook", {
  x: 0.9, y: 6.4, w: 5.3, h: 0.3, color: DIM, fontSize: 11, italic: true, fontFace: "Calibri",
});

// Right: WhatsApp conversation mockup
card(slide, 6.9, 1.7, 5.8, 5.1, "111B12");
slide.addText("Live conversation", {
  x: 7.2, y: 1.85, w: 5.2, h: 0.35, color: DIM, fontSize: 10, bold: true, fontFace: "Calibri", charSpacing: 2,
});

// User msg 1 (photo)
slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
  x: 9.5, y: 2.3, w: 3.0, h: 0.7, fill: { color: "005C4B" }, line: { color: "005C4B" }, rectRadius: 0.1,
});
slide.addText("📸 [Pothole Photo]", { x: 9.55, y: 2.35, w: 2.9, h: 0.3, color: WHITE, fontSize: 10, bold: true, fontFace: "Calibri" });
slide.addText("2:27 am  ✓✓", { x: 9.55, y: 2.65, w: 2.9, h: 0.3, color: MUTED, fontSize: 8, fontFace: "Calibri", align: "right" });

// Bot reply 1
slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
  x: 7.2, y: 3.15, w: 3.6, h: 1.1, fill: { color: "202C33" }, line: { color: "202C33" }, rectRadius: 0.1,
});
slide.addText("📸 Got your photo!\n🤖 🟡 Alligator Crack (87%)\n📍 Now share your location", {
  x: 7.3, y: 3.2, w: 3.4, h: 1.0, color: WHITE, fontSize: 10, fontFace: "Calibri", lineSpacingMultiple: 1.2,
});

// User msg 2 (location)
slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
  x: 9.5, y: 4.4, w: 3.0, h: 0.55, fill: { color: "005C4B" }, line: { color: "005C4B" }, rectRadius: 0.1,
});
slide.addText("📍 Location shared", { x: 9.55, y: 4.43, w: 2.9, h: 0.5, color: WHITE, fontSize: 10, bold: true, fontFace: "Calibri", valign: "middle" });

// Bot reply 2
slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
  x: 7.2, y: 5.1, w: 4.2, h: 1.6, fill: { color: "202C33" }, line: { color: "202C33" }, rectRadius: 0.1,
});
slide.addText([
  { text: "✅ Report RPT-8B20EA submitted!\n", options: { color: EMERALD, fontSize: 10, bold: true } },
  { text: "🟡 Alligator Crack · 66/100 severity\n", options: { color: WHITE, fontSize: 9 } },
  { text: "💰 Est. repair: ₹14,881\n", options: { color: WHITE, fontSize: 9 } },
  { text: "🔧 Method: Routing and sealing\n", options: { color: WHITE, fontSize: 9 } },
  { text: "🏆 +50 XP · +5 coins · New badge: First Report", options: { color: GOLD, fontSize: 9, bold: true } },
], { x: 7.3, y: 5.15, w: 4.0, h: 1.5, fontFace: "Calibri", lineSpacingMultiple: 1.2 });

// ════════════════════════════════════════════════
// SLIDE 6: Multi-Model AI Pipeline
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "Multi-Model AI Pipeline",
  "3 specialized models running in parallel. Zero cloud dependency. Fully offline.");

const models = [
  { n: "YOLOv8s-RDD", acc: "72.6%", role: "Road Damage Detection", d: "Longitudinal, Transverse, Alligator Crack, Pothole", color: EMERALD },
  { n: "YOLOv8s-CrackSeg", acc: "85%+", role: "Building Crack Segmentation", d: "Wall cracks, apartment cracks, concrete fractures", color: CYAN },
  { n: "OpenCV Pipeline", acc: "CV-based", role: "Supplementary Detection", d: "Spalling, water leaks, corrosion, pipeline breaks", color: AMBER },
];
models.forEach((m, i) => {
  const x = 0.6 + i * 4.15;
  card(slide, x, 1.8, 4.0, 4.0);
  slide.addText(m.n, { x: x + 0.3, y: 2.0, w: 3.5, h: 0.5, color: m.color, fontSize: 18, bold: true, fontFace: "Calibri" });
  slide.addText(m.role, { x: x + 0.3, y: 2.5, w: 3.5, h: 0.4, color: DIM, fontSize: 11, fontFace: "Calibri" });
  slide.addText(m.acc, { x: x + 0.3, y: 3.0, w: 3.5, h: 0.8, color: WHITE, fontSize: 42, bold: true, fontFace: "Calibri" });
  slide.addText(m.d, { x: x + 0.3, y: 3.9, w: 3.5, h: 1.0, color: MUTED, fontSize: 12, fontFace: "Calibri", lineSpacingMultiple: 1.3 });
  // mini sector bar
  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: x + 0.3, y: 5.0, w: 3.5, h: 0.35, fill: { color: m.color, transparency: 92 }, line: { color: m.color, width: 1 }, rectRadius: 0.05,
  });
  slide.addText(i === 0 ? "🛣️ Road & Highway" : i === 1 ? "🏢 Building & Structure" : "🔧 Pipeline & Bridge", {
    x: x + 0.3, y: 5.0, w: 3.5, h: 0.35, color: m.color, fontSize: 11, bold: true, fontFace: "Calibri", align: "center",
  });
});

// Bottom specs bar
card(slide, 0.6, 6.1, 12.1, 0.95);
slide.addText([
  { text: "⚡ 757ms", options: { color: EMERALD, fontSize: 16, bold: true, fontFace: "Calibri" } },
  { text: "  inference  •  ", options: { color: MUTED, fontSize: 14, fontFace: "Calibri" } },
  { text: "🎯 10+", options: { color: EMERALD, fontSize: 16, bold: true, fontFace: "Calibri" } },
  { text: "  damage types  •  ", options: { color: MUTED, fontSize: 14, fontFace: "Calibri" } },
  { text: "🌐 0 API calls", options: { color: EMERALD, fontSize: 16, bold: true, fontFace: "Calibri" } },
  { text: "  — runs on $0/month", options: { color: MUTED, fontSize: 14, fontFace: "Calibri" } },
], { x: 0.6, y: 6.1, w: 12.1, h: 0.95, align: "center", valign: "middle" });

// ════════════════════════════════════════════════
// SLIDE 7: Decision Engine — not just detection
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "Not Just Detection — A Decision Engine",
  "Every detection flows through a 6-stage pipeline into an actionable repair plan.");

// 6-stage flow
const stages = [
  { n: "1", h: "Detect", d: "YOLO + CV", color: EMERALD },
  { n: "2", h: "Score", d: "Severity 0-100", color: CYAN },
  { n: "3", h: "Rank", d: "Priority queue", color: VIOLET },
  { n: "4", h: "Cost", d: "INR estimate", color: AMBER },
  { n: "5", h: "Map", d: "Geo-tagged pin", color: GOLD },
  { n: "6", h: "Report", d: "Action plan", color: EMERALD },
];
stages.forEach((s, i) => {
  const x = 0.6 + i * 2.1;
  card(slide, x, 1.9, 1.95, 1.9);
  slide.addShape(pptx.shapes.OVAL, {
    x: x + 0.65, y: 2.1, w: 0.65, h: 0.65, fill: { color: s.color, transparency: 87 }, line: { color: s.color, width: 1.5 },
  });
  slide.addText(s.n, { x: x + 0.65, y: 2.1, w: 0.65, h: 0.65, color: s.color, fontSize: 18, bold: true, fontFace: "Calibri", align: "center", valign: "middle" });
  slide.addText(s.h, { x, y: 2.85, w: 1.95, h: 0.4, color: WHITE, fontSize: 14, bold: true, fontFace: "Calibri", align: "center" });
  slide.addText(s.d, { x, y: 3.3, w: 1.95, h: 0.4, color: DIM, fontSize: 10, fontFace: "Calibri", align: "center" });
  // arrow between stages
  if (i < 5) {
    slide.addText("→", { x: x + 1.95, y: 2.1, w: 0.15, h: 0.65, color: EMERALD, fontSize: 20, bold: true, align: "center", valign: "middle" });
  }
});

// Cost comparison
card(slide, 0.6, 4.2, 12.1, 2.7, "0D2319");
slide.addText("💰 The cost of delay — real numbers from our Repair Plan engine", {
  x: 0.9, y: 4.35, w: 11.5, h: 0.4, color: EMERALD, fontSize: 13, bold: true, fontFace: "Calibri", charSpacing: 1,
});

// Fix now column
slide.addText("FIX NOW", { x: 1.0, y: 4.9, w: 3.5, h: 0.35, color: EMERALD, fontSize: 11, bold: true, fontFace: "Calibri", charSpacing: 2 });
slide.addText("₹47,270", { x: 1.0, y: 5.25, w: 3.5, h: 0.8, color: EMERALD, fontSize: 40, bold: true, fontFace: "Calibri" });
slide.addText("Patch + sealant, 1 crew, 2 hours", { x: 1.0, y: 6.1, w: 3.5, h: 0.4, color: MUTED, fontSize: 11, fontFace: "Calibri" });

// vs arrow
slide.addText("vs", { x: 4.7, y: 5.35, w: 0.5, h: 0.6, color: DIM, fontSize: 22, italic: true, fontFace: "Calibri", align: "center" });

// Ignored column
slide.addText("IF IGNORED 6 MONTHS", { x: 5.3, y: 4.9, w: 4.0, h: 0.35, color: RED, fontSize: 11, bold: true, fontFace: "Calibri", charSpacing: 2 });
slide.addText("₹1,89,080", { x: 5.3, y: 5.25, w: 4.0, h: 0.8, color: RED, fontSize: 40, bold: true, fontFace: "Calibri" });
slide.addText("Full-depth repair, 3 crews, 8 hours", { x: 5.3, y: 6.1, w: 4.0, h: 0.4, color: MUTED, fontSize: 11, fontFace: "Calibri" });

// Savings column
slide.addText("YOU SAVE", { x: 9.5, y: 4.9, w: 3.0, h: 0.35, color: GOLD, fontSize: 11, bold: true, fontFace: "Calibri", charSpacing: 2 });
slide.addText("₹1,41,810", { x: 9.5, y: 5.25, w: 3.0, h: 0.8, color: GOLD, fontSize: 40, bold: true, fontFace: "Calibri" });
slide.addText("per road, per early detection", { x: 9.5, y: 6.1, w: 3.0, h: 0.4, color: MUTED, fontSize: 11, fontFace: "Calibri" });

// ════════════════════════════════════════════════
// SLIDE 8: 🆕 5-Layer Fraud Detection
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "5-Layer Fraud Detection",
  "Every citizen report is scored by 5 independent trust signals before it reaches the inspector.");

tag(slide, 11.1, 0.55, "⭐ NEW", GOLD);

const layers = [
  { icon: "📸", h: "Image Authenticity", d: "Moiré pattern, resolution, brightness, edge sharpness, color distribution, aspect ratio", weight: "30%" },
  { icon: "📍", h: "GPS Validation", d: "Range check, India bounds, spoof detection, null-island rejection", weight: "20%" },
  { icon: "🤖", h: "Content Relevance", d: "AI must actually find damage classes (not selfies, not cats)", weight: "30%" },
  { icon: "🔁", h: "Duplicate Detection", d: "50m Haversine radius — stops spamming the same pothole", weight: "10%" },
  { icon: "⏱️", h: "Rate Limiting", d: "10 reports / hour / user — prevents bot submissions", weight: "10%" },
];
layers.forEach((l, i) => {
  const x = 0.6 + (i % 3) * 4.15;
  const y = 1.9 + Math.floor(i / 3) * 2.15;
  card(slide, x, y, 4.0, 2.0);
  slide.addText(l.icon, { x: x + 0.3, y: y + 0.2, w: 0.7, h: 0.5, fontSize: 24, align: "left" });
  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: x + 3.0, y: y + 0.25, w: 0.75, h: 0.3, fill: { color: EMERALD, transparency: 91 }, line: { color: EMERALD, width: 0.75 }, rectRadius: 0.05,
  });
  slide.addText(l.weight, { x: x + 3.0, y: y + 0.25, w: 0.75, h: 0.3, color: EMERALD, fontSize: 10, bold: true, fontFace: "Calibri", align: "center" });
  slide.addText(l.h, { x: x + 0.3, y: y + 0.75, w: 3.5, h: 0.4, color: WHITE, fontSize: 15, bold: true, fontFace: "Calibri" });
  slide.addText(l.d, { x: x + 0.3, y: y + 1.15, w: 3.5, h: 0.75, color: MUTED, fontSize: 11, fontFace: "Calibri", lineSpacingMultiple: 1.3 });
});

// Verdict triage
card(slide, 4.75, 6.15, 8.0, 0.95);
slide.addText([
  { text: "≥70  →  ", options: { color: EMERALD, fontSize: 13, bold: true, fontFace: "Calibri" } },
  { text: "Auto-approve   ", options: { color: WHITE, fontSize: 13, fontFace: "Calibri" } },
  { text: "45-70  →  ", options: { color: AMBER, fontSize: 13, bold: true, fontFace: "Calibri" } },
  { text: "Flag for review   ", options: { color: WHITE, fontSize: 13, fontFace: "Calibri" } },
  { text: "<45  →  ", options: { color: RED, fontSize: 13, bold: true, fontFace: "Calibri" } },
  { text: "Block submission", options: { color: WHITE, fontSize: 13, fontFace: "Calibri" } },
], { x: 4.75, y: 6.15, w: 8.0, h: 0.95, align: "center", valign: "middle" });

// ════════════════════════════════════════════════
// SLIDE 9: 🆕 Predictive Maintenance
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "Predictive Maintenance",
  "We don't just find damage. We tell you when it will fail.");

tag(slide, 11.1, 0.55, "⭐ NEW", GOLD);

// Left: the prediction card
card(slide, 0.6, 1.9, 6.1, 5.1, "0D2319");
slide.addText("LIVE PREDICTION", { x: 0.9, y: 2.1, w: 5.3, h: 0.35, color: EMERALD, fontSize: 10, bold: true, fontFace: "Calibri", charSpacing: 2 });
slide.addText("Ghodbunder Rd, Thane", { x: 0.9, y: 2.5, w: 5.3, h: 0.5, color: WHITE, fontSize: 20, bold: true, fontFace: "Calibri" });
slide.addText("Alligator Crack · 66% severity now", { x: 0.9, y: 2.95, w: 5.3, h: 0.4, color: MUTED, fontSize: 13, fontFace: "Calibri" });

// Big prediction number
slide.addText("18 days", { x: 0.9, y: 3.5, w: 5.3, h: 1.0, color: AMBER, fontSize: 54, bold: true, fontFace: "Calibri" });
slide.addText("until critical failure", { x: 0.9, y: 4.55, w: 5.3, h: 0.4, color: MUTED, fontSize: 14, fontFace: "Calibri" });

// Urgency badge
slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
  x: 0.9, y: 5.1, w: 2.0, h: 0.4, fill: { color: RED, transparency: 87 }, line: { color: RED, width: 1 }, rectRadius: 0.1,
});
slide.addText("🔴 URGENT", { x: 0.9, y: 5.1, w: 2.0, h: 0.4, color: RED, fontSize: 11, bold: true, fontFace: "Calibri", align: "center", charSpacing: 1 });

slide.addText("+7% severity/week (monsoon factor 2.5×)", { x: 0.9, y: 5.65, w: 5.3, h: 0.4, color: MUTED, fontSize: 12, italic: true, fontFace: "Calibri" });
slide.addText("Cost if fixed now: ₹8,500\nCost if delayed 30 days: ₹23,000", { x: 0.9, y: 6.1, w: 5.3, h: 0.8, color: WHITE, fontSize: 12, fontFace: "Calibri", lineSpacingMultiple: 1.3 });

// Right: the factors
card(slide, 6.9, 1.9, 5.8, 5.1);
slide.addText("How the prediction engine works", { x: 7.2, y: 2.1, w: 5.2, h: 0.35, color: EMERALD, fontSize: 11, bold: true, fontFace: "Calibri", charSpacing: 2 });

const factors = [
  { h: "Damage progression rates", d: "Per type: growth mm/day, worsen %/week from empirical data" },
  { h: "Monsoon acceleration", d: "2.5× faster damage growth during Jun-Sep (India context)" },
  { h: "Severity timeline", d: "Predicted state at 1, 2, 4, 8, 12 weeks" },
  { h: "Cost projection delta", d: "Fix now vs delayed 1wk / 2wk / 1mo / 3mo" },
  { h: "Area-wide forecast", d: "Which zones will fail next — citywide view for PWD" },
];
factors.forEach((f, i) => {
  const y = 2.5 + i * 0.85;
  slide.addShape(pptx.shapes.OVAL, {
    x: 7.2, y: y + 0.05, w: 0.25, h: 0.25, fill: { color: EMERALD }, line: { color: EMERALD },
  });
  slide.addText(f.h, { x: 7.55, y: y, w: 5.0, h: 0.35, color: WHITE, fontSize: 13, bold: true, fontFace: "Calibri" });
  slide.addText(f.d, { x: 7.55, y: y + 0.32, w: 5.0, h: 0.45, color: MUTED, fontSize: 11, fontFace: "Calibri" });
});

// ════════════════════════════════════════════════
// SLIDE 10: 🆕 Gamification
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "Gamification  🏆  Citizens Compete to Fix Their City",
  "XP, Civic Coins, badges, and streaks turn civic duty into a game people actually play.");

tag(slide, 11.1, 0.55, "⭐ NEW", GOLD);

// Left: Pothole Hunter podium
card(slide, 0.6, 1.9, 6.1, 5.1);
slide.addText("🏆 POTHOLE HUNTER LEADERBOARD", { x: 0.9, y: 2.05, w: 5.5, h: 0.35, color: GOLD, fontSize: 10, bold: true, fontFace: "Calibri", charSpacing: 2 });

// Podium pillars
const podium = [
  { rank: "2", name: "Amit Kumar", xp: "2100 XP", color: "C0C0C0", h: 1.6, x: 1.0 },
  { rank: "1", name: "Saud Vinchu", xp: "3200 XP", color: GOLD, h: 2.1, x: 2.7 },
  { rank: "3", name: "Priya Sharma", xp: "1650 XP", color: "CD7F32", h: 1.3, x: 4.4 },
];
podium.forEach((p) => {
  const y = 6.7 - p.h;
  slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: p.x, y, w: 1.5, h: p.h, fill: { color: p.color, transparency: 88 }, line: { color: p.color, width: 1 }, rectRadius: 0.08,
  });
  slide.addShape(pptx.shapes.OVAL, {
    x: p.x + 0.45, y: y + 0.15, w: 0.6, h: 0.6, fill: { color: p.color }, line: { color: p.color },
  });
  slide.addText(p.rank, { x: p.x + 0.45, y: y + 0.15, w: 0.6, h: 0.6, color: "1C1B1D", fontSize: 22, bold: true, fontFace: "Calibri", align: "center", valign: "middle" });
  slide.addText(p.name, { x: p.x, y: y + 0.85, w: 1.5, h: 0.3, color: WHITE, fontSize: 11, bold: true, fontFace: "Calibri", align: "center" });
  slide.addText(p.xp, { x: p.x, y: y + 1.15, w: 1.5, h: 0.3, color: EMERALD, fontSize: 10, bold: true, fontFace: "Calibri", align: "center" });
});

// Right: features
const gameFeatures = [
  { icon: "🎯", h: "13 Badges", d: "Scout · Road Warrior · City Saver · AI Master · Streak badges" },
  { icon: "💰", h: "Civic Coins", d: "Earn for reports, verifications, streaks. Starting bonus: 50" },
  { icon: "🔥", h: "Daily Streaks", d: "3-day, 7-day, 30-day — bonus XP multipliers per streak day" },
  { icon: "🎮", h: "AI Challenge Game", d: "Guess damage type from scenario · +50 XP for correct answers" },
  { icon: "⚡", h: "Quests", d: "Daily + weekly — 'Report 5 potholes today', 'Find a critical road'" },
  { icon: "👥", h: "Community Verify", d: "Vote valid/invalid on reports. Verifiers earn XP + coins" },
];
gameFeatures.forEach((f, i) => {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const x = 6.9 + col * 2.95;
  const y = 1.9 + row * 1.75;
  card(slide, x, y, 2.8, 1.55);
  slide.addText(f.icon, { x: x + 0.2, y: y + 0.15, w: 0.6, h: 0.5, fontSize: 22, align: "left" });
  slide.addText(f.h, { x: x + 0.2, y: y + 0.7, w: 2.4, h: 0.35, color: WHITE, fontSize: 13, bold: true, fontFace: "Calibri" });
  slide.addText(f.d, { x: x + 0.2, y: y + 1.05, w: 2.4, h: 0.45, color: MUTED, fontSize: 9.5, fontFace: "Calibri", lineSpacingMultiple: 1.2 });
});

// ════════════════════════════════════════════════
// SLIDE 11: 🆕 Wall of Shame + Transparency
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "Transparency  ⚡  Accountability  ⚡  Action",
  "Public data + contractor-level tracking forces governments to act.");

// Left: Wall of Shame card
card(slide, 0.6, 1.9, 6.1, 5.1, "2A0F0F");
slide.addText("🔥  WALL OF SHAME", { x: 0.9, y: 2.05, w: 5.3, h: 0.4, color: RED, fontSize: 12, bold: true, fontFace: "Calibri", charSpacing: 2 });
slide.addText("Contractors ranked by negligence", { x: 0.9, y: 2.45, w: 5.3, h: 0.35, color: MUTED, fontSize: 12, italic: true, fontFace: "Calibri" });

const shame = [
  { rank: "#1", name: "PQR Contractors", score: "894", fix: "34%", unfixed: "12" },
  { rank: "#2", name: "ABC Constructions", score: "672", fix: "41%", unfixed: "9" },
  { rank: "#3", name: "XYZ Roadworks", score: "510", fix: "52%", unfixed: "6" },
];
shame.forEach((c, i) => {
  const y = 3.0 + i * 1.1;
  card(slide, 0.9, y, 5.5, 0.95, BG_CARD);
  slide.addText(c.rank, { x: 0.95, y: y + 0.1, w: 0.5, h: 0.4, color: RED, fontSize: 16, bold: true, fontFace: "Calibri" });
  slide.addText(c.name, { x: 1.4, y: y + 0.1, w: 3.0, h: 0.4, color: WHITE, fontSize: 13, bold: true, fontFace: "Calibri" });
  slide.addText(`${c.unfixed} unfixed · ${c.fix} fix rate`, { x: 1.4, y: y + 0.5, w: 3.0, h: 0.3, color: MUTED, fontSize: 10, fontFace: "Calibri" });
  slide.addText(c.score, { x: 4.5, y: y + 0.2, w: 1.8, h: 0.6, color: RED, fontSize: 22, bold: true, fontFace: "Calibri", align: "right" });
  slide.addText("NEGLIGENCE", { x: 4.5, y: y + 0.6, w: 1.8, h: 0.25, color: DIM, fontSize: 8, fontFace: "Calibri", align: "right", charSpacing: 1.5 });
});

slide.addText("Formula: severity × days unresolved × community votes", {
  x: 0.9, y: 6.5, w: 5.3, h: 0.35, color: DIM, fontSize: 10, italic: true, fontFace: "Calibri",
});

// Right: the accountability loop
card(slide, 6.9, 1.9, 5.8, 5.1);
slide.addText("THE ACCOUNTABILITY LOOP", { x: 7.2, y: 2.05, w: 5.2, h: 0.4, color: EMERALD, fontSize: 11, bold: true, fontFace: "Calibri", charSpacing: 2 });

const loop = [
  { n: "1", t: "Citizen photos pothole via WhatsApp or app" },
  { n: "2", t: "AI detects, fraud-checks, scores severity" },
  { n: "3", t: "Report appears on public map — VISIBLE TO ALL" },
  { n: "4", t: "Govt dashboard receives priority queue" },
  { n: "5", t: "Days unresolved compound negligence score" },
  { n: "6", t: "Govt fixes → citizen gets WhatsApp confirmation" },
];
loop.forEach((s, i) => {
  const y = 2.55 + i * 0.68;
  slide.addShape(pptx.shapes.OVAL, {
    x: 7.25, y: y + 0.05, w: 0.4, h: 0.4, fill: { color: EMERALD }, line: { color: EMERALD },
  });
  slide.addText(s.n, { x: 7.25, y: y + 0.05, w: 0.4, h: 0.4, color: "002113", fontSize: 14, bold: true, fontFace: "Calibri", align: "center", valign: "middle" });
  slide.addText(s.t, { x: 7.8, y: y, w: 4.7, h: 0.5, color: WHITE, fontSize: 12, fontFace: "Calibri", valign: "middle" });
  if (i < 5) {
    slide.addText("│", { x: 7.3, y: y + 0.4, w: 0.3, h: 0.3, color: EMERALD, fontSize: 14, align: "center" });
  }
});

// ════════════════════════════════════════════════
// SLIDE 12: Tech Stack
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "Tech Stack",
  "Hackathon-scale. Production-shaped. Zero cloud bills.");

const stack = [
  { h: "AI / ML", icon: "🤖", items: ["YOLOv8s-RDD", "YOLOv8s-CrackSeg", "OpenCV pipeline", "Ultralytics"], color: EMERALD },
  { h: "Backend", icon: "⚙️", items: ["Python 3.12", "FastAPI + Uvicorn", "JWT Authentication", "Pillow EXIF"], color: CYAN },
  { h: "Govt Frontend", icon: "🏛️", items: ["React 19 + Vite", "Tailwind v4", "shadcn/ui", "Framer Motion"], color: VIOLET },
  { h: "Public PWA", icon: "📱", items: ["React 19 + Vite", "Leaflet + routing", "HTTPS + capture=env", "Phone-frame UI"], color: AMBER },
  { h: "Integrations", icon: "🔌", items: ["Twilio WhatsApp", "ngrok tunnel", "OSRM routing", "OpenStreetMap"], color: GOLD },
  { h: "Data", icon: "📊", items: ["RDD2022 (4.8K imgs)", "HuggingFace models", "In-memory + file store", "Local inference"], color: RED },
];
stack.forEach((s, i) => {
  const col = i % 3;
  const row = Math.floor(i / 3);
  const x = 0.6 + col * 4.15;
  const y = 1.9 + row * 2.6;
  card(slide, x, y, 4.0, 2.4);
  slide.addText(s.icon, { x: x + 0.3, y: y + 0.2, w: 0.6, h: 0.5, fontSize: 22, align: "left" });
  slide.addText(s.h, { x: x + 0.95, y: y + 0.25, w: 2.9, h: 0.4, color: s.color, fontSize: 14, bold: true, fontFace: "Calibri" });
  s.items.forEach((it, k) => {
    slide.addText("• " + it, { x: x + 0.3, y: y + 0.85 + k * 0.35, w: 3.5, h: 0.3, color: WHITE, fontSize: 11, fontFace: "Calibri" });
  });
});

// ════════════════════════════════════════════════
// SLIDE 13: Impact & Scalability
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "Impact & Scalability",
  "Built for one city. Deployable to a billion people.");

// Big impact stats
const impact = [
  { big: "70%", small: "Reduction in inspection cost vs manual", color: EMERALD },
  { big: "4×", small: "Faster damage identification", color: CYAN },
  { big: "₹1.4L+", small: "Savings per road fixed early", color: GOLD },
  { big: "100%", small: "Public transparency on govt performance", color: AMBER },
];
impact.forEach((s, i) => {
  const x = 0.6 + i * 3.1;
  card(slide, x, 1.9, 2.9, 2.3);
  slide.addText(s.big, { x, y: 2.2, w: 2.9, h: 1.0, color: s.color, fontSize: 52, bold: true, fontFace: "Calibri", align: "center" });
  slide.addText(s.small, { x: x + 0.15, y: 3.3, w: 2.6, h: 0.8, color: MUTED, fontSize: 12, fontFace: "Calibri", align: "center", lineSpacingMultiple: 1.3 });
});

// Scalability bar
card(slide, 0.6, 4.5, 12.1, 2.3, "0D2319");
slide.addText("Why this scales to 1 billion users", { x: 0.9, y: 4.65, w: 11.5, h: 0.4, color: EMERALD, fontSize: 13, bold: true, fontFace: "Calibri", charSpacing: 2 });

const scaleReasons = [
  { icon: "🌐", h: "Zero cloud cost", d: "Fully offline inference — no AWS bills, no API quotas" },
  { icon: "💬", h: "WhatsApp native", d: "500M Indian users already have the 'app' installed" },
  { icon: "🔓", h: "Open source", d: "Forkable by any municipality. Re-skin, re-deploy" },
  { icon: "📡", h: "Offline-first", d: "Works without internet. Models run on-device" },
];
scaleReasons.forEach((r, i) => {
  const col = i % 4;
  const x = 0.9 + col * 3.0;
  slide.addText(r.icon, { x, y: 5.2, w: 0.6, h: 0.5, fontSize: 22, align: "left" });
  slide.addText(r.h, { x: x + 0.6, y: 5.25, w: 2.4, h: 0.3, color: WHITE, fontSize: 12, bold: true, fontFace: "Calibri" });
  slide.addText(r.d, { x: x + 0.6, y: 5.55, w: 2.3, h: 1.1, color: MUTED, fontSize: 10, fontFace: "Calibri", lineSpacingMultiple: 1.3 });
});

// ════════════════════════════════════════════════
// SLIDE 14: Live Demo Flow
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });
title(slide, "Live Demo — 3 Minutes",
  "Watch the full citizen ↔ government loop happen in real time.");

const demo = [
  { n: "1", t: "0:00 · Hook", d: "₹33,000 Cr spent. 73% of potholes never fixed. ₹1.4L saved per early fix." },
  { n: "2", t: "0:25 · Govt login & upload", d: "Log in, upload road photo → 757ms AI detection → severity + cost + repair plan." },
  { n: "3", t: "0:55 · WhatsApp bot demo", d: "Send pothole photo from my phone to Twilio number. Bot replies with AI analysis in 3s." },
  { n: "4", t: "1:30 · Pin appears on govt map", d: "Report instantly visible on inspector's map. Mark 'Fixed'. Citizen gets confirmation." },
  { n: "5", t: "1:55 · Predictive maintenance", d: "Show 'fails in 18 days' + cost delta if delayed. Forward-looking vs reactive." },
  { n: "6", t: "2:20 · Gamification", d: "Login as saud/123 → Lv.6, 10 badges, #1 leaderboard, 21-day streak." },
  { n: "7", t: "2:45 · Wall of Shame + closing", d: "Contractor ranked by negligence. 'Transparency drives accountability.'" },
];
demo.forEach((s, i) => {
  const y = 1.8 + i * 0.75;
  card(slide, 0.6, y, 12.1, 0.65);
  slide.addShape(pptx.shapes.OVAL, {
    x: 0.85, y: y + 0.13, w: 0.4, h: 0.4, fill: { color: EMERALD }, line: { color: EMERALD },
  });
  slide.addText(s.n, { x: 0.85, y: y + 0.13, w: 0.4, h: 0.4, color: "002113", fontSize: 14, bold: true, fontFace: "Calibri", align: "center", valign: "middle" });
  slide.addText(s.t, { x: 1.45, y: y + 0.07, w: 3.0, h: 0.3, color: EMERALD, fontSize: 12, bold: true, fontFace: "Calibri" });
  slide.addText(s.d, { x: 1.45, y: y + 0.35, w: 11.0, h: 0.3, color: WHITE, fontSize: 11, fontFace: "Calibri" });
});

// ════════════════════════════════════════════════
// SLIDE 15: Thank You / Close
// ════════════════════════════════════════════════
slide = pptx.addSlide({ masterName: "DARK_MASTER" });

// Background glows
slide.addShape(pptx.shapes.OVAL, {
  x: -2, y: -2, w: 7, h: 7,
  fill: { color: EMERALD, transparency: 92 }, line: { color: EMERALD, transparency: 100 },
});
slide.addShape(pptx.shapes.OVAL, {
  x: 9, y: 4, w: 6, h: 6,
  fill: { color: CYAN, transparency: 94 }, line: { color: CYAN, transparency: 100 },
});

slide.addText(
  [
    { text: "CRACK", options: { color: WHITE, fontSize: 80, bold: true, fontFace: "Calibri" } },
    { text: "WATCH", options: { color: EMERALD, fontSize: 80, bold: true, fontFace: "Calibri" } },
  ],
  { x: 0.6, y: 1.4, w: 12.1, h: 1.4, align: "center" }
);
slide.addText("Smart Infrastructure for All", {
  x: 0.6, y: 2.9, w: 12.1, h: 0.6, color: MUTED, fontSize: 22, fontFace: "Calibri", align: "center",
});

// Big thanks
slide.addText("Thank you.", {
  x: 0.6, y: 3.9, w: 12.1, h: 0.8, color: EMERALD, fontSize: 42, bold: true, italic: true, fontFace: "Calibri", align: "center",
});
slide.addText("Questions?", {
  x: 0.6, y: 4.75, w: 12.1, h: 0.5, color: WHITE, fontSize: 22, fontFace: "Calibri", align: "center",
});

// Repo card
card(slide, 3.5, 5.7, 6.3, 0.9, "0D2319");
slide.addText("📦  github.com/SaudSatopay/CrackWatch-NirmanHackathon", {
  x: 3.5, y: 5.7, w: 6.3, h: 0.9, color: EMERALD, fontSize: 14, bold: true, fontFace: "Calibri", align: "center", valign: "middle",
});

slide.addText("Saud Satopay  •  NIRMAN Hackathon 2026  •  Amity University Mumbai", {
  x: 0.6, y: 6.9, w: 12.1, h: 0.35, color: DIM, fontSize: 11, fontFace: "Calibri", align: "center",
});

// ── Save ──
pptx.writeFile({ fileName: "CRACKWATCH_Presentation.pptx" })
  .then((f) => console.log(`✅ Saved: ${f}`))
  .catch((e) => { console.error(e); process.exit(1); });
