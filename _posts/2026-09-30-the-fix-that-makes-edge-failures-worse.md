---
layout: post
title: "The fix that makes edge failures worse"
date: 2026-09-30 09:00:00
description: When restarting or scaling is not an option, how do you deploy critical data-processing and decision-making apps at the edge and keep them from failing?
tags: edge-to-cloud urgent-computing self-healing resilience research
categories: research
---

When an application starts falling behind, the platform usually does one of two things: it adds another copy of the service, or it restarts it. In a data center, that works most of the time. I want to talk about the cases where it doesn't.

Imagine the minutes after an earthquake. The link to the cloud is damaged, and people are leaving buildings that may not hold. Cameras across the district stream video to the one edge device still running nearby. On it, a tracking service detects people, follows them from one camera to the next and works out which way they went, so rescuers know where to look for the ones who didn't make it out.

Suddenly every camera in the area matters. The tracker can't keep up, and frames start to pile up. Its health checks are still green.

The autoscaler sees CPU climbing and adds a second copy of the tracker. There's nowhere else to put it, so it goes on the same device and eats CPU and memory the first copy needed. The cameras now get split between the two copies. Each one keeps its own memory of who it is following, so each sees only part of the path, and neither can say which way people went.

Then the device runs out of memory. The tracker gets killed and restarted, and since everything it knew lived inside the process, it comes back with no idea who it was following or where they were last seen.

Nothing had crashed at the start. The tracker was working, just too slowly, and every automatic fix made things worse.

<div class="row justify-content-center mt-3 mb-3">
  <div class="col-sm-10 col-md-8">
    {% include figure.liquid loading="eager" path="assets/img/edge-failure-timeline.png" class="img-fluid rounded z-depth-1" alt="Timeline of the scenario: at T+00:00 every camera streams to one edge device; at T+00:30 the tracker falls behind; at T+00:45 the autoscaler adds a copy on the same device; at T+01:00 the cameras are split and each copy sees half the path; at T+01:15 the device runs out of memory and the tracker is restarted; at T+01:20 it no longer knows who it was following. The health status reads OK at every step except the out-of-memory kill, and is back to OK after the restart." %}
  </div>
</div>

To be clear, this is a thought experiment, not something I measured. It assumes a simple tracker that keeps its state in memory and a single edge device. A tracker built to share or save its state would lose less. But both assumptions are common at the edge, and the platform has no way of knowing which kind of service it's dealing with.

The same story works after a flood or a wildfire, or during an attack on a public place. Any time software has to follow people through a camera network while everything around it falls apart.

## Why this is hard at the edge

In an emergency, these applications run close to where the data is produced: pipelines that turn camera and sensor streams into something useful, and decision apps that raise an alert, send a team or warn people within seconds. Earthquake early warning has to reach people within seconds to minutes. After a disaster, a few seconds can decide whether rescuers find someone in time.

And they run under the worst conditions you could design. The devices are small, sometimes on battery. The network is saturated, unstable, or partly destroyed. Every sensor in the area becomes important at the same moment, and there is nobody on site to open a dashboard and figure out what went wrong.

That's where the usual self-healing runs out. Kubernetes restarts crashed containers by default, and its autoscaler adds copies once you configure it. But scaling needs spare capacity, and at the edge there may be none. A restart throws away whatever the service had in memory. And many edge failures aren't crashes at all: the process is healthy, but the link is saturated, the model is too slow for the hardware, or input arrives faster than the pipeline can handle.

