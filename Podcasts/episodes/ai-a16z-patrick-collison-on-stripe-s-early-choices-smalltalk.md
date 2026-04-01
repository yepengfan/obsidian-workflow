---
type: podcast-episode
podcast: "AI + a16z"
episode: ""
title: "Patrick Collison on Stripe’s Early Choices, Smalltalk, and What Comes After Coding"
date: 2026-03-24
duration: "00:52:53"
score: 7.3
status: unlistened
listened_date:
archived_date:
audio: "[[Podcasts/audio/ai-a16z-patrick-collison-on-stripe-s-early-choices-smalltalk.mp3]]"
tags: [podcast, api-design, development-environments, stripe, ai-productivity, programming-languages]
---

# Patrick Collison on Stripe’s Early Choices, Smalltalk, and What Comes After Coding

## Summary

> [!abstract]
> Stripe CEO Patrick Collison 与 Cursor CEO 对谈，探讨开发环境应回归 Lisp/Smalltalk 式深度集成理念，API 设计如何深刻塑造企业命运，以及 AI 尚未在宏观生产力数据中显现的原因。
>
> Patrick Collison discusses why dev environments should reclaim Lisp-era integration, how API design shapes business destiny, and why AI productivity gains remain invisible in macro numbers.

## Key Takeaways

- 🧪 Patrick Collison 第一家创业公司用 Smalltalk 编写——因为它提供了类似 Lisp 的交互式开发环境，能在 web request 执行中途 inspect stack frame、修复代码并 resume execution
- 🔧 Collison 认为现代开发环境最大的缺失是 runtime 与编辑器的割裂——理想状态应像 Lisp Machine/Mathematica 那样，hover 代码即可看到 profiling 数据、生产环境变量值和 error log
- 🏗️ Stripe 关键数据：2024 年 critical API availability 达 99.99986%（全年仅 44 秒不可用），使用 MongoDB + Ruby 这两个 2010 年的 big bang 决策至今仍在
- 📐 API 设计的 business impact 被严重低估——Collison 以 iOS vs Android 为例，认为 iOS 生态更繁荣的核心原因是早期 framework 和 abstraction 设计更优（NS 前缀源自 NeXTSTEP，存活超 20 年）
- 🔄 Stripe V2 API 重写的核心教训：定义新 API 很简单，难的是与旧系统共存——更像 chip instruction set migration 而非 product launch；实用建议是「统一一切可统一的实体」和「默认支持 N×M 关系」
- 📊 Collison 引用最新研究称 AI 尚未在 productivity 数据中体现；Anthropic 联合创始人 Jack Clark 预测 AI 每年仅增加 0.5% GDP 增长——这已算乐观估计
- 🧬 ARC Institute 正在利用 read（单细胞测序）+ think（transformer）+ write（CRISPR/bridge editing）构建生物学的「Turing loop」，目标是攻克人类从未真正治愈过的 complex diseases
- 🎯 Collison 对 Cursor 的三个需求：① 深度 runtime 集成（hover 即见生产数据）② AI 驱动的自动 refactoring 降低代码库的变更成本 ③ 确保 AI 产出的是 craft-level 高质量软件而非 slop

## Zettel Candidates

> [!tip] 可转化为 Zettel 的观点
> - API 设计决定企业命运——iOS 生态优于 Android 的根本原因不是硬件或用户规模，而是早期 framework abstraction 的质量差异，且这种优势可持续 20 年以上
> - 生物学正在形成自己的 Turing completeness：单细胞测序（read）+ transformer（think）+ CRISPR/bridge editing（write）构成了一个完整的实验闭环，这可能是攻克 complex disease 的前提条件
> - 技术扩散的时滞被系统性低估——如果 AI 的生产力提升是真实的，它应该同时出现在所有使用 LLM 的国家的 GDP 数据中，但目前只有美国有温和增长，说明 diffusion 本身是瓶颈而非技术能力

## Audio

![[Podcasts/audio/ai-a16z-patrick-collison-on-stripe-s-early-choices-smalltalk.mp3]]

## Transcript

**[00:00:00]** It's interesting to me that we haven't experimented in some sense that much with the paradigm of programming over the past 20 years.

**[00:00:08]** You put those together, you now have the ability to, again, at the kind of level of the individual cell, to read, think, and to write.

**[00:00:15]** And this starts to really feel like a new kind of Turing loop and to have its own sort of completeness.

**[00:00:21]** I think that's a case where the right API design, the right abstraction design, ended up having just quite significant business ramifications.

**[00:00:30]** I think the basic idea of as development environment and not just text editor is really the right idea.

**[00:00:38]** And that's the thing I want to see a return to.

**[00:00:41]** Patrick Collison wrote his first startup in Smalltalk.

**[00:00:44]** Its development environment let him fix errors mid-request, inspect stack frames, and resume execution.

**[00:00:49]** And he wanted that more than he wanted a mainstream language.

**[00:00:52]** He and his brother chose Ruby and MongoDB for Stripe instead.

**[00:00:56]** Those decisions still define the company 15 years and 44 seconds of annual downtime later.

**[00:01:02]** Now Stripe is shipping v2 APIs, rewriting core abstractions first designed in 2010.

**[00:01:08]** It's taken years.

**[00:01:09]** Defining the new APIs is the easy part.

**[00:01:12]** Making them work alongside everything already built on the old ones is, as Collison put it,

**[00:01:16]** more like an instruction set migration than a product launch.

**[00:01:20]** This conversation previously aired on Cursor's podcast also gets into why AI hasn't moved productivity numbers,

**[00:01:26]** what today's dev environment could steal from Lisp machines,

**[00:01:29]** and Collison's work at ARK on foundational models for biology.

**[00:01:33]** Michael Truel, CEO of Cursor, sits down with Patrick Collison, CEO of Stripe.

**[00:01:40]** Well, it's great to have you.

**[00:01:41]** Thank you for being here.

**[00:01:42]** Thanks for having me.

**[00:01:43]** Great to be here.

**[00:01:44]** I've heard that your first startup was written in Smalltalk.

**[00:01:47]** Please explain.

**[00:01:49]** I don't know what there is to explain.

**[00:01:50]** It's the best programming language.

**[00:01:51]** Well, I had worked on Lisp and Lisp dialects before that.

**[00:01:57]** And actually, I worked on Lisp web frameworks.

**[00:02:00]** And when we went to build our first startup, we first implemented it in Rails.

**[00:02:08]** And then I found, compared to Lisp, that development process kind of frustrating.

**[00:02:12]** And I mean, we don't need to get into the full details,

**[00:02:15]** but I thought that continuation-based web frameworks were really the right way to implement web applications.

**[00:02:20]** There were no continuations in...

**[00:02:24]** There's no continuation-based framework in Ruby.

**[00:02:28]** And I was kind of searching around.

**[00:02:30]** I found that there was a good one that had just been written in Smalltalk.

**[00:02:34]** And so I decided to play with it a little bit.

**[00:02:36]** And then I found that Smalltalk is actually this extremely interesting development environment

**[00:02:41]** that had a lot of the aspects of Lisp that I'd really appreciated there,

**[00:02:45]** like a fully interactive environment with a proper debugger,

**[00:02:50]** so that you can edit the code while in the middle of some web request

**[00:02:57]** or deep in some stack trace or something.

**[00:03:00]** And you could, for example, encounter an error with some web request,

**[00:03:05]** edit the code to fix the error,

**[00:03:07]** and then resume higher up in the stack such that the entire web request would just complete.

**[00:03:14]** And so rather than this kind of annoying feedback loop of having to add some log statements

**[00:03:18]** and do this binary search to find the problem

**[00:03:20]** and eventually deploy a fixed version, a process that could take an hour,

**[00:03:24]** you could just literally inspect the stack frame,

**[00:03:27]** see which variable has the wrong value,

**[00:03:29]** fix it, jump back up, hit proceed, and have the whole thing work.

**[00:03:33]** So anyway, the point is, in the hunt for this continuation-based web framework,

**[00:03:37]** realized that Smalltalk in general had just a much more powerful development environment

**[00:03:41]** as compared to Ruby slash as compared to basically every other mainstream programming language.

**[00:03:46]** And so we decided to use it for the company,

**[00:03:51]** which in hindsight was, I mean, I don't know if it was a terrible decision or not.

**[00:03:55]** The reason I think one would think it would be terrible

**[00:03:57]** is that it would be hard to hire people and hard to scale and whatever.

**[00:04:02]** It wasn't hard to hire people, or rather, nobody knew it, but it was easy to teach them.

**[00:04:05]** Did they know before they joined?

**[00:04:07]** No, no, but they learned really quickly.

**[00:04:09]** And then you have smart people who learn languages really quickly.

**[00:04:11]** So I don't think that's really a reason not to use a non-mainstream language.

**[00:04:14]** The company didn't work, I think, for unrelated reasons.

**[00:04:16]** I think just the idea wasn't that strong.

**[00:04:19]** But we also chose Ruby for Stripe, so I don't know.

**[00:04:23]** I think maybe the gains were not quite as large as I hoped.

**[00:04:25]** And was your Smalltalk enthusiasm shared by the acquirers of the startup?

**[00:04:29]** And what was the dynamic, you know, was there like this blissfully ignorant management

**[00:04:34]** that foisted this Smalltalk codebase on a bunch of unsuspecting developers

**[00:04:37]** that were then kind of like piling over, you know?

**[00:04:40]** Or yeah, what was the dynamic between the programmers' management,

**[00:04:43]** sort of what happened to that Smalltalk codebase?

**[00:04:45]** Yeah, yeah, yeah.

**[00:04:45]** Does it still live on somewhere?

**[00:04:47]** I wish, and I'm 99% sure the answer is no.

**[00:04:53]** So the company that acquired us was mainly a talent acquisition,

**[00:04:56]** so the codebase itself was less relevant.

**[00:05:00]** Okay, and it was immediately sort of just gone?

**[00:05:02]** Yeah.

**[00:05:02]** Okay, gotcha.

**[00:05:03]** I've also heard that one of your earliest programming projects

**[00:05:06]** was working on an AI bot written in Lisp.

**[00:05:10]** True.

**[00:05:10]** And it was something like, it was a client for MSN.

**[00:05:14]** Uh-huh, yeah.

**[00:05:15]** I don't know where you found that, but that is true.

**[00:05:17]** And I heard that you got kind of nerds tonight by the idea

**[00:05:19]** of trying to get it to pass the Turing test.

**[00:05:21]** Yes.

**[00:05:22]** And I'm curious, what did you miss?

**[00:05:25]** You know, why didn't you make ChatGPT?

**[00:05:27]** And, well, maybe a little bit more seriously, how did it work?

**[00:05:30]** And what was the state of neural networks at the time?

**[00:05:32]** And did you consider using any antecedents to the technology we use today?

**[00:05:36]** Yeah, so that was the project.

**[00:05:37]** It was a little critter that used MSN Messenger,

**[00:05:40]** which was, you know, all the rage at the time.

**[00:05:42]** I guess that's like maybe a specific kind of sedimentary layer

**[00:05:46]** in the chronology of different instant messaging solutions

**[00:05:49]** and probably dates me quite precisely.

**[00:05:52]** And it was a really simple Bayesian next word predictor.

**[00:05:56]** Like there was nothing really that sophisticated there

**[00:05:58]** to the extent there was anything sophisticated.

**[00:05:59]** It was maybe that it used, like the training data was the conversations

**[00:06:02]** itself had in MSN Messenger rather than kind of general text corp.

**[00:06:06]** But, and anyway, it worked reasonably well.

**[00:06:09]** And, you know, better versions looked a couple of words ahead

**[00:06:11]** and, you know, what have you.

**[00:06:13]** And, I mean, it never really passed the Turing test

**[00:06:16]** where, you know, people have actual suspicion

**[00:06:18]** that they're trying to, you know, exercise this discernment.

**[00:06:21]** But it certainly passed some weaker version of the Turing test

**[00:06:24]** where, you know, they were unsuspecting.

**[00:06:26]** And, you know, people ended up having quite lengthy conversations with it.

**[00:06:30]** And that was part of how I discovered Lisp.

**[00:06:32]** And I remember Paradigms of AI Programming by Peter Norvig

**[00:06:35]** being a really formative book and had, you know,

**[00:06:37]** all sorts of interesting approaches there.

**[00:06:39]** It didn't have anything on neural networks, I'm almost sure.

**[00:06:44]** And I never, I mean, I'd read some Marvin Minsky stuff,

**[00:06:47]** Society of the Mind or whatever, on neural nets.

**[00:06:50]** But I never really seriously looked at them.

**[00:06:52]** And I actually experimented a lot with genetic algorithms.

**[00:06:54]** They were, I guess, more practical on, you know, your own computer.

**[00:06:57]** Like, it takes a lot of computer training in neural nets.

**[00:06:59]** So I experimented a lot with genetic algorithms.

**[00:07:02]** And actually, I used Vorjak at the keyboard layout

**[00:07:04]** because it's more comfortable to type on than QWERTY.

**[00:07:08]** But as does John, my brother, so no one can ever use our computers.

**[00:07:14]** But I wrote a genetic, I don't know, optimizer

**[00:07:19]** to figure out what the optimal keyboard layout was.

**[00:07:22]** And it turns out it is, in fact, basically Vorjak

**[00:07:24]** using a genetic approach.

**[00:07:26]** So I went deep down that rabbit hole,

**[00:07:28]** but I never really played with neural networks.

**[00:07:30]** And I guess that's why, you know, that,

**[00:07:32]** but probably 70 other reasons is why, you know,

**[00:07:35]** I did not create ChatGPT.

**[00:07:37]** There is an old video of you being interviewed,

**[00:07:41]** I think, after selling Octomatic,

**[00:07:45]** where you're asked about Smalltalk.

**[00:07:47]** That's where I found kind of that weird effect.

**[00:07:49]** I think at the time, people asked you why.

**[00:07:52]** And one of the things you said was,

**[00:07:53]** I mean, you liked some features about Smalltalk,

**[00:07:55]** Lisp-style languages.

**[00:07:56]** And you predicted, and I think that this was circa maybe 2008

**[00:07:59]** or something like that,

**[00:08:00]** that the mainline C-style programming languages

**[00:08:02]** would increasingly borrow ideas

**[00:08:03]** from these older programming languages.

**[00:08:04]** And that kind of has been the case

**[00:08:06]** in the JavaScript Python ecosystems.

**[00:08:08]** Do you think that there are any underrated ideas

**[00:08:10]** buried away in kind of older,

**[00:08:12]** more esoteric programming languages

**[00:08:13]** that should be borrowed by the mainline?

**[00:08:15]** Yeah, it's been interesting how a lot of the ideas

**[00:08:20]** have been kind of, have been borrowed

**[00:08:22]** by the JavaScript ecosystem,

**[00:08:23]** and in a strange way, like through the web inspector.

**[00:08:26]** Yeah.

**[00:08:26]** Where you have this, I mean,

**[00:08:28]** that's one of the richest runtimes in some sense

**[00:08:31]** that people have, you know, general exposure to.

**[00:08:33]** I don't think JavaScript has first-class stack frames.

**[00:08:37]** Maybe there's some weird extension or something

**[00:08:39]** where you can get that,

**[00:08:39]** but ECMAScript doesn't have that, I'm pretty sure.

**[00:08:44]** First-class stack frames actually let you do

**[00:08:45]** a lot of other things for kind of obvious reasons.

**[00:08:47]** So maybe that's very, that's kind of too specific.

**[00:08:51]** I mean, I think the idea of,

**[00:08:53]** and maybe this is what cursor becomes,

**[00:08:55]** I think the basic idea of,

**[00:08:57]** as development environment,

**[00:08:59]** and not just text editor,

**[00:09:01]** is really the right idea.

**[00:09:03]** And that's the thing I want to see a return to.

**[00:09:05]** That's the thing that the Lisp machines had,

**[00:09:07]** and Genera, that's the thing that,

**[00:09:09]** to some extent, Mathematica has,

**[00:09:10]** that's the thing that Smalltalk has,

