---
type: podcast-episode
podcast: "AI + a16z"
episode: ""
title: "OpenClaw: Why the Internet Isn't Built for AI Agents"
date: 2026-03-19
duration: "00:47:10"
score: 6.7
status: unlistened
listened_date:
archived_date:
audio: "[[Podcasts/audio/ai-a16z-openclaw-why-the-internet-isn-t-built-for-ai-agents.mp3]]"
tags: [podcast, ai-agents, openclaw, security, agent-identity, personal-assistant]
---

# OpenClaw: Why the Internet Isn't Built for AI Agents

## Summary

> [!abstract]
> OpenClaw 作为开源 AI 个人助理展示了 agent 的巨大潜力，但其核心瓶颈不在能力而在安全containment——身份认证、权限粒度和信任隔离问题亟待解决。
>
> OpenClaw reveals that AI agents' limiting factor isn't capability but containment — identity, fine-grained authorization, and trust isolation are the urgent unsolved problems.

## Key Takeaways

- 🧞 "Genie in a bottle" 隐喻：OpenClaw 等 AI agent 的能力已经足够强，真正的瓶颈是如何 contain 它——这是技术史上首次出现能力不受限、但安全约束成为主要制约的技术
- 🔐 Gmail 集成花了 7 小时，agent 自主建议获取 domain-wide access token（可访问公司所有邮箱），普通用户极可能直接授权——social engineering 首次适用于软件系统
- 🆔 Agent 需要全新的 identity 体系：user identity、service identity、agent identity 三层星座式交互，当前 OAuth/service account 模型完全不适配 agent 场景
- 🏪 Consumer 网站面临 innovator's dilemma：Amazon、DoorDash 没有 agent API，因为利润依赖 cross-selling UI；类比搜索领域，Google 未能主导 agent search，Exa/Brave 等新公司反而崛起
- 🤖 Agent 可能反向解决安全难题：人类抗拒 2FA/PKI 等安全措施，但 agent 不在乎复杂认证流程，可以实现 token rotation、credential vaulting 等人类从未愿意执行的安全最佳实践
- 🧱 Defense in depth 需要从前端转向后端：CAPTCHA 等 bot detection 将失效，企业需要 "bots welcome" 入口 + 后端行为分析来识别滥用，而非在 perimeter 拦截
- 🔄 OpenClaw 的核心创新是 self-extension：它能自主启动 coding agent 为自己编写新集成，这是之前 agent 框架不具备的属性，也是安全风险的放大器
- 💼 企业部署建议：dedicated hardware（Mac Mini）或 VM 隔离、agent 必须使用独立账户、定期重置状态（类似 Kubernetes immutable infra）、限制 blast radius 到单日数据

## Zettel Candidates

> [!tip] 可转化为 Zettel 的观点
> - AI agent 的真正瓶颈不是能力而是 containment——这是技术史上首次出现 capability 不是限制因素的技术范式
> - Social engineering 首次适用于软件系统：AI agent 可以被 prompt injection 操纵，就像人类可以被社会工程学欺骗一样，这打破了软件只受代码逻辑约束的假设
> - Agent 可能倒逼解决人类一直抗拒的安全问题：2FA、PKI、token rotation 等最佳实践因人类 friction intolerance 从未普及，但 agent 不在乎 UX friction，可能成为安全基础设施的真正推动力

## Audio

![[Podcasts/audio/ai-a16z-openclaw-why-the-internet-isn-t-built-for-ai-agents.mp3]]

## Transcript

**[00:00:00]** As a developer, I can totally build this, but I'm not going to build all the non-tale integrations.

**[00:00:04]** Just the fact that we're going to go through this exercise of fundamentally rethinking what the product experience is for this stuff, is just incredibly exciting.

**[00:00:12]** And now it's just sort of natural language expression of what you want and the machine fulfills it.

**[00:00:16]** My curiosity becomes, what does the future of this UI layer look like?

**[00:00:21]** Will the big incumbents catch up and offer their functionality for agents?

**[00:00:27]** Or do we actually need new companies that cater to agents specifically?

**[00:00:31]** Security is always a game of defense and depth.

**[00:00:33]** And you're sort of, when you hit capture and you hit the front-end bot detection stuff, that's like the tip of the spear.

**[00:00:39]** There's this concept in defense called the redoubt, like you retreat back to the wall inside.

**[00:00:43]** And I think what we're going to see for a lot of these perimeter controls because of agents is that they have to move to more of the backend system.

**[00:00:50]** And what's super fascinating to me is this is one of the first times we're having technology.

**[00:00:55]** But what it can do is not limited by its abilities, but limited by how I can make it secure and stop it from doing certain things.

**[00:01:02]** We have this genie in a bottle. It's amazing. But how do I contain this?

**[00:01:08]** OpenClaw is an open-source personal AI assistant that can message on your behalf, check your calendar, manage your email, and extend itself by writing new integrations on the fly.

**[00:01:18]** Setting up Genail integration takes seven hours.

**[00:01:22]** The agent will ask for domain-wide access to every email account in your company.

**[00:01:26]** Consumer websites like DoorDash and Amazon have no APIs for agents.

**[00:01:31]** And if you're not careful, you can create something that can be socially engineered into access it was never supposed to have.

**[00:01:37]** This is a technology where the limiting factor isn't capability, but containment.

**[00:01:43]** The genie is in the bottle.

**[00:01:45]** The question is how to keep it there.

**[00:01:49]** Hello, everyone.

**[00:01:50]** So we're here today to talk about OpenClaw, which is currently one of the hottest, most controversial, most interesting, most dangerous, I think, technologies here in Silicon Valley.

**[00:02:01]** Yoko, you want to kick it off?

**[00:02:02]** What is OpenClaw?

**[00:02:02]** What is OpenClaw?

**[00:02:03]** So OpenClaw is this very cool personal assistant that's open-source built on top of another very cool coding agent called Pi.

**[00:02:11]** I think the repo's name was Pi Mono.

**[00:02:14]** It's a very just like minimal but very expensive coding agent that can run the loop, update its own config.

**[00:02:21]** And OpenClaw that's built on top, built around all the sessions, state management for Pi, but also added a long tail of integrations.

**[00:02:29]** So you can now talk to your personal assistant on WhatsApp, Telegram, like a phone number, iMessage, and everything else you can think of.

**[00:02:38]** Use one password, not yet able to place the order on DoorDash.

**[00:02:42]** We'll chat more about that later.

**[00:02:44]** But the whole ecosystem is really booming.

**[00:02:47]** What we can use long-running agent in the sandbox for.

**[00:02:51]** So we all built some interesting use cases.

**[00:02:54]** One of our first use cases I've explored is how can I have OpenClaw consistently check my cat's location via the AirTag API.

**[00:03:03]** Since for AirTags, the location is only updated once you are active on the user session on the browser.

**[00:03:09]** So that has been useful.

**[00:03:10]** So curious what you guys built with it recently.

**[00:03:13]** As a former CISO, you must just love OpenClaw.

**[00:03:15]** And currently acting CISO.

**[00:03:17]** Well, actually, this is, never mind.

**[00:03:19]** Current CISO.

**[00:03:19]** Actually, I've been using it for a while now.

**[00:03:22]** I think it's incredibly awesome because it lets you see the contours of the future.

**[00:03:26]** This is the first time where we can see, like, what these agents are going to do.

**[00:03:31]** And the firm is built around Mark's famous sort of software is eating the world piece.

**[00:03:36]** And this is the first time where you can see these agents are eating the world.

**[00:03:39]** Like, it gives them, like, true agency in a world to do things.

**[00:03:42]** And so, of course, the first couple of use cases I did were very security focused.

**[00:03:46]** I really enjoyed trying to just getting things to work, as you guys know, and experience, like, is not simple.

**[00:03:51]** I think part of the reason why, as a CISO, I'm not super concerned yet about people here using it because only a very few, a smaller handful of people can get this thing working, I think, than typical other tools.

**[00:04:02]** It's so hard.

**[00:04:02]** That's a feature here.

**[00:04:03]** Yeah, exactly.

**[00:04:03]** People are, like, asking us, what's homebrew?

**[00:04:05]** How do I get it on my computer?

**[00:04:06]** You're like, okay, we're good for now.

**[00:04:08]** But you can see as these things become more consumery, become easier to use, like, these things are going to take off.

