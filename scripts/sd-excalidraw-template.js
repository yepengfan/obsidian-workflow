#!/usr/bin/env node
/**
 * Generate an Excalidraw template for System Design practice.
 * Pre-fills Delivery Framework 6-step structure.
 *
 * Usage: node scripts/sd-excalidraw-template.js <topic>
 * Output: Excalidraw .md file content to stdout
 *
 * Example:
 *   node scripts/sd-excalidraw-template.js "Dropbox" > Solutions/Dropbox/Dropbox.excalidraw.md
 */

const topic = process.argv[2];
if (!topic) {
  console.error("Usage: node sd-excalidraw-template.js <topic>");
  process.exit(1);
}

function makeId() {
  return Array.from({ length: 8 }, () => Math.random().toString(36)[2]).join("");
}

const sections = [
  { title: `Design: ${topic}`, fontSize: 36, y: 0, color: "#1e1e1e" },

  // Step 1: Requirements
  { title: "1. Requirements", fontSize: 28, y: 96, color: "#1971c2" },
  { title: "Functional Requirements", fontSize: 20, y: 168, color: "#495057" },
  { title: "1.\n2.\n3.\n4.\n5.", fontSize: 16, y: 204, color: "#868e96" },
  { title: "Below the line (out of scope)", fontSize: 20, y: 330, color: "#495057" },
  { title: "1.\n2.", fontSize: 16, y: 366, color: "#868e96" },
  { title: "Non-Functional Requirements", fontSize: 20, y: 456, color: "#495057" },
  { title: "1.\n2.\n3.\n4.\n5.", fontSize: 16, y: 492, color: "#868e96" },
  { title: "Below the line (out of scope)", fontSize: 20, y: 624, color: "#495057" },
  { title: "1.\n2.", fontSize: 16, y: 660, color: "#868e96" },
  { title: "Back-of-Envelope", fontSize: 20, y: 744, color: "#495057" },
  { title: "- read/write ratio:\n- QPS:\n- storage:", fontSize: 16, y: 780, color: "#868e96" },

  // Step 2
  { title: "2. Core Entities", fontSize: 28, y: 960, color: "#1971c2" },

  // Step 3
  { title: "3. API / Interface", fontSize: 28, y: 1320, color: "#1971c2" },

  // Step 4
  { title: "4. Data Flow", fontSize: 28, y: 1680, color: "#1971c2" },
  { title: "Write Flow:", fontSize: 20, y: 1752, color: "#495057" },
  { title: "Read Flow:", fontSize: 20, y: 1992, color: "#495057" },

  // Step 5
  { title: "5. High-Level Design", fontSize: 28, y: 2280, color: "#1971c2" },

  // Step 6
  { title: "6. Deep Dives", fontSize: 28, y: 2880, color: "#1971c2" },
];

const elements = sections.map((s, i) => {
  const id = makeId();
  return {
    id,
    el: {
      id,
      type: "text",
      x: 100,
      y: s.y,
      width: s.fontSize > 24 ? 500 : 350,
      height: Math.round(s.fontSize * 1.5),
      angle: 0,
      strokeColor: s.color,
      backgroundColor: "transparent",
      fillStyle: "solid",
      strokeWidth: 2,
      strokeStyle: "solid",
      roughness: 1,
      opacity: 100,
      groupIds: [],
      frameId: null,
      index: `a${String(i).padStart(2, "0")}`,
      roundness: null,
      seed: Math.floor(Math.random() * 2e9),
      version: 1,
      versionNonce: Math.floor(Math.random() * 2e9),
      isDeleted: false,
      boundElements: null,
      updated: Date.now(),
      link: null,
      locked: false,
      text: s.title,
      fontSize: s.fontSize,
      fontFamily: 5,
      textAlign: "left",
      verticalAlign: "top",
      containerId: null,
      originalText: s.title,
      autoResize: true,
      lineHeight: 1.25,
    },
    text: s.title,
  };
});

const textSection = elements.map((e) => `${e.text} ^${e.id}`).join("\n\n");

const drawing = {
  type: "excalidraw",
  version: 2,
  source: "https://github.com/zsviczian/obsidian-excalidraw-plugin",
  elements: elements.map((e) => e.el),
  appState: {
    theme: "light",
    viewBackgroundColor: "#ffffff",
    currentItemStrokeColor: "#1e1e1e",
    currentItemBackgroundColor: "transparent",
    currentItemFillStyle: "solid",
    currentItemStrokeWidth: 2,
    currentItemStrokeStyle: "solid",
    currentItemRoughness: 1,
    currentItemOpacity: 100,
    currentItemFontFamily: 5,
    currentItemFontSize: 20,
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
