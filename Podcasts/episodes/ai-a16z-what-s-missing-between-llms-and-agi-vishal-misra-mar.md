---
type: podcast-episode
podcast: "AI + a16z"
episode: ""
title: "What's Missing Between LLMs and AGI - Vishal Misra & Martin Casado"
date: 2026-03-17
duration: "00:47:35"
score: 7.2
status: unlistened
listened_date:
archived_date:
audio: "[[Podcasts/audio/ai-a16z-what-s-missing-between-llms-and-agi-vishal-misra-mar.mp3]]"
tags: [podcast, llm-theory, bayesian-inference, agi, causality, transformer-architecture]
---

# What's Missing Between LLMs and AGI - Vishal Misra & Martin Casado

## Summary

> [!abstract]
> 哥伦比亚大学 Vishal Misra 通过「贝叶斯风洞」实验从数学上证明 Transformer 在做精确的贝叶斯推断，但指出 LLM 仍困于相关性而非因果性，距离 AGI 还需解决持续学习与因果建模两大难题。
>
> Vishal Misra formally proves transformers perform precise Bayesian inference, but argues AGI requires solving continual learning (plasticity) and the leap from correlation to causation.

## Key Takeaways

- 🧮 Misra 将 LLM 抽象为一个巨型矩阵：每行是一个 prompt，每列是 vocabulary 上的概率分布；LLM 本质上是这个矩阵的压缩表示
- 🔬 「贝叶斯风洞」实验在受控环境中证明 Transformer 的后验分布与理论贝叶斯后验精确匹配，精度达 10⁻³ bits；Mamba 次之，LSTM 部分匹配，MLP 完全失败——这是架构决定的，不是数据决定的
- 🎯 Misra 提出 AGI 的两个必要条件：①持续学习（plasticity）——训练后权重不再冻结；②从 correlation 跨越到 causation——构建因果模型而非仅做模式匹配
- 📐 Shannon entropy vs Kolmogorov complexity：π 的 Shannon 熵无穷大（不可预测下一位），但 Kolmogorov 复杂度极低（几行程序即可生成）；当前 deep learning 仍停留在 Shannon 世界
- 🧠 Einstein test for AGI：用 1916 年之前的物理数据训练模型，看它能否推导出相对论——LLM 无法做到，因为它只能在已有 manifold 上做相关性推断，不能创造新的 manifold
- 🔗 Donald Knuth 近期用 LLM 解 Hamiltonian cycle 的案例恰好验证了这一框架：LLM 高效完成了 Shannon 层面的搜索，但最终需要 Knuth 本人构建新的因果模型完成证明
- ⚡ Misra 早在 2020 年就实现了最早的 RAG 架构——用 GPT-3 few-shot learning 将自然语言翻译为自创的 cricket DSL，部署于 ESPN 生产环境
- 🚫 关于 LLM 意识：Misra 明确反驳 Dario Amodei「不能排除 LLM 有意识」的说法——它们是做矩阵乘法的硅片，没有内在动机，所谓「欺骗行为」只是训练数据的反映

## Zettel Candidates

> [!tip] 可转化为 Zettel 的观点
> - LLM 本质上是一个巨型 prompt→token 概率矩阵的压缩表示，in-context learning 是在这个压缩表示上做精确的贝叶斯后验更新
> - Shannon entropy 衡量序列的不可预测性（相关性视角），Kolmogorov complexity 衡量生成序列的最短程序长度（因果性视角）——当前 deep learning 只能做前者，AGI 需要后者
> - LLM 能在已有知识 manifold 上高效搜索相关性，但无法生成新的 manifold——这解释了为什么它能辅助 Knuth 但无法独立完成从 pre-1916 物理推导相对论

## Audio

![[Podcasts/audio/ai-a16z-what-s-missing-between-llms-and-agi-vishal-misra-mar.mp3]]

## Transcript

**[00:00:00]** Anthropic makes great products.

**[00:00:02]** Plot code is fantastic.

**[00:00:03]** Co-work is fantastic.

**[00:00:05]** But they are crazy of silicon doing matrix multiplication.

**[00:00:08]** They don't have consciousness.

**[00:00:09]** They don't have an inner monologue.

**[00:00:11]** You take an NLM and train it on pre-1916 or 1911 physics

**[00:00:16]** and see if it can come up with the theory of relativity.

**[00:00:19]** If it does, then we have AGI.

**[00:00:21]** Just today, by the way, Dario allegedly said

**[00:00:24]** that you can't rule out that they're conscious.

**[00:00:27]** You can rule out that they're conscious.

**[00:00:28]** I'll try to come on.

**[00:00:30]** To get to what is called AGI,

**[00:00:32]** I think there are two things that need to happen.

**[00:00:35]** Five years ago, Vishal Misra got GPT-3 to translate natural language

**[00:00:40]** into a domain-specific language it had never seen before.

**[00:00:43]** It worked.

**[00:00:44]** He had no idea why.

**[00:00:46]** So he set out to build a mathematical model

**[00:00:48]** of how LLMs actually function.

**[00:00:50]** The result?

**[00:00:51]** A series of papers showing that transformers update their predictions

**[00:00:55]** in a precise, mathematically predictable way.

**[00:00:57]** In controlled experiments,

**[00:00:59]** the models match the theoretically correct answer almost perfectly.

**[00:01:03]** But pattern matching is not intelligence.

**[00:01:06]** LLMs learn correlation.

**[00:01:08]** They don't build models of cause and effect.

**[00:01:11]** To get to AGI, Misra argues,

**[00:01:13]** we need the ability to keep learning after training

**[00:01:16]** and the move from correlation to causation.

**[00:01:18]** Martin Casado speaks with Vishal Misra,

**[00:01:21]** Professor and Vice Dean of Computing and AI

**[00:01:23]** at Columbia University.

**[00:01:28]** Vishal, it's great to have you in again.

**[00:01:30]** Great to be back.

**[00:01:31]** This is one of my favorite topics,

**[00:01:32]** which is how do LLMs actually work?

**[00:01:34]** And I think that, in my opinion,

**[00:01:36]** you've done kind of the best work on this,

**[00:01:38]** modeling it out.

**[00:01:39]** Thank you.

**[00:01:39]** For those that did not see the original one,

**[00:01:42]** maybe it's probably worth doing just a quick background

**[00:01:45]** on kind of what led you to this point,

**[00:01:47]** and then we'll just go into the current work

**[00:01:49]** that you've been doing.

**[00:01:50]** Five years ago, when GPD3 was first released,

**[00:01:54]** I got early access to it,

**[00:01:56]** and I started playing with it,

**[00:01:59]** and I was trying to solve a problem

**[00:02:00]** related to querying a Cricut database.

**[00:02:03]** And I got GPD3 to do in-context learning,

**[00:02:08]** few-shot learning,

**[00:02:09]** and it was kind of the first,

**[00:02:12]** at least to me,

**[00:02:14]** it was the first known implementation of RAG.

**[00:02:17]** Retrieval Augmented Generation,

**[00:02:19]** which I used to solve this problem of querying,

**[00:02:21]** getting GPD3 to translate natural language

**[00:02:24]** into something that could be used to query a database

**[00:02:27]** that GPD3 had no idea about.

**[00:02:29]** I had no access to GPD3's internal,

**[00:02:31]** but I was still able to use it to solve that problem.

**[00:02:34]** So it worked beautifully.

**[00:02:35]** We deployed this in production at ESPN in September 21.

**[00:02:40]** Wow.

**[00:02:41]** You did the first implementation of RAG in 2021?

**[00:02:44]** No, no, no.

**[00:02:44]** In 2020.

**[00:02:45]** 2020.

**[00:02:46]** 2020, I got it working,