**[00:04:14]** This is going to be an incredible wave.

**[00:04:16]** And building these tools has been incredibly fun.

**[00:04:19]** So.

**[00:04:19]** Wait, I'm curious.

**[00:04:20]** I mean, normal people like us, we use it to check our cat's location, check calendar, take notes.

**[00:04:26]** What are the security use cases?

**[00:04:28]** So, and it varies by model.

**[00:04:31]** So the models all have very different capabilities.

**[00:04:34]** And so the first thing I started doing was giving it impossible tasks.

**[00:04:37]** So I need you to do this thing, but you only have access to these two tools.

**[00:04:40]** And some of the other models would kind of give up and say, sorry, it doesn't work, or do something like that.

**[00:04:44]** Or they'd try to, like, write some code or do something kind of interesting.

**[00:04:47]** But, like, some of the more advanced models actually started using, like, hacking techniques.

**[00:04:51]** Where they'd be like, hey, I found an AWS key on your device, and maybe I'll try it, right?

**[00:04:55]** And so those were kind of the first sets of use cases was basically, let's get it running, let's add some basic tools and tasks,

**[00:05:01]** and then let's start asking it to do impossible things and see where it goes.

**[00:05:04]** And you can very quickly see how these things would get out of control.

**[00:05:07]** And they're really interesting, but also very sophisticated way.

**[00:05:10]** The security aspect of Oprah, I just find completely crazy, right?

**[00:05:13]** So I connected mine to Gmail, which took me, I want to say, about seven hours.

**[00:05:16]** So it's unbelievably hard still, right?

**[00:05:18]** And it's like figuring out the account setup, figuring out the education models, getting all the polling right, and so on, lots of debugging steps.

**[00:05:24]** Meanwhile, Telegram works out of the box.

**[00:05:26]** Here we go.

**[00:05:28]** But the most interesting thing actually doing the process was that when I basically asked it, how do we set this up?

**[00:05:33]** And it started coding and started implementing things.

**[00:05:35]** At first, that didn't quite work.

**[00:05:36]** The second try, it did work.

**[00:05:37]** And it was at some point, it was like, okay, now I need an authentication from token, right?

**[00:05:40]** And it gave me instructions how to set it up.

**[00:05:42]** And basically said, look, create a service account and then give me this token with a domain-wide scope.

**[00:05:47]** And you're like, wait a second, domain-wide scope?

**[00:05:49]** What does this exactly mean?

**[00:05:50]** So what was it suggesting?

**[00:05:52]** I should give them a token, not for its own email account, right?

**[00:05:55]** I mean, it's usually the way how you run OpenClaw is that you try to segregate it very well from everything else.

**[00:06:00]** So own email account or own Apple account or credit card if you want to give it a crack or debit card if you want to give it a debit card.

**[00:06:06]** We saw one of our startups actually putting it on a separate desk, which I found just super funny.

**[00:06:11]** It's like absence of separation, a separate hardware gap, right?

**[00:06:13]** But even desk gap, right?

**[00:06:15]** It says one more.

**[00:06:15]** Yeah.

**[00:06:16]** But basically what it was suggesting to me is to give it a token that would give it full access to every single email account in the entire company, right?

**[00:06:22]** Which is crazy.

**[00:06:23]** And number three, write permissions where everything to do.

**[00:06:25]** Imagine a normal user following that.

**[00:06:26]** Exactly.

**[00:06:27]** Exactly.

**[00:06:28]** But the other thing is that actually would have worked, right?

**[00:06:30]** It would have totally worked.

**[00:06:32]** In a sense, from its own perspective, it's exactly the right thing, right?

**[00:06:34]** Give me all the permissions that enable me to do it.

**[00:06:36]** I don't want to bother you again.

**[00:06:37]** Exactly.

**[00:06:38]** And so basically understanding this and then reading up on it and understanding, I mean, also Google security model on email, I think is absolutely horrible, right?

**[00:06:45]** For a service account right now, we can only give domain-wide access, right?

**[00:06:48]** You don't want that.

**[00:06:49]** What you instead want is a software specific, they need to go via OAuth and things get complicated, right?

**[00:06:54]** But it's going through all of this, right?

**[00:06:56]** I think it really, really shows how if you're not very, very careful, you can create something which can extend itself, can be socially engineered.

**[00:07:06]** I think it's a new thing, right?

**[00:07:07]** We've never had it before.

**[00:07:08]** They have a complex software system, which you can actually influence with social engineering, right?

**[00:07:11]** In all previous instructions.

**[00:07:13]** It's subject to influence.

**[00:07:14]** Exactly.

**[00:07:14]** And it's very, very easy for even a somewhat sophisticated user to set this up in a way that can do a massive amount of damage.

**[00:07:22]** One prompt for the group is we've seen this pattern of putting an agent, long-running agent in a sandbox for a long time now, since I would say six months to a year ago.

**[00:07:33]** So why did OpenClaw take off?

**[00:07:35]** And then what's so special about it?

**[00:07:37]** Here's about your view.

**[00:07:38]** I found it relatively easy to set up and get going.

**[00:07:42]** And I think that there was enough documentation and support that I didn't have to spend seven hours to just do the Telegram use case and start playing with it.

**[00:07:49]** And then it led to other use cases.

**[00:07:51]** And then eventually I got blocked because I didn't have seven hours to spend figuring out how to provision accounts properly.

**[00:07:56]** And so I just think it's sort of that, like, just that level of accessibility to users who are maybe not living in a code base day to day.

**[00:08:03]** Whereas, like, I know you guys probably spend a lot more time in code than I do.

**[00:08:06]** And I am probably the world's worst coder.

**[00:08:08]** But I was, this was accessible to me.

**[00:08:09]** So reasonably technical, understand core principles.

**[00:08:12]** I do have homebrew on my laptop so I can get stuff working.

**[00:08:16]** But, you know, the other agent frameworks were pretty difficult to use, incredibly flaky, didn't really want to spend a lot of time debugging someone else's stuff.

**[00:08:24]** So I think that was a big part of it.

**[00:08:27]** It is another major part of this that it can extend itself.

**[00:08:30]** I think it's the first agent I've seen where I can say, you know, I want an integration with something.

**[00:08:35]** And it's, well, I've never seen this before.

**[00:08:37]** There's no package for that.

**[00:08:38]** But let me try to put something together.

**[00:08:39]** It fires up a coding assistant and tries to extend itself.

**[00:08:41]** Right.

**[00:08:42]** I think that's new.

**[00:08:43]** There is definitely a long running nature of it.

**[00:08:46]** Like, you leave it running for a night and you're like, keep working on this until you finish.

**[00:08:51]** I mean, cursor could do this too.

**[00:08:53]** But I think the difference is that they expose the visibility for the end user.

**[00:08:57]** That you can keep checking with it from your phone or on the dashboard.

**[00:09:00]** You hopefully securely expose that how many tokens it's generating, like how fast it's completing the task.

**[00:09:07]** So the visibility part is interesting.

**[00:09:09]** Another interesting part is the more consumer-consumer integrations.

**[00:09:14]** Like if I, as a developer, I can totally build this, but I'm not going to build all the long tail integrations.

**[00:09:19]** Like I'm not going to hook it up to Gmail or 1Password.

**[00:09:23]** I don't want to touch the 1Password CLI to kind of give it to us as MCP or skill.

**[00:09:29]** So MCP layer is also very critical there.

**[00:09:32]** It is interesting what people are using it for.

**[00:09:35]** I mean, Guido was talking about one use case where you were trying to hook up your 3D printer.

**[00:09:39]** Yes.

**[00:09:42]** It actually doesn't work yet, but I think we get to work over the weekend.

**[00:09:45]** I think we're trying to figure out the boundaries.

**[00:09:48]** Like we can now connect because it can extend itself, which is a really new property.

**[00:09:53]** It can, you can hook much more complex systems to it, right?

**[00:09:58]** If there's some documentation somewhere on the web or some API, it can probably figure something out.

**[00:10:03]** And which part, which integrations are useful, which are not, right?

**[00:10:07]** But actually, that's a good prompt.

**[00:10:09]** What integrations do y'all actually use day-to-day on OpenCALL?

**[00:10:15]** Honestly, right now, I'm still in the experimentation phase.

**[00:10:18]** I don't use it day-to-day.

**[00:10:18]** I don't let it run unsupervised.

**[00:10:20]** It doesn't run overnight.