**[00:09:13]** and I think it's just such a mistake

**[00:09:14]** that we have ended up with development environments

**[00:09:17]** where there is such a separation

**[00:09:18]** between the runtime and the text editing

**[00:09:21]** and the environment in which the code,

**[00:09:27]** I mean, well, the runtime and the place

**[00:09:30]** where the code runs can be the same or different,

**[00:09:31]** but there are kind of three,

**[00:09:33]** maybe slightly conceptually different things.

**[00:09:35]** And in those three environments,

**[00:09:36]** they can all coexist in the same place.

**[00:09:38]** And I, like, I mean, still to this day,

**[00:09:40]** I use Mathematica a lot,

**[00:09:41]** not because I'm doing some particularly arcane,

**[00:09:44]** you know, symbolic mathematics,

**[00:09:45]** but because it's just a more efficient

**[00:09:47]** development environment.

**[00:09:48]** Now, that's maybe a bit less true with LLMs

**[00:09:51]** because the Mathematica, you know,

**[00:09:54]** Mathematica does not support

**[00:09:55]** cursor-style prompted development,

**[00:09:59]** but that, I think, is the core idea

**[00:10:00]** that I wish others would borrow.

**[00:10:02]** And VS Code has been a step to some extent,

**[00:10:05]** slightly in that direction,

**[00:10:06]** but I think we could take it way further

**[00:10:08]** and it'd be really, I mean,

**[00:10:10]** what I'd love to see, for example,

**[00:10:11]** is when I hover over a line of code,

**[00:10:15]** I would like to see, you know,

**[00:10:17]** profiling information about, you know,

**[00:10:20]** just the runtime characteristics

**[00:10:21]** of that code or that function or whatever.

**[00:10:24]** I would like to see logging

**[00:10:25]** and error information overlaid.

**[00:10:27]** When I hover over a variable,

**[00:10:28]** I would like to see how, like,

**[00:10:31]** the most common values that it takes

**[00:10:33]** on in production.

**[00:10:34]** These kinds of, like, just rich, deep integrations.

**[00:10:36]** Are you a fan of inventing on principle

**[00:10:38]** and those dogs?

**[00:10:39]** Yes, yes.

**[00:10:40]** I think Brett leans too much.

**[00:10:42]** I mean, I'm a huge fan of Brett.

**[00:10:44]** But just, he's such an incredibly...

**[00:10:46]** Have you been to Dynamic Land?

**[00:10:48]** Yes.

**[00:10:48]** Okay.

**[00:10:48]** Yeah.

**[00:10:50]** And have supported it.

**[00:10:52]** So, you're a huge fan of Brett.

**[00:10:55]** The place that I've maybe differed,

**[00:10:57]** or at least that just resonates with me,

**[00:10:59]** you know, somewhat less,

**[00:11:00]** is Brett is really into this idea of,

**[00:11:04]** obviously, of graphical and visual representations

**[00:11:07]** for phenomena.

**[00:11:10]** And I think that works very well

**[00:11:12]** in certain domains,

**[00:11:14]** like the kinds of dynamical systems

**[00:11:15]** that, you know,

**[00:11:16]** he has demonstrated some of the ideas with.

**[00:11:20]** I think it's often very hard

**[00:11:22]** to find such useful,

**[00:11:25]** spatial, continuous representations

**[00:11:27]** for arbitrary systems,

**[00:11:29]** like for various parts of Stripe.

**[00:11:31]** I'm not quite sure what that would be,

**[00:11:32]** and I'm not sure,

**[00:11:33]** even if we could find it,

**[00:11:34]** you know, exactly how useful it would be.

**[00:11:35]** Maybe it's just me.

**[00:11:36]** I reason much more kind of symbolically

**[00:11:38]** and sort of lexically

**[00:11:39]** than I do visually and graphically.

**[00:11:42]** It might just be personal preference,

**[00:11:43]** but I don't know.

**[00:11:43]** The kind of paradigm breaking

**[00:11:46]** that he's been engaged in,

**[00:11:48]** I think, is hugely admirable.

**[00:11:49]** Are you going to make

**[00:11:50]** a truly integrated development environment?

**[00:11:52]** So, we are playing with ideas

**[00:11:55]** around letting the AI

**[00:11:57]** increasingly take time

**[00:11:58]** into the background

**[00:11:58]** to run its code

**[00:12:00]** and react to the output.

**[00:12:01]** And we think that

**[00:12:02]** this should all work well together.

**[00:12:04]** Like, you know,

**[00:12:05]** we've focused a ton

**[00:12:06]** on inflow, speed, and control.

**[00:12:09]** And we think that

**[00:12:10]** that's really, really important

**[00:12:11]** for AI is, you know,

**[00:12:12]** to give programmers

**[00:12:13]** the control over everything,

**[00:12:14]** have them understand

**[00:12:15]** everything the AI is producing,

**[00:12:16]** also to give them

**[00:12:17]** really, really fast iteration loops.

**[00:12:18]** Programmers hate waiting for things.

**[00:12:20]** But in some cases,

**[00:12:21]** we think it's now becoming possible

**[00:12:23]** to go tell the AI

**[00:12:24]** to think for a bit

**[00:12:25]** and then come back to you

**[00:12:26]** and have the API

**[00:12:27]** be a little bit more

**[00:12:28]** like the API

**[00:12:28]** with another human being.

**[00:12:30]** And we think you want that

**[00:12:31]** all to work well together.

**[00:12:31]** So, you know,

**[00:12:32]** the AI can come back to you

**[00:12:33]** with 70% of something

**[00:12:34]** and then you can bring it

**[00:12:35]** into the foreground

**[00:12:35]** really quickly,

**[00:12:36]** work with it,

**[00:12:37]** and then spin it back off

**[00:12:37]** to the background.

**[00:12:39]** And, you know,

**[00:12:40]** as part of having the AI

**[00:12:41]** spend a bunch of time

**[00:12:43]** thinking in the background,

**[00:12:44]** to make that thinking useful,

**[00:12:45]** you kind of needed

**[00:12:46]** to run the code

**[00:12:47]** and then react to it.

**[00:12:48]** Or else it's just kind of

**[00:12:49]** staring at the thing

**[00:12:50]** that it wrote

**[00:12:50]** and thinking more.

**[00:12:51]** Maybe I'm supposed to be

**[00:12:52]** the one answering the questions

**[00:12:54]** rather than asking them,

**[00:12:55]** but do you think

**[00:12:56]** in five years

**[00:12:59]** the main thing

**[00:13:00]** that I'm looking at

**[00:13:01]** in Cursor

**[00:13:02]** will be code

**[00:13:03]** or something else?

**[00:13:06]** I think it might be

**[00:13:07]** something else.

**[00:13:08]** I think that

**[00:13:10]** there are

**[00:13:12]** big, big, big simplification

**[00:13:13]** but kind of when you're

**[00:13:14]** defining what a piece

**[00:13:15]** of software is,

**[00:13:15]** there's like the

**[00:13:16]** logic component,

**[00:13:17]** which is what engineers

**[00:13:18]** spend a lot of time on,

**[00:13:19]** of designing exactly

**[00:13:20]** how the software works.

**[00:13:21]** There's also,

**[00:13:22]** for end user applications

**[00:13:23]** and things that have GUIs,

**[00:13:24]** there's like this visual component.

**[00:13:25]** And I think that there is,

**[00:13:26]** you know,

**[00:13:26]** maybe it's going to be us,

**[00:13:27]** maybe it's going to be someone else.

**[00:13:28]** There is a future version

**[00:13:29]** of the world

**[00:13:31]** where the way you interact

**[00:13:32]** with AI

**[00:13:33]** is a little bit less like,

**[00:13:34]** you know,

**[00:13:35]** it's a human helper

**[00:13:35]** that you're delegating work to

**[00:13:36]** or looking over your shoulder

**[00:13:37]** predicting the next set

**[00:13:38]** of things you're going to do.

**[00:13:39]** And instead,

**[00:13:39]** it's a little bit more

**[00:13:40]** of an advanced compiler

**[00:13:41]** or interpreter technology.

**[00:13:43]** And it could lead you

**[00:13:43]** to a world

**[00:13:44]** where programming languages

**[00:13:45]** actually change.

**[00:13:46]** And they can start

**[00:13:47]** to get a little bit less formal.

**[00:13:48]** They can start to get

**[00:13:49]** a little bit higher level.

**[00:13:50]** They can start to be

**[00:13:51]** a little bit more

**[00:13:52]** about what you want

**[00:13:54]** and a little bit less

**[00:13:55]** about how you do it.

**[00:13:57]** And I think that it won't look

**[00:13:58]** like a Google Doc necessarily.

**[00:14:00]** I think that there are things

**[00:14:01]** you want to keep around

**[00:14:02]** from programming,

**[00:14:02]** like the naming

**[00:14:03]** of logic somewhere

**[00:14:05]** and then using that

**[00:14:06]** in a bunch of other places.

**[00:14:07]** I think that there's also

**[00:14:08]** this other element too

**[00:14:09]** of the visuals

**[00:14:09]** of what a piece of software

**[00:14:11]** looks like.

**[00:14:11]** And I think,

**[00:14:12]** you know,

**[00:14:12]** maybe us,

**[00:14:13]** maybe some other tool,

**[00:14:14]** but I think there's a world

**[00:14:15]** where kind of direct manipulation

**[00:14:16]** of the UI

**[00:14:17]** starts to play

**[00:14:17]** a little bit more into it.

**[00:14:18]** But these are kind of

**[00:14:19]** far-flung experimental ideas.

**[00:14:22]** And...

**[00:14:23]** In general,

**[00:14:24]** I will say,

**[00:14:25]** and it's not terrible,

**[00:14:26]** but I feel like

**[00:14:29]** it's interesting to me

**[00:14:30]** that we haven't

**[00:14:33]** experimented in some sense

**[00:14:34]** that much

**[00:14:34]** with the paradigm

**[00:14:35]** of programming

**[00:14:37]** over the past 20 years.

**[00:14:38]** Yes.

**[00:14:38]** And the main things

**[00:14:39]** we're discussing here

**[00:14:40]** are from the 80s

**[00:14:42]** or the 70s.

**[00:14:43]** And, you know,

**[00:14:44]** there are way more developers

**[00:14:45]** obviously now

**[00:14:46]** than there ever have been

**[00:14:47]** in the past.

**[00:14:47]** But in some sense,

**[00:14:49]** the sort of,

**[00:14:49]** the aperture of experimentation

**[00:14:52]** there feels like

**[00:14:53]** it's really not that wide.

**[00:14:54]** And again,

**[00:14:54]** the JavaScript ecosystem

**[00:14:55]** and a couple of others

**[00:14:56]** have done some cool things.

**[00:14:57]** And there's been a lot of,

**[00:14:59]** you know,

**[00:14:59]** experimentation at the language level

**[00:15:00]** with Rust and Go

**[00:15:01]** and everything else.

**[00:15:02]** But at the kind of

**[00:15:03]** the development environment level,

**[00:15:05]** I don't know why it is.

**[00:15:06]** But maybe it's just too hard

**[00:15:07]** and complicated now,

**[00:15:08]** but there's been less

**[00:15:09]** than I would have expected.

**[00:15:09]** Yeah.

**[00:15:10]** I agree.

**[00:15:12]** And I think...

**[00:15:13]** Maybe this helps...

**[00:15:15]** Something we're working on.

**[00:15:16]** Yeah.

**[00:15:16]** Maybe this explains

**[00:15:17]** Cursor's success

**[00:15:18]** to some extent

**[00:15:19]** where, you know,

**[00:15:20]** you guys are the first people

**[00:15:21]** to really take it seriously

**[00:15:22]** in quite a while.

**[00:15:23]** Well, I mean, yeah,

**[00:15:24]** I think we also benefit a lot

**[00:15:25]** from the why now

**[00:15:25]** of, like,

**[00:15:26]** there's now this, you know,

**[00:15:27]** great new color to paint with

**[00:15:28]** or set of colors to paint with.

**[00:15:30]** I think also there's just

**[00:15:31]** a ton of lock-in

**[00:15:32]** with programming languages

**[00:15:33]** around both the neurons

**[00:15:34]** in your head

**[00:15:35]** of, like,

**[00:15:36]** programming languages

**[00:15:36]** are kind of complex UI

**[00:15:37]** for programmers

**[00:15:38]** to define exactly

**[00:15:38]** how the computer should function.

**[00:15:40]** And so, you know,

**[00:15:40]** people learn languages

**[00:15:41]** and those, you know,

**[00:15:43]** people don't like

**[00:15:44]** to learn that many things.

**[00:15:45]** And then there's also

**[00:15:46]** the lock-in of

**[00:15:46]** you have a lot of logic

**[00:15:47]** sitting around in one language

**[00:15:48]** and you need to maintain that.

**[00:15:50]** And I actually think

**[00:15:51]** that that's a pretty interesting

**[00:15:53]** or one of our hopes

**[00:15:54]** is that as AI programming

**[00:15:57]** gets better and better and better,

**[00:15:58]** one of the downsides

**[00:15:59]** of working on professional applications

**[00:16:00]** with hundreds of people

**[00:16:02]** dealing with many millions

**[00:16:03]** of lines of logic

**[00:16:03]** is the weight of the code base

**[00:16:04]** really starts to weigh on you.

**[00:16:06]** Yeah.

**[00:16:07]** And so the feeling

**[00:16:08]** of being in a net new code base

**[00:16:09]** where it's just

**[00:16:10]** everything feels effortless,

**[00:16:11]** goes away,

**[00:16:11]** everything's, you know,

**[00:16:12]** a chore,

**[00:16:13]** you have to, you know,

**[00:16:14]** change one thing here,

**[00:16:15]** brace, you know,

**[00:16:16]** something else here,

**[00:16:17]** and it becomes kind of

**[00:16:18]** this big ball of mud.

**[00:16:21]** And making that effortless,

**[00:16:23]** reducing the kind of weight

**[00:16:24]** of an existing set of logic,

**[00:16:25]** I think is, you know,

**[00:16:25]** one of the areas

**[00:16:26]** in which AI can, you know,

**[00:16:27]** make programming better.

**[00:16:28]** Someone said on Twitter today,

**[00:16:31]** maybe it was Andre Carpathy,

**[00:16:34]** but maybe I'm misattributing that

**[00:16:36]** and, you know,

**[00:16:37]** too many things to do

**[00:16:39]** with a vibe coding

**[00:16:40]** get attributed to Andre,

**[00:16:41]** like, you know,

**[00:16:42]** to Churchill or Einstein

**[00:16:43]** or something,

**[00:16:43]** but I think about him.

**[00:16:47]** But this person,

**[00:16:48]** whoever it was,

**[00:16:48]** was making an observation

**[00:16:49]** that, you know,

**[00:16:50]** it's one thing to be prompting

**[00:16:52]** the creation of code,

**[00:16:53]** but another place

**[00:16:54]** where AI could conceivably

**[00:16:55]** do a lot to help

**[00:16:56]** is in the beautification

**[00:16:58]** and the refactoring

**[00:16:58]** of code bases,

**[00:16:59]** and you can imagine

**[00:17:00]** that, you know,

**[00:17:00]** you're producing all this,

**[00:17:01]** you know,

**[00:17:02]** a little bit ungainly,

**[00:17:03]** not quite correctly factored,

**[00:17:05]** you know,

**[00:17:06]** detritus at the front

**[00:17:07]** and you have this,

**[00:17:09]** you know,

**[00:17:09]** and then nocturnally

**[00:17:10]** this thing comes up behind you

**[00:17:12]** and makes it all,

**[00:17:12]** you know,

**[00:17:12]** beautifully factored.

**[00:17:13]** And the only CS class

**[00:17:14]** I ever took

**[00:17:15]** was this class

**[00:17:16]** from Jerry Sussman

**[00:17:18]** on,

**[00:17:20]** it was basically focused on,

**[00:17:22]** I mean,

**[00:17:22]** he called it

**[00:17:22]** large-scale symbolic systems,

**[00:17:24]** but really what he was

