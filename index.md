---
layout: default
title: Abstraction
---

{% assign parent_categories = "English,Mathematics,Physics" | split: "," %}

{% for parent in parent_categories %}
  <section style="margin-bottom: 40px;">
    <h2 style="color: #000; padding-bottom: 10px;">
      {{ parent }}
    </h2>
    <hr>

    {% comment %} 1. 소분류(두 번째 카테고리) 목록 추출 (더 확실한 방식) {% endcomment %}
    {% assign sub_cats = "" | split: "" %}
    {% for post in site.posts %}
      {% if post.categories contains parent %}
        {% assign current_sub = post.categories[1] | default: "General" %}
        {% unless sub_cats contains current_sub %}
          {% assign sub_cats = sub_cats | push: current_sub %}
        {% endunless %}
      {% endif %}
    {% endfor %}
    {% assign sub_cats = sub_cats | sort %}

    {% comment %} 2. 추출된 소분류 순회하며 포스트 출력 {% endcomment %}
    {% for sub in sub_cats %}
      <div style="margin-left: 20px; margin-top: 25px;">
        <h3 style="color: #444; font-size: 1.1rem; border-left: 4px solid #eee; padding-left: 12px; margin-bottom: 15px;">
          {{ sub | split: " " | map: "capitalize" | join: " " }}
        </h3>
        
        <ul class="custom-list">
          {% for post in site.posts %}
            {% comment %} 대분류와 소분류가 모두 일치하는지 확인 {% endcomment %}
            {% if post.categories[0] == parent and post.categories[1] == sub %}
              <li>
                <a href="{{ site.baseurl }}{{ post.url }}" style="text-decoration: none; color: #159957; font-weight: 500;">
                  {{ post.title }}
                </a>
                <span style="color: #999; font-size: 0.85em; margin-left: 8px;">
                  - {{ post.date | date: "%B %d, %Y" }}
                </span>
              </li>
            {% elsif post.categories[0] == parent and sub == "General" and post.categories.size == 1 %}
              {% comment %} 소분류가 없는 General 케이스 처리 {% endcomment %}
              <li>
                <a href="{{ site.baseurl }}{{ post.url }}" style="text-decoration: none; color: #929292; font-weight: 500;">
                  {{ post.title }}
                </a>
                <span style="color: #999; font-size: 0.85em; margin-left: 8px;">
                  - {{ post.date | date: "%B %d, %Y" }}
                </span>
              </li>
            {% endif %}
          {% endfor %}
        </ul>
      </div>
    {% endfor %}
  </section>
{% endfor %}

<style>
  .custom-list { list-style-type: disc !important; padding-left: 20px; margin-left: 10px; }
  .custom-list li::marker { color: #00000064; font-size: 0.7em; }
  .custom-list li { margin-bottom: 10px; }
  .custom-list li a:hover { text-decoration: underline; }
</style>