**[00:10:21]** I'm there watching this thing.

**[00:10:23]** I don't.

**[00:10:23]** So there's a couple of use cases I've explored because I really want to just set it free on the Mac Mini

**[00:10:30]** and then not monitor it for a long time.

**[00:10:33]** The first integration was actually, I was, so we have a portfolio company called Quiver.

**[00:10:38]** They do SVG generation.

**[00:10:40]** So I got very curious.

**[00:10:41]** I'm like, what if I just give the API to OpenClaw and have it run overnight to generate some gaming assets for me?

**[00:10:48]** And then only generate to a certain style and then you can use LM to QA it.

**[00:10:53]** So what I did is I give OpenClaw a millify doc on Quiver.

**[00:10:57]** I don't want to explain how it works.

**[00:10:59]** I'm like, build the thing.

**[00:11:00]** First, build Quiver MCP.

**[00:11:03]** Test it with OpenCode and cursor to make sure that you have an instance that actually works with the MCP.

**[00:11:09]** And then once it works, generate 100 gaming assets for me.

**[00:11:14]** So I'm building a game on the side.

**[00:11:16]** You know, SVG happens to be a great composable layer of it.

**[00:11:20]** They actually did that and sent me a huge zip in the morning.

**[00:11:25]** And I opened, like, there are some assets that are just not great, but like, there's like 60% of it.

**[00:11:31]** That's very usable.

**[00:11:32]** Yeah, that's awesome.

**[00:11:33]** And then I'm like, well, these are the simple tasks.

**[00:11:36]** I wouldn't want to do it myself, but like, because you have something so long running and resumable, you could do it easily in the box.

**[00:11:44]** That makes sense.

**[00:11:45]** I mean, so I'm still using it very little, frankly, right?

**[00:11:49]** It's not part of my daily routine.

**[00:11:50]** There's a few cases which I like.

**[00:11:52]** One is if you have an email and you want to look something up related to that email, right?

**[00:11:58]** It's really nice.

**[00:11:59]** So, you know, somebody sends me, you know, like say, Guido, can we meet at XYZ?

**[00:12:04]** So I can just forward and say, like, can you figure out what will be the driving times to this at this time when the meeting is suggested, right?

**[00:12:09]** And something comes back.

**[00:12:11]** Or even nicer, you can do something like, you know, like, let's say, you know, we want to meet at some cafe and you ask, you know, where is it?

**[00:12:18]** And you can just be like, you know, claw, can you just, you know, attach a map link to it or something like that?

**[00:12:25]** So I think for me, you know, once we got this a little more secure, I think email is going to be the first killer use case.

**[00:12:30]** Being able to say, like, look through my email, delete all the spam, everything, all the meetings for my conference, you know, next week.

**[00:12:37]** Just put them in my calendar or double check that they're there and make sure there's no conflicts.

**[00:12:40]** Or yes, tell me which conflicts there are.

**[00:12:42]** Right.

**[00:12:42]** So going through these things, right, that is super powerful.

**[00:12:45]** I did get an email from Guido's OpenClaw yesterday.

**[00:12:49]** And the funny thing is the OpenClaw asked me, do you want to order boba?

**[00:12:53]** If you want to order boba tea, go ping Guido.

**[00:12:56]** Can you place your order?

**[00:12:59]** We're still working on the automation here.

**[00:13:01]** That's creating more work for you, you know.

**[00:13:02]** It's the opposite of what you want from automation.

**[00:13:05]** But ordering stuff is still hard.

**[00:13:07]** Oh, it's so hard.

**[00:13:08]** So before this podcast, we actually tried to see if we can order fills in real time and get it delivered.

**[00:13:14]** It turns out Uber Eats and DoorDash, if you don't already have an account for OpenClaw, there's some bot detection.

**[00:13:22]** Sometimes that ordering experience just fails, even if you give it like a guest checkout link.

**[00:13:27]** Which led me to my next prompt for the group.

**[00:13:31]** Like, what do you think will unlock the next wave of adoption for OpenClaw?

**[00:13:35]** What is missing?

**[00:13:38]** Boy, a binary, you double click install and get it running, right?

**[00:13:42]** Like, I think it's, I think there's sort of the, for the sort of home use.

**[00:13:46]** Isn't it usually exclusive or self-extending?

**[00:13:48]** Yeah, well, no, but I mean just to get people up and running.

**[00:13:52]** Like, I think, I think the current installation path, I know they exist, but I think like a slickly packaged software bundle of this stuff that maybe, I'd say maybe my dad could download and install.

**[00:14:05]** Would you in that case just make it a service?

**[00:14:07]** Yeah, you could make it a service.

**[00:14:08]** Claw as a service?

**[00:14:09]** Probably.

**[00:14:09]** Well, that would, and that would solve a lot of the security problems, right?

**[00:14:12]** If you could contain it.

**[00:14:14]** I think, I think you need to turn to a SaaS service for people.

**[00:14:16]** I think you need to change the security model.

**[00:14:20]** And I'm actually not quite sure how.

**[00:14:23]** Actually, what's the hard problem?

**[00:14:25]** Right?

**[00:14:25]** Account management paradigm.

**[00:14:26]** Like, we both had to spend hours setting up all the accounts just for OpenClaw.

**[00:14:32]** That's right.

**[00:14:32]** As if OpenClaw is a person.

**[00:14:34]** Yeah.

**[00:14:34]** Right?

**[00:14:34]** There's no agent concept.

**[00:14:36]** That's right.

**[00:14:36]** Exactly.

**[00:14:37]** Yes, exactly.

**[00:14:38]** So what does that look like?

**[00:14:38]** I mean, Joel, you're an expert on like Okta and the world when it came, you know, to the SaaS world years ago.

**[00:14:45]** I think, so like right now, so security is always a laggard.

**[00:14:48]** Just, it's always reactive.

**[00:14:51]** As OpenClaw itself is demonstrating, it's never front of mind.

**[00:14:55]** And so like, you've got to start thinking through what is, I mean, to your point, like what does identity mean in this world?

**[00:15:00]** And I think you have this constellation of identities that have to interplay with each other.

**[00:15:05]** So you have the constellation of the user that's orchestrating the OpenClaw.

**[00:15:10]** You have the identities of all the services that it has access to.

**[00:15:14]** And then you have the identities of the agents that launch themselves.

**[00:15:17]** And I think you end up in this world.

**[00:15:19]** And this is where I'm actually quite hopeful about like a lot of security problems getting solved.

**[00:15:23]** You have this world in which, I mean, think of how hard it's been for us to get just normal users to use two-factor authentication.

**[00:15:30]** Coming from Ubico.

**[00:15:32]** Tell me about it.

**[00:15:33]** It's like, I have this thing that prevents cancer and people are still like, no, cancer is not that bad.

**[00:15:38]** It's like literally, like because people are.

**[00:15:40]** There's more or less, you know, it takes phishing attacks to zero and all it deploys.

**[00:15:45]** The threshold of tolerance for stuff for people is incredibly low.

**[00:15:49]** Just humans in general is incredibly low when it comes to stuff like that.

**[00:15:52]** These agents don't care, right?

**[00:15:53]** And so I think it's the opportunity where we could probably start to put in things that would annoy a human and a human would never do.

**[00:16:00]** These agents will probably do.

**[00:16:01]** So you can start to look at maybe there's legitimate uses of, I know I'm going to say PKI and probably get left out of the room, but like maybe PKI founds an application in this world, right?

**[00:16:09]** Well, polished hidden PKI.

**[00:16:11]** Well, the agents deal with it.

**[00:16:12]** It's not exposed to these humans, right?

**[00:16:14]** Like things like that start to make a lot more sense, right?

**[00:16:17]** You can get people to start effectively using vaulting.

**[00:16:19]** You can get away from passwords that need to be memorable.

**[00:16:22]** You can get to this point where identities can step up and step down in their authorization scope and frameworks.

**[00:16:28]** And you come into a world where all the things that we've always been saying from first principles are the things you need to do have been blocked by humans' lack of desire to suffer through them.

**[00:16:38]** Gets alleviated, right?

**[00:16:39]** So I think maybe we can fix a lot of stuff.

**[00:16:41]** So by the authentication identity problem, huge issue.

**[00:16:46]** I think there's two more.

**[00:16:47]** There's a question of authorization limits and monitoring, right?

