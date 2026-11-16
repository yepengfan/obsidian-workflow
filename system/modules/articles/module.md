---
module: articles
label: Articles 文章收藏
type: knowledge
status: active
enabled: true
created: 2026-11-17
updated: 2026-11-17
depends_on:
- dashboard
requires:
  plugins:
  - dataview
commands: []
templates: []
scripts:
- scripts/dashboard/articles/view.js
hooks: []
folders:
- Library/
config_files:
- Library/Articles.md
tags:
- system/module
---

# Articles 文章收藏

## Overview
Home 展示精简摘要，完整内容通过本模块的独立仪表盘查看。

## Quick Start
打开 [[Library/Articles]] 查看内容和来源入口。

## Dashboard UI

The module dashboard uses the shared Home shell in `scripts/dashboard/ui/`. See `scripts/dashboard/README.md` for navigation, controls, private-data boundaries, and validation.