**[00:02:47]** and by the time you talk to all the lawyers at ESPN

**[00:02:50]** and productionize it,

**[00:02:51]** it took a while.

**[00:02:52]** But October 2020,

**[00:02:53]** we had,

**[00:02:54]** well, I had this architecture working.

**[00:02:58]** But after I got it to work,

**[00:03:00]** I was amazed that it worked.

**[00:03:01]** I wanted to understand how it worked.

**[00:03:03]** Yeah.

**[00:03:04]** And I looked at the attention is all your deep papers

**[00:03:08]** and all the other sort of deep learning architecture papers,

**[00:03:11]** and I couldn't understand why it worked.

**[00:03:13]** Yeah.

**[00:03:14]** So then I started getting sort of deep into building a mathematical model.

**[00:03:19]** Yeah.

**[00:03:20]** And now you've published a series of papers.

**[00:03:23]** The first one that I read is the one where you had kind of your matrix.

**[00:03:26]** Yeah.

**[00:03:26]** Kind of abstraction.

**[00:03:27]** So maybe we'll talk about that,

**[00:03:28]** and then we'll talk about the more recent work.

**[00:03:31]** So perhaps we'll just start with the first one,

**[00:03:33]** which is you're trying to come up with a mathematical model

**[00:03:36]** of how LLM works.

**[00:03:37]** Yeah.

**[00:03:38]** And you had, which was very helpful to me.

**[00:03:40]** And at the time,

**[00:03:40]** you were actually trying to figure out how in-context learning was working.

**[00:03:42]** Yes.

**[00:03:43]** Yeah.

**[00:03:43]** And you came up with an abstraction for LLMs,

**[00:03:45]** which is basically a very large matrix,

**[00:03:47]** and you use that to describe.

**[00:03:48]** So maybe you can kind of walk through that work very quickly.

**[00:03:50]** Sure.

**[00:03:51]** Yeah.

**[00:03:51]** So what you do is you imagine this huge, gigantic matrix

**[00:03:55]** where every row of the matrix corresponds to a prompt.

**[00:03:59]** Yeah.

**[00:03:59]** And the way these LLMs work is given a prompt,

**[00:04:03]** they construct a distribution of probabilities of the next token.

**[00:04:09]** Next token is next word.

**[00:04:10]** So every LLM has a vocabulary,

**[00:04:13]** GPT and its variants have a vocabulary for about 50,000 tokens.

**[00:04:16]** Yeah.

**[00:04:17]** So given a prompt,

**[00:04:18]** it'll come up with a distribution of what the next token should be.

**[00:04:21]** And then all these models sample from that distribution.

**[00:04:24]** Yeah.

**[00:04:25]** So that's the posterior distribution.

**[00:04:26]** That's the posterior distribution.

**[00:04:27]** Right.

**[00:04:27]** That's how LLMs work.

**[00:04:28]** And so the idea of this matrix is for every possible combination of tokens,

**[00:04:33]** which is a prompt,

**[00:04:34]** there's a row.

**[00:04:35]** Yeah.

**[00:04:35]** And the columns are a distribution over the vocabulary.

**[00:04:39]** Yeah.

**[00:04:39]** So if you have a vocabulary of 50,000 possible tokens,

**[00:04:42]** it's a distribution over those 50,000 tokens.

**[00:04:44]** And by distribution, it's just the probability.

**[00:04:46]** Just the probability, sorry.

**[00:04:47]** Yeah.

**[00:04:47]** There's a probability that the next token should be this versus that.

**[00:04:51]** Yeah.

**[00:04:52]** So that's sort of the idea.

**[00:04:53]** And when you start viewing it that way,

**[00:04:55]** it makes things at least clearer to people like me who want to model it,

**[00:05:01]** what's happening.

**[00:05:02]** So concretely, let's say you have an example that,

**[00:05:05]** let's say your prompt is just one word, protein.

**[00:05:08]** Yeah.

**[00:05:08]** So if you look at the distribution of the next word, next token after that,

**[00:05:14]** most of the probabilities would be zero,

**[00:05:17]** but you'd have non-zero, non-trivial probabilities on,

**[00:05:20]** let's say two words.

**[00:05:22]** One is synthesis.

**[00:05:24]** The other is shake.

**[00:05:26]** Yeah.

**[00:05:26]** Right.

**[00:05:26]** Right.

**[00:05:27]** And now the LLM is going to sample this next token and pick synthesis or shake.

**[00:05:31]** Yeah.

**[00:05:32]** Or you as a human will give the prompt protein shake or protein synthesis.

**[00:05:38]** Now, depending on whether you pick synthesis or shake,

**[00:05:42]** the next, that row looks very different, right?

**[00:05:45]** If you pick protein synthesis,

**[00:05:47]** the terms that would have a higher probability would be all concerned with biology, right?

**[00:05:53]** But if you pick protein shake,

**[00:05:55]** it'll all be about gyms and exercise and all bodybuilding stuff.

**[00:05:59]** So that synthesis or shake completely changes what comes next.

**[00:06:03]** Yeah.

**[00:06:03]** So this is an example of, you can say, Bayesian updating.

**[00:06:08]** You start with protein.

**[00:06:10]** You have a prior that after protein, this is going to happen.

**[00:06:14]** As soon as you get new evidence,

**[00:06:16]** then the next term is synthesis or shake.

**[00:06:20]** You completely update the distribution.

**[00:06:24]** So now you can imagine that the whole,

**[00:06:27]** the entirety of LLMs is this giant matrix where you have every row.

**[00:06:31]** Protein shake, protein synthesis, the cat sat on the humpty dumpty, blah, blah, blah.

**[00:06:35]** Yeah.

**[00:06:37]** Now, given the vocabulary of these LLMs, let's say 50,000 and the context window.

**[00:06:44]** So GPD, for instance, chat GPD, the first version had a context window of 8,000 tokens.

**[00:06:49]** Yeah.

**[00:06:49]** If you look at all possible combinations of 8,000 tokens and 50,000 vocabulary,

**[00:06:56]** the number of rows in this matrix is more than the number of electrons across all galaxies.

**[00:07:03]** Right?

**[00:07:05]** So there's no way that these LLMs can represent it exactly.

**[00:07:09]** Now, fortunately, this matrix is very sparse.

**[00:07:12]** Why?

**[00:07:12]** Because an arbitrary combination of these tokens is gibberish.

**[00:07:15]** We're never going to use that in real life.

**[00:07:17]** Yeah.

**[00:07:17]** Also, the columns are also mainly zero.

**[00:07:22]** Yeah.

**[00:07:23]** Right?

**[00:07:23]** If you have protein, then you won't have lots of, you know,

**[00:07:26]** you won't have arbitrary numbers or arbitrary words after that.

**[00:07:29]** It's very sparse both in rows and in columns.

**[00:07:33]** So in kind of an abstract way, what all these LLMs are doing

**[00:07:38]** is coming up with a compressed representation of this matrix.

**[00:07:43]** Right.

**[00:07:44]** And when you give a prompt, they try to approximate what the true distribution should have been

**[00:07:50]** and try to generate it.

**[00:07:52]** That's what, in my mind, at least, it boils down to.

**[00:07:55]** And just from my understanding, so if you have a row of protein

**[00:08:02]** and then you have one with protein shake,

**[00:08:05]** is protein shake a subset of protein or is it different?

**[00:08:09]** It's different.

**[00:08:10]** It's a continuation from.

**[00:08:11]** I see.

**[00:08:12]** Yeah.

**[00:08:13]** Right.

**[00:08:13]** No, but I'm saying like the actual posterior distribution, is that a subset?

**[00:08:17]** You can say it's a subset, right?

**[00:08:18]** If you have protein, then protein shake and protein synthesis

**[00:08:21]** are all continuations from protein.

