---
layout: page
permalink: /teaching/
title: Teaching
description: Courses, trainings, and supervision activities across systems, cloud, DevOps, and applied computing.
nav: false
nav_order: 6
---

{% assign teaching_section = site.data.cv | where: "title", "Teaching Experience" | first %}
{% assign supervision_section = site.data.cv | where: "title", "Supervision Activities" | first %}

<div class="teaching-hero">
  <p class="home-kicker">Teaching and mentoring</p>
  <p class="home-lead">
    I teach systems, cloud, middleware, and DevOps topics with a practical orientation, and I also
    supervise applied student work in smart energy and data-driven systems.
  </p>

  <div class="teaching-stats">
    <div class="teaching-stat">
      <span class="teaching-stat-value">{{ teaching_section.contents | size }}</span>
      <span class="teaching-stat-label">courses and trainings</span>
    </div>
    <div class="teaching-stat">
      <span class="teaching-stat-value">{{ supervision_section.contents | size }}</span>
      <span class="teaching-stat-label">supervision projects</span>
    </div>
    <div class="teaching-stat">
      <span class="teaching-stat-value">2017-present</span>
      <span class="teaching-stat-label">teaching period</span>
    </div>
  </div>

  <div class="focus-tags">
    <span>Operating Systems</span>
    <span>Cloud Computing</span>
    <span>Middleware</span>
    <span>DevOps</span>
    <span>Signal Processing</span>
    <span>Applied Supervision</span>
  </div>
</div>

## Teaching Experience

<div class="teaching-grid">
  {% for item in teaching_section.contents %}
    <article class="teaching-card">
      <div class="teaching-card-top">
        {% if item.period %}
          <span class="teaching-badge">{{ item.period }}</span>
        {% endif %}
        {% if item.level %}
          <span class="teaching-badge subtle">{{ item.level }}</span>
        {% endif %}
      </div>

      <h3>{{ item.title }}</h3>
      <p class="teaching-card-meta">{{ item.institution }}</p>

      <div class="teaching-card-notes">
        {% if item.responsible %}
          <p><strong>Responsible:</strong> {{ item.responsible }}</p>
        {% endif %}
        {% if item.duration %}
          <p><strong>Duration:</strong> {{ item.duration }}</p>
        {% endif %}
      </div>

      <p>{{ item.description }}</p>
    </article>
  {% endfor %}
</div>

## Supervision Activities

<div class="teaching-grid supervision-grid">
  {% for item in supervision_section.contents %}
    {% if item.student %}
      {% assign student_names = item.student %}
    {% elsif item.students %}
      {% assign student_names = item.students | join: ", " %}
    {% else %}
      {% assign student_names = "" %}
    {% endif %}

    <article class="teaching-card supervision-card">
      <div class="teaching-card-top">
        {% if item.year %}
          <span class="teaching-badge">{{ item.year }}</span>
        {% endif %}
        {% if item.type %}
          <span class="teaching-badge subtle">{{ item.type }}</span>
        {% endif %}
      </div>

      <h3>{{ item.title }}</h3>
      <p class="teaching-card-meta">{{ item.institution }}</p>

      <div class="teaching-card-notes">
        {% if student_names != "" %}
          <p><strong>Student{% if item.students %}s{% endif %}:</strong> {{ student_names }}</p>
        {% endif %}
        {% if item.responsible %}
          <p><strong>Supervisor:</strong> {{ item.responsible }}</p>
        {% endif %}
      </div>
    </article>
  {% endfor %}
</div>
