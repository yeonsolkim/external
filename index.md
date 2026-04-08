---
layout: default
title: Abstraction
---
{% assign parent_categories = "English,Mathematics,Physics" | split: "," %}

{% for parent in parent_categories %}
  <section style="margin-bottom: 40px;">
    <h2 style="color: #000; padding-bottom: 10px; border-bottom: 2px solid #159957;">
      {{ parent }}
    </h2>

    {% comment %} 1. 해당 대분류에 속하는 포스트만 필터링 {% endcomment %}
    {% assign posts = site.categories[parent] %}
    
    {% comment %} 2. 소분류(두 번째 카테고리)들을 중복 없이 추출 {% endcomment %}
    {% assign sub_cats = "" | split: "" %}
    {% for post in posts %}
      {% assign current_sub = post.categories[1] | default: "General" %}
      {% unless sub_cats contains current_sub %}
        {% assign sub_cats = sub_cats | push: current_sub %}
      {% endunless %}
    {% endfor %}
    {% assign sub_cats = sub_cats | sort %}

    {% comment %} 3. 소분류별로 루프를 돌며 포스트 출력 {% endcomment %}
    {% for sub in sub_cats %}
      <div style="margin-left: 20px; margin-top: 25px;">
        <h3 style="color: #444; font-size: 1.1rem; border-left: 4px solid #eee; padding-left: 12px; margin-bottom: 15px;">
          {{ sub | split: " " | map: "capitalize" | join: " " }}
        </h3>
        
        <ul class="custom-list">
          {% for post in posts %}
            {% assign post_sub = post.categories[1] | default: "General" %}
            {% if post_sub == sub %}
              <li>
                <a href="{{ site.baseurl }}{{ post.url }}" style="text-decoration: none; color: #159957; font-weight: 500;">
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