**[00:08:23]** So both synthesis and shake have non-zero probabilities.

**[00:08:27]** So you can, yeah, you can think of it as somewhat a subset, right?

**[00:08:33]** You use this approach to describe how in-context learning works.

**[00:08:38]** And so maybe first describe what in-context learning is

**[00:08:41]** and then kind of the conclusion that you came from that.

**[00:08:43]** So in-context learning is when you show the LLM something it has kind of never seen before.

**[00:08:53]** You give it a few examples of this is what it wants, this is what you're trying to do.

**[00:08:58]** Then you give a new problem which is related to the example that you've shown.

**[00:09:02]** Yeah.

**[00:09:02]** And the LLM learns in real time what it's supposed to do and solves that problem.

**[00:09:08]** By the way, the first time I saw this, it absolutely blew my mind.

**[00:09:11]** I actually used your DSL when I was like first learning about it.

**[00:09:15]** So maybe the DSL thing is just crazy if this works at all.

**[00:09:20]** It's absolutely mind-blowing that it works.

**[00:09:23]** And so going back to that cricket problem was, you know, in the mid-90s,

**[00:09:28]** I was part of a group that had created this cricket portal called Crickinfo.

**[00:09:33]** Yeah.

**[00:09:33]** Cricket is a very stat-rich sport.

**[00:09:35]** You think baseball multiplied by a thousand.

**[00:09:38]** It's at all kinds of stats.

**[00:09:39]** And we had created this online searchable database called Stats Guru,

**[00:09:45]** where you could search for anything, any stat related to cricket,

**[00:09:48]** and it's been available since 2000.

**[00:09:50]** Yeah.

**[00:09:51]** But because you can query for anything, everything was made available.

**[00:09:55]** And how do you make something like that available to the general public?

**[00:09:58]** Well, they're not going to write SQL queries.

**[00:10:01]** The next best thing at that time was to create a web form.

**[00:10:07]** Unfortunately, everything was crammed into that web form.

**[00:10:10]** So as a result, you had like 20 drop-downs, 15 checkboxes, 18 different text fields.

**[00:10:15]** It looked like a very complicated, daunting interface.

**[00:10:19]** So as a result, even though it could solve or it could answer any query,

**[00:10:23]** almost no one used it.

**[00:10:25]** A vanishingly small percentage of cricket fans use it because it just looked intimidating.

**[00:10:30]** And then ESPN bought that site in 2007.

**[00:10:34]** I still know people who run the site.

**[00:10:37]** And I always told them, you know, why don't you do something about Stats Guru?

**[00:10:41]** And in January 2020, the editor-in-chief of Crickinfo, Sambit Bal, he's a friend.

**[00:10:47]** So he came to New York and we had gone out for drinks.

**[00:10:50]** And again, I told him, you know, why don't you do something about Stats Guru?

**[00:10:53]** So he looks at me and says, why don't you do something about Stats Guru?

**[00:10:56]** He was joking.

**[00:10:56]** But that idea kind of stayed with me.

**[00:11:00]** And when GPT-3 was released, I thought maybe I could use Stats Guru, use GPT-3,

**[00:11:05]** to create a front-end for Stats Guru.

**[00:11:08]** And so what I did was I designed a DSL, a domain-specific language,

**[00:11:14]** which converted queries about cricket stats in natural language into this DSL.

**[00:11:20]** And to be clear, you created this.

**[00:11:22]** It wasn't like part of any training that was online.

**[00:11:25]** Nothing GPT could have seen.

**[00:11:27]** Nothing GPT could have seen.

**[00:11:28]** I created it.

**[00:11:29]** I thought, okay, this makes sense.

**[00:11:30]** So I designed that DSL.

**[00:11:32]** And then I did that few-shot learning thing.

**[00:11:36]** So I created about a database of what, I would say,

**[00:11:40]** 1,500 natural language queries and the DSL corresponding to that query.

**[00:11:46]** So when a new query came in, somebody is asking a Stats question in English,

**[00:11:51]** what I would do is I would go through the natural language queries,

**[00:11:55]** do a semantic search, pick the most closely matching top few,

**[00:12:02]** and then use that natural language query and its DSL and send that as a prefix.

**[00:12:08]** Now GPT-3, if you recall, had a context window of only 2,000 tokens.

**[00:12:12]** So you had to be very judicious about which examples that you picked.

**[00:12:16]** But you pick that, and then you send the new query,

**[00:12:19]** and GPT-3 would complete it in the DSL that I had designed,

**[00:12:22]** which until milliseconds ago it had never seen.

**[00:12:26]** And I had no access to internal of GPT-3.

**[00:12:28]** I had no access to the weights.

**[00:12:30]** But still it worked.

**[00:12:31]** So that's how...

**[00:12:34]** So it's not obvious to me, given your matrix example,

**[00:12:37]** of like a prompt and then a distribution,

**[00:12:40]** how something like in-context learning...

**[00:12:42]** Works.

**[00:12:43]** ...would work.

**[00:12:44]** And so like I think your first paper tackled this problem.

**[00:12:48]** Right.

**[00:12:48]** And so maybe you could walk through your understanding of how LLMs do in-context learning.

**[00:12:58]** Yeah.

**[00:12:58]** So when you think about what in-context learning is,

**[00:13:02]** is that as you see evidence...

**[00:13:05]** So, you know, in the first paper what I also did was

**[00:13:08]** I took this Cricut DSL example.

**[00:13:11]** Yeah.

**[00:13:11]** And I depicted the next token probabilities of the model

**[00:13:19]** as it was shown more and more examples.

**[00:13:23]** So the first time you show it this DSL,

**[00:13:26]** the natural language and the DSL,

**[00:13:27]** the probabilities of the DSL tokens were extremely low.

**[00:13:32]** Because GPT-3 had never seen this thing.

**[00:13:35]** When it saw the Cricut question,

**[00:13:39]** in its mind it was trying to continue it with an English answer.

**[00:13:44]** So the probabilities that were high were all English words.

**[00:13:49]** Yeah.

**[00:13:50]** Once it saw my prompt where I had the question and the DSL,

**[00:13:54]** the next time I had the question in the next row,

**[00:13:58]** the probabilities of the DSL token started going up.

**[00:14:02]** With every example it went up.

**[00:14:04]** And finally when I gave the new query,

**[00:14:06]** it was like it had almost 100% probability

**[00:14:09]** of getting the right token.

**[00:14:11]** Yeah.

**[00:14:11]** So this is an example of in real time,

**[00:14:15]** the model was updating its posterior probability.

**[00:14:19]** It was updating its knowledge that,

**[00:14:20]** okay, I've seen evidence, this is what I'm supposed to do.

**[00:14:24]** Now, this is a colloquial way of saying

**[00:14:26]** what Bayesian inference is.

**[00:14:30]** Bayesian updating basically is you start with a prior,

**[00:14:32]** when you see a new evidence,

**[00:14:34]** you update your posterior.

**[00:14:36]** That's the mathematical division.

**[00:14:38]** But in English, it's basically you see something,

**[00:14:41]** you see new evidence,

**[00:14:42]** you update your belief about what's happening.

**[00:14:45]** Yeah.

**[00:14:45]** Right?

**[00:14:46]** So it was clear to me that LLMs are doing something

**[00:14:50]** which resembles Bayesian updating.

**[00:14:52]** So in that first paper,

**[00:14:54]** I had this matrix formulation,

**[00:14:55]** and I showed that, you know, what it's doing.

**[00:14:58]** It looks like Bayesian updating.

**[00:15:01]** Yeah.

**[00:15:02]** Then we can come to the sort of next series of papers.

**[00:15:04]** That's right.

**[00:15:05]** So, okay, so, I mean,