**[00:17:25]** trying to focus on

**[00:17:26]** was the idea

**[00:17:27]** of creating code bases

**[00:17:28]** and environments

**[00:17:30]** and abstractions

**[00:17:32]** that were easy to modify.

**[00:17:34]** And like,

**[00:17:34]** there were no assignments

**[00:17:35]** in the class

**[00:17:35]** where you had to write

**[00:17:35]** something from scratch.

**[00:17:36]** Every assignment

**[00:17:37]** was about modifying

**[00:17:38]** an existing system

**[00:17:39]** and thinking about

**[00:17:40]** how could you design things

**[00:17:40]** in such a way

**[00:17:41]** that those modifications

**[00:17:42]** become,

**[00:17:42]** and you know,

**[00:17:43]** there might be quite

**[00:17:43]** deep modifications,

**[00:17:45]** become straightforward.

**[00:17:47]** And I think

**[00:17:47]** that's a lovely idea.

**[00:17:49]** Obviously in practice

**[00:17:50]** it's often very difficult

**[00:17:52]** to do that

**[00:17:52]** given all the exigencies

**[00:17:53]** and pressures

**[00:17:54]** of the things you want to ship,

**[00:17:55]** you know,

**[00:17:55]** today and next week

**[00:17:55]** and so forth.

**[00:17:56]** But if you could have an AI,

**[00:17:57]** like often when you're

**[00:17:58]** writing this stuff

**[00:17:58]** you realize,

**[00:17:58]** well,

**[00:17:59]** I really should be doing it

**[00:18:00]** the beautiful way,

**[00:18:00]** but I'm not.

**[00:18:01]** Maybe we could have an AI

**[00:18:03]** coming up behind us

**[00:18:03]** to change it.

**[00:18:04]** Yes,

**[00:18:04]** yes,

**[00:18:05]** maybe soon.

**[00:18:06]** One thing that happens

**[00:18:07]** to a lot of developers

**[00:18:08]** that care,

**[00:18:09]** or a lot of people

**[00:18:10]** come to development

**[00:18:10]** because they care

**[00:18:11]** about building things.

**[00:18:12]** They want to make things

**[00:18:13]** happen on the computer screen.

**[00:18:14]** And so then that leads

**[00:18:16]** them to coding.

**[00:18:16]** And then something

**[00:18:17]** that happens to,

**[00:18:19]** you know,

**[00:18:19]** a big group of developers

**[00:18:20]** is they eventually realize

**[00:18:21]** the software they want to create

**[00:18:22]** is too big

**[00:18:23]** that they can't write,

**[00:18:24]** you know,

**[00:18:24]** all of the code themselves

**[00:18:25]** and they have to go to humans

**[00:18:26]** to help them write the code.

**[00:18:28]** And so maybe they then

**[00:18:29]** become an engineering manager,

**[00:18:30]** director,

**[00:18:31]** whatever it is.

**[00:18:31]** Maybe they start a company,

**[00:18:32]** right?

**[00:18:33]** And then most of the work

**[00:18:34]** becomes not typing code.

**[00:18:35]** It becomes,

**[00:18:35]** you know,

**[00:18:35]** coordinating amongst people.

**[00:18:36]** Do you think that there are

**[00:18:37]** any ideas from programming

**[00:18:39]** that are helpful

**[00:18:39]** for the act of kind of

**[00:18:41]** programming amongst

**[00:18:42]** the organization

**[00:18:42]** to get a group of people

**[00:18:43]** to build software together?

**[00:18:46]** Interesting.

**[00:18:46]** I think taking APIs

**[00:18:49]** and data models

**[00:18:51]** really seriously.

**[00:18:52]** If I was to do everything

**[00:18:54]** at Stripe again,

**[00:18:55]** I mean,

**[00:18:56]** there's a million small things

**[00:18:57]** that you would do differently

**[00:18:58]** and even some kind of big things.

**[00:19:00]** But the thing that I think

**[00:19:01]** we could maybe foreseeably

**[00:19:04]** and beneficially done differently

**[00:19:09]** would be to have spent

**[00:19:10]** even more time than we did

**[00:19:12]** on APIs and data models.

**[00:19:16]** And, you know,

**[00:19:17]** part of the reason is

**[00:19:21]** the, I guess,

**[00:19:22]** Conway's law effect

**[00:19:23]** of how both of those things

**[00:19:24]** end up shaping the organization.

**[00:19:26]** So I guess if you don't

**[00:19:27]** deeply internalize that,

**[00:19:28]** then maybe you've less control

**[00:19:30]** over the organizational dynamics

**[00:19:32]** than you might otherwise

**[00:19:33]** like to have.

**[00:19:34]** But also,

**[00:19:35]** I think it ends up

**[00:19:37]** shaping not only,

**[00:19:38]** I mean,

**[00:19:38]** the weak version of Conway's law

**[00:19:39]** is that it shapes your organization.

**[00:19:42]** I think the strong version

**[00:19:43]** is that it substantially

**[00:19:44]** shapes your strategy

**[00:19:45]** and just your business outcomes.

**[00:19:48]** And this isn't exactly

**[00:19:52]** maybe a version of that,

**[00:19:54]** but I often reflect

**[00:19:55]** on how the iOS software ecosystem

**[00:19:59]** for a very long time

**[00:20:00]** and, you know,

**[00:20:01]** plausibly still today

**[00:20:02]** was so much more vibrant

**[00:20:04]** and kind of vital

**[00:20:05]** and successful

**[00:20:08]** than the Android app ecosystem.

**[00:20:10]** And, you know,

**[00:20:11]** there's a lot of things

**[00:20:12]** that are different

**[00:20:13]** across those two ecosystems.

**[00:20:16]** There are now way more

**[00:20:17]** Android devices in use,

**[00:20:18]** I believe,

**[00:20:19]** than iOS devices.

**[00:20:21]** But I think much of the,

**[00:20:24]** the fact that app developers

**[00:20:27]** tended to prefer

**[00:20:29]** building their apps on iOS

**[00:20:31]** and releasing their apps

**[00:20:31]** first on iOS

**[00:20:32]** and maybe the iOS version

**[00:20:33]** being better

**[00:20:34]** than the Android version

**[00:20:34]** or, you know, whatever,

**[00:20:35]** is because the frameworks

**[00:20:37]** and the abstractions

**[00:20:39]** for iOS

**[00:20:39]** were just originally better

**[00:20:41]** than the Android ones.

**[00:20:42]** And so,

**[00:20:43]** but I think that's a case

**[00:20:44]** where the right API design,

**[00:20:45]** the right abstraction design,

**[00:20:47]** ended up having

**[00:20:48]** just quite significant

**[00:20:49]** business ramifications.

**[00:20:51]** And, you know,

**[00:20:51]** I think there's kind of a sense

**[00:20:52]** that maybe it's not worth

**[00:20:53]** dwelling on these things

**[00:20:54]** because, you know,

**[00:20:55]** everything in technology

**[00:20:55]** changes so rapidly

**[00:20:56]** and, you know,

**[00:20:58]** whatever assumptions you make,

**[00:20:58]** they'll be, you know,

**[00:20:59]** obsolete in two years

**[00:21:00]** or something.

**[00:21:00]** I think in practice

**[00:21:02]** that's not true.

**[00:21:03]** And that, like,

**[00:21:03]** the right API design

**[00:21:04]** and the right abstractions

**[00:21:05]** and the right data models

**[00:21:06]** can really endure.

**[00:21:07]** And, you know,

**[00:21:07]** for the first versions of iOS,

**[00:21:09]** many of the classes

**[00:21:10]** that one used

**[00:21:11]** were prefixed with NS.

**[00:21:13]** NS, of course,

**[00:21:14]** standing for next step, right?

**[00:21:16]** And so that's a case

**[00:21:16]** where the API design

**[00:21:17]** survived for, you know,

**[00:21:19]** two decades or more.

**[00:21:21]** And in the case of Stripe,

**[00:21:23]** you know,

**[00:21:23]** Stripe is now 15 years old

**[00:21:24]** and, you know,

**[00:21:25]** there were lots of things

**[00:21:25]** that we designed 15 years ago

**[00:21:26]** that are still, you know,

**[00:21:27]** in use today,

**[00:21:28]** which is, you know,

**[00:21:29]** kind of good and bad

**[00:21:30]** in the sense that

**[00:21:31]** they endured,

**[00:21:32]** but also we are still,

**[00:21:33]** you know,

**[00:21:35]** we are still under the...

**[00:21:38]** Living with their faults.

**[00:21:38]** Exactly.

**[00:21:39]** And so, anyway,

**[00:21:41]** that's maybe the thing

**[00:21:42]** that I would,

**[00:21:43]** that's the first thing

**[00:21:44]** that comes to mind.

**[00:21:44]** In fact,

**[00:21:45]** on that final note,

**[00:21:46]** I was talking with

**[00:21:47]** an engineering leader

**[00:21:49]** at, you know,

**[00:21:49]** kind of a preeminent,

**[00:21:50]** successful Silicon Valley

**[00:21:52]** private company.

**[00:21:54]** And they were talking

**[00:21:55]** about how their code base

**[00:21:56]** is largely in Scala.

**[00:21:58]** and they said

**[00:21:59]** that they like to think

**[00:22:00]** of kind of the beginnings

**[00:22:01]** of the startup

**[00:22:02]** as this big bang moment

**[00:22:04]** where this,

**[00:22:05]** these, you know,

**[00:22:06]** tired, overworked,

**[00:22:08]** maybe over-caffeinated

**[00:22:09]** founding team members

**[00:22:10]** are willy-nilly

**[00:22:11]** making these initial

**[00:22:12]** technical decisions

**[00:22:13]** that then dictate the lives

**[00:22:14]** of hundreds of professional

**[00:22:15]** engineers in the future.

**[00:22:17]** And that Scala choice

**[00:22:18]** was one of them

**[00:22:18]** and they sort of live

**[00:22:20]** with the faults of that now.

**[00:22:22]** But what are those kind of,

**[00:22:24]** what were the consequential,

**[00:22:25]** it could be good or bad,

**[00:22:27]** initial conditions

**[00:22:27]** of the stripe big bang

**[00:22:29]** that you guys still live

**[00:22:29]** with right now?

**[00:22:31]** I mean, I think that

**[00:22:34]** metaphor is,

**[00:22:36]** well, it sounds true to me

**[00:22:39]** is the first thing I'd say.

**[00:22:40]** I mean, maybe it's a little bit

**[00:22:42]** of kind of survivorship bias

**[00:22:43]** where like the actual statement

**[00:22:44]** is the early decisions

**[00:22:47]** that we made

**[00:22:48]** that we never changed

**[00:22:49]** are decisions that we lived with.

**[00:22:51]** But, you know,

**[00:22:51]** there's a kind of

**[00:22:53]** tautology there or something.

**[00:22:54]** And there are certainly

**[00:22:56]** design decisions

**[00:22:57]** we made pretty early on

**[00:22:58]** that are not true today.

**[00:23:00]** So, you know,

**[00:23:01]** early versions of

**[00:23:02]** the Stripe dashboard

**[00:23:03]** or something

**[00:23:03]** were built extraordinarily

**[00:23:04]** differently to,

**[00:23:05]** you know,

**[00:23:05]** the dashboard today.

**[00:23:07]** And the converse

**[00:23:08]** is also true.

**[00:23:09]** So, you know,

**[00:23:10]** initially,

**[00:23:10]** we decided to use

**[00:23:12]** MongoDB at Stripe

**[00:23:13]** and we decided to use

**[00:23:14]** Ruby at Stripe.

**[00:23:15]** And those are still

**[00:23:16]** quite foundational technologies

**[00:23:19]** at Stripe.

**[00:23:20]** And, you know,

**[00:23:21]** we had to build

**[00:23:22]** a lot of, you know,

**[00:23:25]** infrastructure

**[00:23:25]** in order to make

**[00:23:26]** MongoDB as fault tolerant

**[00:23:28]** and as distributed

**[00:23:29]** and as durable

**[00:23:31]** and as reliable

**[00:23:32]** and everything

**[00:23:32]** as we needed it to be

**[00:23:34]** and as it now is.

**[00:23:36]** Like we had Stripe's

**[00:23:38]** critical API availability

**[00:23:39]** last year

**[00:23:40]** was 99.99986%,

**[00:23:43]** which is 44 seconds

**[00:23:45]** of unavailability

**[00:23:46]** through the whole year,

**[00:23:48]** which is,

**[00:23:49]** we thin,

**[00:23:50]** and others don't publish

**[00:23:52]** statistics that are

**[00:23:53]** kind of granular,

**[00:23:53]** but we believe that is

**[00:23:54]** the best in the industry.

**[00:23:56]** And so, you know,

**[00:23:57]** everything that our

**[00:23:58]** storage team has built

**[00:23:59]** and many other teams,

**[00:24:00]** you know,

**[00:24:00]** it ended up really

**[00:24:01]** working there,

**[00:24:02]** but that was a quite

**[00:24:03]** important critical decision,

**[00:24:05]** initial decision.

**[00:24:06]** And, you know,

**[00:24:07]** Ruby, similarly,

**[00:24:09]** I guess,

**[00:24:10]** companies sometimes

**[00:24:11]** change languages,

**[00:24:11]** you know,

**[00:24:12]** along the way,

**[00:24:13]** but I feel like

**[00:24:13]** the initial language

**[00:24:15]** chosen tends to have a...

**[00:24:16]** I heard there were

**[00:24:16]** debates in Stripe about,

**[00:24:18]** or one of,

**[00:24:19]** actually,

**[00:24:20]** one of our co-founders,

**[00:24:22]** interned at Stripe

**[00:24:23]** early on,

**[00:24:24]** or not early on

**[00:24:25]** in Stripe's history,

**[00:24:26]** early on in kind of

**[00:24:27]** our collective

**[00:24:27]** personal history.

**[00:24:29]** And he remembers

**[00:24:30]** there being documents

**[00:24:31]** upon documents

**[00:24:32]** about a potential

**[00:24:33]** Java migration.

**[00:24:34]** Yeah.

**[00:24:34]** So we,

**[00:24:36]** that partly happened,

**[00:24:38]** as in,

**[00:24:39]** we have rewritten

**[00:24:40]** a bunch of key

**[00:24:40]** services on Java,

**[00:24:42]** so some services

**[00:24:43]** for which,

**[00:24:44]** I don't know,

**[00:24:45]** throughput,

**[00:24:46]** throughput in particular

**[00:24:47]** is really important.

**[00:24:48]** And if you torture

**[00:24:50]** Ruby enough

**[00:24:51]** and, you know,

**[00:24:52]** maybe rewrite

**[00:24:53]** parts of it,

**[00:24:54]** you know,

**[00:24:54]** parts of some

**[00:24:56]** hot paths

**[00:24:57]** in C or something,

**[00:24:58]** you can get it

**[00:24:59]** to be pretty fast.

**[00:25:00]** But you're often

**[00:25:01]** fighting against

**[00:25:01]** the allocator

**[00:25:03]** and, you know,

**[00:25:04]** various parts of,

**[00:25:05]** even just like Ruby strings

**[00:25:06]** are not that efficient

**[00:25:07]** and stuff.

**[00:25:07]** So we've written

**[00:25:09]** certain services

**[00:25:09]** in Java

**[00:25:10]** and now we use both.

**[00:25:13]** Why did you,

**[00:25:13]** or did you consider

**[00:25:14]** anything other than Mongo

**[00:25:15]** and why did you pick

**[00:25:17]** Mongo early on?

**[00:25:18]** And what was the,

**[00:25:19]** what was the RFC process,

**[00:25:21]** RFP process,

**[00:25:22]** decision making process

**[00:25:24]** for that?

**[00:25:25]** it was just me and John.

**[00:25:26]** So, you know,

**[00:25:26]** we were sitting on the couch

**[00:25:27]** and it's like,

**[00:25:28]** should we use Mongo?

**[00:25:28]** Yeah, fine.

**[00:25:29]** Did they,

**[00:25:30]** did they get through

**[00:25:31]** to you with like a blog