There's also a problem people tend to forget: you can't start a container without its image. Pulling the image is already the slowest part of starting a container in normal conditions. [One study](https://www.usenix.org/conference/fast16/technical-sessions/presentation/harter) put it at 76% of startup time. Images that bundle an AI model are big. If the image isn't already cached somewhere near the event, the device has to fetch it over the same broken link, and that can take minutes nobody has.

Scaling isn't always the wrong answer, though. When a service simply stops, starting a fresh copy is fast and works well. The hard part is telling which kind of failure you're looking at.

## What others have done

None of this is new, and a lot of people have worked on parts of it.

On the orchestrator side, [KEDA](https://keda.sh/) lets Kubernetes scale on queue length or event rates instead of CPU, which is a better signal, although the only action is still adding or removing copies. [KubeEdge](https://kubeedge.io/) keeps edge nodes and their apps running when the link to the cloud drops. For images, [Dragonfly](https://d7y.io/) lets nodes share image layers peer to peer, and research on the edge has gone further with [collaborative lazy pulling](https://dl.acm.org/doi/10.1109/TNSM.2024.3462408), which starts a container before the whole image has arrived, and [adaptive image placement across the cloud-edge continuum](https://arxiv.org/html/2407.12605v2). All of these still assume the image, or part of it, is somewhere nearby.

Several teams have built self-adaptive loops around Kubernetes, for example to [decide between scaling and offloading AI tasks across edge devices](https://arxiv.org/abs/2604.13542). [CODECO](https://arxiv.org/html/2511.08354) and [QONNECT](https://arxiv.org/pdf/2510.09851) take application-level quality of service into account when placing workloads. Most of this work still acts on the infrastructure, meaning where things run and with how many resources. The closest thing I've found to what I care about is [BumbleBee](https://www.microsoft.com/en-us/research/wp-content/uploads/2022/04/main.pdf) from Microsoft Research, which lets developers attach their own adaptation logic to a container so the orchestrator can use it.

On the application side, many systems adapt themselves. [Spatula](https://www.microsoft.com/en-us/research/publication/spatula-efficient-cross-camera-video-analytics-on-large-camera-networks/) tracks people across cameras by only processing the cameras where they're likely to show up next. [Distream](https://dl.acm.org/doi/10.1145/3384419.3430721) shifts video analytics work between cameras and the edge as load changes. Chameleon and AWStream lower resolution or frame rate to fit the resources available. The catch is that this logic lives inside each application, and the orchestrator doesn't know it exists.

Connecting the two is where a lot of current research is. Rainbow did it early on at the architecture level. More recently there's been a wave of work on cloud microservices that goes from diagnosis to action automatically, often with LLM agents, and benchmarks like [MicroRemed](https://arxiv.org/pdf/2511.01166) that measure how well it works. I've seen much less of it at the edge, where a pipeline spans several tiers, resources are tight and nobody is around to decide.

## The questions I'm left with

The first is diagnosis. When the whole pipeline slows down, how does the system figure out which part is actually to blame, and not just which part shows the symptom? And can it do that without training data, when no two emergencies look alike?

Then what to do about it. If restarting and scaling are off the table, what else is there? Developers usually know better fixes: compress the video, lower the resolution, switch to a lighter model, skip an optional step. I still don't think we have a good way to hand that knowledge to an automatic system. Should an application be allowed to degrade itself on purpose to keep delivering results? If so, who decides what's acceptable to lose?

When several fixes are possible, which one goes first? Fixed rules written by a person, or a system that learns from past incidents? And once a fix has worked, when do you undo it?

There's deployment too. What should be decided in advance and what should be left to runtime? Which images should already be sitting near places where a disaster could happen, and with the little storage edge devices have, which ones do you leave out?

Last, evaluation. Scaling is sometimes the right call, so how do you make sure a system still picks it when it should? And how do you build a fair test between infrastructure fixes and application-level fixes, one that doesn't quietly favor the approach you're hoping will win?

## Where this comes from

I worked on these questions as an R&D engineer at IMT Atlantique, on [feedback mechanisms for edge-to-cloud applications](/blog/2023/new-poste/). We built video-processing pipelines across edge and cloud, instrumented them, and pushed them until they broke on Grid'5000. Part of that work is in our UCC '25 paper, [Application-level observability for adaptive Edge to Cloud continuum systems](https://dl.acm.org/doi/10.1145/3773274.3774855) (there's also a [preprint on arXiv](https://arxiv.org/abs/2601.14923)).

I'll write about what we learned in another post. If you've run critical services at the edge and had to keep them alive without being able to restart or scale, I'd really like to hear how you did it.