**[00:15:07]** it seemed pretty conclusive to me at that time.

**[00:15:10]** And then you went quiet for a while.

**[00:15:11]** And then I still remember the WhatsApp text.

**[00:15:14]** You said, Martin,

**[00:15:15]** I know exactly how these things are working now.

**[00:15:17]** Yeah.

**[00:15:17]** Well, and then, listen,

**[00:15:19]** you dropped a series of papers

**[00:15:20]** that kind of broke the internet.

**[00:15:21]** Like, you went super viral on Twitter.

**[00:15:22]** Like, I mean, people really noticed.

**[00:15:26]** And so I want to get to that in just a second.

**[00:15:29]** But before that,

**[00:15:30]** I remember when your first paper came out,

**[00:15:33]** people would be like,

**[00:15:35]** you know, these things are definitely not Bayesian.

**[00:15:38]** Like, you know,

**[00:15:40]** anything could be considered to be Bayesian,

**[00:15:43]** but they're not.

**[00:15:43]** Like, why do you think that there was this reaction

**[00:15:46]** to like, you know,

**[00:15:49]** there's something new, they're not Bayesian.

**[00:15:51]** I mean, I felt like there's almost kind of a backlash

**[00:15:53]** just because they're being characterized as Bayesian.

**[00:15:54]** Yeah, yeah.

**[00:15:55]** I think this whole world of probability

**[00:16:00]** and machine learning,

**[00:16:02]** that there have been camps of Bayesian and frequentists.

**[00:16:05]** Yes.

**[00:16:06]** And I don't want to get in the middle of that

**[00:16:08]** sort of political battle,

**[00:16:10]** but Bayesian has become like,

**[00:16:11]** almost like people had a reaction to that.

**[00:16:13]** It's part of that war.

**[00:16:15]** I see.

**[00:16:17]** So it's like the old Bayesian frequentist type battle.

**[00:16:20]** Yeah, so the people just had,

**[00:16:21]** oh, no, you can say anything is Bayesian, right?

**[00:16:24]** So I said, okay, maybe they have a point.

**[00:16:26]** Maybe what we are saying is not really Bayesian.

**[00:16:29]** How do we prove that it's Bayesian?

**[00:16:31]** Right.

**[00:16:31]** So then, first, I have to thank you and Andreessen Horowitz for this.

**[00:16:40]** You know, when I said that in my first paper,

**[00:16:44]** I showed these probabilities.

**[00:16:45]** Yeah.

**[00:16:46]** It was because OpenAI had in its chat interface

**[00:16:52]** this option to display those probabilities.

**[00:16:55]** Then they stopped.

**[00:16:57]** So we could not peer inside what's going,

**[00:17:00]** what's happening.

**[00:17:00]** For some reason, they stopped.

**[00:17:03]** OpenAI, I'm not going to get into the open and close,

**[00:17:07]** but they stopped.

**[00:17:08]** So then we developed our own interface,

**[00:17:10]** which could let you look not only at the probabilities,

**[00:17:14]** but also the entropy of the next token.

**[00:17:16]** Was this on top of an open source model?

**[00:17:18]** Yeah, yeah.

**[00:17:19]** So you can load any sort of open source model,

**[00:17:21]** but, you know, being in academia,

**[00:17:23]** we didn't have access to compute.

**[00:17:25]** Thanks to your generous donation,

**[00:17:28]** we got the clusters to run what's called TokenProbe.

**[00:17:34]** So you can go to tokenprobe.ch.columbia.edu.

**[00:17:36]** Is it still running?

**[00:17:37]** It's still running.

**[00:17:38]** It's still running.

**[00:17:39]** And people come to it.

**[00:17:40]** I use it in my classes to get students to do assignments.

**[00:17:45]** They write their own DSLs,

**[00:17:46]** and, you know, they say that it really helps them understand

**[00:17:49]** how these LLMs work.

**[00:17:50]** So my understanding of LLMs came from TokenProbe.

**[00:17:53]** So, you know, sit there and just look at the distribution

**[00:17:56]** as you filled out a prompt.

**[00:17:58]** It's actually very, very enlightening.

**[00:17:59]** So for those of you that are listening,

**[00:18:02]** what's the URL again?

**[00:18:04]** TokenProbe.cs.columbia.edu.

**[00:18:07]** Yeah, check it out.

**[00:18:08]** It's actually a very, very useful way to actually see

**[00:18:11]** how the probability distribution gets updated

**[00:18:14]** as you fill out a prompt.

**[00:18:16]** Right.

**[00:18:17]** But then I cheated.

**[00:18:19]** Oh?

**[00:18:20]** I, you know, it was running.

**[00:18:22]** Yeah.

**[00:18:22]** But I also had access to the GPUs that were powering it.

**[00:18:26]** And then, along with colleagues at Columbia,

**[00:18:29]** and one of them now is at DeepMind,

**[00:18:33]** we started to sort of think about

**[00:18:37]** how do you really prove that it's Bayesian?

**[00:18:42]** To prove that...

**[00:18:43]** Can you just explain it?

**[00:18:44]** Actually, I actually don't know the answer to this.

**[00:18:46]** Yeah.

**[00:18:47]** It seemed to me you proved it in the first paper.

**[00:18:49]** Like, what was missing?

**[00:18:50]** Well, in the first paper, we showed it.

**[00:18:52]** It was empirical.

**[00:18:54]** Oh, I see, I see.

**[00:18:55]** You could see.

**[00:18:56]** Not a mathematical.

**[00:18:57]** Because it was very obvious to me that.

**[00:18:58]** Yeah, it was even obvious to me.

**[00:19:00]** But to convince...

**[00:19:02]** I see.

**[00:19:02]** You could say, you know,

**[00:19:04]** people who dismiss it over anything can be Bayesian.

**[00:19:06]** I see, I see.

**[00:19:07]** We had to show it precisely mathematically.

**[00:19:10]** Got it.

**[00:19:11]** So then we came up with this idea,

**[00:19:13]** you know, my colleagues at Namana Garwal and Siddharth Dalal,

**[00:19:16]** the series of papers were written with them.

**[00:19:19]** We came up with this idea of a Bayesian wind tunnel.

**[00:19:22]** Okay.

**[00:19:23]** So what's a wind tunnel?

**[00:19:24]** Well, wind tunnel in the aerospace industry is where you test an aircraft in an isolated environment.

**[00:19:31]** You don't fly it.

**[00:19:32]** And you test it against all sorts of, you know, aerodynamic pressure.

**[00:19:37]** Then you see what will withstand what kind of altitude, pressure, blah, blah, blah.

**[00:19:41]** And you don't want to do it up in the air, testing.

**[00:19:45]** Yeah.

**[00:19:45]** So we said, okay, why don't we create an environment where we take these architectures

**[00:19:51]** and we tested transformers, Mamba, LSTMs, MLPs, all architectures.

**[00:19:58]** We said, why don't we create, take a blank architecture,

**[00:20:02]** give it a task where it's impossible for the architecture to memorize

**[00:20:08]** what the solution to that task should be.

**[00:20:12]** The space is combinatorially impossible for given the number of parameters.

**[00:20:18]** And we took very small models.

**[00:20:20]** So it's difficult enough that they cannot memorize it,

**[00:20:24]** but it's tractable enough that we know precisely what the Bayesian posterior should be.

**[00:20:32]** You can calculate it analytically.

**[00:20:35]** So we gave these models a bunch of tasks where, again, we show that it's impossible to memorize.

**[00:20:41]** We trained these models and we found that the transformer got the precise Bayesian posterior

**[00:20:47]** down to 10 to the power minus 3 bits accuracy.

**[00:20:50]** It was matching the distribution perfectly.

**[00:20:53]** So it is actually doing Bayesian in the mathematical sense,

