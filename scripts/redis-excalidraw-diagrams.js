#!/usr/bin/env node
/**
 * Generate Excalidraw diagrams for Redis 7 Use Cases.
 * Each use case is a frame (~900px wide) with boxes + arrows.
 *
 * Usage: node scripts/redis-excalidraw-diagrams.js
 * Output: Excalidraw .md content to stdout
 */

let seedCounter = 1;
function makeId() {
  return Array.from({ length: 10 }, () =>
    (Math.random().toString(36) + "000").charAt(2)
  ).join("");
}
function makeSeed() {
  return seedCounter++ * 127 + Math.floor(Math.random() * 1e6);
}

const FRAME_W = 920;
const BOX_H = 50;
const FONT_SIZE = 16;
const LABEL_FONT = 14;
const TITLE_FONT = 24;
const FRAME_GAP_Y = 100;

const COLORS = {
  client: "#a5d8ff",
  redis: "#ffc9c9",
  db: "#b2f2bb",
  process: "#ffec99",
  result: "#d0bfff",
  reject: "#ffa8a8",
  stroke: "#1e1e1e",
  title: "#1971c2",
  arrow: "#495057",
  frame: "#868e96",
  note: "#868e96",
};

const allElements = [];
const allTextElements = [];

function addRect(x, y, w, h, label, bgColor, frameId) {
  const rectId = makeId();
  const textId = makeId();

  allElements.push({
    id: rectId,
    type: "rectangle",
    x, y, width: w, height: h,
    angle: 0,
    strokeColor: COLORS.stroke,
    backgroundColor: bgColor,
    fillStyle: "solid",
    strokeWidth: 1,
    strokeStyle: "solid",
    roughness: 0,
    opacity: 100,
    groupIds: [],
    frameId: frameId || null,
    roundness: { type: 3 },
    seed: makeSeed(),
    version: 1,
    versionNonce: makeSeed(),
    isDeleted: false,
    boundElements: [{ id: textId, type: "text" }],
    updated: Date.now(),
    link: null,
    locked: false,
  });

  allElements.push({
    id: textId,
    type: "text",
    x: x + 10,
    y: y + (h - FONT_SIZE * 1.25) / 2,
    width: w - 20,
    height: FONT_SIZE * 1.25,
    angle: 0,
    strokeColor: COLORS.stroke,
    backgroundColor: "transparent",
    fillStyle: "solid",
    strokeWidth: 1,
    strokeStyle: "solid",
    roughness: 0,
    opacity: 100,
    groupIds: [],
    frameId: frameId || null,
    roundness: null,
    seed: makeSeed(),
    version: 1,
    versionNonce: makeSeed(),
    isDeleted: false,
    boundElements: null,
    updated: Date.now(),
    link: null,
    locked: false,
    text: label,
    fontSize: FONT_SIZE,
    fontFamily: 5,
    textAlign: "center",
    verticalAlign: "middle",
    containerId: rectId,
    originalText: label,
    autoResize: true,
    lineHeight: 1.25,
  });

  allTextElements.push({ id: textId, text: label });
  return { id: rectId, x, y, w, h };
}

function addArrow(fromRect, toRect, frameId) {
  const arrowId = makeId();
  const startX = fromRect.x + fromRect.w;
  const startY = fromRect.y + fromRect.h / 2;
  const endX = toRect.x;
  const endY = toRect.y + toRect.h / 2;

  allElements.push({
    id: arrowId,
    type: "arrow",
    x: startX,
    y: startY,
    width: endX - startX,
    height: endY - startY,
    angle: 0,
    strokeColor: COLORS.arrow,
    backgroundColor: "transparent",
    fillStyle: "solid",
    strokeWidth: 2,
    strokeStyle: "solid",
    roughness: 0,
    opacity: 100,
    groupIds: [],
    frameId: frameId || null,
    roundness: { type: 2 },
    seed: makeSeed(),
    version: 1,
    versionNonce: makeSeed(),
    isDeleted: false,
    boundElements: [],
    updated: Date.now(),
    link: null,
    locked: false,
    points: [
      [0, 0],
      [endX - startX, endY - startY],
    ],
    lastCommittedPoint: null,
    startBinding: { elementId: fromRect.id, focus: 0, gap: 5, fixedPoint: null },
    endBinding: { elementId: toRect.id, focus: 0, gap: 5, fixedPoint: null },
    startArrowhead: null,
    endArrowhead: "arrow",
    elbowed: false,
  });

  // Bidirectional binding: register arrow in both rects' boundElements
  const arrowBinding = { id: arrowId, type: "arrow" };
  for (const el of allElements) {
    if (el.id === fromRect.id || el.id === toRect.id) {
      if (Array.isArray(el.boundElements)) {
        el.boundElements.push(arrowBinding);
      } else {
        el.boundElements = [arrowBinding];
      }
    }
  }

  return arrowId;
}

