---
layout: page
title: R&D Engineer at IMT Atlantique
description: Feedback mechanisms for Edge-to-Cloud applications
img: assets/img/img_2.png

importance: 2
category: work
---

During a one-year project at **STACK Team - IMT Atlantique**, I worked as a **Research and Development Engineer** on feedback mechanisms for **Edge-to-Cloud applications**,  
**under the supervision of Daniel Balouek and Baptiste Jonglez**.

This project was carried out in collaboration with **INRIA** and deployed entirely on the large-scale experimentation platform **[Grid'5000](https://www.grid5000.fr)**.  
It focused on designing, implementing, and evaluating adaptive systems capable of reacting to runtime changes through feedback loops.

---

### ⚙️ Technical Scope

Over the course of the project, I worked with a wide range of tools and technologies, covering the full edge-to-cloud lifecycle:

- **Containerization & Orchestration**:  
  - Docker  
  - k3s / Kubernetes  

- **Monitoring & Observability**:  
  - Prometheus (metrics collection)  
  - Grafana (dashboards)  
  - OpenTelemetry (instrumentation)  
  - Zipkin / Jaeger (distributed tracing)  

- **Chaos Engineering & Testing**:  
  - **Chaos Mesh** (fault injection and resilience testing)  

- **Infrastructure & Deployment**:  
  - Helm charts  
  - CI/CD workflows  
  - YAML-based configuration for microservices  

---

### 💡 Use Case Development

As part of this work, I developed a fully functional use case illustrating feedback mechanisms across edge and cloud environments.  
The full project is **publicly available on INRIA’s GitLab**:  
👉 [INRIA GitLab – edge-to-cloud-video-processing](https://gitlab.inria.fr/STACK-RESEARCH-GROUP/software/edge-to-cloud-video-processing)

This use case includes:
- A **motion detection module** at the edge
- An **object recognition module** in the cloud using a YOLO model
- Instrumentation and monitoring of components to track latency, throughput, and resource usage
- Feedback mechanisms to react to SLO violations (e.g., frame skipping, resource reallocation)

---

### 🎯 Outcome

This project allowed me to:
- Design adaptive edge-to-cloud systems from scratch
- Integrate modern observability and chaos engineering practices
- Use **Grid'5000** for reproducible experiments at scale
- Collaborate in an academic research environment with real-world constraints

It was a rich and rewarding experience combining **distributed systems**, **cloud-native engineering**, and **research-driven software development**.