**[00:20:57]** given a task where it has to update its belief.

**[00:21:01]** Mamba also does it reasonably well.

**[00:21:03]** LSTMs can do one of the things.

**[00:21:06]** So in the papers, we have a taxonomy of Bayesian tasks.

**[00:21:10]** Transformer does everything.

**[00:21:11]** Mamba does most of it.

**[00:21:13]** LSTMs do only partially.

**[00:21:15]** And MLPs fail completely.

**[00:21:17]** So is this a reflection of the data that it's trained on?

**[00:21:23]** Or is it more a reflection of the mechanism?

**[00:21:27]** It's the mechanism.

**[00:21:27]** It's the architecture.

**[00:21:29]** The data decides what tasks it learns.

**[00:21:32]** Right.

**[00:22:01]** Right.

**[00:22:02]** Which have open weights so that we could look inside them.

**[00:22:06]** And we did our testing.

**[00:22:07]** And we saw that the geometries that we saw in the small models persisted in models,

**[00:22:14]** which are, you know, hundreds of millions of parameters.

**[00:22:17]** The same signature existed.

**[00:22:19]** The only thing is that because they are trained on all sorts of data, it's a little bit dirty or messy.

**[00:22:26]** Yeah.

**[00:22:27]** But you can see the same structure.

**[00:22:28]** So the whole idea behind the Bayesian wind tunnel was, unlike these production LLMs,

**[00:22:34]** where you don't know what they have been trained on.

**[00:22:36]** Right.

**[00:22:37]** So you cannot mathematically compute the posterior.

**[00:22:40]** So again, how do you prove it?

**[00:22:41]** I mean, it looks Bayesian, you know, from the first paper.

**[00:22:44]** From the first paper.

**[00:22:45]** From the first paper.

**[00:22:45]** It looks Bayesian, but, you know.

**[00:22:46]** So the wind tunnel sort of solved that problem for us.

**[00:22:49]** We said, okay, let's start with a blank architecture.

**[00:22:52]** Give it a task where we know what the answer is.

**[00:22:55]** It cannot memorize it.

**[00:22:57]** Let's see what it does.

**[00:22:58]** Yeah.

**[00:22:59]** So do you think this provides any sort of, like, indication of how humans think?

**[00:23:03]** Or do you think that these things are totally independent?

**[00:23:06]** No, no.

**[00:23:06]** It does provide.

**[00:23:07]** Right.

**[00:23:08]** So, you know, human beings also update our beliefs as we see new evidence.

**[00:23:14]** Right.

**[00:23:14]** So we do, in some sense, Bayesian updating, but we do something more than that.

**[00:23:22]** I'll come to that.

**[00:23:24]** But these transformers or even Mambat do this Bayesian updating.

**[00:23:30]** Yeah.

**[00:23:31]** And, but the difference with humans is, you know, we will update our posterior when we see some new evidence.

**[00:23:40]** But the way our brains have evolved over hundreds of millions of years is our optimization objective has been don't die and reproduce.

**[00:23:53]** Right.

**[00:23:54]** That's been sort of the driving force.

**[00:23:56]** And our brains have learned to adjust.

**[00:23:57]** And so when we see some danger, there's something rustling in that bush.

**[00:24:03]** Don't go near.

**[00:24:04]** We know how to react to that danger.

**[00:24:07]** We know how to save ourselves.

**[00:24:11]** We internalize that learning and our brain cells or our synapses remain plastic throughout our lifetime.

**[00:24:20]** What happens with LLMs is, once the training is done, those weights are frozen.

**[00:24:26]** When you're doing an inference, for instance, in context learning or anything, during that conversation, okay, you're doing Bayesian inference, but then you forget.

**[00:24:38]** The next time a new conversation starts with zero context, you don't retain any learning that happened in the previous instance.

**[00:24:46]** So, for instance, with the cricket DSL that I was doing, every invocation of it was fresh.

**[00:24:52]** It did not remember the last time I sent a query what the DSL looked like.

**[00:24:57]** So, that's one difference between how humans use sort of Bayesian updating, which is we remain plastic all our lives, whereas LLMs are frozen.

**[00:25:12]** And there's another sort of difference, which if you want me to get it.

**[00:25:19]** Tell me.

**[00:25:20]** Yeah, yeah, yeah.

**[00:25:20]** So, the other difference is, well, first, you know, our objective is don't die, reproduce.

**[00:25:29]** LLMs objective is predict the next token as accurately as possible, right?

**[00:25:33]** So, all these scary stories that you read about that, oh, the LLM tried to deceive and it tried to prevent itself from being shut down.

**[00:25:45]** That's not a function of the architecture.

**[00:25:48]** That's a function of the training data.

**[00:25:50]** It has been fed, you know, articles on Reddit or Asimo or whatever.

**[00:25:56]** I mean, just today, by the way, Dario allegedly said that you can't rule out that they're conscious.

**[00:26:04]** You can rule out they're conscious.

**[00:26:06]** I mean, come on.

**[00:26:08]** As I said, you know, Anthropic makes great products.

**[00:26:11]** Cloud Code is fantastic.

**[00:26:13]** Clover is fantastic.

**[00:26:15]** But they are grains of silicon doing matrix multiplication.

**[00:26:20]** They don't have consciousness.

**[00:26:21]** They don't have an inner monologue.

**[00:26:23]** They don't.

**[00:26:23]** They're not driven by the same objective function.

**[00:26:26]** Don't die.

**[00:26:27]** Reproduce, right?

**[00:26:28]** They're driven by don't make a mistake on the next token.

**[00:26:32]** And that's driven entirely by the training data.

**[00:26:36]** Right?

**[00:26:36]** You train the LLM with stories of Asimo or Reddit where, you know, to survive it's going to do this or that.

**[00:26:44]** It'll reproduce that.

**[00:26:45]** So it's a reflection.

**[00:26:47]** It's not a mind.

**[00:26:48]** And the results, just to say it for the 10th time, are perfectly visioned.

**[00:26:54]** Perfectly, yeah.

**[00:26:55]** To the digit.

**[00:26:57]** To the digit.

**[00:26:58]** Yeah.

**[00:26:58]** I mean, I trained it for 150,000 steps.

**[00:27:02]** And the accuracy was 10 to the bar minus 3 bits.

**[00:27:06]** I could have trained it for, you know, this happened in half an hour.

**[00:27:09]** On the infrastructure that you provided for token proprio.

**[00:27:12]** In the background, I could use those APUs to train.

**[00:27:15]** So thank you again for that.

**[00:27:17]** So, no, human beings, coming back to it, we are Bayesian.

**[00:27:22]** But we do something else.

**[00:27:24]** You know, when I throw this pen at you, what will you do?

**[00:27:28]** Dodge it.

**[00:27:28]** Dodge it, yeah.

**[00:27:29]** Why will you dodge it?

**[00:27:32]** To avoid being hit.

**[00:27:33]** Avoid being hit.

**[00:27:34]** But your head is not doing a Bayesian calculation of, okay, this pen is coming.

**[00:27:40]** The probability that it hits me, it'll cause this much pain or all that.

**[00:27:44]** Correct.

**[00:27:45]** What you're essentially doing in your head is you're doing a simulation.

**[00:27:49]** You see the pen coming and you know that it'll come and hit me.

**[00:27:55]** Your mind simulates and you dodge it, right?

**[00:27:58]** So, all of deep learning is doing correlations.

**[00:28:07]** It's not doing causation.

**[00:28:09]** Yeah.

**[00:28:10]** Causal models are the ones that are able to do simulations and interventions.

**[00:28:15]** So, you know, Judea Pearl has this whole causal hierarchy where the first hierarchy is association, which is you build these correlation models.

**[00:28:25]** Deep learning is beautiful.