function addLabel(text, x, y, frameId, fontSize, color) {
  const id = makeId();
  allElements.push({
    id,
    type: "text",
    x, y,
    width: text.length * (fontSize || LABEL_FONT) * 0.55,
    height: (fontSize || LABEL_FONT) * 1.25,
    angle: 0,
    strokeColor: color || COLORS.arrow,
    backgroundColor: "transparent",
    fillStyle: "solid",
    strokeWidth: 1,
    strokeStyle: "solid",
    roughness: 0,
    opacity: 100,
    groupIds: [],
    frameId: frameId || null,
    roundness: null,
    seed: makeSeed(),
    version: 1,
    versionNonce: makeSeed(),
    isDeleted: false,
    boundElements: null,
    updated: Date.now(),
    link: null,
    locked: false,
    text,
    fontSize: fontSize || LABEL_FONT,
    fontFamily: 5,
    textAlign: "center",
    verticalAlign: "top",
    containerId: null,
    originalText: text,
    autoResize: true,
    lineHeight: 1.25,
  });
  allTextElements.push({ id, text });
  return id;
}

function addTitle(text, x, y, frameId) {
  return addLabel(text, x, y, frameId, TITLE_FONT, COLORS.title);
}

function addNote(text, x, y, frameId) {
  return addLabel(text, x, y, frameId, LABEL_FONT, COLORS.note);
}

function addFrame(name, x, y, w, h) {
  const id = makeId();
  allElements.push({
    id,
    type: "frame",
    x, y, width: w, height: h,
    angle: 0,
    strokeColor: COLORS.frame,
    backgroundColor: "transparent",
    fillStyle: "solid",
    strokeWidth: 1,
    strokeStyle: "solid",
    roughness: 0,
    opacity: 100,
    groupIds: [],
    frameId: null,
    roundness: null,
    seed: makeSeed(),
    version: 1,
    versionNonce: makeSeed(),
    isDeleted: false,
    boundElements: null,
    updated: Date.now(),
    link: null,
    locked: false,
    name,
  });
  return id;
}

// ─── Diagram Definitions ─────────────────────────────────────────────────────
// Each diagram shows Redis's role in a real system architecture, not just commands.

