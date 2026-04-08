---
layout: default
title: Abstraction
---

# **Categories**

{% assign postsByCustom = site.posts | group_by: "categories" %}

{% for category in postsByCustom %}
  {% assign category_name = category.name | replace: '[', '' | replace: ']', '' | replace: '"', '' %}
  
  <h3 style="color: #000; padding-bottom: 5px; margin-top: 40px;">
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
  /* 3. Unordered list의 심볼을 작은 점으로 설정 */
  .custom-list {
    list-style-type: disc; /* 기본 점 모양 */
    padding-left: 20px;
    margin-top: 10px;
  }

  .custom-list li {
    margin-bottom: 8px;
    font-size: 1.05rem;
  }

  /* 점의 크기를 더 미세하게 조정하고 싶을 때 */
  .custom-list li::marker {
    font-size: 0.8em; /* 점 크기를 글자보다 약간 작게 */
    color: #666;    /* 점 색상을 살짝 연하게 */
  }
</style>