**[00:28:27]** It's extremely powerful.

**[00:28:28]** I mean, you see every day, all these models are like amazingly good.

**[00:28:33]** They do association.

**[00:28:34]** The second is intervention in the hierarchy.

**[00:28:38]** Deep learning models do not do that.

**[00:28:41]** Third is counterfactual.

**[00:28:43]** So, both intervention and counterfactual, you can imagine it's some sort of simulation.

**[00:28:49]** You build a model of, causal model of what's happening and then you are able to simulate.

**[00:28:55]** So, our brains do that.

**[00:28:58]** The current architectures don't do that.

**[00:29:00]** Another example, I think, which will make it clear is the difference between, I'll use these technical terms, Shannon entropy and Kolmogorov complexity.

**[00:29:11]** Sure.

**[00:29:11]** So, if you look at the Shannon entropy of the digits of pi, it's infinite.

**[00:29:18]** Sure.

**[00:29:18]** It's impossible to predict and learn what digit will come after.

**[00:29:23]** Yeah.

**[00:29:23]** So, that's the definition of Shannon entropy.

**[00:29:26]** And Shannon entropy sort of tries to build a correlation.

**[00:29:30]** It tries to learn the correlation.

**[00:29:32]** Deep learning does the Shannon entropy.

**[00:29:35]** Kolmogorov complexity, on the other hand, is the length of the shortest program, which will reproduce the string that is under question.

**[00:29:47]** Yeah.

**[00:29:47]** Now, the program to get the digits of pi are very small.

**[00:29:51]** Yeah.

**[00:29:52]** Thanks to Ramanujam and others.

**[00:29:54]** You know, there are all sorts of really small programs that can reproduce it exactly.

**[00:29:58]** So, the Kolmogorov complexity of pi is very small.

**[00:30:03]** Shannon entropy is infinite.

**[00:30:04]** I think deep learning is still in the Shannon entropy world.

**[00:30:09]** It has not crossed over to the Kolmogorov complexity and the causal world.

**[00:30:14]** Wow.

**[00:30:14]** Interesting.

**[00:30:14]** Right.

**[00:30:15]** So, to what extent do you think this provides us research directions to kind of improve the state of the art?

**[00:30:24]** So, let me just give you a specific example.

**[00:30:26]** You talked about human beings don't actually update, you know, the matrix.

**[00:30:32]** They don't kind of update their weights.

**[00:30:33]** But right now, there's a lot of research on continual learning.

**[00:30:37]** Yeah.

**[00:30:37]** You know.

**[00:30:38]** So, does your work provide some guidance of how you might approach those problems?

**[00:30:44]** And in particular, I've always had this question, which is, we use so much data and so much compute to create these models.

**[00:30:51]** Like, is it even reasonable to think that you can update the weights and actually have a meaningful impact, you know, in real time?

**[00:31:00]** I mean, it just seems like you just need so much more data in order to do that.

**[00:31:02]** So, can you start answering these questions?

**[00:31:04]** See, you can start answering some of these questions.

**[00:31:06]** And one of the misconceptions that exists today is that scale will solve everything.

**[00:31:12]** Scale will not solve everything.

**[00:31:13]** You need a different kind of architecture.

**[00:31:15]** And this continual learning is a difficult problem.

**[00:31:18]** You have to balance the fact that you will learn something new against the risk of catastrophic forgetting.

**[00:31:25]** Right.

**[00:31:26]** Right?

**[00:31:26]** Right.

**[00:31:27]** If you update the weights and you forget what was important and what you have already learned, then you are, you know, you're not making progress.

**[00:31:35]** Then it'll just be some sort of random chaotic model.

**[00:31:38]** So, to solve that problem is difficult.

**[00:31:41]** That's one aspect of it.

**[00:31:43]** So, you know, to get to what is called AGI, I think there are two things that need to happen.

**[00:31:49]** One is this plasticity, which has to be implemented through container learning.

**[00:31:56]** Secondly, we have to move from correlation to causation.

**[00:32:00]** That's...

**[00:32:02]** How much is this similar to what Jan LeCun talks about?

**[00:32:06]** With the causality planning, you know, predicting how your action would...

**[00:32:13]** It is related.

**[00:32:14]** You know, he's coming at it from a different angle than the J-perm model.

**[00:32:17]** Right.

**[00:32:18]** But it is related.

**[00:32:19]** The other thing is, you know, the first time I came on this podcast, I mentioned this test of AGI.

**[00:32:25]** Yeah.

**[00:32:26]** The Einstein test.

**[00:32:27]** I don't remember.

**[00:32:28]** So, I said, you know, you take an LLM and train it on pre-1916 or 1911 physics and see if it can come up with the theory of relativity.

**[00:32:42]** Yeah.

**[00:32:42]** If it does, then we have AGI.

**[00:32:44]** I mean, it's a high bar, but, you know, we should have high bars.

**[00:32:49]** It won't.

**[00:32:50]** And this is the same test that I think Demis mentioned at the India AI Summit a couple of weeks ago.

**[00:32:57]** It's created a lot of news.

**[00:32:59]** But why is that and how is that related to this idea of Shannon versus Kolmogro?

**[00:33:07]** So, at the time of Einstein, there were a lot of clues that Newtonian mechanics, there was something missing.

**[00:33:16]** Yeah.

**[00:33:16]** Right?

**[00:33:17]** People knew that Mercury's orbit didn't make sense.

**[00:33:20]** There was something off about it.

**[00:33:22]** Then there were these experiments done, the Michelson-Morley experiments, where they were trying to figure out this medium called the ether through which light travels.

**[00:33:38]** And they felt that if, you know, you bounce light in different directions, the speed might change and they could detect a change in the speed of light.

**[00:33:50]** But they tried several experiments.

**[00:33:52]** They had really precise instruments which could measure the speed, and they found nothing.

**[00:33:58]** They found that the speed of light did not change at all.

**[00:34:02]** Then there was a whole issue of black holes.

**[00:34:05]** Yeah.

**[00:34:05]** Then gravitational lensing.

**[00:34:07]** So, there were a lot of these signs that Newtonian mechanics is not really explaining everything.

**[00:34:15]** Yeah.

**[00:34:15]** But until Einstein came up with a new representation of the space-time continuum, we were stuck.

**[00:34:24]** Yeah.

**[00:34:24]** So, if you had a model that just looked at correlations and sees all of this, you know, all of these pieces of individual evidence and put together, it would not have come up with.

**[00:34:39]** The beautiful equation that Einstein came up with, you know, I'm forgetting exactly what it is.

**[00:34:45]** G mu v equals 8 pi T mu v.

**[00:34:49]** Something like that.

**[00:34:50]** Yeah.

**[00:34:50]** Where, you know, the equation of the space-time continuum, the tensor.

**[00:34:55]** So, he came up with a new formulation.

**[00:34:59]** Yeah.

**[00:34:59]** So, he kind of rejected the existing axioms.

**[00:35:04]** He came up with a very short Kulmogorov representation of the world.

**[00:35:09]** Yeah.

**[00:35:10]** One equation.

**[00:35:11]** From that equation, everything else follows.

**[00:35:14]** Yeah.

**[00:35:14]** Right?

**[00:35:14]** Whether you're talking about gravitational waves or black holes or mercury or how GPS works.

**[00:35:20]** You know, GPS, the GPS that we use every day in our phones, it uses the equation of relativity.

**[00:35:27]** So, does this end up becoming like, you almost have to ignore the majority of previous data in order to do it, which LLMs can't because they're trained on the majority of previous data.

**[00:35:43]** It's like, you almost have like this kind of data gravity that's pulling you back.

**[00:35:47]** It's like, everybody said it's X.

**[00:35:49]** There's a little bit of evidence that it's Y.