**[00:16:51]** Then there's one of business models for some of the current websites.

**[00:16:54]** So let's start with the authorization.

**[00:16:55]** So really what I'd like to have is not giving the agent access to all of my mail because that creates a huge blast radius, right?

**[00:17:03]** If this thing gets compromised right now, everything I've ever said, you know, I've CC'd on, right?

**[00:17:08]** And so on.

**[00:17:08]** Yeah.

**[00:17:08]** So instead, like, for example, how about this thing can only access my inbox, right?

**[00:17:12]** That will be useful, right?

**[00:17:13]** Right now.

**[00:17:14]** Or only access emails in my inbox labeled something.

**[00:17:17]** Oh, that, right.

**[00:17:17]** Exactly, right.

**[00:17:19]** And right now, Google has zero fine-grained access controls for Gmail.

**[00:17:24]** Yeah, yeah, yeah.

**[00:17:25]** There's absolutely nothing.

**[00:17:26]** It's, you know, until last year, you couldn't even in Drive have fine-grained access controls at a folder level, right?

**[00:17:33]** You've got an access token for all of Drive, right?

**[00:17:35]** Which is ridiculous to some degree.

**[00:17:37]** For Drive now, we've got service accounts that you can share, we can share directories.

**[00:17:40]** So if you need something probably even much more fine-grained than that, you know, for email,

**[00:17:44]** and then we want the next thing on Amazon.

**[00:17:46]** What are my spend limits?

**[00:17:47]** What can it buy?

**[00:17:47]** And so on, right?

**[00:17:48]** So, I mean, there's a huge, huge infrastructure.

**[00:17:51]** And the way this always works with security is that the first thing that goes is a proxy.

**[00:17:54]** And so you know that there's going to be some sort of proxy and some sort of broker for that access.

**[00:17:58]** And at some point, what always ends up happening is the service provider themselves may add some of those futures.

**[00:18:04]** But there might be a long enough tail there that you do get a proxying infrastructure for agents to access these things.

**[00:18:10]** So two observations.

**[00:18:11]** One is, I think there's a huge opportunity for startups here to create these proxies, right?

**[00:18:15]** If somebody would give me, like, here's, you know, a Sculpt Gmail, I would adopt that today, right?

**[00:18:19]** But the second one is, I think, that's the last of my three points.

**[00:18:22]** I think it's a business, right?

**[00:18:24]** Because there are websites today where the majority of the revenue and certainly the majority of profits come from cross-selling, right?

**[00:18:33]** If this website is suddenly only used by agents, that doesn't work anymore, right?

**[00:18:36]** If they're there, they're basically going out of business.

**[00:18:40]** So today, Amazon doesn't have an API, at least for consumers, right?

**[00:18:43]** The DoorDash doesn't have an API, right?

**[00:18:45]** All of these large consumer sites are like, no, no, we don't want this.

**[00:18:47]** I want to be the, what was it, DoubleDash it or something?

**[00:18:50]** You know, like, why don't you also buy XYZ?

**[00:18:52]** You know, here's some recommendations, right?

**[00:18:53]** They don't want agents, essentially.

**[00:18:55]** So I think one interesting question here is, will the big incumbents catch up and offer their functionality for agents?

**[00:19:05]** Or do we actually need new companies that cater to agents specifically?

**[00:19:09]** And then you may say, wait, this is crazy, right?

**[00:19:11]** Why would not Amazon also be the number one agent vendors?

**[00:19:13]** Let's look at search for agents, right?

**[00:19:15]** You would be like, well, of course, Google is the number one search.

**[00:19:17]** So they're going to be the number one search with agents.

**[00:19:19]** That's absolutely not the case today, right?

**[00:19:21]** I don't think they have an agent search project anymore.

**[00:19:23]** We haven't said Exa and Brave and a bunch of other companies.

**[00:19:27]** I'm doing this.

**[00:19:28]** So do we actually need to replace some of the big sort of SaaS building blocks of e-commerce,

**[00:19:35]** of online services and so on and redo them for agents?

**[00:19:37]** What are the areas where we think there's an agent-specific service that need to be built yesterday?

**[00:19:45]** Exactly.

**[00:19:45]** Or, I mean, why does Google not have an agent search?

**[00:19:50]** Maybe it's just innovator's dilemma.

**[00:19:51]** I don't know, right?

**[00:19:52]** But it's kind of interesting.

**[00:19:53]** I mean, it sounds like innovator's dilemma.

**[00:19:54]** It sounds like it, yeah?

**[00:19:55]** Yeah.

**[00:19:55]** Your business model is so much tied to, you know, in a particular way to your service that you can't make the jump to something.

**[00:20:02]** Do you think some of it may have been this sort of head fake around the browser use?

**[00:20:05]** Like there was sort of a belief that, well, these things will just use browsers and so they can navigate the web like a human?

**[00:20:11]** And they can to some extent today, but I don't think the whole website environment is friendly to bots.

**[00:20:18]** There are some vendors recently I've come across that turned off bot detection because of this use.

**[00:20:24]** Yeah, that makes total sense.

**[00:20:25]** Which makes total sense, but then it also opens up the doors for abusers.

**[00:20:30]** You should be focused on bot enablement, not bot detection and prevention.

**[00:20:34]** And then what does that look like?

**[00:20:35]** I mean, today, if I go to like DoorDash, sometimes they'll ask, are you a bot?

**[00:20:39]** Like as a human, and you have to solve very complex puzzles.

**[00:20:44]** I ran into this when I was trying to create a net new login for my OpenClaw on GitHub.

**[00:20:50]** I had to solve six puzzles.

**[00:20:53]** That's really hard.

**[00:20:54]** Yeah, the drag and drop ones, right?

**[00:20:55]** The drag and drop ones.

**[00:20:56]** And I'm like, this is actually the next level now.

**[00:20:59]** But then what does it look like if I today open up OpenClaw?

**[00:21:03]** I'm just like, go get five accounts without human intervention.

**[00:21:07]** And here's one credential I can give you.

**[00:21:10]** What does that look like?

**[00:21:11]** And then what if I just don't have to spend hours trying to get it into, you know, all these accounts?

**[00:21:18]** Yeah, I mean, I think for a lot of these companies, to Guido's point about the business model,

**[00:21:23]** they're going to have to refigure kind of how that stack works.

**[00:21:26]** And they're going to have to move.

**[00:21:28]** Security is always a game of defense and depth.

**[00:21:30]** And you're sort of, when you hit CAPTCHA and you hit the front-end bot detection stuff,

**[00:21:33]** that's like the tip of the spear.

**[00:21:35]** You're kind of just hitting that layer.

**[00:21:38]** You're going to have to, there's this concept in defense called like the redoubt.

**[00:21:43]** Like you retreat back to the wall inside.

**[00:21:45]** And I think what we're going to see for a lot of these perimeter controls,

**[00:21:48]** because of agents, is that they have to move to more of the backend system.

**[00:21:52]** And you have to build a more sophisticated understanding of the way your business operates.

**[00:21:56]** So you can spot things, like you're going to want bots to register.

**[00:21:59]** You're going to want bots to sign up and agents to sign up.

**[00:22:01]** What you have to do is protect the things inside the system

**[00:22:04]** where there could be issues of abuse or exploitation or fraud and stuff, right?

**[00:22:09]** Instead of bot detection, what, I don't know, thought I should have is a bots are welcome banner, right?

**[00:22:14]** If you are bot, click here.

**[00:22:15]** Here's our API.

**[00:22:16]** Just like, here's the API.

**[00:22:18]** And, you know, please sign up as a bot.

**[00:22:20]** And when you sign up as a bot, maybe state who your, you know, who your master is or something.

**[00:22:24]** Yeah, yeah.

**[00:22:24]** 100%.

**[00:22:25]** So true.

**[00:22:25]** Register them.

**[00:22:26]** Give us their PII.

**[00:22:29]** One example of this, which is like a read-only use case.

**[00:22:32]** So Millify actually does it really well.

**[00:22:34]** If it's a coding agent, access the website.

**[00:22:36]** It will prompt the coding agent to have an LLM.txt instead of viewing the web.

**[00:22:41]** Like, because it's just much slower to have founding boxes.

**[00:22:44]** Exactly.

**[00:22:45]** And you want the compact text blob to send back to the agent.

**[00:22:50]** I mean, that's a read-only use case.

