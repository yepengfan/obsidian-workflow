---
tags: [system]
created: 2026-03-29
updated: 2026-03-29
---

# 🎛️ Module Registry

> [!abstract] Vault 控制中心
> 所有功能模块的统一视图。数据来自 `system/modules/` 下的模块清单文件。

## 模块总览

```dataviewjs
const modules = dv.pages('"system/modules"')
  .where(p => p.module)
  .sort(p => p.type);

// — 统计卡片 —
const active = modules.where(p => p.status === "active").length;
const inactive = modules.where(p => p.status === "inactive").length;
const deprecated = modules.where(p => p.status === "deprecated").length;
const totalCmds = modules.array().reduce((sum, p) => {
  const cmds = p.commands;
  return sum + (Array.isArray(cmds) ? cmds.length : 0);
}, 0);

dv.paragraph(
  `> **${active}** active · **${inactive}** inactive · **${deprecated}** deprecated · **${totalCmds}** commands total`
);
```

## 模块列表

```dataviewjs
const typeEmoji = {
  knowledge: "🧠",
  work: "💼",
  feed: "📡",
  utility: "🔧",
  profile: "👤"
};

const statusStyle = {
  active: "🟢",
  inactive: "⚪",
  deprecated: "🔴"
};

const modules = dv.pages('"system/modules"')
  .where(p => p.module)
  .sort(p => p.type);

dv.table(
  ["状态", "模块", "类型", "命令", "依赖", "脚本", "Hooks"],
  modules.map(p => {
    const cmds = Array.isArray(p.commands) ? p.commands : [];
    const deps = Array.isArray(p.depends_on) ? p.depends_on : [];
    const scripts = Array.isArray(p.scripts) ? p.scripts : [];
    const hooks = Array.isArray(p.hooks) ? p.hooks : [];
    return [
      statusStyle[p.status] || "❓",
      p.file.link,
      (typeEmoji[p.type] || "❓") + " " + (p.type || "—"),
      cmds.length > 0 ? cmds.map(c => "`/" + c + "`").join(" ") : "—",
      deps.length > 0 ? deps.map(d => "`" + d + "`").join(" ") : "—",
      scripts.length > 0 ? scripts.length + " files" : "—",
      hooks.length > 0 ? hooks.join(", ") : "—"
    ];
  })
);
```

## 依赖关系

```dataviewjs
const modules = dv.pages('"system/modules"')
  .where(p => p.module)
  .sort(p => p.module);

let lines = [];
for (const m of modules) {
  const deps = Array.isArray(m.depends_on) ? m.depends_on : [];
  if (deps.length > 0) {
    for (const dep of deps) {
      lines.push(`- **${m.label || m.module}** → depends on → **${dep}**`);
    }
  }
}

if (lines.length > 0) {
  dv.paragraph(lines.join("\n"));
} else {
  dv.paragraph("*所有模块独立运行，无依赖关系。*");
}
```

## 命令 × 模块映射

```dataviewjs
const modules = dv.pages('"system/modules"')
  .where(p => p.module && p.commands)
  .sort(p => p.module);

let cmdMap = [];
for (const m of modules) {
  const cmds = Array.isArray(m.commands) ? m.commands : [];
  for (const cmd of cmds) {
    cmdMap.push(["`/" + cmd + "`", m.file.link, m.label || m.module]);
  }
}

cmdMap.sort((a, b) => a[0].localeCompare(b[0]));

dv.table(
  ["命令", "所属模块", "模块名称"],
  cmdMap
);
```

## 配置文件分布

```dataviewjs
const modules = dv.pages('"system/modules"')
  .where(p => p.module)
  .sort(p => p.module);

let configMap = [];
for (const m of modules) {
  const configs = Array.isArray(m.config_files) ? m.config_files : [];
  const templates = Array.isArray(m.templates) ? m.templates : [];
  const scripts = Array.isArray(m.scripts) ? m.scripts : [];
  const allFiles = [...configs, ...templates, ...scripts];

  if (allFiles.length > 0) {
    configMap.push([
      m.file.link,
      allFiles.length,
      allFiles.map(f => "`" + f + "`").join("<br>")
    ]);
  }
}

dv.table(
  ["模块", "文件数", "配置文件"],
  configMap
);
```

## 按类型分组

```dataviewjs
const typeInfo = {
  knowledge: { emoji: "🧠", label: "知识管理" },
  work: { emoji: "💼", label: "工作系统" },
  feed: { emoji: "📡", label: "内容管线" },
  utility: { emoji: "🔧", label: "工具 & 运维" },
  profile: { emoji: "👤", label: "个人档案" }
};

const modules = dv.pages('"system/modules"')
  .where(p => p.module)
  .groupBy(p => p.type);

for (const group of modules) {
  const info = typeInfo[group.key] || { emoji: "❓", label: group.key };
  dv.header(3, `${info.emoji} ${info.label}`);

  const items = group.rows.sort(p => p.module);
  for (const m of items) {
    const cmds = Array.isArray(m.commands) ? m.commands : [];
    const cmdStr = cmds.length > 0
      ? " — " + cmds.map(c => "`/" + c + "`").join(" ")
      : "";
    const status = m.status === "active" ? "🟢" : m.status === "inactive" ? "⚪" : "🔴";
    dv.paragraph(`${status} ${m.file.link}${cmdStr}`);
  }
}
```