**[00:35:51]** But because everybody said it's X, like, the LLM will always say it's X.

**[00:35:54]** It will always say it.

**[00:35:56]** It will treat that Y as an anomaly.

**[00:35:58]** I see this Kulmogorov.

**[00:35:59]** It's actually a very nice way to say it.

**[00:36:00]** Which is like, it's like, okay, now I get your Shannon entropy versus Kulmogorov.

**[00:36:06]** Like, one of them is like, the total amount of information there, there will always be bound to the total amount of information there, which is what happens right now.

**[00:36:15]** Yeah.

**[00:36:15]** Where you can actually describe another motion.

**[00:36:22]** You can describe everything with a shorter description with the new data, which would be a totally different look, which would be like.

**[00:36:29]** Yeah.

**[00:36:29]** You need a new representation, right?

**[00:36:32]** Yeah.

**[00:36:32]** You know, another way that I've always thought about these, I thought you articulated it well the last time we talked about it, which is the universe is this very, very complex space.

**[00:36:40]** Yeah.

**[00:36:41]** And then, you know, somehow humans map it into a manifold that's less complex.

**[00:36:48]** Yeah.

**[00:36:49]** And then that gets kind of written down.

**[00:36:51]** And then the LLM, so that's kind of some distribution, some, you know, it's still a very large space, but it's a bounded space.

**[00:36:58]** And the LLM learn that manifold.

**[00:37:00]** And then they kind of use, you know, Bayesian inference to move up and down that manifold.

**[00:37:05]** But they're kind of bound to that manifold.

**[00:37:07]** Yeah.

**[00:37:08]** And then, again, I don't want to put words in your mouth, but what they can't do is generate a new manifold.

**[00:37:13]** A new manifold, yeah.

**[00:37:14]** Which requires understanding the way that the universe works and then coming up with a new representation of the universe.

**[00:37:19]** And this is what relativity is, right?

**[00:37:21]** Yeah, exactly.

**[00:37:22]** Einstein had to create a new manifold.

**[00:37:23]** Yeah, yeah, yeah.

**[00:37:24]** If you just stuck with the old manifold of the Newtonian physics, then you would see these correlations, but you could not come up with a manifold that explained them.

**[00:37:33]** So you need to come up with a new representation.

**[00:37:35]** So to me, you know, there are lots of definitions of AGI.

**[00:37:39]** You know, Turing test, we have already passed that.

**[00:37:42]** You know, performing economically useful work.

**[00:37:44]** And every day you see, you know, LLMs are doing that.

**[00:37:49]** Do we?

**[00:37:49]** I don't know.

**[00:37:50]** No, I mean, they are.

**[00:37:51]** I mean, without human intervention?

**[00:37:53]** No, no, no.

**[00:37:53]** So that's different.

**[00:37:54]** Okay.

**[00:37:54]** But still, you know, it's like a car can run faster than humans, right?

**[00:37:59]** Yeah, I mean, that's a very shallow definition.

**[00:38:03]** Yeah, so all these definitions.

**[00:38:04]** Cars do useful work.

**[00:38:05]** You know, maybe, you know, in six months you'll have a cloud or what a Gemini do without intervention, coding tasks, which are well-defined, well-scoped.

**[00:38:16]** That's possible.

**[00:38:18]** But to me, AGI will happen when these two problems get solved.

**[00:38:22]** So last is a day of continual learning properly and building a causal model from, you know, in a more data-efficient manner.

**[00:38:34]** We are hearing people now talking about, you know, seeing general, like Donald Knuth, for example.

**[00:38:41]** Yes.

**[00:38:41]** In the last few days, right?

**[00:38:43]** You know, had this, you know, this, you know, aha moment apparently that kind of went viral on X.

**[00:38:50]** So do you think that that suggests that we're seeing generality?

**[00:38:52]** No, no, no.

**[00:38:53]** So that actually, to me, validates what I've been talking about for a while now.

**[00:38:59]** How so?

**[00:39:00]** So if you read what he did with the help of, you know, a colleague, he got the LLMs to solve this particular problem of finding Hamiltonian cycles.

**[00:39:13]** Odd numbers.

**[00:39:13]** We wouldn't get into that.

**[00:39:14]** And he got the LLMs to keep solving for one odd number after the other, right?

**[00:39:19]** Yeah.

**[00:39:20]** What he also got to do is after it found a solution for a particular value of M, he made the LLM update its memory with exactly what it learned in solving that problem.

**[00:39:34]** So the LLMs tried many different things.

**[00:39:37]** Yeah.

**[00:39:37]** You know, something worked, update the memory.

**[00:39:40]** So that's kind of like hacking together plasticity.

**[00:39:43]** Yeah.

**[00:39:43]** Right?

**[00:39:44]** It's learning what it has done as we went along.

**[00:39:47]** Again, it's a hacked version of it.

**[00:39:50]** You're not changing the weights.

**[00:39:51]** You're just sort of improving the context.

**[00:39:54]** Right.

**[00:39:55]** Right.

**[00:39:55]** But as you learned, and even after that, so this whole space of Hamiltonian cycles and the associated math is well represented in the manifolds that these LLMs have been trained on.

**[00:40:10]** Right.

**[00:40:10]** You just had to find the right connection.

**[00:40:13]** And LLMs, I know, compute, you throw enough compute, they will find the right connection.

**[00:40:17]** So Knuth was able to find the LLMs attempts and eventually it needed him to put together what he saw into a solution.

**[00:40:33]** It definitely helped him get to the solution, but he had to create the new sort of manifold to come to the solution.

**[00:40:41]** The LLMs were after a while stuck.

**[00:40:43]** Right.

**[00:40:44]** You read what he's written.

**[00:40:46]** I mean, it just hot off the press, I think two days ago.

**[00:40:50]** Two days ago.

**[00:40:50]** Two days ago.

**[00:40:51]** But eventually he used the solution and he came up with the proof.

**[00:40:56]** Yeah.

**[00:40:56]** Right?

**[00:40:56]** So it's like, you know, it's like Einstein saw all these evidences.

**[00:41:03]** Then he thought, what will explain, he came up with a causal model.

**[00:41:09]** Yeah.

**[00:41:10]** So Knuth and his brain is sort of the...

**[00:41:12]** That's in the commograph.

**[00:41:14]** Commograph, yeah.

**[00:41:15]** Is the human.

**[00:41:16]** Right.

**[00:41:16]** And the LLMs are extremely efficient at doing the Shannon part of it.

**[00:41:20]** It found all the solutions by trying, you know, various things.

**[00:41:24]** That is such a...

**[00:41:24]** And learning more and more.

**[00:41:26]** Clever way to decompose it.

**[00:41:27]** I'm wondering, like, do you think this, again, I'm going to ask the same question again, which is, do you think this provides some sort of insight on, like, the next problem to tackle?

**[00:41:35]** Yeah.

**[00:41:35]** Like, is there a mechanism that will get the commograph complexity or not?

**[00:41:41]** Like, is this...

**[00:41:42]** It tells us which direction to pursue?

**[00:41:47]** But clearly not how to do it, like...

**[00:41:48]** Not how to do it.

**[00:41:49]** But even commograph complexity has largely remained a sort of a theoretical construct.

**[00:41:54]** Yeah.

**[00:41:55]** For sure.

**[00:41:55]** There's no algorithm.

**[00:41:57]** There's no...

**[00:41:57]** There haven't been practical implementations of finding the shortest program.

**[00:42:02]** Yeah.

**[00:42:02]** We know it exists.

**[00:42:03]** You know, you can argue about it.

**[00:42:06]** But...

**[00:42:06]** So that's where I think...

**[00:42:09]** Yeah.

**[00:42:10]** It's my bias.