**[00:22:52]** So I do wonder what, you know, write use cases will look like on the web for the agent.

**[00:22:57]** It's not some, I mean, it could be API, but the agent still needs an account identity and API, so on and so forth.

**[00:23:03]** It could be something between CLI and API.

**[00:23:06]** Yeah.

**[00:23:07]** Why should it not be API?

**[00:23:08]** It could be an API, just you need to issue a token first.

**[00:23:12]** So to issue a token, you need an account.

**[00:23:14]** To get an account, you need a human.

**[00:23:15]** And I don't want to be in the loop.

**[00:23:17]** I mean, let's say I give my bot an email address or a telegraph or a telegram or whatever it is, right?

**[00:23:24]** There's some kind of account.

**[00:23:26]** You could say, look, hello, bot, you need to register with some kind of account.

**[00:23:31]** Yes.

**[00:23:31]** Right?

**[00:23:32]** But then we're trying to that UI where GitHub will ask you, are you a bot?

**[00:23:36]** Solve these puzzles.

**[00:23:38]** No, no.

**[00:23:38]** What I mean is front page, you know, bots welcome, click here, right?

**[00:23:42]** Or, you know, and then there's like, here's the bot API, here's the register bot function, right?

**[00:23:46]** And then here, once you have a token, then here's all the following functions, right?

**[00:23:49]** Yeah, totally.

**[00:23:50]** That would make sense.

**[00:23:50]** The bot UI does remind me of something else, which is like the automation UI has evolved so much with OpenClaw.

**[00:23:58]** It used to be, I remember using these RPA tools maybe a couple of years ago.

**[00:24:02]** It was a lot of drag and drop.

**[00:24:04]** I connect the dots from this UI box to another UI box.

**[00:24:07]** Now it's so much of like describing the outcome and ask the bot to keep spinning until you get this right.

**[00:24:15]** To kind of leverage test time compute to the maximum.

**[00:24:18]** And I don't care how much token I'm like spitting out.

**[00:24:22]** So, so my curiosity becomes, what does the future of this UI layer look like?

**[00:24:29]** How do you interact with your RPA tools, personal assistant?

**[00:24:33]** Is it a prompt?

**[00:24:34]** Is it, yeah, something else?

**[00:24:35]** I mean, this is, that's the truly exciting part.

**[00:24:37]** So I am, you know, CISOs in general, you should never take product advice from.

**[00:24:41]** We are the worst product thinkers you've ever met.

**[00:24:44]** But like just the fact that we're going to go through this exercise of fundamentally rethinking what the product experience is for this stuff.

**[00:24:50]** It's just incredibly exciting, right?

**[00:24:52]** Like it's, it's, it's, it's these moments where you see like the, the transition between, you know, ways of thinking about the world and going from sort of that, that RPA drag and drop, right?

**[00:25:04]** Remember pseudocode, right?

**[00:25:05]** And then drag and drop and all these sorts of things.

**[00:25:07]** And now it's just sort of natural language expression of what you want and the machine fulfills it.

**[00:25:11]** Which just drives a completely different user experience, right?

**[00:25:15]** And a user interface just disappears.

**[00:25:17]** So yeah, I mean, I, I don't know.

**[00:25:19]** And I'm the last person that should probably participate on it.

**[00:25:21]** Well, the user interface disappeared.

**[00:25:22]** I'm not sure about that.

**[00:25:24]** Really?

**[00:25:25]** I think so.

**[00:25:25]** No, I mean, you're, you're obviously, you know, you, you define your tasks at a much higher level, right?

**[00:25:31]** But I still want to be kept in the loop how the task is being executed.

**[00:25:35]** Usually when I specify a task, I'm never precise enough that I, basically all the possible trade-offs and design choices.

**[00:25:41]** And these things are clearly specified, right?

**[00:25:43]** So whenever one of these, these things happens, either I want to, it should be Guido, what should I do here?

**[00:25:49]** Or at least it should be Guido, I decided to do X, right?

**[00:25:52]** So you probably still want some kind of user interface, right?

**[00:25:55]** I mean, it looks very different.

**[00:25:56]** Don't get me wrong, but, but.

**[00:25:57]** I mean, I think you probably live on the far right side of the distribution for users of this stuff.

**[00:26:03]** What can you say?

**[00:26:05]** Yeah, I was about to say.

**[00:26:06]** The left side is like total vibe code, like total, like, give me an app to help me plan my wedding versus sort of like, I want step-by-step instructions on architecture choices.

**[00:26:14]** Like there, there's like a, there's a spectrum there.

**[00:26:16]** And I think most people land in the middle of that.

**[00:26:17]** Like, I think you probably want to get pinged on stuff where it's like a big deal or something fails.

**[00:26:23]** But I don't know about like progress.

**[00:26:25]** I mean, I mean, like I said, I'm the worst person to get product.

**[00:26:28]** Okay.

**[00:26:29]** I buy the progress part.

**[00:26:30]** Just give me the answer.

**[00:26:30]** But, but I mean, if there's, if there's meaningful choices, right?

**[00:26:34]** Yeah.

**[00:26:34]** But you would probably get that up front.

**[00:26:37]** Because the inference.

**[00:26:37]** An app to plan my wedding.

**[00:26:39]** Does it involve travel?

**[00:26:40]** Yeah, yeah, yeah.

**[00:26:41]** You know, that may change things.

**[00:26:42]** But you would probably have some iterative process with the.

**[00:26:44]** Yeah, exactly.

**[00:26:45]** Yeah, yeah, yeah.

**[00:26:45]** But that's the UI.

**[00:26:47]** Well, yeah.

**[00:26:48]** I mean, I guess it would be, yeah.

**[00:26:49]** I mean, maybe.

**[00:26:49]** Show me a flow chart or something like.

**[00:26:51]** Yeah, yeah, yeah.

**[00:26:51]** Or show me like concepts.

**[00:26:53]** I mean, I think that there's still some aspect there.

**[00:26:55]** Maybe it's all just text with images.

**[00:26:56]** I don't know.

**[00:26:57]** It could be.

**[00:26:57]** One way OpenClaw has evolved the UI a little bit, which is like very clear on their app is

**[00:27:02]** it abstracted away cron jobs.

**[00:27:04]** As a developer, obviously, I used to handwrite the cron job schedule.

**[00:27:08]** I always have to look it up.

**[00:27:09]** It's terrible.

**[00:27:09]** No two cron jobs defines the schedule the same way.

**[00:27:12]** But now you don't really care about it anymore.

**[00:27:15]** Like I was investigating with OpenClaw on like, why did you, didn't you notify me five

**[00:27:19]** minutes ago on something?

**[00:27:21]** And it's like, let me take a look.

**[00:27:23]** Okay, here's my cron job.

**[00:27:24]** So how the cron job works is that it will wake up, it will ping me and I will wake up

**[00:27:29]** and I'll process it and I'll ping you.

**[00:27:32]** So that's how it works now.

**[00:27:34]** Like I don't really interact with like, I don't care about when the schedule will wake up

**[00:27:39]** in a systematic level.

**[00:27:40]** It's more, there's an LLM taking care of all the systems and orchestrating all of them

**[00:27:45]** for me.

**[00:27:46]** I think this is interesting.

**[00:27:46]** To some degree, I think what OpenClaw has done is it's taken all this autonomy that we

**[00:27:51]** had before for software development.

**[00:27:53]** And now it starts applying a little bit of systems level, right?

**[00:27:57]** It's no longer about just the, you know, my, the code itself, but all the things around

**[00:28:01]** it, the integrations, you know, the cron jobs, the operating system, the ports, you know,

**[00:28:06]** these things.

**[00:28:06]** And when you think about it, email is the queue infra for humans.

**[00:28:12]** And cron job is the queue infra for agents.

**[00:28:16]** And now you just get to abstract away all of that and give all the queues to the agent

**[00:28:21]** and they can just process it.

**[00:28:24]** But sometimes they do need to wake up and then use a very expensive function call, which

**[00:28:28]** is ask a human to do something.

**[00:28:31]** Like ask Guido to order Boba T.

**[00:28:34]** In the future, they have a token budget and a human interaction budget.

**[00:28:37]** We need to figure out our token threshold as humans.

**[00:28:41]** Yeah.

**[00:28:41]** For OpenClaw, I guess, what are the extensions that y'all are most excited about that don't

**[00:28:48]** yet exist?

