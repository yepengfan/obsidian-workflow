---
module: profile
label: "Profile 个人档案"
type: profile
status: active
enabled: true
created: 2026-03-29
updated: 2026-03-29
depends_on: [dashboard]
requires:
  plugins: [dataview]
commands: []
templates: []
scripts: []
hooks: []
folders: [Profile/]
config_files: []
tags: [system/module]
---

# Profile 个人档案

## Overview
个人评估和自我发展模块。包含 Ray Dalio 风格的 Baseball Card（PrinciplesYou 测评 + 自评 + 交叉验证），在 Home.md 通过雷达图展示。

## 架构

```
Profile/
├── Personal Baseball Card.md   # Baseball Card（雷达图数据）
├── Skill Radar.md              # 技能矩阵
├── ted-profile.png             # 头像
└── PrinciplesYou*.pdf          # 测评原始报告
```

### 展示
- Home.md 的 Profile 标签页 → Dataview 雷达图（全息效果）
- Home.md 的 Skills 标签页 → 技能雷达可视化

### 数据来源
- PrinciplesYou 测评结果
- 自我评估
- 团队/同事交叉验证

## 配置位置
| 组件 | 位置 |
|------|------|
| Baseball Card | `Profile/Personal Baseball Card.md` |
| 技能雷达 | `Profile/Skill Radar.md` |
| 展示层 | `Home.md`（Dataviewjs 雷达图代码） |
