---
type: dashboard
---

# Podcast Feed

## New Episodes

> [!tip] 上次更新：2026-04-01 | 共 10 期新内容

### 👍 Worth Listening (7-8)

| Podcast | Episode | Score | Duration | Summary |
|---------|---------|:-----:|----------|----------|
| AI + a16z | [[Podcasts/episodes/ai-a16z-patrick-collison-on-stripe-s-early-choices-smalltalk\|Patrick Collison on Stripe’s Early Choices, Smalltalk, and What Comes After Coding]] | 7.3 | 00:52:53 | Patrick Collison discusses why dev environments should reclaim Lisp-era integration, how API design shapes business destiny, and why AI productivity gains remain invisible in macro numbers. |
| AI + a16z | [[Podcasts/episodes/ai-a16z-what-s-missing-between-llms-and-agi-vishal-misra-mar\|What's Missing Between LLMs and AGI - Vishal Misra & Martin Casado]] | 7.2 | 00:47:35 | Vishal Misra formally proves transformers perform precise Bayesian inference, but argues AGI requires solving continual learning (plasticity) and the leap from correlation to causation. |

### 📋 Optional (5-6)

| Podcast | Episode | Score | Duration | Summary |
|---------|---------|:-----:|----------|----------|
| What's Next｜科技早知道 | [[Podcasts/episodes/what-s-next-bonus-ai\|Bonus | AI 制药，怎样才能真正商业化？]] | 5.6 | 43:32 | Insilico Medicine's Dr. Wang Jue explains AI drug discovery's three business models and details their first-in-class TNIC inhibitor pipeline, demonstrating AI's end-to-end impact from target discovery to molecular design. |
| What's Next｜科技早知道 | [[Podcasts/episodes/what-s-next-ai-s10e03\|杀伤链上的红线之争：当 AI 能够决定战场上的生死，人类离集体卸责还有多远？| S10E03]] | 5.6 | 56:09 |  |
| AI + a16z | [[Podcasts/episodes/ai-a16z-jack-altman-martin-casado-on-the-future-of-vc\|Jack Altman & Martin Casado on the Future of VC]] | 5.1 | 00:53:28 | A16Z GP Martin Casado discusses VC evolution from generalist to specialist, why AI infrastructure holds durable value, and how to invest when markets are expanding too fast to predict TAMs. |
| AI + a16z | [[Podcasts/episodes/ai-a16z-replit-s-ceo-on-vibe-coding-wealth-building-and-what\|Replit's CEO on Vibe Coding, Wealth Building, and What Most People Get Wrong About AI]] | 5.0 | 01:39:18 | Replit CEO Amjad Massad argues that AI has made coding skills obsolete for entrepreneurs — idea generation, domain knowledge, and grit are the new bottlenecks to building wealth. |

### ⏭️ Skip (<5)

| Podcast | Episode | Score | Duration | Summary |
|---------|---------|:-----:|----------|----------|
| What's Next｜科技早知道 | [[Podcasts/episodes/what-s-next-trailer-what-s-next\|Trailer｜从硅谷到世界，What's Next？]] | 1.6 | 7:20 | Silicon Valley podcast rebrands to 'What's Next? 科技早知道', sharing the rationale, behind-the-scenes design process, and new season content plans. |
| What's Next｜科技早知道 | [[Podcasts/episodes/what-s-next-s7-trailer\|S7 Trailer｜第七季正式跟大家见面啦]] | 1.5 | 5:25 | Tech podcast 'Guiguren' previews Season 7 lineup covering AI, overseas expansion, career growth, with new video and offline event formats. |

## Recently Listened

```dataviewjs
const pages = dv.pages('"Podcasts/episodes"')
  .where(p => p.status === "listened")
  .sort(p => p.listened_date, "desc")
  .limit(10);
dv.table(
  ["Episode", "Podcast", "Score", "Listened"],
  pages.map(p => [p.file.link, p.podcast, p.score, p.listened_date])
);
```

## Stats

```dataviewjs
const pages = dv.pages('"Podcasts/episodes"');
const counts = {unlistened: 0, listened: 0, archived: 0};
for (const p of pages) {
  const s = p.status || "unlistened";
  counts[s] = (counts[s] || 0) + 1;
}
dv.paragraph(
  `📥 Unlistened: **${counts.unlistened}** | ` +
  `✅ Listened: **${counts.listened}** | ` +
  `🗄️ Archived: **${counts.archived}**`
);
```