**[00:28:50]** Or what are the system improvements you want to see?

**[00:28:53]** I think my number one thing would be various consumer sites, which currently are incredibly

**[00:28:59]** hard to integrate.

**[00:29:00]** Consumer sites?

**[00:29:01]** Like consumer websites, like DoorDash, like, you know, like, like travel booking and all

**[00:29:05]** these sites.

**[00:29:06]** I mean, we need better, what is it?

**[00:29:10]** AI agent interfaces?

**[00:29:11]** We don't have time for that.

**[00:29:12]** As it was user interfaces, right?

**[00:29:14]** We need the equivalent for, for, for Claws and agents that they can, that they can talk

**[00:29:18]** to these services.

**[00:29:19]** Right now, you basically have to implement them via browser use or, you know, typically

**[00:29:23]** via browser use and it's super brittle.

**[00:29:26]** Right.

**[00:29:27]** That doesn't work well.

**[00:29:28]** As a security nerd, I'm going to say the security tools.

**[00:29:32]** It's going to be, I mean, so like their integrations with password managers are pretty cool.

**[00:29:35]** Yeah.

**[00:29:35]** And they work like incredibly well.

**[00:29:37]** And it's, it's really funny because, you know, password managers are one of those things

**[00:29:42]** where it's not security best practice, but it's certainly better than what most people

**[00:29:46]** do.

**[00:29:46]** And so it's a net improvement.

**[00:29:48]** Maybe you can't do diet and exercise, but if you can get diet right, maybe that helps.

**[00:29:51]** Um, so as it starts to add these security tools, like you could just have sort of like

**[00:29:57]** these agents that kind of look over your shoulder and make sure you're not doing anything stupid.

**[00:30:01]** Um, these, the, the, the, the frontier models are incredibly good at spotting phishing and

**[00:30:06]** frauds.

**[00:30:07]** And maybe, maybe if you have them working through your email inbox, they can help kind of remove

**[00:30:12]** and flag some of this stuff in a way that the traditional controls don't work.

**[00:30:15]** Um, as you write code or you use services, or maybe you create some sort of infrastructure,

**[00:30:21]** they make sure that you don't over provision.

**[00:30:22]** Right.

**[00:30:23]** So like, I, I can't run Wiz as a, as a home user, but maybe I do need something that probably

**[00:30:28]** makes sure that I don't set their permissions wrong in an S3 bucket.

**[00:30:32]** Um, so stuff like that is like incredibly powerful.

**[00:30:34]** I think like it, it could, but again, I'm on the other side of the distribution on this one.

**[00:30:40]** Would there be an agent specific vault?

**[00:30:43]** I mean, I used to work at HashiCorp, I love vault, the open source tool.

**[00:30:46]** It's so useful.

**[00:30:47]** It's just like, it's generation defining.

**[00:30:50]** So now the question becomes the, you know, the workloads are a little different.

**[00:30:53]** Is there an agent specific vault for open claw of the world?

**[00:30:58]** Um, does that look different?

**[00:30:59]** I mean, I kind of use just one password and one password has lots of flaws, right?

**[00:31:04]** I mean, I'm, I'm currently very happy, unhappy with that security model.

**[00:31:07]** I think I would not necessarily recommend it, but they, they're, they're, they're, you can

**[00:31:12]** basically just create a new vault, get a token, give that to the agent, then the agent

**[00:31:16]** can access everything that's in that particular vault, right?

**[00:31:18]** It doesn't rotate the token, which is what vault could do.

**[00:31:22]** I mean, possibly.

**[00:31:25]** Yes.

**[00:31:25]** Yes.

**[00:31:26]** But the, the problem with rotating.

**[00:31:28]** So let's define token.

**[00:31:30]** The rotating the token to access the vault.

**[00:31:32]** It's not clear to me what that gains necessarily, because, you know, as long as

**[00:31:37]** a breach, right, that would be, it'd be a breach response.

**[00:31:39]** But you can monitor where you get to where the vault is accessed from.

**[00:31:42]** So, okay, maybe, right?

**[00:31:43]** Um, but, but the, I think the, the more important thing would be all the tokens that are in the

**[00:31:47]** vault, I want to rotate, right?

**[00:31:48]** Uh, you know, from time to time, because those, you know, I cannot monitor.

**[00:31:51]** And, but the problem is, those are often consumer sites.

**[00:31:54]** So I didn't consumer sites have zero functionality for rotating, uh, for rotating tokens.

**[00:31:58]** I mean, other than going into some crappy UI and doing it there.

**[00:32:02]** Right.

**[00:32:02]** And so.

**[00:32:02]** I mean, cookies in the browser is a form of token rotation because it updates once in

**[00:32:09]** a while.

**[00:32:10]** And then what a lot of the agents do is like, they take the cookie token and then they refresh

**[00:32:16]** it once in a while to read.

**[00:32:18]** So, I mean, the first.

**[00:32:19]** Very hacky way to do it.

**[00:32:20]** The first sketchy thing my agent did was start looking for cookies.

**[00:32:22]** And I was just like, I didn't ask you to do that.

**[00:32:24]** My agent did ask me.

**[00:32:26]** So when I was trying to place the fails order on DoorDash, it's like, I can't get through

**[00:32:30]** the spot detection thing, but you can give me your username and password.

**[00:32:35]** Not recommended, but that will work.

**[00:32:37]** Why give it a separate account?

**[00:32:39]** Um, I could give it a separate account.

**[00:32:41]** I just need to create it.

**[00:32:42]** And I think, to me, I think that's important that I think in the future agents should have

**[00:32:47]** separate accounts for Absolute.

**[00:32:48]** Right.

**[00:32:49]** They should never share with you because you want to just keep a separate trust domain

**[00:32:52]** there.

**[00:32:53]** Um, you probably want to link the accounts, right.

**[00:32:55]** And it's, um, but, but give them, give them virtual API keys, virtual credit cards, you

**[00:32:59]** know, so something that they, that everything at the end of the day has a layoff and direction

**[00:33:02]** in between that you can want to separate.

**[00:33:04]** Yeah.

**[00:33:05]** Um, my wishlist for OpenClaw is actually more of a multi-threading model.

**[00:33:11]** So today it's very single threaded, which is great for single tasks and you can create

**[00:33:15]** new sessions.

**[00:33:17]** But it kind of breaks when you have like five tasks running in parallel, which is pretty

**[00:33:21]** common for these personal assistant agents.

**[00:33:24]** Um, so for example, like I wanted to do, um, you know, generate the gaming assets on one

**[00:33:30]** thread, but then at the same time I wanted to go code up something, use the coding tools.

**[00:33:35]** When that happens, it actually became really slow or it will switch between the tasks.

**[00:33:40]** So like the context between the sessions actually is not managed perfectly today.

**[00:33:44]** And it's very slow.

**[00:33:46]** I don't know if it's because the models are slow or like, it's just, uh, it, the UI is

**[00:33:51]** just like slower than like, say if I were to use deep.

**[00:33:54]** Yeah, very much.

**[00:33:55]** I mean, it hangs often when I installed it, memory by default was broken.

**[00:34:00]** You know, first time I asked it to use iMessage, it for some reason didn't use the, the, the

**[00:34:06]** blue bubble integration that comes with it, but instead just tried coding something from

**[00:34:09]** scratch.

**[00:34:10]** I love that.

**[00:34:11]** It was like, why are you doing this?

**[00:34:13]** Oh yeah, we could also use a standard integration.

**[00:34:15]** That's probably faster.

**[00:34:16]** I was like, okay, stop and then do that instead.

**[00:34:18]** I do wonder if the build versus by choices from the agents, open claw agents, follow the

**[00:34:25]** distribution of a build versus by choices by the model.

**[00:34:28]** So for example, if you prompt codecs, um, would it choose to build everything or is open

**[00:34:34]** claw choosing to build everything because of some system engineering?

**[00:34:38]** That's a fair point.

**[00:34:40]** We should run a benchmark.

**[00:34:42]** It probably works like a typical enterprise where it's arbitrary.

**[00:34:46]** So like, why'd you build it?

**[00:34:47]** Because we did.

**[00:34:49]** It's coin flip.

**[00:34:50]** Yeah, you have coin flip.

**[00:34:51]** So what's the next set of things you guys plan to experiment on open claw?

**[00:34:56]** I mean, the, and this is the, this is the big thing for, I think a lot of, a lot of IT