**[00:25:32]** or was it

**[00:25:34]** the,

**[00:25:34]** just the reputation

**[00:25:35]** of Mongo at the time

**[00:25:36]** and open source communities,

**[00:25:37]** something else?

**[00:25:38]** I think it was,

**[00:25:40]** so I wrote

**[00:25:41]** a data store

**[00:25:42]** for our,

**[00:25:43]** for our prior company

**[00:25:45]** and object-based

**[00:25:47]** data store

**[00:25:48]** and I didn't really

**[00:25:50]** like SQL.

**[00:25:51]** I thought it was,

**[00:25:52]** there was too much

**[00:25:53]** of a translational

**[00:25:54]** kind of mismatch

**[00:25:55]** between the domain

**[00:25:57]** of the application

**[00:25:58]** and, you know,

**[00:26:00]** that's which SQL

**[00:26:01]** natively,

**[00:26:02]** you know,

**[00:26:03]** makes expressible.

**[00:26:04]** And so,

**[00:26:05]** you know,

**[00:26:06]** with SQL,

**[00:26:06]** obviously you have

**[00:26:07]** to collapse down

**[00:26:07]** into,

**[00:26:08]** you know,

**[00:26:08]** a relatively restricted

**[00:26:09]** set of primitive forms

**[00:26:10]** whereas in your application,

**[00:26:12]** you know,

**[00:26:12]** you might have a concept

**[00:26:13]** of,

**[00:26:14]** I don't know,

**[00:26:15]** let's say in the case

**[00:26:15]** of Stripe,

**[00:26:16]** of money

**[00:26:16]** that doesn't like

**[00:26:17]** exactly comport

**[00:26:18]** with how the particular

**[00:26:19]** SQL database you're using

**[00:26:20]** happens to represent money

**[00:26:21]** or, you know,

**[00:26:22]** whatever the case might be.

**[00:26:23]** And so,

**[00:26:24]** yeah,

**[00:26:24]** I just had this like

**[00:26:25]** principled objection

**[00:26:26]** to SQL.

**[00:26:27]** I'm not endorsing this

**[00:26:28]** or saying it was good

**[00:26:29]** but I,

**[00:26:30]** as this interview shows,

**[00:26:33]** I suppose,

**[00:26:33]** I had all sorts of,

**[00:26:34]** you know,

**[00:26:35]** strange notions

**[00:26:35]** about technology

**[00:26:37]** and with Stripe

**[00:26:39]** we wanted to be

**[00:26:40]** more mainstream

**[00:26:41]** than,

**[00:26:42]** and a little bit more,

**[00:26:44]** you know,

**[00:26:45]** a little bit

**[00:26:46]** less heterodox

**[00:26:47]** in our technology choices

**[00:26:49]** than our prior company

**[00:26:50]** and so instead of using

**[00:26:50]** Smalltalk,

**[00:26:52]** you know,

**[00:26:52]** okay,

**[00:26:52]** we weren't going to go to Java

**[00:26:53]** but we went to Ruby

**[00:26:54]** which at least

**[00:26:54]** on a relative basis

**[00:26:55]** seemed more mainstream

**[00:26:56]** and similarly,

**[00:26:57]** rather than write

**[00:26:57]** our own object database,

**[00:26:59]** we went relatively

**[00:27:00]** more mainstream

**[00:27:00]** and used Mongo

**[00:27:02]** which still give a lot

**[00:27:03]** of flexibility,

**[00:27:04]** you know,

**[00:27:05]** by virtue of being

**[00:27:05]** a kind of object

**[00:27:07]** data store

**[00:27:08]** so that was fine.

**[00:27:10]** Everything I've said

**[00:27:11]** might disqualify me

**[00:27:12]** from,

**[00:27:12]** you know,

**[00:27:12]** ever making technology choices

**[00:27:13]** for another company

**[00:27:16]** but...

**[00:27:17]** Would you do anything

**[00:27:18]** differently about Stripe V2?

**[00:27:19]** We haven't talked

**[00:27:20]** that much about it

**[00:27:22]** publicly yet

**[00:27:24]** and the answer

**[00:27:25]** might be a bit like,

**[00:27:26]** you know,

**[00:27:27]** there's the

**[00:27:28]** Zhu Enlai

**[00:27:28]** quote about the

**[00:27:30]** or is it Deng Xiaoping?

**[00:27:31]** About the French Revolution,

**[00:27:33]** you know,

**[00:27:33]** it's too soon to judge

**[00:27:35]** and so back in

**[00:27:38]** 2022,

**[00:27:40]** I believe,

**[00:27:43]** we,

**[00:27:44]** I mean,

**[00:27:44]** to this discussion

**[00:27:45]** about data models

**[00:27:46]** and abstractions,

**[00:27:47]** we realized that

**[00:27:48]** a couple of the core

**[00:27:49]** abstractions in Stripe

**[00:27:50]** were just

**[00:27:52]** not the right

**[00:27:53]** long-term abstractions

**[00:27:53]** and we

**[00:27:54]** had to fix that

**[00:27:55]** and so we

**[00:27:57]** designed a bunch

**[00:27:58]** of V2 APIs.

**[00:28:00]** Fortunately,

**[00:28:00]** we had contemplated

**[00:28:02]** the possibility

**[00:28:02]** of this earlier

**[00:28:03]** at Stripe

**[00:28:03]** so,

**[00:28:03]** you know,

**[00:28:04]** most of the,

**[00:28:05]** you know,

**[00:28:06]** REST URIs

**[00:28:07]** that people

**[00:28:08]** are familiar with

**[00:28:09]** in Stripe

**[00:28:09]** are prefixed

**[00:28:10]** with slash V1

**[00:28:11]** and they've been

**[00:28:12]** prefixed with slash V1

**[00:28:13]** from,

**[00:28:13]** you know,

**[00:28:14]** 2010

**[00:28:14]** and so then

**[00:28:16]** in 2022

**[00:28:16]** we decided,

**[00:28:17]** okay,

**[00:28:17]** we might use the,

**[00:28:19]** you know,

**[00:28:19]** increment the

**[00:28:21]** namespace.

**[00:28:22]** So we designed

**[00:28:23]** those new APIs.

**[00:28:24]** They started to ship

**[00:28:26]** this year

**[00:28:27]** and,

**[00:28:28]** congratulations.

**[00:28:29]** Thank you.

**[00:28:30]** And we're extremely

**[00:28:31]** excited about the

**[00:28:32]** functionality that it's

**[00:28:33]** going to enable

**[00:28:33]** and,

**[00:28:34]** you know,

**[00:28:34]** without getting into

**[00:28:35]** the arcana of it,

**[00:28:37]** you know,

**[00:28:37]** they will enable

**[00:28:38]** things like,

**[00:28:39]** historically,

**[00:28:40]** we have,

**[00:28:41]** we have drawn

**[00:28:42]** distinctions

**[00:28:43]** and represented

**[00:28:45]** separately

**[00:28:45]** things like

**[00:28:46]** end customers,

**[00:28:48]** things like

**[00:28:49]** sub accounts,

**[00:28:50]** things like

**[00:28:51]** recipients

**[00:28:51]** for different

**[00:28:52]** kinds of

**[00:28:53]** payments

**[00:28:54]** and we're

**[00:28:54]** unifying all

**[00:28:55]** of those

**[00:28:56]** into being,

**[00:28:57]** you know,

**[00:28:57]** into the

**[00:28:58]** same kind of

**[00:29:00]** entity representation

**[00:29:01]** which is,

**[00:29:02]** on some level,

**[00:29:02]** clearly the right

**[00:29:03]** answer and,

**[00:29:04]** you know,

**[00:29:04]** makes a lot of,

**[00:29:06]** it will

**[00:29:07]** and is already

**[00:29:11]** changing the

**[00:29:11]** businesses

**[00:29:12]** of some of our

**[00:29:12]** customers because

**[00:29:13]** they can,

**[00:29:15]** you know,

**[00:29:15]** enable their users

**[00:29:16]** to do various

**[00:29:17]** things without

**[00:29:18]** having to

**[00:29:18]** re-enter details

**[00:29:19]** or maybe to

**[00:29:20]** bring the same

**[00:29:20]** account across

**[00:29:21]** different countries

**[00:29:21]** or, you know,

**[00:29:22]** whatever the case

**[00:29:22]** might be.

**[00:29:23]** Anyway,

**[00:29:23]** it's been a

**[00:29:24]** long journey

**[00:29:24]** and the

**[00:29:26]** reason it

**[00:29:27]** was a long

**[00:29:28]** journey is

**[00:29:31]** I guess

**[00:29:32]** because

**[00:29:35]** it's not

**[00:29:35]** that useful

**[00:29:36]** to just

**[00:29:37]** define these

**[00:29:38]** APIs in

**[00:29:38]** isolation.

**[00:29:39]** If we just

**[00:29:39]** wanted to

**[00:29:39]** define them

**[00:29:40]** in isolation,

**[00:29:40]** that's a

**[00:29:40]** pretty easy

**[00:29:41]** thing to do.

**[00:29:42]** The thing

**[00:29:42]** that's difficult

**[00:29:43]** is to make

**[00:29:43]** them interoperable

**[00:29:44]** with all the

**[00:29:45]** existing things

**[00:29:46]** at Stripe

**[00:29:46]** and to build

**[00:29:46]** translation layers

**[00:29:47]** and so forth

**[00:29:51]** and then to

**[00:29:52]** figure out

**[00:29:52]** with our

**[00:29:53]** customers

**[00:29:54]** what a

**[00:29:54]** sensible

**[00:29:55]** upgrade path

**[00:29:56]** might look

**[00:29:57]** like because

**[00:29:57]** we control

**[00:29:58]** our code base,

**[00:29:58]** we don't

**[00:29:58]** control theirs.

**[00:30:01]** I don't want to

**[00:30:02]** exaggerate it,

**[00:30:03]** but in a certain

**[00:30:04]** respect at least

**[00:30:05]** it feels a bit

**[00:30:05]** more like an

**[00:30:06]** instruction set

**[00:30:06]** migration for

**[00:30:07]** a chip architecture

**[00:30:09]** or something

**[00:30:09]** where the

**[00:30:10]** instruction set

**[00:30:11]** by itself is

**[00:30:12]** easy but it's

**[00:30:13]** all the kind of

**[00:30:13]** coexistence questions

**[00:30:14]** that become hard.

**[00:30:15]** It started to

**[00:30:16]** ship this year

**[00:30:16]** and we're

**[00:30:18]** excited about it.

**[00:30:19]** I mean I guess

**[00:30:19]** your question was

**[00:30:20]** maybe what

**[00:30:21]** lessons we've

**[00:30:21]** learned from it

**[00:30:22]** and do you

**[00:30:24]** think there's

**[00:30:24]** anything bigger

**[00:30:25]** to draw out

**[00:30:25]** of that on

**[00:30:26]** either projects

**[00:30:27]** that are

**[00:30:28]** rewrites or

**[00:30:29]** thinking about

**[00:30:29]** these kind of

**[00:30:30]** decades long

**[00:30:31]** abstractions and

**[00:30:32]** how to do that

**[00:30:33]** well?

**[00:30:34]** My trite

**[00:30:36]** answer to that

**[00:30:37]** is to

**[00:30:38]** unify

**[00:30:40]** everything you

**[00:30:41]** can plausibly

**[00:30:41]** unify and

**[00:30:43]** How do you

**[00:30:43]** test design ideas

**[00:30:44]** for V2?

**[00:30:45]** Well the people

**[00:30:47]** designing it

**[00:30:47]** well I'll give

**[00:30:49]** you one other

**[00:30:49]** lesson and then

**[00:30:50]** I'll answer that

**[00:30:50]** question.

**[00:30:50]** And also is there

**[00:30:53]** some chief API

**[00:30:54]** designer who's

**[00:30:55]** the mastermind

**[00:30:56]** and it's one

**[00:30:57]** person it's not

**[00:30:58]** some sort of

**[00:30:58]** working group?

**[00:30:59]** There is a

**[00:30:59]** working group

**[00:31:00]** there are

**[00:31:00]** working groups

**[00:31:01]** but there is

**[00:31:02]** also a singular

**[00:31:03]** person who

**[00:31:05]** understands and

**[00:31:06]** is more than

**[00:31:08]** anyone else

**[00:31:08]** responsible for

**[00:31:09]** the whole

**[00:31:10]** and I think

**[00:31:11]** that's necessary.

**[00:31:13]** My other

**[00:31:15]** trite

**[00:31:15]** exhortation

**[00:31:16]** would be

**[00:31:16]** to make

**[00:31:17]** anything that

**[00:31:18]** plausibly could

**[00:31:19]** be an

**[00:31:19]** N by M

**[00:31:20]** relationship

**[00:31:21]** to support

**[00:31:22]** that because

**[00:31:23]** if you only

**[00:31:24]** support 1 to

**[00:31:25]** N or

**[00:31:25]** N to 1

**[00:31:26]** or whatever

**[00:31:27]** and even if

**[00:31:29]** it's non-obvious

**[00:31:29]** how it could

**[00:31:30]** possibly be

**[00:31:30]** N to M

**[00:31:31]** just inevitably

**[00:31:33]** you'll end up

**[00:31:34]** needing that

**[00:31:34]** and you'll

**[00:31:35]** think well

**[00:31:35]** you could never

**[00:31:36]** have a company

**[00:31:37]** that's owned

**[00:31:38]** by two different

**[00:31:39]** companies or

**[00:31:39]** something but

**[00:31:40]** it turns out

**[00:31:40]** that every

**[00:31:41]** permutation

**[00:31:42]** in the space

**[00:31:42]** is in fact

**[00:31:43]** eventually

**[00:31:44]** explored.

**[00:31:47]** As to

**[00:31:50]** how to

**[00:31:51]** do that

**[00:31:52]** well

**[00:31:52]** I really

**[00:31:54]** feel like

**[00:31:54]** it's

**[00:31:57]** these new

**[00:31:57]** APIs

**[00:31:58]** we think

**[00:31:58]** they're the

**[00:31:59]** well

**[00:31:59]** you asked

**[00:32:00]** the question

**[00:32:00]** how do we

**[00:32:01]** know they're

**[00:32:01]** the right

**[00:32:01]** APIs

**[00:32:02]** partly from

**[00:32:03]** showing early

**[00:32:04]** versions of

**[00:32:05]** them to

**[00:32:05]** customers

**[00:32:06]** partly because

**[00:32:07]** the people

**[00:32:07]** who designed

**[00:32:07]** them had

**[00:32:08]** spent many

**[00:32:09]** many years

**[00:32:09]** in the

**[00:32:12]** witnessing

**[00:32:12]** and living

**[00:32:13]** with the

**[00:32:14]** shortcomings

**[00:32:14]** of the

**[00:32:15]** prior versions

**[00:32:15]** so we were

**[00:32:16]** coming with

**[00:32:17]** strong opinions

**[00:32:18]** but even

**[00:32:19]** the strong

**[00:32:19]** opinions

**[00:32:19]** one can

**[00:32:20]** sometimes

**[00:32:21]** predict

**[00:32:21]** wrongly

**[00:32:23]** or

**[00:32:23]** over-engineer

**[00:32:24]** something

**[00:32:24]** or whatever

**[00:32:25]** so I think

**[00:32:25]** the cycles

**[00:32:26]** of customer

**[00:32:26]** validation

**[00:32:27]** and customer

**[00:32:27]** feedback

**[00:32:28]** are extremely

**[00:32:29]** important

**[00:32:29]** and it's

**[00:32:30]** also very

**[00:32:30]** important

**[00:32:30]** we did

**[00:32:30]** a lot

**[00:32:31]** of this

**[00:32:31]** to literally

**[00:32:32]** write the

**[00:32:33]** integrations

**[00:32:33]** that would

**[00:32:34]** exist

**[00:32:34]** in the new

**[00:32:35]** world

**[00:32:35]** because

**[00:32:36]** I mean

**[00:32:37]** you really

**[00:32:37]** I mean

**[00:32:38]** I think

