---
layout: post
title: "Seeing the problem was the easy part"
date: 2026-10-17 00:05:00 +0200
description: What we learned from making an edge-to-cloud video pipeline report its own health, and why seeing a backlog is not the same as knowing how to fix it.
tags: edge-to-cloud observability self-healing resilience research
categories: research
---

Near the end of our busiest run, a tiger walks past a camera. The motion detector next to it sees something move and forwards the frame to the object recognizer. The recognizer will find the tiger. It just won't get to that frame for another 25 minutes.

The recognizer is working the whole time. It's answering frames that arrived long before the tiger, and every new frame joins the back of the line.

In my [last post](/blog/2026/the-fix-that-makes-edge-failures-worse/), I described a tracker that fell behind while its health checks stayed green, and promised to write about what we learned working on these problems at IMT Atlantique. This is the first half: getting the application to say what's wrong. The second half, getting the system to do the right thing about it, is still in progress.

## A tiger, not an earthquake

Our use case was less dramatic than an earthquake. It was a video surveillance system that watches for dangerous animals and alerts residents and authorities when one shows up.

Each camera sends its frames to its own motion detector at the edge, and the three detectors send the frames where something moved to one object recognizer. In our runs, the recognizer ran in the cloud. It doesn't have to: it can also run on the edge, next to the detectors. That choice comes back later.

The [application is open source](https://gitlab.inria.fr/STACK-RESEARCH-GROUP/software/edge-to-cloud-video-processing). We ran it on Grid'5000 virtual machines with K3s. Camera nodes had 1 CPU and 1 GB of memory, edge nodes 4 CPUs and 8 GB, and cloud nodes 8 CPUs and 16 GB.

## What the platform sees, and what matters

Out of the box, Kubernetes tells you about containers: CPU, memory, network, whether the process is up. Those are the numbers an autoscaler acts on. But when a tiger walks past a camera, how long until someone gets the alert? None of them can tell you.

Only the application knows that. So the developers instrument it with OpenTelemetry: frame rate, processing time, detection accuracy, how many frames each motion detector forwards. Those go to Prometheus, next to the infrastructure metrics.

The developer also writes one configuration file for the feedback loop. It says what the objectives are, for example a maximum processing time, and which metrics measure them. It says which services depend on which. And it lists what can be done when something goes wrong: lower the frame rate, switch to a lighter model, or scale a service.

The loop reads the metrics and checks the objectives. When one is missed, it tries to work out which component is responsible and picks an action from that list. To test it, Chaos Mesh injects faults like network latency and CPU pressure.

## What the metrics showed

The most useful experiment was also the simplest. We generated footage where animals appear at a controlled rate, a number of expected appearances per hour for each camera, and watched the object recognizer.

{% include figures/ucc-backlog.html %}

With all three cameras at 30 appearances per hour, the recognizer's response time climbs for the whole run. It ends at about 25 minutes and never comes back down. In the paper's plots it rises in steps, each time the motion detectors forward a new batch of frames. Even at 5 appearances per hour, it climbed to about 12 minutes before the backlog drained.

That's the first part of the last post's story, measured: a service that is working, and falling further behind. Frames with motion arrive faster than the recognizer can answer them, and each new one waits behind all the others. Every cat that crosses a camera is motion too, and it waits in the same line as the tiger. These runs measured the backlog. They didn't test what to do about it.

## So what should the system do?

Seeing the backlog is one thing. Choosing the fix is another, and the right one depends on where the recognizer can run.

The animation below plays out how the loop could respond as conditions change. It's an illustration of the options, not something we measured.

{% include figures/ucc-pipeline.html %}

If the site is connected, the obvious fix is the cloud. Send the frames there and add recognizer replicas until they keep up. The cloud has machines to spare, so this is the case where scaling works. It costs bandwidth and money, and every frame pays the trip over the network.

Sometimes the link is up but slow. Then more replicas don't help, and neither does a lighter model: the frames spend their time on the network, not in the recognizer. What helps is sending less over the link, which means fewer frames.

Now take the earthquake from the last post. The link to the cloud is damaged or gone, and the recognizer has to run on the edge, next to the detectors. There's no spare machine to add a replica to, and, as in the last post's thought experiment, a second copy on the same device can make things worse. What's left is to do less work per frame, look at fewer frames, or both. A lighter model answers faster, but it gets more wrong: it may take a cat for a tiger and wake people for nothing, or take the tiger for a cat and say nothing. A lower frame rate sends fewer frames to the recognizer, but a tiger that walks past between two frames is never seen.

Each of these fixes costs something different: money, bandwidth, accuracy, or frames nobody looks at. Which cost is acceptable isn't in any metric. It depends on whether the cloud is reachable right now and how fast the link is, and on how much detection the people relying on the alert can afford to lose. The developer knows that. The platform doesn't.

## What we learned

The first lesson is that the metric that explained the problem came from the developer. Response time moved with how many frames the edge forwards, and that depends on how much moves in front of the cameras. No infrastructure metric measures that. Someone who knows the application had to decide it was worth counting.

The second is that the loop should read the application's needs from a file, not have them built in. Objectives, dependencies and actions all live in that file, and the metrics the loop watches can change while the system runs, without touching code. When the application changes, you change the file, not the loop.

The third is the one I'd put first: seeing was the easy part. The metrics showed the backlog clearly. Deciding what to do about it depends on things the metrics don't say: where the recognizer can run, whether the cloud is reachable and how fast, which fixes are even possible right now, and what each one costs in missed detections. The configuration file can list the fixes. Choosing between them automatically, at the right moment, is the hard part, and it was left for later work.

That's also why I'd call these results preliminary, as the [paper](https://dl.acm.org/doi/10.1145/3773274.3774855) does. They come from one application on a handful of virtual machines. They show what the loop can observe, not that it keeps the objectives.

## What comes next

Remember the questions from the last post? This work answers part of the first one: with the right metrics, you can see the problem. It doesn't answer the harder half. Which part of the pipeline is to blame, and which part is only showing the symptom? And it raises the others more sharply. When the cloud is there, is scaling the right call? When it isn't, which fix do you use, and in what order? When do you undo it? And how do you compare a fix that costs money with one that costs missed detections?

Those are the questions I've been working on since, and I'll write about them once the results are out.

The paper is [Application-level observability for adaptive Edge to Cloud continuum systems](https://dl.acm.org/doi/10.1145/3773274.3774855), UCC '25, with a [preprint on arXiv](https://arxiv.org/abs/2601.14923).

In the meantime, I'm curious about the other side. If you've run something like this at the edge, how did you decide what to give up when it couldn't keep up? I'd really like to hear about it.
