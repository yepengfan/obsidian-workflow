---
module: essays
label: "Essays 写作"
type: knowledge
status: active
enabled: true
created: 2026-11-17
updated: 2026-11-17
depends_on: [dashboard]
requires:
  plugins: [dataview]
commands: []
templates: []
scripts: [scripts/dashboard/essays/view.js]
hooks: []
folders: ['Essays/']
config_files: ['Essays/index.md']
tags: [system/module]
---

# Essays 写作

## Overview
Home 展示精简摘要，完整内容通过本模块的独立仪表盘查看。

## Quick Start
打开 [[Essays/index]] 查看内容和来源入口。

## Dashboard UI

The module dashboard uses the shared Home shell in `scripts/dashboard/ui/`. See `scripts/dashboard/README.md` for navigation, controls, private-data boundaries, and validation.