**[00:32:39]** Java

**[00:32:40]** is maybe

**[00:32:40]** an example

**[00:32:40]** of

**[00:32:41]** yes

**[00:32:42]** it fixes

**[00:32:42]** a bunch

**[00:32:43]** of problems

**[00:32:44]** with memory

**[00:32:44]** management

**[00:32:44]** or whatever

**[00:32:45]** that existed

**[00:32:45]** with C

**[00:32:47]** or C++

**[00:32:47]** and antecedents

**[00:32:48]** but at the

**[00:32:49]** cost of a lot

**[00:32:50]** of prolixity

**[00:32:51]** and overhead

**[00:32:53]** and in order

**[00:32:55]** to kind of

**[00:32:56]** safeguard

**[00:32:57]** ourselves

**[00:32:57]** against

**[00:32:59]** inadvertently

**[00:33:00]** over-engineering

**[00:33:01]** things

**[00:33:01]** we force

**[00:33:02]** ourselves

**[00:33:02]** to write

**[00:33:04]** a lot

**[00:33:04]** of API

**[00:33:05]** code

**[00:33:05]** specifically

**[00:33:06]** describing

**[00:33:07]** how we

**[00:33:07]** would

**[00:33:07]** implement

**[00:33:08]** various

**[00:33:08]** business

**[00:33:09]** models

**[00:33:09]** and flows

**[00:33:09]** and so

**[00:33:10]** forth

**[00:33:10]** just to

**[00:33:10]** make sure

**[00:33:11]** that when

**[00:33:11]** you look

**[00:33:12]** at it

**[00:33:12]** it feels

**[00:33:12]** right

**[00:33:12]** but I

**[00:33:13]** don't

**[00:33:13]** want to

**[00:33:14]** endorse

**[00:33:14]** our

**[00:33:14]** approaches

**[00:33:15]** too strongly

**[00:33:15]** just yet

**[00:33:16]** I mean

**[00:33:16]** I'm feeling

**[00:33:16]** very optimistic

**[00:33:17]** but

**[00:33:17]** you know

**[00:33:18]** we're

**[00:33:20]** I don't know

**[00:33:20]** what fraction

**[00:33:21]** but

**[00:33:23]** 60-70%

**[00:33:24]** done or

**[00:33:24]** something

**[00:33:24]** but not

**[00:33:25]** like 100%

**[00:33:25]** and so

**[00:33:26]** I don't

**[00:33:27]** want to

**[00:33:27]** prematurely

**[00:33:28]** declare any

**[00:33:29]** victory

**[00:33:29]** How do

**[00:33:30]** you

**[00:33:30]** Patrick

**[00:33:31]** Collison

**[00:33:31]** use

**[00:33:31]** AI?

**[00:33:31]** Well

**[00:33:33]** I

**[00:33:35]** the main

**[00:33:36]** ways

**[00:33:37]** are

**[00:33:37]** the

**[00:33:38]** predictable

**[00:33:38]** ones

**[00:33:38]** where

**[00:33:39]** I

**[00:33:39]** use

**[00:33:40]** LLM

**[00:33:41]** chat

**[00:33:41]** tools

**[00:33:41]** a lot

**[00:33:43]** and

**[00:33:45]** mainly

**[00:33:47]** for

**[00:33:49]** answering

**[00:33:49]** kind of

**[00:33:51]** factual

**[00:33:51]** or empirical

**[00:33:52]** questions

**[00:33:52]** I'm curious

**[00:33:53]** about

**[00:33:53]** so for

**[00:33:55]** deep

**[00:33:56]** research

**[00:33:56]** style

**[00:33:56]** questions

**[00:33:57]** I don't

**[00:33:57]** always

**[00:33:57]** use

**[00:33:57]** deep

**[00:33:58]** research

**[00:33:58]** and now

**[00:33:58]** the

**[00:33:58]** LLMs

**[00:33:59]** are getting

**[00:33:59]** better

**[00:33:59]** at

**[00:34:00]** tool

**[00:34:00]** use

**[00:34:00]** and

**[00:34:01]** deep

**[00:34:03]** research

**[00:34:03]** as much

**[00:34:04]** but

**[00:34:05]** for

**[00:34:05]** answering

**[00:34:05]** empirical

**[00:34:06]** or

**[00:34:06]** factual

**[00:34:06]** questions

**[00:34:07]** I wish

**[00:34:08]** they were

**[00:34:08]** useful

**[00:34:09]** for

**[00:34:11]** writing

**[00:34:11]** but

**[00:34:12]** I

**[00:34:13]** usually

**[00:34:14]** end up

**[00:34:14]** dissatisfied

**[00:34:14]** with the

**[00:34:15]** writing

**[00:34:15]** that they

**[00:34:15]** produce

**[00:34:16]** so

**[00:34:17]** I don't

**[00:34:18]** reuse them

**[00:34:18]** very much

**[00:34:19]** for that

**[00:34:19]** and even

**[00:34:19]** for

**[00:34:20]** editing

**[00:34:21]** or

**[00:34:21]** grading

**[00:34:22]** my own

**[00:34:23]** writing

**[00:34:23]** I

**[00:34:24]** mean

**[00:34:24]** Have you

**[00:34:25]** seen any

**[00:34:25]** improvements

**[00:34:26]** as the

**[00:34:26]** models

**[00:34:26]** have

**[00:34:27]** progressed

**[00:34:27]** !

**[00:34:27]** I agree

**[00:34:28]** also

**[00:34:29]** it's

**[00:34:29]** surprisingly

**[00:34:29]** generic

**[00:34:32]** I'm

**[00:34:32]** trying to

**[00:34:32]** prompt it

**[00:34:33]** to not

**[00:34:33]** be generic

**[00:34:34]** inserting names

**[00:34:35]** of people

**[00:34:36]** and it

**[00:34:37]** just doesn't

**[00:34:38]** work

**[00:34:38]** so I've

**[00:34:39]** been

**[00:34:39]** disappointed

**[00:34:39]** at the

**[00:34:39]** times

**[00:34:40]** people

**[00:34:40]** tell me

**[00:34:41]** that the

**[00:34:41]** base

**[00:34:42]** models

**[00:34:42]** are better

**[00:34:43]** at this

**[00:34:43]** and it's

**[00:34:44]** the normification

**[00:34:46]** of RLHF

**[00:34:47]** that puts

**[00:34:48]** it in

**[00:34:48]** some kind

**[00:34:49]** of

**[00:34:50]** attractor

**[00:34:51]** basin

**[00:34:52]** I have

**[00:34:54]** not

**[00:34:54]** succeeded

**[00:34:54]** in using

**[00:34:55]** them

**[00:34:55]** effectively

**[00:34:56]** there

**[00:34:57]** people

**[00:34:58]** say

**[00:34:59]** that

**[00:35:00]** Plod

**[00:35:00]** is

**[00:35:01]** better

**[00:35:01]** and

**[00:35:01]** O3

**[00:35:01]** is

**[00:35:02]** better

**[00:35:02]** than

**[00:35:03]** earlier

**[00:35:03]** opening

**[00:35:03]** models

**[00:35:04]** and

**[00:35:04]** on a

**[00:35:04]** relative

**[00:35:04]** basis

**[00:35:05]** that might

**[00:35:05]** be true

**[00:35:05]** but

**[00:35:06]** I

**[00:35:06]** don't

**[00:35:07]** want to

**[00:35:07]** sound

**[00:35:11]** self-laudatory

**[00:35:12]** here

**[00:35:12]** and suggesting

**[00:35:13]** that I'm

**[00:35:13]** some particularly

**[00:35:14]** talented writer

**[00:35:15]** I don't think

**[00:35:15]** I am

**[00:35:16]** it's just

**[00:35:16]** like

**[00:35:16]** my personal

**[00:35:17]** style

**[00:35:17]** differs from

**[00:35:19]** the

**[00:35:19]** personal style

**[00:35:20]** so to speak

**[00:35:20]** of the

**[00:35:21]** models

**[00:35:21]** and

**[00:35:22]** in some

**[00:35:23]** self-centered

**[00:35:24]** way

**[00:35:24]** when I

**[00:35:25]** write

**[00:35:25]** I want

**[00:35:26]** to use

**[00:35:26]** my

**[00:35:26]** personal

**[00:35:26]** style

**[00:35:28]** so

**[00:35:29]** I use

**[00:35:29]** them

**[00:35:29]** for the

**[00:35:30]** factual

**[00:35:30]** stuff

**[00:35:31]** a lot

**[00:35:31]** and I

**[00:35:31]** find them

**[00:35:32]** terrific

**[00:35:32]** for that

**[00:35:33]** and

**[00:35:33]** even

**[00:35:34]** when I'm

**[00:35:34]** reading a

**[00:35:35]** book

**[00:35:35]** I'll

**[00:35:35]** sometimes

**[00:35:35]** activate

**[00:35:36]** I've been

**[00:35:37]** recently

**[00:35:37]** using

**[00:35:37]** Grok's

**[00:35:38]** voice mode

**[00:35:39]** and I'll

**[00:35:40]** just passively

**[00:35:41]** ask questions

**[00:35:42]** while I'm

**[00:35:42]** reading

**[00:35:42]** and

**[00:35:43]** Grok is

**[00:35:44]** just listening

**[00:35:44]** in the

**[00:35:45]** background

**[00:35:45]** and

**[00:35:45]** the answers

**[00:35:46]** are

**[00:35:46]** very helpful

**[00:35:49]** and then

**[00:35:49]** I

**[00:35:49]** obviously

**[00:35:50]** use

**[00:35:50]** LMs

**[00:35:50]** for

**[00:35:51]** writing

**[00:35:51]** code

**[00:35:52]** and

**[00:35:53]** typically

**[00:35:53]** mediated

**[00:35:54]** through

**[00:35:55]** Cursor

**[00:35:55]** so we

**[00:35:56]** are

**[00:35:56]** interviewing

**[00:35:56]** you

**[00:35:57]** Patrick

**[00:35:57]** Collison

**[00:35:58]** as

**[00:35:59]** kind of

**[00:36:00]** the

**[00:36:01]** most

**[00:36:01]** if you

**[00:36:02]** had to

**[00:36:02]** pick

**[00:36:03]** the

**[00:36:04]** archetype

**[00:36:04]** of a

**[00:36:04]** software

**[00:36:05]** industrialist

**[00:36:06]** I feel

**[00:36:06]** like you

**[00:36:06]** would be

**[00:36:07]** kind of

**[00:36:07]** straight out

**[00:36:07]** of central

**[00:36:08]** casting

**[00:36:09]** for a

**[00:36:10]** number

**[00:36:10]** of reasons

**[00:36:10]** one is

**[00:36:11]** that you

**[00:36:12]** are running

**[00:36:12]** a large

**[00:36:13]** software

**[00:36:13]** company

**[00:36:14]** a successful

**[00:36:15]** large

**[00:36:15]** software

**[00:36:15]** company

**[00:36:15]** two is

**[00:36:16]** you

**[00:36:16]** started

**[00:36:17]** as a

**[00:36:17]** programmer

**[00:36:17]** and then

**[00:36:18]** moved

**[00:36:19]** to running

**[00:36:19]** the company

**[00:36:19]** and then

**[00:36:20]** three is

**[00:36:21]** the company

**[00:36:21]** also

**[00:36:21]** builds

**[00:36:22]** things

**[00:36:22]** for

**[00:36:22]** developers

**[00:36:23]** and so

**[00:36:23]** it's

**[00:36:23]** kind of

**[00:36:23]** the

**[00:36:24]** intersection

**[00:36:24]** of

**[00:36:25]** many

**[00:36:26]** circles

**[00:36:26]** in the

**[00:36:26]** Venn diagram

**[00:36:27]** and so

**[00:36:28]** it's helpful

**[00:36:28]** to hear

**[00:36:29]** about

**[00:36:31]** discussing

**[00:36:31]** experiences

**[00:36:32]** with

**[00:36:32]** Stripe

**[00:36:33]** we're

**[00:36:33]** we're

**[00:36:34]** interviewing

**[00:36:34]** Patrick

**[00:36:34]** Collison

**[00:36:35]** the

**[00:36:35]** moonlighting

**[00:36:40]** economist

**[00:36:40]** and student

**[00:36:41]** of the

**[00:36:41]** world

**[00:36:41]** and so

**[00:36:42]** are

**[00:36:43]** progress

**[00:36:43]** studies

**[00:36:43]** doomed

**[00:36:43]** now that

**[00:36:44]** AI is

**[00:36:44]** here

**[00:36:45]** is there

**[00:36:45]** any need

**[00:36:46]** for them

**[00:36:47]** well

**[00:36:47]** I was

**[00:36:48]** going to

**[00:36:48]** say I

**[00:36:48]** think the

**[00:36:48]** need for

**[00:36:49]** progress

**[00:36:49]** studies

**[00:36:49]** has increased

**[00:36:49]** but again

**[00:36:50]** I don't

**[00:36:50]** mean to

**[00:36:51]** suggest

**[00:36:51]** that

**[00:36:52]** proper

**[00:36:52]** noun

**[00:36:52]** progress

**[00:36:53]** studies

**[00:36:53]** sees

**[00:36:54]** increased

**[00:36:55]** need

**[00:36:55]** but I

**[00:36:55]** think

**[00:36:55]** the

**[00:36:55]** kinds

**[00:36:56]** of

**[00:36:56]** questions

**[00:36:57]** that

**[00:36:57]** progress

**[00:36:58]** studies

**[00:36:58]** tries

**[00:36:59]** to

**[00:36:59]** answer

**[00:37:00]** are

**[00:37:01]** now

**[00:37:02]** more

**[00:37:02]** pressing

**[00:37:03]** and urgent

**[00:37:03]** because

**[00:37:04]** I think

**[00:37:05]** the degrees

**[00:37:05]** of freedom

**[00:37:06]** are increasing

**[00:37:07]** and

**[00:37:08]** I think

**[00:37:09]** there's

**[00:37:09]** some

**[00:37:11]** Pandasian

**[00:37:11]** view

**[00:37:11]** that AI

**[00:37:12]** will just

**[00:37:12]** magically

**[00:37:13]** solve

**[00:37:13]** all the

**[00:37:13]** problems

**[00:37:14]** and

**[00:37:14]** predictions

**[00:37:15]** of the

**[00:37:15]** future

**[00:37:16]** are hard

**[00:37:16]** but

**[00:37:16]** one

**[00:37:17]** I don't

**[00:37:18]** think

**[00:37:18]** that's

**[00:37:18]** true

**[00:37:18]** and two

**[00:37:19]** in as

**[00:37:20]** much

**[00:37:20]** as we

**[00:37:20]** have

**[00:37:20]** evidence

**[00:37:21]** to date

**[00:37:22]** I don't

**[00:37:22]** think

**[00:37:22]** that's

**[00:37:22]** been

**[00:37:22]** the

**[00:37:23]** track

**[00:37:23]** record

**[00:37:23]** so

**[00:37:23]** I

**[00:37:24]** think

**[00:37:24]** that

**[00:37:26]** how

**[00:37:27]** we

**[00:37:27]** use

**[00:37:27]** these

**[00:37:27]** things

**[00:37:28]** what

**[00:37:28]** kinds

**[00:37:29]** of

**[00:37:29]** decisions

**[00:37:29]** we

**[00:37:29]** make

**[00:37:30]** what

**[00:37:30]** kind

**[00:37:30]** of

**[00:37:32]** considerations

**[00:37:33]** and

**[00:37:36]** margins

**[00:37:36]** of

**[00:37:37]** human

**[00:37:38]** welfare

**[00:37:38]** we

**[00:37:38]** seek

**[00:37:38]** to

**[00:37:38]** further

**[00:37:39]** I

**[00:37:39]** think

**[00:37:39]** all

**[00:37:39]** those

**[00:37:40]** judgments

**[00:37:41]** are

**[00:37:41]** going

**[00:37:42]** to

**[00:37:42]** really

**[00:37:42]** matter

**[00:37:42]** and

**[00:37:43]** maybe

**[00:37:43]** a