const diagrams = [
  {
    // Cache-Aside: App Server orchestrates — checks Redis first, falls back to DB
    name: "Cache",
    title: "1. Cache-Aside Pattern",
    height: 310,
    build(frameId, ox, oy) {
      addTitle(this.title, ox + 30, oy + 15, frameId);

      // Row 1: Hit path — Client → App → Redis → App → Client
      const r1 = oy + 65;
      addLabel("Hit Path", ox + 30, r1, frameId, LABEL_FONT, "#2b8a3e");
      const client1 = addRect(ox + 100, r1 + 20, 110, BOX_H, "Client", COLORS.client, frameId);
      const app1 = addRect(ox + 300, r1 + 20, 120, BOX_H, "App Server", COLORS.process, frameId);
      const redis1 = addRect(ox + 530, r1 + 20, 140, BOX_H, "Redis Cache", COLORS.redis, frameId);
      const resp1 = addRect(ox + 780, r1 + 20, 110, BOX_H, "Response", COLORS.result, frameId);

      addArrow(client1, app1, frameId);
      addLabel("request", ox + 220, r1, frameId);
      addArrow(app1, redis1, frameId);
      addLabel("GET key", ox + 440, r1, frameId);
      addArrow(redis1, resp1, frameId);
      addLabel("✓ hit → return", ox + 680, r1, frameId);

      // Row 2: Miss path — Client → App → Redis (miss) → DB → App → SET Redis
      const r2 = oy + 170;
      addLabel("Miss Path", ox + 30, r2, frameId, LABEL_FONT, "#c92a2a");
      const client2 = addRect(ox + 100, r2 + 20, 110, BOX_H, "Client", COLORS.client, frameId);
      const app2 = addRect(ox + 300, r2 + 20, 120, BOX_H, "App Server", COLORS.process, frameId);
      const db = addRect(ox + 530, r2 + 20, 120, BOX_H, "Database", COLORS.db, frameId);
      const redis2 = addRect(ox + 780, r2 + 20, 110, BOX_H, "SET + TTL", COLORS.redis, frameId);

      addArrow(client2, app2, frameId);
      addLabel("request", ox + 220, r2, frameId);
      addArrow(app2, db, frameId);
      addLabel("✗ miss → query DB", ox + 425, r2, frameId);
      addArrow(db, redis2, frameId);
      addLabel("populate cache", ox + 670, r2, frameId);

      addNote("App Server is the orchestrator: check cache → on miss, query DB → write back to cache", ox + 60, oy + 275, frameId);
    },
  },
  {
    // Distributed Lock: Two independent horizontal rows — no shared box
    name: "Distributed Lock",
    title: "2. Distributed Lock",
    height: 310,
    build(frameId, ox, oy) {
      addTitle(this.title, ox + 30, oy + 15, frameId);

      // Row 1: Service A wins — fully horizontal
      const r1 = oy + 65;
      addLabel("Service A", ox + 30, r1, frameId, LABEL_FONT, "#2b8a3e");
      const svcA = addRect(ox + 30, r1 + 20, 130, BOX_H, "Service A", COLORS.client, frameId);
      const redisA = addRect(ox + 260, r1 + 20, 150, BOX_H, "Redis Lock", COLORS.redis, frameId);
      const work = addRect(ox + 510, r1 + 20, 130, BOX_H, "Do Work", COLORS.process, frameId);
      const del = addRect(ox + 740, r1 + 20, 130, BOX_H, "DEL lock", COLORS.redis, frameId);

      addArrow(svcA, redisA, frameId);
      addLabel("SET NX EX 30", ox + 165, r1, frameId);
      addArrow(redisA, work, frameId);
      addLabel("acquired ✓", ox + 420, r1, frameId);
      addArrow(work, del, frameId);
      addLabel("release", ox + 655, r1, frameId);

      // Row 2: Service B blocked — fully horizontal
      const r2 = oy + 175;
      addLabel("Service B", ox + 30, r2, frameId, LABEL_FONT, "#c92a2a");
      const svcB = addRect(ox + 30, r2 + 20, 130, BOX_H, "Service B", COLORS.client, frameId);
      const redisB = addRect(ox + 260, r2 + 20, 150, BOX_H, "Redis Lock", COLORS.redis, frameId);
      const blocked = addRect(ox + 510, r2 + 20, 150, BOX_H, "✗ Blocked", COLORS.reject, frameId);

      addArrow(svcB, redisB, frameId);
      addLabel("SET NX EX 30", ox + 165, r2, frameId);
      addArrow(redisB, blocked, frameId);
      addLabel("key exists → fail", ox + 420, r2, frameId);

      addNote("NX = set only if Not eXists | EX = auto-expire TTL (crash safety)", ox + 60, oy + 265, frameId);
      addNote("Only one holder at a time — mutual exclusion across distributed services", ox + 60, oy + 285, frameId);
    },
  },
  {
    // Leaderboard: Write path (score update) and Read path (top-K query) separated
    name: "Leaderboard",
    title: "3. Leaderboard (Sorted Set)",
    height: 310,
    build(frameId, ox, oy) {
      addTitle(this.title, ox + 30, oy + 15, frameId);

      // Redis Sorted Set in center-right
      const redis = addRect(ox + 430, oy + 100, 160, BOX_H, "Redis Sorted Set", COLORS.redis, frameId);

      // Write path: Game Server → ZADD → Redis
      const r1 = oy + 65;
      addLabel("Write Path", ox + 30, r1, frameId, LABEL_FONT, "#2b8a3e");
      const game = addRect(ox + 30, r1 + 20, 140, BOX_H, "Game Server", COLORS.client, frameId);
      addArrow(game, redis, frameId);
      addLabel("ZADD player score", ox + 210, r1, frameId);

      // Read path: Client → App → Redis → Top-K
      const r2 = oy + 175;
      addLabel("Read Path", ox + 30, r2, frameId, LABEL_FONT, "#1971c2");
      const client = addRect(ox + 30, r2 + 20, 140, BOX_H, "Client", COLORS.client, frameId);
      addArrow(client, redis, frameId);
      addLabel("ZREVRANGE 0 K", ox + 210, r2 + 15, frameId);
      const topk = addRect(ox + 720, r2 + 20, 150, BOX_H, "Top-K Results", COLORS.result, frameId);
      addArrow(redis, topk, frameId);
      addLabel("ranked list", ox + 615, r2, frameId);

      addNote("ZADD auto-updates score if member exists | ZREMRANGEBYRANK to prune old entries", ox + 60, oy + 265, frameId);
      addNote("O(log N) insert, O(log N + K) range query — scales where SQL ORDER BY struggles", ox + 60, oy + 285, frameId);
    },
  },
  {
    // Rate Limiting: API Gateway checks Redis before forwarding to Backend
    name: "Rate Limiting",
    title: "4. Rate Limiting",
    height: 300,
    build(frameId, ox, oy) {
      addTitle(this.title, ox + 30, oy + 15, frameId);

      const ry = oy + 80;
      const client = addRect(ox + 30, ry, 110, BOX_H, "Client", COLORS.client, frameId);
      const gw = addRect(ox + 230, ry, 140, BOX_H, "API Gateway", COLORS.process, frameId);
      const redis = addRect(ox + 460, ry, 140, BOX_H, "Redis Counter", COLORS.redis, frameId);

      addArrow(client, gw, frameId);
      addLabel("request", ox + 150, ry - 22, frameId);
      addArrow(gw, redis, frameId);
      addLabel("INCR + EXPIRE", ox + 385, ry - 22, frameId);

      // Accept → Backend
      const backend = addRect(ox + 700, ry - 30, 130, BOX_H, "Backend", COLORS.db, frameId);
      addArrow(redis, backend, frameId);
      addLabel("count ≤ N → forward", ox + 610, ry - 55, frameId);

      // Reject → 429
      const reject = addRect(ox + 700, ry + 50, 130, BOX_H, "429 Too Many", COLORS.reject, frameId);
      addArrow(redis, reject, frameId);
      addLabel("count > N → reject", ox + 612, ry + 40, frameId);

      addNote("Fixed window: INCR + EXPIRE | Sliding window: Sorted Set + Lua script (atomic)", ox + 60, oy + 220, frameId);
      addNote("Gateway checks Redis BEFORE forwarding — protects backend from overload", ox + 60, oy + 245, frameId);
      addNote("Sliding: ZREMRANGEBYSCORE → ZCARD → ZADD (all in one Lua call)", ox + 60, oy + 268, frameId);
    },
  },
  {
    // Proximity Search: Drivers report location, Rider queries nearby
    name: "Proximity Search",
    title: "5. Proximity Search (Geo)",
    height: 310,
    build(frameId, ox, oy) {
      addTitle(this.title, ox + 30, oy + 15, frameId);

      // Redis Geo Index in center
      const redis = addRect(ox + 400, oy + 100, 160, BOX_H, "Redis Geo Index", COLORS.redis, frameId);

      // Write: Driver → GEOADD → Redis
      const r1 = oy + 65;
      addLabel("Write", ox + 30, r1, frameId, LABEL_FONT, "#2b8a3e");
      const driver = addRect(ox + 30, r1 + 20, 140, BOX_H, "Driver App", COLORS.client, frameId);
      addArrow(driver, redis, frameId);
      addLabel("GEOADD lon lat driver_id", ox + 190, r1, frameId);

      // Read: Rider → GEOSEARCH → Nearby Drivers
      const r2 = oy + 175;
      addLabel("Read", ox + 30, r2, frameId, LABEL_FONT, "#1971c2");
      const rider = addRect(ox + 30, r2 + 20, 140, BOX_H, "Rider App", COLORS.client, frameId);
      addArrow(rider, redis, frameId);
      addLabel("GEOSEARCH BYRADIUS 5km", ox + 185, r2 + 15, frameId);
      const results = addRect(ox + 700, r2 + 20, 160, BOX_H, "Nearby Drivers", COLORS.result, frameId);
      addArrow(redis, results, frameId);
      addLabel("driver list", ox + 590, r2, frameId);

      addNote("Drivers continuously report location | Riders query within radius", ox + 60, oy + 265, frameId);
      addNote("Also: nearby restaurants, stores, points of interest", ox + 60, oy + 285, frameId);
    },
  },
  {
    // Event Sourcing: Service writes events → Stream → Consumer Group fans out
    name: "Event Sourcing",
    title: "6. Event Sourcing (Streams)",
    height: 260,
    build(frameId, ox, oy) {
      addTitle(this.title, ox + 30, oy + 15, frameId);

      const ry = oy + 80;
      const svc = addRect(ox + 30, ry, 130, BOX_H, "Order Service", COLORS.client, frameId);
      const stream = addRect(ox + 270, ry, 160, BOX_H, "Redis Stream", COLORS.redis, frameId);
      const cg = addRect(ox + 530, ry, 160, BOX_H, "Consumer Grp", COLORS.process, frameId);
      const c1 = addRect(ox + 760, ry - 40, 140, BOX_H, "Email Worker", COLORS.result, frameId);
      const c2 = addRect(ox + 760, ry + 40, 140, BOX_H, "Analytics", COLORS.result, frameId);

      addArrow(svc, stream, frameId);
      addLabel("XADD event", ox + 175, ry - 22, frameId);
      addArrow(stream, cg, frameId);
      addLabel("XREADGROUP", ox + 445, ry - 22, frameId);
      addArrow(cg, c1, frameId);
      addArrow(cg, c2, frameId);

      addNote("Append-only log with persistence | Consumer groups for parallel processing", ox + 60, oy + 190, frameId);
      addNote("XCLAIM to reclaim unprocessed messages on consumer failure", ox + 60, oy + 212, frameId);
      addNote("vs Kafka: lighter-weight; use Kafka for massive-scale, long-retention", ox + 60, oy + 234, frameId);
    },
  },
  {
    // Pub/Sub: Chat Service broadcasts to connected clients via channels
    name: "Pub/Sub",
    title: "7. Pub/Sub",
    height: 260,
    build(frameId, ox, oy) {
      addTitle(this.title, ox + 30, oy + 15, frameId);

      const ry = oy + 80;
      const svc = addRect(ox + 30, ry, 140, BOX_H, "Chat Service", COLORS.client, frameId);
      const channel = addRect(ox + 310, ry, 160, BOX_H, "Redis Channel", COLORS.redis, frameId);
      const s1 = addRect(ox + 630, ry - 40, 160, BOX_H, "User A (WS)", COLORS.result, frameId);
      const s2 = addRect(ox + 630, ry + 40, 160, BOX_H, "User B (WS)", COLORS.result, frameId);

      addArrow(svc, channel, frameId);
      addLabel("PUBLISH msg", ox + 190, ry - 22, frameId);
      addArrow(channel, s1, frameId);
      addLabel("SUBSCRIBE", ox + 510, ry - 55, frameId);
      addArrow(channel, s2, frameId);

      addNote("Fire-and-forget — no persistence, offline subscribers miss messages", ox + 60, oy + 180, frameId);
      addNote("Use case: chat, live updates, cache invalidation broadcast", ox + 60, oy + 202, frameId);
      addNote("For durable messaging, use Redis Streams or Kafka instead", ox + 60, oy + 224, frameId);
    },
  },
];

