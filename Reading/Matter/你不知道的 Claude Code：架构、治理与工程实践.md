## Metadata
* URL: [https://x.com/hitw93/status/2032091246588518683](https://x.com/hitw93/status/2032091246588518683)
* Author: Tw93
* Publisher: x.com
* Published Date: 2026-03-12
* Note: 六层层级：

- CLAUDE.md / rules / memory：长期上下文，告诉 Claude "是什么
- Tools / MCP：动作能力，告诉 Claude "能做什么
- Skills：按需加载的方法论，告诉 Claude "怎么做
- Hooks：强制执行某些行为，不依赖 Claude 自己判断
- Subagents：隔离上下文的工作者，负责受控自治
- Verifiers：验证闭环，让输出可验、可回滚、可审计
* Tags: 

## Highlights
* 我觉得最直接的理解方式，是把 Claude Code 拆成六层来看：
* "progressive disclosure"，意思不是让模型一次性看到所有信息，而是先获得索引和导航，再按需拉取细节：