**[00:37:43]** critique

**[00:37:43]** you

**[00:37:43]** could

**[00:37:44]** have

**[00:37:44]** leveled

**[00:37:44]** at

**[00:37:45]** progress

**[00:37:46]** studies

**[00:37:46]** or

**[00:37:46]** progress

**[00:37:47]** studies

**[00:37:47]** style

**[00:37:47]** thinking

**[00:37:48]** five

**[00:37:48]** years

**[00:37:48]** ago

**[00:37:49]** is

**[00:37:49]** these

**[00:37:50]** are

**[00:37:50]** all

**[00:37:50]** nice

**[00:37:50]** questions

**[00:37:51]** but

**[00:37:51]** the

**[00:37:51]** world

**[00:37:52]** is

**[00:37:52]** on

**[00:37:52]** a

**[00:37:52]** kind

**[00:37:52]** of

**[00:37:54]** foreordained

**[00:37:55]** escalator

**[00:37:56]** path

**[00:37:56]** to

**[00:37:57]** some

**[00:37:57]** kind

**[00:37:58]** of

**[00:37:58]** teleological

**[00:37:58]** outcome

**[00:37:59]** and

**[00:37:59]** I don't

**[00:38:00]** think

**[00:38:00]** the world

**[00:38:00]** feels

**[00:38:01]** that way

**[00:38:01]** today

**[00:38:02]** or

**[00:38:02]** certainly

**[00:38:02]** feels

**[00:38:02]** much

**[00:38:02]** less

**[00:38:03]** that way

**[00:38:03]** today

**[00:38:03]** than it

**[00:38:04]** did

**[00:38:04]** and so

**[00:38:05]** because of

**[00:38:05]** global affairs

**[00:38:06]** or something else

**[00:38:06]** no

**[00:38:07]** maybe

**[00:38:08]** maybe

**[00:38:08]** global affairs

**[00:38:09]** but

**[00:38:10]** the

**[00:38:11]** trifecta

**[00:38:11]** of

**[00:38:12]** global

**[00:38:14]** affairs

**[00:38:14]** writ large

**[00:38:15]** second

**[00:38:16]** I think

**[00:38:17]** that

**[00:38:18]** aspirations

**[00:38:19]** and ideals

**[00:38:20]** are

**[00:38:21]** becoming

**[00:38:21]** contested

**[00:38:23]** more

**[00:38:23]** actively

**[00:38:23]** and

**[00:38:24]** there's

**[00:38:25]** an

**[00:38:25]** ambiguity

**[00:38:25]** these

**[00:38:26]** days

**[00:38:26]** in

**[00:38:27]** the

**[00:38:27]** US

**[00:38:27]** as to

**[00:38:28]** what

**[00:38:28]** the

**[00:38:28]** left

**[00:38:29]** and

**[00:38:29]** the

**[00:38:29]** right

**[00:38:29]** even

**[00:38:29]** stand

**[00:38:30]** for

**[00:38:30]** and

**[00:38:30]** I guess

**[00:38:31]** we

**[00:38:31]** currently

**[00:38:32]** have

**[00:38:32]** one

**[00:38:32]** party

**[00:38:34]** endorsing

**[00:38:34]** tariffs

**[00:38:35]** and another

**[00:38:35]** party

**[00:38:35]** opposing

**[00:38:36]** them

**[00:38:36]** but

**[00:38:36]** with

**[00:38:36]** the

**[00:38:37]** valences

**[00:38:37]** kind of

**[00:38:37]** shift

**[00:38:38]** flipped

**[00:38:38]** from what

**[00:38:39]** one might

**[00:38:40]** have expected

**[00:38:41]** historically

**[00:38:42]** and

**[00:38:43]** third

**[00:38:43]** technology

**[00:38:45]** and

**[00:38:46]** first and

**[00:38:47]** foremost

**[00:38:48]** AI

**[00:38:48]** but

**[00:38:49]** in

**[00:38:50]** our

**[00:38:50]** industry

**[00:38:51]** stable

**[00:38:51]** coins

**[00:38:52]** the

**[00:38:53]** rise

**[00:38:53]** of

**[00:38:54]** China

**[00:38:55]** as

**[00:38:55]** the

**[00:38:56]** preeminent

**[00:38:57]** manufacturing

**[00:38:57]** power

**[00:38:58]** in many

**[00:38:58]** technologies

**[00:38:59]** of the

**[00:38:59]** future

**[00:38:59]** like

**[00:39:00]** drones

**[00:39:01]** and

**[00:39:01]** robots

**[00:39:02]** and

**[00:39:02]** batteries

**[00:39:02]** and

**[00:39:03]** solar

**[00:39:03]** etc

**[00:39:04]** so

**[00:39:05]** in

**[00:39:06]** many

**[00:39:07]** different

**[00:39:07]** ways

**[00:39:07]** I feel

**[00:39:07]** like

**[00:39:08]** the

**[00:39:08]** future

**[00:39:08]** is

**[00:39:10]** Peter

**[00:39:11]** Schwartz

**[00:39:12]** has this

**[00:39:13]** concept

**[00:39:13]** of

**[00:39:14]** the

**[00:39:14]** Schwartz

**[00:39:14]** window

**[00:39:15]** as

**[00:39:15]** the

**[00:39:17]** window

**[00:39:18]** of

**[00:39:20]** contemplatable

**[00:39:20]** futures

**[00:39:22]** in

**[00:39:23]** whatever

**[00:39:24]** number

**[00:39:24]** of

**[00:39:24]** years

**[00:39:24]** hence

**[00:39:25]** and

**[00:39:26]** I feel

**[00:39:27]** like

**[00:39:27]** that

**[00:39:27]** Schwartz

**[00:39:27]** window

**[00:39:29]** as

**[00:39:29]** of

**[00:39:30]** 2005

**[00:39:31]** as

**[00:39:31]** we

**[00:39:31]** contemplate

**[00:39:32]** the

**[00:39:32]** world

**[00:39:32]** of

**[00:39:32]** 2015

**[00:39:33]** was

**[00:39:33]** fairly

**[00:39:34]** narrow

**[00:39:34]** and

**[00:39:34]** was

**[00:39:34]** correctly

**[00:39:35]** fairly

**[00:39:35]** narrow

**[00:39:36]** I think

**[00:39:36]** the

**[00:39:36]** world

**[00:39:36]** of

**[00:39:36]** 2015

**[00:39:37]** did

**[00:39:37]** in

**[00:39:37]** fact

**[00:39:37]** unfold

**[00:39:38]** largely

**[00:39:38]** the way

**[00:39:38]** we

**[00:39:39]** would

**[00:39:39]** have

**[00:39:39]** expected

**[00:39:39]** in

**[00:39:40]** 2005

**[00:39:40]** and

**[00:39:41]** I

**[00:39:41]** feel

**[00:39:41]** like

**[00:39:41]** today

**[00:39:41]** in

**[00:39:41]** 2025

**[00:39:43]** that

**[00:39:43]** window

**[00:39:44]** for

**[00:39:44]** 2035

**[00:39:45]** it

**[00:39:45]** feels

**[00:39:45]** extremely

**[00:39:46]** broad

**[00:39:46]** so

**[00:39:48]** I think

**[00:39:49]** the progress

**[00:39:49]** study

**[00:39:50]** questions

**[00:39:50]** are

**[00:39:51]** more

**[00:39:52]** pressing

**[00:39:54]** so

**[00:39:54]** you

**[00:39:54]** are

**[00:39:55]** on

**[00:39:55]** the

**[00:39:55]** record

**[00:39:57]** saying

**[00:39:59]** people

**[00:39:59]** should

**[00:39:59]** focus

**[00:39:59]** more

**[00:40:00]** on

**[00:40:00]** the

**[00:40:00]** question

**[00:40:00]** of

**[00:40:00]** why

**[00:40:01]** we

**[00:40:01]** don't

**[00:40:01]** see

**[00:40:01]** improvements

**[00:40:02]** in

**[00:40:02]** productivity

**[00:40:02]** numbers

**[00:40:03]** as

**[00:40:04]** information

**[00:40:04]** technology

**[00:40:04]** increases

**[00:40:05]** and

**[00:40:06]** also

**[00:40:06]** as

**[00:40:06]** more

**[00:40:07]** people

**[00:40:07]** have

**[00:40:07]** started

**[00:40:07]** working

**[00:40:08]** on

**[00:40:08]** science

**[00:40:08]** and

**[00:40:08]** technology

**[00:40:08]** and

**[00:40:09]** more

**[00:40:09]** money

**[00:40:09]** has

**[00:40:10]** gone

**[00:40:10]** into

**[00:40:10]** it

**[00:40:11]** and

**[00:40:11]** what

**[00:40:12]** do

**[00:40:12]** the

**[00:40:12]** numbers

**[00:40:12]** look

**[00:40:12]** like

**[00:40:12]** now

**[00:40:13]** do

**[00:40:13]** we

**[00:40:13]** see

**[00:40:13]** AI

**[00:40:14]** in

**[00:40:14]** the

**[00:40:14]** numbers

**[00:40:14]** there

**[00:40:15]** was

**[00:40:15]** a

**[00:40:15]** new

**[00:40:15]** paper

**[00:40:16]** published

**[00:40:17]** in

**[00:40:17]** this

**[00:40:17]** very

**[00:40:18]** recently

**[00:40:18]** that

**[00:40:21]** I've

**[00:40:21]** not

**[00:40:21]** had a

**[00:40:22]** chance

**[00:40:22]** to

**[00:40:22]** read

**[00:40:23]** so

**[00:40:24]** I've

**[00:40:25]** at this

**[00:40:25]** moment

**[00:40:25]** only

**[00:40:25]** read

**[00:40:26]** the

**[00:40:26]** abstract

**[00:40:26]** its

**[00:40:27]** claim

**[00:40:28]** is

**[00:40:29]** that

**[00:40:29]** one

**[00:40:30]** does

**[00:40:30]** not

**[00:40:31]** in

**[00:40:31]** fact

**[00:40:31]** observe

**[00:40:32]** productivity

**[00:40:33]** improvements

**[00:40:34]** stemming

**[00:40:34]** from

**[00:40:36]** use

**[00:40:37]** of

**[00:40:37]** language

**[00:40:37]** models

**[00:40:38]** they

**[00:40:41]** appear

**[00:40:42]** to be

**[00:40:42]** undertaking

**[00:40:43]** some

**[00:40:44]** kind

**[00:40:44]** of

**[00:40:44]** natural

**[00:40:44]** experiment

**[00:40:45]** looking

**[00:40:46]** at

**[00:40:46]** the

**[00:40:46]** individual

**[00:40:46]** level

**[00:40:47]** based

**[00:40:48]** on

**[00:40:50]** intensity

**[00:40:51]** of

**[00:40:51]** LLM

**[00:40:51]** usage

**[00:40:51]** but

**[00:40:52]** I

**[00:40:52]** certainly

**[00:40:52]** cannot

**[00:40:53]** endorse

**[00:40:53]** their

**[00:40:53]** methodological

**[00:40:54]** rigor

**[00:40:54]** and

**[00:40:54]** upon

**[00:40:55]** understanding

**[00:40:55]** it

**[00:40:55]** better

**[00:40:55]** I might

**[00:40:56]** be

**[00:40:56]** either

**[00:40:57]** really

**[00:40:58]** impressed

**[00:40:58]** and

**[00:40:58]** find it

**[00:40:59]** very

**[00:40:59]** credible

**[00:40:59]** or

**[00:40:59]** horrified

**[00:41:00]** I don't

**[00:41:00]** know

**[00:41:00]** but

**[00:41:01]** that

**[00:41:01]** was

**[00:41:01]** the

**[00:41:01]** finding

**[00:41:01]** I

**[00:41:01]** happened

**[00:41:01]** to

**[00:41:02]** stumble

**[00:41:02]** upon

**[00:41:02]** today

**[00:41:03]** overall

**[00:41:03]** GDP

**[00:41:04]** growth

**[00:41:05]** in

**[00:41:06]** the

**[00:41:06]** US

**[00:41:06]** looks

**[00:41:07]** well

**[00:41:08]** over

**[00:41:08]** the

**[00:41:08]** last

**[00:41:08]** two

**[00:41:09]** years

**[00:41:09]** it's

**[00:41:09]** been

**[00:41:10]** somewhat

**[00:41:10]** better

**[00:41:10]** than

**[00:41:11]** we

**[00:41:11]** expected

**[00:41:15]** we

**[00:41:16]** certainly

**[00:41:17]** don't

**[00:41:17]** see

**[00:41:17]** any

**[00:41:18]** evidence

**[00:41:18]** for

**[00:41:19]** exponential

**[00:41:20]** takeoff

**[00:41:21]** and

**[00:41:22]** if

**[00:41:22]** we

**[00:41:24]** in

**[00:41:24]** as

**[00:41:24]** much

**[00:41:24]** as

**[00:41:25]** we

**[00:41:25]** thought

**[00:41:25]** that

**[00:41:25]** the

**[00:41:25]** encouraging

**[00:41:27]** GDP

**[00:41:27]** figures

**[00:41:28]** we

**[00:41:28]** have

**[00:41:28]** seen

**[00:41:28]** in the

**[00:41:28]** US

**[00:41:28]** for

**[00:41:28]** the

**[00:41:28]** last

**[00:41:29]** two

**[00:41:29]** years

**[00:41:29]** are

**[00:41:29]** attributable

**[00:41:30]** to

**[00:41:30]** some

**[00:41:30]** of

**[00:41:30]** these

**[00:41:30]** new

**[00:41:30]** technologies

**[00:41:31]** I

**[00:41:31]** think

**[00:41:32]** you

**[00:41:32]** would

**[00:41:32]** also

**[00:41:32]** expect

**[00:41:32]** to

**[00:41:33]** see

**[00:41:33]** them

**[00:41:33]** in

**[00:41:33]** other

**[00:41:33]** countries

**[00:41:33]** because

**[00:41:34]** these

**[00:41:34]** technologies

**[00:41:34]** are

**[00:41:35]** quasi

**[00:41:35]** public

**[00:41:36]** good

**[00:41:36]** anybody

**[00:41:36]** can

**[00:41:37]** use

**[00:41:38]** these

**[00:41:38]** LLMs

**[00:41:38]** GDP

**[00:41:39]** growth

**[00:41:40]** outside

**[00:41:40]** of

**[00:41:40]** the

**[00:41:40]** US

**[00:41:41]** has

**[00:41:44]** accelerated

**[00:41:45]** period

**[00:41:45]** of

**[00:41:45]** economic

**[00:41:45]** growth

**[00:41:46]** for

**[00:41:46]** the

**[00:41:46]** world

**[00:41:46]** writ

**[00:41:47]** large

**[00:41:47]** and

**[00:41:48]** so

**[00:41:49]** obviously

**[00:41:50]** it's

**[00:41:50]** early

**[00:41:50]** days

**[00:41:51]** but

**[00:41:52]** I

**[00:41:53]** think

**[00:41:55]** we're

**[00:41:55]** seeing

**[00:41:55]** that

**[00:41:56]** the

**[00:41:56]** diffusion

**[00:41:56]** of

**[00:41:56]** these

**[00:41:56]** technologies

**[00:41:57]** through

**[00:41:57]** the

**[00:41:57]** economy

**[00:41:57]** really

**[00:41:58]** takes

**[00:41:58]** time

**[00:41:59]** and

**[00:42:00]** involves

**[00:42:00]** substantial

**[00:42:01]** complexity

**[00:42:01]** and

**[00:42:02]** maybe

**[00:42:02]** just

**[00:42:02]** last

**[00:42:02]** point

**[00:42:02]** of

**[00:42:02]** that

**[00:42:03]** is

**[00:42:03]** I

**[00:42:04]** believe

**[00:42:04]** Jack

**[00:42:04]** Clark

**[00:42:04]** said

**[00:42:05]** in

**[00:42:05]** an

**[00:42:05]** interview

**[00:42:05]** with

**[00:42:05]** Tyler

**[00:42:05]** Cohen

**[00:42:06]** one