// ─── Generate ────────────────────────────────────────────────────────────────

let currentY = 0;

for (const d of diagrams) {
  const frameId = addFrame(d.name, 0, currentY, FRAME_W, d.height);
  d.build(frameId, 0, currentY);
  currentY += d.height + FRAME_GAP_Y;
}

// ─── Output ──────────────────────────────────────────────────────────────────

const textSection = allTextElements
  .map((e) => `${e.text} ^${e.id}`)
  .join("\n\n");

const drawing = {
  type: "excalidraw",
  version: 2,
  source: "https://github.com/zsviczian/obsidian-excalidraw-plugin",
  elements: allElements,
  appState: {
    theme: "light",
    viewBackgroundColor: "#ffffff",
    currentItemStrokeColor: "#1e1e1e",
    currentItemBackgroundColor: "transparent",
    currentItemFillStyle: "solid",
    currentItemStrokeWidth: 2,
    currentItemStrokeStyle: "solid",
    currentItemRoughness: 0,
    currentItemOpacity: 100,
    currentItemFontFamily: 5,
    currentItemFontSize: 16,
    currentItemTextAlign: "left",
    currentItemStartArrowhead: null,
    currentItemEndArrowhead: "arrow",
    currentItemRoundness: "round",
    gridSize: 20,
    gridStep: 5,
    gridModeEnabled: false,
    objectsSnapModeEnabled: false,
  },
  files: {},
};

const output = `---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠== You can decompress Drawing data with the command palette: 'Decompress current Excalidraw file'. For more info check in plugin settings under 'Saving'


# Excalidraw Data

## Text Elements
${textSection}

%%
## Drawing
\`\`\`json
${JSON.stringify(drawing)}
\`\`\`
%%`;

process.stdout.write(output);
