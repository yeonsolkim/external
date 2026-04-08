---
layout: default
title: Abstraction
---

### Categories

{% assign postsByCustom = site.posts | group_by: "categories" %}

{% for category in postsByCustom %}
  <h2 style="padding-bottom: 5px; margin-top: 40px;">
    {{ category.name | capitalize }}
  </h2>
    {% for post in category.items %}
      <li>
        <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a> 
        <span style="color: #999; font-size: 0.9em;">- {{ post.date | date: "%B %d, %Y" }}</span>
      </li>
    {% endfor %}
{% endfor %}