**[00:42:06]** of

**[00:42:06]** the

**[00:42:07]** co-founders

**[00:42:07]** of

**[00:42:07]** Anthropic

**[00:42:07]** !

**[00:42:14]** the

**[00:42:15]** concept

**[00:42:15]** of

**[00:42:15]** AGI

**[00:42:16]** and

**[00:42:16]** even

**[00:42:16]** ASI

**[00:42:17]** I

**[00:42:17]** feel

**[00:42:17]** extremely

**[00:42:17]** seriously

**[00:42:18]** and

**[00:42:18]** Dario

**[00:42:19]** speaks

**[00:42:19]** with

**[00:42:19]** this

**[00:42:19]** publicly

**[00:42:21]** he's

**[00:42:21]** written

**[00:42:21]** about

**[00:42:22]** it

**[00:42:22]** and

**[00:42:22]** again

**[00:42:23]** Jack

**[00:42:23]** Clark

**[00:42:23]** one of

**[00:42:23]** the

**[00:42:23]** co-founders

**[00:42:24]** and

**[00:42:24]** he

**[00:42:24]** said

**[00:42:25]** that

**[00:42:25]** he

**[00:42:25]** expects

**[00:42:25]** AI

**[00:42:26]** to

**[00:42:27]** increase

**[00:42:27]** GDP

**[00:42:28]** growth

**[00:42:28]** by

**[00:42:28]** half

**[00:42:29]** percent

**[00:42:29]** a

**[00:42:29]** year

**[00:42:30]** and

**[00:42:30]** I

**[00:42:33]** interpret

**[00:42:33]** Jack

**[00:42:34]** as

**[00:42:34]** really

**[00:42:34]** an

**[00:42:34]** optimist

**[00:42:35]** and

**[00:42:35]** half

**[00:42:36]** a

**[00:42:36]** point

**[00:42:36]** a

**[00:42:36]** year

**[00:42:36]** is

**[00:42:36]** in

**[00:42:36]** fact

**[00:42:37]** a

**[00:42:37]** lot

**[00:42:37]** of

**[00:42:37]** incremental

**[00:42:44]** figure

**[00:42:44]** Do you

**[00:42:46]** think

**[00:42:46]** that

**[00:42:46]** with

**[00:42:47]** the

**[00:42:47]** form

**[00:42:48]** factor

**[00:42:48]** that

**[00:42:49]** AI

**[00:42:49]** is

**[00:42:49]** taking

**[00:42:50]** in

**[00:42:50]** the

**[00:42:50]** economy

**[00:42:51]** right

**[00:42:51]** now

**[00:42:52]** if

**[00:42:52]** we

**[00:42:52]** just

**[00:42:52]** kind

**[00:42:52]** of

**[00:42:53]** stretch

**[00:42:54]** the

**[00:42:54]** line

**[00:42:54]** forward

**[00:42:54]** do you

**[00:42:55]** think

**[00:42:55]** we're

**[00:42:55]** going

**[00:42:55]** to

**[00:42:55]** need

**[00:42:56]** new

**[00:42:56]** measures

**[00:42:56]** in

**[00:42:57]** economic

**[00:42:57]** productivity

**[00:42:57]** than we

**[00:42:58]** have

**[00:42:59]** right

**[00:42:59]** now

**[00:42:59]** assume

**[00:43:00]** real

**[00:43:00]** productivity

**[00:43:00]** goes up

**[00:43:01]** assume

**[00:43:01]** AI

**[00:43:01]** keeps

**[00:43:02]** getting

**[00:43:02]** better

**[00:43:02]** it

**[00:43:02]** gets

**[00:43:03]** deployed

**[00:43:03]** in

**[00:43:03]** the

**[00:43:03]** way

**[00:43:03]** you

**[00:43:03]** would

**[00:43:04]** expect

**[00:43:04]** do you

**[00:43:04]** think

**[00:43:04]** we'll

**[00:43:04]** need

**[00:43:05]** new

**[00:43:05]** measures

**[00:43:05]** !

**[00:43:14]** Any

**[00:43:14]** world

**[00:43:15]** where

**[00:43:15]** what

**[00:43:16]** we

**[00:43:18]** generally

**[00:43:18]** think of

**[00:43:19]** as

**[00:43:20]** the

**[00:43:21]** economy

**[00:43:21]** is

**[00:43:22]** massively

**[00:43:22]** enhanced

**[00:43:22]** it'll

**[00:43:23]** show up

**[00:43:23]** in

**[00:43:23]** GDP

**[00:43:23]** I believe

**[00:43:24]** When

**[00:43:24]** will

**[00:43:25]** we

**[00:43:25]** be

**[00:43:25]** able

**[00:43:25]** to

**[00:43:26]** program

**[00:43:26]** human

**[00:43:26]** biology?

**[00:43:27]** I'm

**[00:43:27]** very

**[00:43:27]** excited

**[00:43:27]** about

**[00:43:28]** this

**[00:43:28]** At

**[00:43:28]** ARC

**[00:43:29]** which

**[00:43:29]** is

**[00:43:29]** this

**[00:43:29]** biomedical

**[00:43:30]** research

**[00:43:31]** organization

**[00:43:31]** which

**[00:43:31]** I

**[00:43:32]** was

**[00:43:32]** involved

**[00:43:33]** in

**[00:43:33]** founding

**[00:43:35]** we're

**[00:43:35]** working

**[00:43:36]** on

**[00:43:36]** training

**[00:43:36]** foundation

**[00:43:37]** models

**[00:43:37]** for

**[00:43:38]** biology

**[00:43:39]** using

**[00:43:39]** DNA

**[00:43:40]** and

**[00:43:40]** things

**[00:43:41]** like

**[00:43:41]** that

**[00:43:41]** we're

**[00:43:42]** working

**[00:43:42]** on a

**[00:43:42]** !

**[00:43:42]** virtual

**[00:43:43]** cell

**[00:43:43]** and

**[00:43:45]** generally

**[00:43:45]** we're

**[00:43:46]** trying

**[00:43:46]** I mean

**[00:43:46]** the thing

**[00:43:47]** that I

**[00:43:48]** didn't

**[00:43:49]** appreciate

**[00:43:49]** until

**[00:43:49]** really

**[00:43:50]** spending

**[00:43:50]** more

**[00:43:50]** time

**[00:43:50]** in

**[00:43:50]** biology

**[00:43:50]** is

**[00:43:51]** we

**[00:43:51]** have

**[00:43:51]** never

**[00:43:51]** cured

**[00:43:53]** a

**[00:43:53]** complex

**[00:43:54]** disease

**[00:43:54]** so

**[00:43:55]** one

**[00:43:56]** ontology

**[00:43:57]** or

**[00:43:58]** of

**[00:43:58]** diseases

**[00:43:59]** would be

**[00:44:00]** infectious

**[00:44:00]** diseases

**[00:44:01]** the flu

**[00:44:01]** the cold

**[00:44:02]** COVID

**[00:44:02]** whatever

**[00:44:04]** and

**[00:44:05]** tuberculosis

**[00:44:05]** and

**[00:44:07]** diseases

**[00:44:08]** with

**[00:44:08]** high

**[00:44:09]** mortality

**[00:44:09]** rates

**[00:44:09]** then

**[00:44:10]** you

**[00:44:11]** have

**[00:44:11]** monogenic

**[00:44:12]** diseases

**[00:44:12]** where

**[00:44:13]** there's

**[00:44:13]** one

**[00:44:14]** genetic

**[00:44:14]** mutation

**[00:44:14]** that

**[00:44:15]** is

**[00:44:15]** responsible

**[00:44:16]** for

**[00:44:16]** the

**[00:44:16]** disease

**[00:44:16]** like

**[00:44:16]** Huntington's

**[00:44:17]** and

**[00:44:18]** then

**[00:44:18]** you

**[00:44:18]** have

**[00:44:18]** complex

**[00:44:18]** diseases

**[00:44:20]** and

**[00:44:21]** the

**[00:44:21]** complex

**[00:44:21]** diseases

**[00:44:22]** are

**[00:44:22]** the

**[00:44:22]** residual

**[00:44:23]** that

**[00:44:23]** are

**[00:44:24]** now

**[00:44:24]** left

**[00:44:24]** after

**[00:44:25]** we

**[00:44:25]** have

**[00:44:25]** cured

**[00:44:25]** most

**[00:44:26]** of the

**[00:44:26]** problematic

**[00:44:26]** infectious

**[00:44:27]** diseases

**[00:44:27]** at least

**[00:44:27]** in the

**[00:44:28]** western

**[00:44:28]** world

**[00:44:29]** most

**[00:44:30]** cardiovascular

**[00:44:30]** disease

**[00:44:31]** most cancers

**[00:44:31]** most autoimmune

**[00:44:32]** disease

**[00:44:33]** most neurodegenerative

**[00:44:34]** disease

**[00:44:34]** etc

**[00:44:34]** for certain

**[00:44:36]** of these

**[00:44:36]** conditions

**[00:44:36]** we have

**[00:44:37]** maybe

**[00:44:37]** treatments

**[00:44:37]** that help

**[00:44:37]** like

**[00:44:38]** statins

**[00:44:38]** with

**[00:44:39]** cardiovascular

**[00:44:39]** disease

**[00:44:40]** !

**[00:44:40]** but

**[00:44:40]** for

**[00:44:40]** none

**[00:44:41]** of them

**[00:44:41]** can

**[00:44:41]** we

**[00:44:41]** really

**[00:44:41]** say

**[00:44:41]** that we've

**[00:44:41]** cured it

**[00:44:42]** that we

**[00:44:42]** understand

**[00:44:43]** the causal

**[00:44:43]** pathways

**[00:44:44]** and meaningful

**[00:44:45]** detail

**[00:44:45]** and that

**[00:44:46]** we can

**[00:44:47]** vaccinate

**[00:44:48]** against it

**[00:44:48]** or something

**[00:44:49]** and I

**[00:44:51]** think

**[00:44:51]** this is

**[00:44:53]** our

**[00:44:53]** hypothesis

**[00:44:54]** could be

**[00:44:54]** wrong

**[00:44:54]** is that

**[00:44:55]** this is

**[00:44:55]** in part

**[00:44:56]** because

**[00:44:56]** we don't

**[00:44:57]** have

**[00:44:59]** experimental

**[00:45:00]** and

**[00:45:01]** kind of

**[00:45:03]** maybe

**[00:45:03]** epistemic

**[00:45:04]** is too

**[00:45:04]** grandiose

**[00:45:04]** a word

**[00:45:05]** but kind

**[00:45:05]** of epistemic

**[00:45:05]** technology

**[00:45:06]** that's up

**[00:45:06]** to the

**[00:45:07]** task

**[00:45:07]** like

**[00:45:07]** the

**[00:45:09]** the

**[00:45:10]** pleiotropy

**[00:45:11]** of the

**[00:45:11]** genes

**[00:45:12]** in terms

**[00:45:12]** of all

**[00:45:12]** the different

**[00:45:12]** parts of

**[00:45:13]** the body

**[00:45:13]** and the

**[00:45:13]** systems

**[00:45:14]** and the

**[00:45:15]** mechanisms

**[00:45:15]** inside the

**[00:45:16]** cell

**[00:45:16]** that they

**[00:45:16]** affect

**[00:45:17]** there's so

**[00:45:18]** much

**[00:45:18]** combinatoric

**[00:45:19]** complexity

**[00:45:20]** there

**[00:45:20]** and then

**[00:45:21]** the

**[00:45:21]** environment

**[00:45:22]** is such

**[00:45:22]** a vast

**[00:45:23]** and

**[00:45:23]** difficult

**[00:45:24]** to quantify

**[00:45:25]** thing

**[00:45:25]** that it's

**[00:45:26]** really hard

**[00:45:27]** to understand

**[00:45:27]** for any

**[00:45:28]** of these

**[00:45:28]** conditions

**[00:45:29]** the etiology

**[00:45:30]** and the

**[00:45:30]** dynamics

**[00:45:31]** and so

**[00:45:31]** forth

**[00:45:32]** then over

**[00:45:34]** the last

**[00:45:34]** 10-ish

**[00:45:35]** years

**[00:45:35]** a bit

**[00:45:36]** longer

**[00:45:36]** but a

**[00:45:37]** lot of

**[00:45:37]** the development

**[00:45:38]** has happened

**[00:45:38]** the last

**[00:45:38]** 10 years

**[00:45:39]** we've

**[00:45:39]** gotten

**[00:45:42]** three new

**[00:45:43]** classes of

**[00:45:43]** technology

**[00:45:44]** and biology

**[00:45:45]** for

**[00:45:46]** reading

**[00:45:47]** we've

**[00:45:48]** gotten

**[00:45:48]** much

**[00:45:49]** better

**[00:45:49]** sequencing

**[00:45:49]** technology

**[00:45:50]** single

**[00:45:51]** cell

**[00:45:51]** sequencing

**[00:45:52]** the ability

**[00:45:53]** to sequence

**[00:45:54]** single cell

**[00:45:55]** sequencing

**[00:45:55]** of RNA

**[00:45:57]** and those

**[00:45:59]** improvements

**[00:45:59]** at the

**[00:46:00]** think

**[00:46:01]** level

**[00:46:03]** we've

**[00:46:03]** gotten

**[00:46:04]** neural

**[00:46:04]** networks

**[00:46:04]** and deep

**[00:46:05]** learning

**[00:46:05]** and

**[00:46:06]** transformers

**[00:46:07]** and everything

**[00:46:07]** there

**[00:46:08]** they've existed

**[00:46:09]** for a long

**[00:46:09]** time but we've

**[00:46:10]** gotten the

**[00:46:10]** recent improvements

**[00:46:11]** in them

**[00:46:12]** and the

**[00:46:13]** transformer

**[00:46:13]** in particular

**[00:46:13]** and then

**[00:46:15]** on the

**[00:46:15]** right side

**[00:46:15]** we've seen

**[00:46:16]** obviously

**[00:46:17]** huge improvements

**[00:46:17]** in functional

**[00:46:18]** genomics

**[00:46:19]** and CRISPR

**[00:46:19]** and bridge

**[00:46:21]** editing

**[00:46:21]** which is a

**[00:46:22]** technology

**[00:46:23]** that kind

**[00:46:23]** of hark

**[00:46:23]** but the

**[00:46:24]** ability to

**[00:46:25]** kind of make

**[00:46:25]** very specific

**[00:46:26]** directed

**[00:46:27]** perturbations

**[00:46:28]** in cells

**[00:46:28]** but if you put

**[00:46:29]** those together

**[00:46:29]** you now have

**[00:46:30]** the ability

**[00:46:30]** to again

**[00:46:31]** at the

**[00:46:31]** level of

**[00:46:32]** the individual

**[00:46:32]** cell

**[00:46:33]** to read

**[00:46:34]** think

**[00:46:35]** and to

**[00:46:35]** write

**[00:46:35]** and this

**[00:46:36]** starts to

**[00:46:37]** really feel

**[00:46:37]** like a new

**[00:46:38]** kind of

**[00:46:39]** Turing

**[00:46:39]** loop

**[00:46:40]** and to have

**[00:46:40]** its own

**[00:46:41]** sort of

**[00:46:41]** completeness

**[00:46:42]** and we

**[00:46:44]** will see

**[00:46:45]** how much

**[00:46:45]** this can

**[00:46:46]** do

**[00:46:46]** against

**[00:46:47]** these

**[00:46:48]** complex

**[00:46:48]** diseases

**[00:46:49]** and whether

**[00:46:49]** this

**[00:46:50]** systematic

**[00:46:51]** approach

**[00:46:52]** is up

**[00:46:53]** to the

**[00:46:54]** task

**[00:46:55]** of

**[00:46:55]** shedding

**[00:46:56]** new

**[00:46:57]** light

**[00:46:57]** on their

**[00:46:57]** dynamics

**[00:46:58]** but we

**[00:46:58]** are hopeful

**[00:46:59]** and excited

**[00:47:01]** if we

**[00:47:02]** here at

**[00:47:03]** Kirscher