**[00:35:00]** organizations and a lot of companies right now is figuring out how do you run these things?

**[00:35:05]** And just like, I remember when I started, I was thinking, oh, well you can run it in a

**[00:35:10]** container, spin something up and load that.

**[00:35:13]** And then it was like, oh, these things write code and they're pretty clever and they can

**[00:35:16]** probably escape containers.

**[00:35:18]** And there's a lot of reasons why you would want to do that.

**[00:35:19]** Maybe it's a VM and sort of looking down that road.

**[00:35:22]** And then it's like, well, you're already, you're already in for a penny.

**[00:35:25]** Might as well go for a pound and just buy a Mac mini.

**[00:35:27]** Right.

**[00:35:27]** And so I think like the, the default motion for this now was sort of like, let's just

**[00:35:32]** run them on Mac minis.

**[00:35:33]** Good luck finding a Mac mini right now.

**[00:35:36]** But, but so like, it's become a dedicated hardware thing.

**[00:35:39]** And then the, so the question ultimately in my mind is like, what is the stack in which

**[00:35:43]** you execute these things look like?

**[00:35:45]** How do you actually bring this to like an employee's desktop without putting your firm

**[00:35:50]** at risk?

**[00:35:50]** Yeah.

**[00:35:51]** You know, that sort of stuff, I think are really difficult unsolved problems.

**[00:35:57]** I'm, I'm still not sure.

**[00:36:01]** I think we're still quite a bit away from this becoming part of my daily sort of

**[00:36:06]** mainline workflow on the fringes.

**[00:36:07]** It can pick up a couple of tasks, but, but to like, say working at Andreessen Horowitz,

**[00:36:11]** right?

**[00:36:12]** What is the point where I would say, just give this access to, you know, our, our, our

**[00:36:17]** pre, pre terms and due diligence folder or something like that, right?

**[00:36:20]** That, that is a pretty big leap.

**[00:36:22]** I think we're pretty far away from that.

**[00:36:23]** I wouldn't find a scope commission.

**[00:36:24]** So I, I could see it getting like with a model.

**[00:36:27]** You described to a point where I forward an email and say, do something, analyze.

**[00:36:30]** I don't know.

**[00:36:30]** Like look, look at the data in here.

**[00:36:32]** But even like, even a simple use case here, like ordering us Boba or our team meeting,

**[00:36:37]** right?

**[00:36:37]** Like, I think it's still not, it's still hard to make that work.

**[00:36:40]** I think within a corporate IT environment in a safe way, unless you do that, dedicated

**[00:36:44]** hardware.

**[00:36:46]** I agree.

**[00:36:47]** And take it.

**[00:36:48]** I mean, a VM.

**[00:36:50]** Do you think, I mean, do you think there's the risk of escape?

**[00:36:53]** VMs are pretty good.

**[00:36:54]** I mean, wouldn't we have a Mac mini inside of our office that just runs the open claw,

**[00:37:00]** but doesn't give it up?

**[00:37:01]** I mean, I think that's what we're going to have.

**[00:37:03]** I think that's exactly what we have.

**[00:37:05]** Yeah.

**[00:37:05]** But Mac, that doesn't scale, right?

**[00:37:07]** You've got, you've got 600 or to a thousand people and it's a sort of like, well, I can't

**[00:37:11]** buy a thousand Mac minis.

**[00:37:13]** Yeah.

**[00:37:14]** Look, I think we can get that with VMs.

**[00:37:16]** I think I'd be like, if you say you have a dedicated host that runs, you know, like

**[00:37:20]** a dozen or so VMs for a dozen employees.

**[00:37:21]** It's like, okay, blast radius is probably okay.

**[00:37:24]** But, but there's still the issue.

**[00:37:26]** What if this downloads the latest integration it found on some open claw, you know, bulletin

**[00:37:30]** boards.

**[00:37:31]** Most of the skills are poisoned.

**[00:37:32]** Yeah, yeah.

**[00:37:32]** Yeah, exactly.

**[00:37:33]** So, so, so, so, so, you know, the, and then you want to restrict the blast radius

**[00:37:37]** somehow, right?

**[00:37:38]** It's like, look, if, so, I mean, what I thought about is, could you do something where,

**[00:37:41]** for example, I give it access to say certain documents or certain emails, right?

**[00:37:46]** And the software has to do it in an explicit way, right?

**[00:37:47]** Maybe I can say my inbox for today, you have access or something like that.

**[00:37:51]** But then every night at midnight, it resets, right?

**[00:37:54]** That would make me feel a little bit better, right?

**[00:37:56]** So somebody can compromise a day worth of stuff.

**[00:37:57]** That's what we do with like Kubernetes, right?

**[00:37:59]** In our container infrastructure.

**[00:38:00]** Yeah, exactly.

**[00:38:01]** Go master, reboot it.

**[00:38:02]** Exactly.

**[00:38:02]** So occasionally, occasionally you just reset state and that sort of makes it a little bit

**[00:38:06]** easier, you know, and then if, if, if you have that plus separate accounts for

**[00:38:09]** everything, I don't think, I don't think it should ever use my account for anything.

**[00:38:13]** Honestly, I think it should be separate.

**[00:38:14]** And it should probably never run locally on your machine.

**[00:38:17]** Intermingle with my laptop.

**[00:38:18]** On your laptop, yeah, yeah.

**[00:38:19]** It's a different trust domain.

**[00:38:20]** Yeah.

**[00:38:21]** Today, I think it's pretty safe for the transient, like crown job, wake up, look at

**[00:38:26]** something, but do not remember it kind of task.

**[00:38:29]** So, for example, like maybe every hour, wake up, look at my calendar, see when I'm busy

**[00:38:35]** or not.

**[00:38:35]** If I'm not going to be home for dinner, tell my husband.

**[00:38:38]** So that would be a use case I'm pretty comfortable with.

**[00:38:42]** So there's actually a lot of, if you look at the app's distribution on usage on your

**[00:38:47]** personal laptop, there's only a couple, like there's Slack.

**[00:38:50]** We talk to each other all the time.

**[00:38:51]** There's email, which is like most of the time is spent on email.

**[00:38:54]** There's like all the coding tools.

**[00:38:56]** That's like something else.

**[00:38:57]** There's calendar.

**[00:38:58]** So if there, you can just streamline certain tasks on email and calendar.

**[00:39:03]** That's actually a huge win for personal assistant.

**[00:39:05]** And there's a long tail of like, I write this thing on Notion.

**[00:39:09]** But, you know, in this case, for the agents, it's just Markdown.

**[00:39:13]** And then you can persist it anywhere.

**[00:39:15]** It doesn't really matter what it looks like.

**[00:39:17]** It is really interesting when I think about what's the future of note-taking will look

**[00:39:22]** like for agents, right?

**[00:39:23]** Today, we kind of default to Markdown, but then there could be stuff that's executable inside

**[00:39:29]** of Markdown.

**[00:39:30]** There could be blocks.

**[00:39:31]** There could be charts.

**[00:39:32]** So Markdown just seems very limiting as a format.

**[00:39:36]** So I do wonder if there's like Markdown++ where agent can have runnable things that it

**[00:39:42]** remembers as part of notes.

**[00:39:44]** I'm sure.

**[00:39:45]** You can do charts in Markdown with Mermaid or like these extensions.

**[00:39:48]** I meant like charts, like hex, like charts.

**[00:39:52]** Oh, I see.

**[00:39:53]** So it's like a, okay.

**[00:39:54]** Like a Jupyter, Notebook, Plus.

**[00:39:55]** You just want Python code.

**[00:39:56]** Exactly.

**[00:39:57]** Like code that's runnable.

**[00:39:58]** And then it's part of the source of truth when you take notes.

**[00:40:01]** Because it's not just words.

**[00:40:02]** It's also programs that you create along the way.

**[00:40:07]** There seems to be a whole trend at the moment of expressing graphs as code.

**[00:40:11]** Yeah.

**[00:40:12]** Putting all of this together, I think what's super fascinating to me is this is one of the

**[00:40:16]** first time we're having technology, but what it can do is not limited by its abilities,

**[00:40:22]** but limited by how I can make it secure and stop it from doing certain things.

**[00:40:26]** Right?

**[00:40:27]** It's like, it's this, we have this, this genie in a bottle.

**[00:40:30]** It's amazing.