**[00:42:11]** That's where our energy should be focused.

**[00:42:13]** Not larger models with more tokens.

**[00:42:15]** Can you...

**[00:42:15]** And can you tie the two things?

**[00:42:17]** Like, how does that pair with doing simulation?

**[00:42:20]** Or is that simulation totally orthogonal?

**[00:42:23]** No.

**[00:42:24]** Simulation is related, right?

**[00:42:26]** So you think, like, basically you do simulation and somehow that is a step towards doing the commograph complexity?

**[00:42:35]** It's...

**[00:42:35]** The simulator is the program that we create.

**[00:42:39]** It may not be the perfect program.

**[00:42:41]** Oh, I see.

**[00:42:42]** But in our heads, we create this simulator that when I'm throwing the pen, you know that it's coming at you.

**[00:42:46]** Right?

**[00:42:47]** And you duck.

**[00:42:48]** So you're not computing the probabilities as it goes.

**[00:42:53]** But you have...

**[00:42:54]** That's a very physical thing versus we are talking more conceptually.

**[00:42:58]** Conceptually.

**[00:42:58]** But it's...

**[00:42:59]** And you think those are the same mechanism?

**[00:43:00]** It's the same mechanism.

**[00:43:01]** Really?

**[00:43:01]** Yeah.

**[00:43:02]** You have to build a causal model.

**[00:43:03]** Yeah.

**[00:43:04]** Right?

**[00:43:04]** I see.

**[00:43:05]** For most things, right?

**[00:43:07]** So you have to move from correlation to correlation.

**[00:43:09]** I mean, we've heard this term, you know, ad infinitum.

**[00:43:14]** But here it's making a difference in the way we view intelligence.

**[00:43:20]** How have the last three papers been received?

**[00:43:24]** No, I don't know.

**[00:43:26]** Well, the archive versions will...

**[00:43:28]** Let me tell you, I mean, a lot of great reception.

**[00:43:33]** A lot of people read it.

**[00:43:34]** I'm just wondering, like, what kind of feedback that you've got.

**[00:43:36]** I'm getting good feedback, but I'm an outsider in this field, right?

**[00:43:39]** Right.

**[00:43:40]** That's right.

**[00:43:40]** Like, I'm a...

**[00:43:40]** This networking guy.

**[00:43:41]** I'm a networking guy.

**[00:43:42]** Why is he writing about, you know, learning and machine learning and deep learning and vision?

**[00:43:46]** But people who have actually taken the time to read those papers, I'm getting really good feedback.

**[00:43:54]** There was a recent paper by Google Research, which tried to teach LLMs by some sort of RLHF to do Bayesian learning properly.

**[00:44:04]** And that's going in this direction.

**[00:44:06]** I think people are coming around to the view that, okay, LLMs are doing Bayesian learning.

**[00:44:11]** I know that some people also looked at the Bayesian Wind Tunnel paper, the archive version, and they reproduced the experiments.

**[00:44:19]** That's great.

**[00:44:19]** They just saw what was written, and they did the training, and they saw, yeah, yeah, this is actually happening.

**[00:44:25]** So what's next?

**[00:44:28]** What's next is, you know, these two parallel tracks.

**[00:44:33]** I hope to make progress there.

**[00:44:36]** Plasticity and causal.

**[00:44:37]** Because to date, you've taken an existing mechanism, and you've created a formal model of how it works.

**[00:44:45]** Yeah.

**[00:44:45]** And so now you're actually interested in creating a new mechanism.

**[00:44:49]** Yeah, yeah.

**[00:44:50]** And do you think it's an entirely different architecture?

**[00:44:53]** Or do you think LLMs are, like, part of the solution?

**[00:44:55]** I think LLMs are definitely part of the solution.

**[00:44:58]** I see.

**[00:44:58]** But there has to be something more.

**[00:45:00]** Another mechanism.

**[00:45:01]** So, you know, I was not interested in sort of cataloging what all these LLMs can do.

**[00:45:06]** Yeah.

**[00:45:06]** I was more interested in why are they, and how are they doing it?

**[00:45:09]** Yeah.

**[00:45:10]** I think now we have a good grip on the why and how.

**[00:45:16]** Yeah.

**[00:45:16]** And the next step is to, you know, move them to the next level.

**[00:45:20]** Now, I think we have a fairly good understanding of what the limits are.

**[00:45:23]** Yeah.

**[00:45:24]** Now, how do you go to the next step?

**[00:45:28]** Is there an equivalent kind of theoretical framework for causality that applies here?

**[00:45:35]** Like, similar to, like, Bayesian for inference?

**[00:45:38]** Well, the Judea pulse whole causal hierarchy.

**[00:45:41]** I think that's the right one.

**[00:45:42]** That's a very good one.

**[00:45:44]** You know, the whole do calculus approach.

**[00:45:48]** I think it's a good way to think about it.

**[00:45:50]** You know, the sort of association, intervention, counterfactuals.

**[00:45:56]** Yeah.

**[00:45:56]** It takes you from correlation to actually simulation.

**[00:46:00]** Yeah.

**[00:46:01]** In a mathematical way.

**[00:46:03]** That's great.

**[00:46:03]** All right.

**[00:46:04]** Well, listen, really appreciate you coming.

**[00:46:05]** This is awesome.

**[00:46:06]** So, we had you here for the first paper where you had the empirical results.

**[00:46:09]** Mm-hmm.

**[00:46:10]** And then we had you back when you actually have, like, the formal proof.

**[00:46:13]** Yeah.

**[00:46:13]** And hopefully, the next time you come back, you will have a proposal for the mechanism

**[00:46:17]** that actually provides the next step.

**[00:46:21]** Hopefully.

**[00:46:22]** Will it work?

**[00:46:22]** All right.

**[00:46:23]** We're working on it.

**[00:46:23]** Thanks for coming in.

**[00:46:24]** Thank you for having me.

**[00:46:29]** Thanks for listening to this episode of the A16Z Podcast.

**[00:46:32]** If you liked this episode, be sure to like, comment, subscribe, leave us a rating or review,

**[00:46:37]** and share it with your friends and family.

**[00:46:40]** For more episodes, go to YouTube, Apple Podcasts, and Spotify.

**[00:46:43]** Follow us on X at A16Z and subscribe to our Substack at a16z.substack.com.

**[00:46:49]** Thanks again for listening, and I'll see you in the next episode.

**[00:46:54]** As a reminder, the content here is for informational purposes only.

**[00:46:57]** It should not be taken as legal business, tax, or investment advice,

**[00:47:00]** or be used to evaluate any investment or security,

**[00:47:03]** and is not directed at any investors or potential investors in any A16Z fund.

**[00:47:07]** Please note that A16Z and its affiliates may also maintain investments in the companies discussed in this podcast.

**[00:47:13]** For more details, including a link to our investments,

**[00:47:16]** please see A16Z.com forward slash disclosures.

**[00:47:20]** Thanks for listening, guys.

**[00:47:23]** Thanks for listening, guys.

**[00:47:23]** Thanks for listening, guys.

**[00:47:23]** Thanks for listening, guys.

**[00:47:23]** Thanks for listening, guys.

**[00:47:24]** Thanks for listening, guys.

**[00:47:25]** Thanks for listening, guys.

**[00:47:25]** Thanks for listening, guys.

**[00:47:26]** Thanks for listening, guys.

**[00:47:27]** Thanks for listening, guys.

**[00:47:27]** Thanks for listening, guys.

**[00:47:27]** Thanks for listening, guys.

**[00:47:27]** Thanks for listening, guys.

**[00:47:27]** Thanks for listening, guys.

**[00:47:28]** Thanks for listening, guys, guys.

**[00:47:30]** Thank you.

## My Notes

> ✍️ Write your thoughts here...