**[00:47:04]** and also

**[00:47:04]** others in

**[00:47:05]** the industry

**[00:47:05]** are successful

**[00:47:06]** in automating

**[00:47:07]** lots of

**[00:47:07]** programming

**[00:47:08]** as we

**[00:47:08]** know it

**[00:47:08]** today

**[00:47:08]** and replacing

**[00:47:10]** it with

**[00:47:11]** a form

**[00:47:11]** of software

**[00:47:12]** building

**[00:47:12]** that's

**[00:47:12]** much higher

**[00:47:13]** level

**[00:47:13]** and more

**[00:47:13]** productive

**[00:47:14]** and it's

**[00:47:15]** much more

**[00:47:16]** just focused

**[00:47:16]** on defining

**[00:47:16]** what you

**[00:47:17]** would like

**[00:47:17]** the software

**[00:47:18]** to look

**[00:47:18]** like

**[00:47:19]** if we

**[00:47:20]** succeed

**[00:47:20]** in that

**[00:47:23]** who are

**[00:47:24]** you long

**[00:47:24]** people talk

**[00:47:25]** about the

**[00:47:25]** designers

**[00:47:26]** and how

**[00:47:27]** this will

**[00:47:27]** be like

**[00:47:27]** a renaissance

**[00:47:28]** for them

**[00:47:28]** but are you

**[00:47:30]** long the

**[00:47:30]** grad students

**[00:47:31]** I mean

**[00:47:32]** there are

**[00:47:32]** lots of

**[00:47:32]** really amazing

**[00:47:33]** grad students

**[00:47:33]** who are

**[00:47:35]** awesome

**[00:47:35]** and then

**[00:47:36]** maybe are

**[00:47:37]** less skilled

**[00:47:37]** at making

**[00:47:38]** things happen

**[00:47:38]** on computers

**[00:47:39]** but who do

**[00:47:40]** you think

**[00:47:40]** is the most

**[00:47:41]** unexpected

**[00:47:41]** beneficiary

**[00:47:42]** of a world

**[00:47:42]** where both

**[00:47:43]** many more

**[00:47:44]** people can

**[00:47:44]** make things

**[00:47:45]** on computers

**[00:47:45]** and then

**[00:47:46]** also

**[00:47:46]** especially if

**[00:47:47]** it's an

**[00:47:47]** evolution

**[00:47:47]** away from

**[00:47:48]** programming

**[00:47:49]** the people

**[00:47:50]** who are

**[00:47:50]** already making

**[00:47:50]** things on

**[00:47:50]** computers

**[00:47:51]** are much

**[00:47:51]** more productive

**[00:47:52]** I don't

**[00:47:53]** have a high

**[00:47:53]** confidence

**[00:47:54]** answer to that

**[00:47:54]** there's all

**[00:47:55]** sorts of

**[00:47:56]** trite

**[00:47:56]** stock

**[00:47:57]** answers

**[00:47:57]** like

**[00:47:58]** real assets

**[00:47:59]** especially

**[00:48:00]** constrained

**[00:48:01]** real assets

**[00:48:01]** maybe we

**[00:48:02]** should be

**[00:48:03]** long

**[00:48:03]** SF real

**[00:48:04]** estate

**[00:48:04]** or something

**[00:48:05]** because

**[00:48:07]** it is

**[00:48:08]** one of the

**[00:48:09]** most beautiful

**[00:48:09]** cities in the

**[00:48:10]** world

**[00:48:10]** and will be

**[00:48:11]** enduringly so

**[00:48:12]** maybe we should

**[00:48:13]** be long

**[00:48:13]** the inputs

**[00:48:14]** and the

**[00:48:14]** ingredients

**[00:48:15]** to these

**[00:48:15]** systems

**[00:48:16]** because

**[00:48:16]** demand

**[00:48:17]** for them

**[00:48:18]** will go

**[00:48:19]** parabolic

**[00:48:19]** and so

**[00:48:20]** maybe we

**[00:48:20]** should be

**[00:48:20]** long

**[00:48:21]** copper

**[00:48:22]** maybe we

**[00:48:22]** should be

**[00:48:23]** long

**[00:48:25]** positional

**[00:48:25]** goods

**[00:48:26]** and

**[00:48:26]** celebrities

**[00:48:27]** and

**[00:48:28]** Taylor

**[00:48:28]** Swift's

**[00:48:29]** music

**[00:48:29]** catalogue

**[00:48:30]** there's

**[00:48:30]** a lot

**[00:48:31]** of

**[00:48:31]** compelling

**[00:48:31]** theories

**[00:48:32]** here

**[00:48:32]** but

**[00:48:32]** part

**[00:48:32]** of

**[00:48:32]** what

**[00:48:33]** I

**[00:48:33]** think

**[00:48:33]** is

**[00:48:33]** interesting

**[00:48:33]** at this

**[00:48:33]** economic

**[00:48:34]** moment

**[00:48:35]** is

**[00:48:35]** the

**[00:48:36]** unpredictability

**[00:48:36]** and the

**[00:48:37]** contingency

**[00:48:38]** and sensitivity

**[00:48:39]** to the

**[00:48:39]** precise

**[00:48:40]** assumptions

**[00:48:41]** in the

**[00:48:41]** technology

**[00:48:42]** trajectory

**[00:48:42]** itself

**[00:48:43]** and the

**[00:48:44]** shape

**[00:48:45]** that it

**[00:48:45]** takes

**[00:48:45]** in 5

**[00:48:46]** or 10

**[00:48:46]** years

**[00:48:46]** is going

**[00:48:47]** to do

**[00:48:47]** a lot

**[00:48:48]** to determine

**[00:48:48]** the answer

**[00:48:48]** to that

**[00:48:49]** and

**[00:48:49]** as I

**[00:48:50]** look

**[00:48:50]** backwards

**[00:48:50]** the last

**[00:48:51]** couple

**[00:48:51]** of years

**[00:48:52]** I'm struck

**[00:48:53]** by how many

**[00:48:53]** predictions

**[00:48:54]** have held up

**[00:48:55]** reasonably poorly

**[00:48:57]** even for people

**[00:48:58]** who are

**[00:48:58]** on the face

**[00:48:58]** of it

**[00:48:59]** extremely well

**[00:49:00]** informed

**[00:49:01]** and so

**[00:49:03]** I've asked

**[00:49:04]** a lot of

**[00:49:04]** people

**[00:49:04]** this question

**[00:49:05]** and I

**[00:49:07]** have not

**[00:49:07]** heard any

**[00:49:07]** answers

**[00:49:08]** that are

**[00:49:08]** so compelling

**[00:49:09]** that I

**[00:49:10]** feel like

**[00:49:10]** I have

**[00:49:10]** conviction

**[00:49:11]** so we

**[00:49:12]** are very

**[00:49:13]** happy to be

**[00:49:13]** serving Stripe

**[00:49:14]** and your guys

**[00:49:15]** mission

**[00:49:16]** what would you

**[00:49:17]** like us to

**[00:49:17]** build

**[00:49:17]** how can we

**[00:49:18]** make

**[00:49:18]** Chriser

**[00:49:18]** better for

**[00:49:19]** you

**[00:49:19]** either you

**[00:49:20]** Patrick

**[00:49:20]** Collison

**[00:49:20]** or you

**[00:49:21]** Stripe

**[00:49:21]** better

**[00:49:23]** so keep

**[00:49:25]** doing what

**[00:49:25]** you're doing

**[00:49:26]** would not

**[00:49:27]** be a bad

**[00:49:27]** outcome

**[00:49:28]** from our

**[00:49:28]** vantage point

**[00:49:29]** Cursor

**[00:49:30]** has

**[00:49:31]** today

**[00:49:32]** hundreds

**[00:49:33]** and soon

**[00:49:34]** thousands

**[00:49:35]** of extremely

**[00:49:36]** enthusiastic

**[00:49:37]** Stripe employees

**[00:49:38]** who are

**[00:49:38]** daily users

**[00:49:39]** of Cursor

**[00:49:41]** and they

**[00:49:42]** report that

**[00:49:43]** it's a

**[00:49:43]** very significant

**[00:49:44]** productivity

**[00:49:45]** enhancement

**[00:49:46]** and so

**[00:49:48]** wait for the

**[00:49:49]** economic numbers

**[00:49:50]** well

**[00:49:51]** the economy

**[00:49:52]** is pretty

**[00:49:52]** big

**[00:49:53]** and these

**[00:49:54]** diffusions

**[00:49:54]** take time

**[00:49:55]** so

**[00:49:56]** it seems

**[00:49:57]** greedy

**[00:49:58]** to want

**[00:49:59]** more

**[00:49:59]** if you're

**[00:49:59]** already

**[00:50:00]** making

**[00:50:00]** Stripe

**[00:50:01]** spends more

**[00:50:02]** on R&D

**[00:50:03]** and software

**[00:50:03]** creation

**[00:50:04]** than we

**[00:50:04]** spend on

**[00:50:05]** any single

**[00:50:05]** undertaking

**[00:50:06]** and so

**[00:50:06]** if you're

**[00:50:07]** making that

**[00:50:08]** process

**[00:50:08]** more efficient

**[00:50:09]** and more

**[00:50:10]** productive

**[00:50:10]** then maybe

**[00:50:11]** it seems

**[00:50:11]** greedy

**[00:50:12]** to want

**[00:50:12]** anything

**[00:50:12]** more

**[00:50:12]** if I'm

**[00:50:14]** being

**[00:50:14]** selfish

**[00:50:15]** three

**[00:50:16]** things

**[00:50:17]** the

**[00:50:18]** runtime

**[00:50:19]** characteristics

**[00:50:20]** and integration

**[00:50:20]** stuff

**[00:50:21]** that we

**[00:50:21]** just

**[00:50:21]** discussed

**[00:50:22]** I think

**[00:50:22]** would be

**[00:50:23]** really

**[00:50:23]** valuable

**[00:50:24]** I think

**[00:50:25]** the

**[00:50:25]** refactoring

**[00:50:26]** and the

**[00:50:27]** beautification

**[00:50:27]** stuff

**[00:50:28]** would be

**[00:50:30]** extremely

**[00:50:30]** helpful

**[00:50:30]** and

**[00:50:31]** I think

**[00:50:32]** really

**[00:50:32]** change

**[00:50:33]** our

**[00:50:33]** degrees

**[00:50:33]** of

**[00:50:33]** freedom

**[00:50:33]** as in

**[00:50:34]** if you

**[00:50:34]** could

**[00:50:34]** lower

**[00:50:35]** the

**[00:50:35]** cost

**[00:50:36]** of

**[00:50:36]** future

**[00:50:36]** changes

**[00:50:37]** to

**[00:50:37]** Stripe

**[00:50:37]** and

**[00:50:38]** improve

**[00:50:38]** the quality

**[00:50:39]** of the

**[00:50:39]** architecture

**[00:50:39]** and then

**[00:50:40]** third

**[00:50:40]** we really

**[00:50:41]** care about

**[00:50:42]** what we

**[00:50:43]** call at

**[00:50:44]** Stripe

**[00:50:44]** craft and

**[00:50:45]** beauty

**[00:50:45]** and we

**[00:50:46]** want our

**[00:50:47]** software to

**[00:50:48]** be well

**[00:50:50]** designed

**[00:50:50]** and pleasant

**[00:50:51]** to use

**[00:50:52]** and pleasant

**[00:50:53]** to use

**[00:50:53]** not only

**[00:50:54]** in the

**[00:50:54]** superficial

**[00:50:56]** pixel sense

**[00:50:57]** but also

**[00:50:58]** in the

**[00:50:58]** deep

**[00:50:59]** it works

**[00:50:59]** very well

**[00:51:00]** sense

**[00:51:01]** and is

**[00:51:02]** something you

**[00:51:03]** can set up

**[00:51:04]** and largely

**[00:51:04]** forget about

**[00:51:05]** and just

**[00:51:05]** trust

**[00:51:06]** or forget

**[00:51:07]** about it

**[00:51:07]** in as much

**[00:51:08]** as you

**[00:51:08]** want to

**[00:51:09]** there's

**[00:51:10]** obviously

**[00:51:10]** a concern

**[00:51:10]** with AI

**[00:51:11]** that it

**[00:51:11]** leads to

**[00:51:12]** the creation

**[00:51:12]** of more

**[00:51:12]** slop

**[00:51:13]** and more

**[00:51:15]** kind of

**[00:51:16]** crappy

**[00:51:16]** things

**[00:51:17]** but not

**[00:51:17]** more of

**[00:51:18]** the best

**[00:51:18]** things

**[00:51:18]** I don't

**[00:51:19]** know

**[00:51:19]** what it

**[00:51:20]** would be

**[00:51:21]** that Cursor

**[00:51:21]** would do

**[00:51:22]** to ensure

**[00:51:24]** that the

**[00:51:25]** world is

**[00:51:25]** creating

**[00:51:26]** more of

**[00:51:26]** the best

**[00:51:27]** software

**[00:51:27]** and not

**[00:51:28]** just more

**[00:51:29]** software

**[00:51:29]** but I

**[00:51:30]** think that's

**[00:51:31]** an interesting

**[00:51:31]** and important

**[00:51:32]** dimension

**[00:51:33]** so those

**[00:51:33]** would be

**[00:51:34]** my

**[00:51:35]** besides all

**[00:51:35]** the obvious

**[00:51:36]** things to

**[00:51:36]** do

**[00:51:37]** those would

**[00:51:37]** be

**[00:51:38]** three

**[00:51:39]** suggestions

**[00:51:39]** amazing

**[00:51:40]** thank you

**[00:51:40]** Patrick

**[00:51:40]** all right

**[00:51:41]** thank you

**[00:51:41]** for having

**[00:51:42]** me

**[00:51:42]** yes

**[00:51:45]** thanks for

**[00:51:45]** listening to

**[00:51:46]** this episode

**[00:51:46]** of the

**[00:51:47]** a16z podcast

**[00:51:48]** if you like

**[00:51:49]** this episode

**[00:51:49]** be sure to

**[00:51:50]** like comment

**[00:51:51]** subscribe

**[00:51:51]** leave us a

**[00:51:52]** rating or review

**[00:51:53]** and share it

**[00:51:54]** with your

**[00:51:54]** friends and

**[00:51:55]** family

**[00:51:55]** for more

**[00:51:56]** episodes go

**[00:51:57]** to youtube

**[00:51:57]** apple podcast

**[00:51:58]** and spotify

**[00:51:59]** follow us on x

**[00:52:01]** a16z and

**[00:52:02]** subscribe to

**[00:52:03]** our sub stack

**[00:52:03]** at a16z.substack.com

**[00:52:06]** thanks again for

**[00:52:06]** listening and I'll

**[00:52:07]** see you in the

**[00:52:08]** next episode

**[00:52:10]** this information

**[00:52:11]** is for educational

**[00:52:12]** purposes only and

**[00:52:13]** is not a

**[00:52:13]** recommendation to

**[00:52:14]** buy hold or

**[00:52:15]** sell any

**[00:52:15]** investment or

**[00:52:16]** financial product

**[00:52:17]** this podcast has

**[00:52:18]** been produced by

**[00:52:18]** a third party

**[00:52:19]** and may include

**[00:52:20]** paid promotional

**[00:52:20]** advertisements

**[00:52:21]** other company

**[00:52:22]** references and

**[00:52:23]** individuals unaffiliated

**[00:52:24]** with a16z

**[00:52:25]** such advertisements

**[00:52:26]** companies and

**[00:52:27]** individuals are not

**[00:52:28]** endorsed by ah

**[00:52:29]** capital management

**[00:52:29]** LLC a16z or

**[00:52:31]** any of its

**[00:52:32]** affiliates

**[00:52:32]** information is

**[00:52:33]** from sources

**[00:52:34]** deemed reliable on

**[00:52:35]** the date of

**[00:52:35]** publication but a16z

**[00:52:36]** does not guarantee

**[00:52:37]** its accuracy

**[00:52:49]** diplomacy

## My Notes

> ✍️ Write your thoughts here...