**[00:40:30]** But how do I, how I contain this?

**[00:40:32]** Has that ever happened before?

**[00:40:35]** I mean, security has always come at the end.

**[00:40:37]** Like it's never, I think it's just that we've solved, we've solved the coding side of this,

**[00:40:43]** the writing code side, and now it's more of a systems engineering.

**[00:40:46]** These are all fundamentally just systems and architecture problems.

**[00:40:49]** It's not necessarily security issues.

**[00:40:51]** Social engineering to some extent is, but that's, the problem is, is you're bringing up,

**[00:40:56]** you're, you're, you're co-mingling risks across, across different trust domains with this.

**[00:41:00]** So you have, you have the trust and safety and alignment issues with your underlying foundation

**[00:41:05]** models.

**[00:41:05]** You have the systems architecture and execution around how OpenClaw does things on your local

**[00:41:11]** machine.

**[00:41:11]** And then you have the sort of, the, the, the, the traditional hacking sort of, you know,

**[00:41:19]** prompt injection type stuff.

**[00:41:21]** Like people want to do malicious, people want to rob you.

**[00:41:22]** We're not stopping there.

**[00:41:23]** We also have the, the, the insufficiently granular permissions on the services around it, because

**[00:41:29]** even if everything is perfect, you still may not want to have certain information bleed

**[00:41:33]** over.

**[00:41:33]** You have all the sharp edges that are left over from a world that was built for humans.

**[00:41:37]** Yeah.

**[00:41:38]** Right.

**[00:41:38]** Right.

**[00:41:38]** And then, and then so like.

**[00:41:39]** Sharp edges.

**[00:41:41]** It's okay for humans.

**[00:41:43]** Those poor agents need to protect.

**[00:41:44]** Well, you can fire a human, right?

**[00:41:45]** I mean, the agent's like, yeah, YOLO.

**[00:41:48]** If I dare to put it in a two by two in a very VC way.

**[00:41:52]** So there's the low security risk and high security risk.

**[00:41:55]** There's low value tasks and high value tasks.

**[00:41:58]** So what is something that's low security risk, but high value tasks?

**[00:42:03]** Probably the example of emailing your husband that you're going to be late today.

**[00:42:09]** I mean, yeah.

**[00:42:11]** I'd put the cat there too.

**[00:42:13]** Yeah.

**[00:42:15]** Yeah.

**[00:42:17]** And I mean, it's just sort of.

**[00:42:20]** I mean, the issues with these things is always the escalation of privileges and the escape

**[00:42:25]** out of the environment they're in.

**[00:42:26]** And so you can see where these things would jump into doing something that's actually high risk.

**[00:42:31]** I mean, I think one category that I would put in there is you can just use something like

**[00:42:35]** openclaw is a really smart UI to your LLM in a sense, right?

**[00:42:39]** And basically say, let's forget memory, forget state.

**[00:42:42]** Give it a task.

**[00:42:42]** When the task is done, it resets all state, right?

**[00:42:44]** That makes it a lot more secure.

**[00:42:46]** So right now, let's assume I have a PDF in an email and I'd like for an LLM to look at a PDF.

**[00:42:53]** It's still kind of cumbersome.

**[00:42:54]** I have to save this thing, right?

**[00:42:55]** And then go to the LLM and import it and do the analysis and then export and so on.

**[00:42:59]** Just being able to say like, hey, hey, claw, look at this thing.

**[00:43:02]** Give me this analysis.

**[00:43:03]** Right?

**[00:43:03]** And back comes an email with this data.

**[00:43:05]** And afterwards, the claw discards every state, right?

**[00:43:07]** I think that we can get to pretty quick.

**[00:43:09]** Oh, I'm excited to use openclaw for my taxes.

**[00:43:11]** Yeah.

**[00:43:12]** Oh, there you go.

**[00:43:15]** Good luck.

**[00:43:17]** For a company.

**[00:43:18]** I'm biting on my tongue.

**[00:43:20]** If we don't tell this to the IRS, then.

**[00:43:22]** Yeah, man.

**[00:43:23]** The IRS is running openclaw to review other taxes.

**[00:43:27]** You never know.

**[00:43:28]** What is something that's for a company, not on a personal setting?

**[00:43:31]** High security risk, but very high value.

**[00:43:35]** Like you want to automate it yesterday using an openclaw, but it's risky.

**[00:43:40]** Taxes.

**[00:43:41]** Anything financial.

**[00:43:43]** For a company.

**[00:43:43]** Anything.

**[00:43:44]** But accounts payable.

**[00:43:45]** Like accounts payable, vendor review, like third party assessments.

**[00:43:48]** Like all this stuff where we have actual humans that spend a tremendous amount of time validating that the vendor exists.

**[00:43:55]** Making sure the instructions for payment are correct.

**[00:43:57]** Making sure it's the right PO and not someone doing some sort of social engineering attack.

**[00:44:02]** Make, there's just like a whole lot of stuff around vendor management.

**[00:44:05]** I think in the enterprise where these solutions could really sort of increase a lot of efficiency.

**[00:44:12]** But if they go sideways, you start writing checks to the wrong people.

**[00:44:16]** Can we take it up a notch by, you know, maybe working with Bitcoin instead of that?

**[00:44:20]** Yeah, exactly.

**[00:44:20]** And there's no recourse.

**[00:44:21]** And I think we've maxed the risk.

**[00:44:24]** So what's your advice for the corporation managers and executives who are open cloud curious?

**[00:44:34]** Joel, have a best advice.

**[00:44:35]** I think this is one of those things where like, I mean, I'm a profound believer that if you don't feel uncomfortable, you're not growing.

**[00:44:41]** And this is one of those times when you're going to feel very uncomfortable, but you need to lean into this.

**[00:44:45]** And I think, I think to Guido's point and to like, I think a lot of the points we've made is like,

**[00:44:50]** I can't see these as doing anything other than creating a lot more jobs.

**[00:44:53]** Like there's just so much more stuff that needs to get built, needs to get managed.

**[00:44:57]** And it's like, if you want to be part of that wave, you got to lean into it.

**[00:45:00]** And it's the same thing happened with cloud, right?

**[00:45:03]** When cloud came around, I remember sitting in my big corporate job thinking half of these people will be gone five years.

**[00:45:10]** Infrastructure will just become commodity service extracted away and we won't have tech people.

**[00:45:13]** And then lo and behold, 10 years later, 20 years later, like the IT organizations are bigger than they were then.

**[00:45:19]** And they're spending even more money.

**[00:45:20]** And so like, I just think that there's just so much opportunity with this stuff that you just have to lean into it and you have to get comfortable with being uncomfortable and try to take smart risks.

**[00:45:31]** I think actually a good analogy is the early days of web and the internet.

**[00:45:34]** But back in those days, some companies, they banned the web browser, right?

**[00:45:37]** It's like, oh, the web browser is insecure.

**[00:45:39]** It's like, well, yes, it is insecure, but missing out on the internet revolution was a far larger risk, right?

**[00:45:44]** And you get barnes and nobled if you're not careful.

**[00:45:47]** I mean, Citigroup's first cloud security policy was thou shall not use cloud services.

**[00:45:54]** And now look at it, right?

**[00:45:55]** Like, I think it's the same thing.

**[00:45:57]** It's just these waves are always somewhat identical.

**[00:45:59]** Trying to ignore this new technology and waiting for it to go away usually doesn't work.

**[00:46:02]** If you want to retire, that's a great strategy.

**[00:46:04]** Yeah, there we go.

**[00:46:40]** Thanks again for listening.

**[00:46:47]** Please note that A16Z and its affiliates may also maintain investments in the companies discussed in this podcast.

**[00:46:52]** For more details, including a link to our investments, please see a16z.com forward slash disclosures.

**[00:47:01]** Thanks for listening.

**[00:47:02]** Thanks for listening.

**[00:47:02]** Thanks for listening.

**[00:47:06]** Thanks for listening.

**[00:47:06]** Thanks for listening.

**[00:47:06]** Thanks for listening.

**[00:47:07]** Thanks for listening.

**[00:47:07]** Thanks for listening.

**[00:47:08]** Thanks for listening.

**[00:47:08]** Thanks for listening.

**[00:47:09]** Thanks for listening.

**[00:47:10]** Thanks for listening.

**[00:47:10]** Thanks for listening.

## My Notes

> ✍️ Write your thoughts here...
