---
layout: default
title: Abstraction
---

<h1 style="color: #333;">Categories</h1>

{% assign postsByCustom = site.posts | group_by: "categories" %}

{% for category in postsByCustom %}
  {% assign category_name = category.name | replace: '[', '' | replace: ']', '' | replace: '"', '' %}
  
  <h3 style="color: #333; padding-bottom: 5px; margin-top: 40px;">
    {{ category_name | capitalize }}
  </h3>
  <hr>
  <ul class="custom-list">
    {% for post in category.items %}
      <li>
        <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a> 
        <span style="color: #999; font-size: 0.85em;">- {{ post.date | date: "%B %d, %Y" }}</span>
      </li>
    {% endfor %}
  </ul>
{% endfor %}

<style>
  .custom-list {
    list-style-type: disc; 
    padding-left: 20px;
    margin-top: 10px;
  }

  .custom-list li {
    margin-bottom: 8px;
    font-size: 1.05rem;
  }

  .custom-list li::marker {
    font-size: 0.8em; 
    color: #666;    
  }
</style>