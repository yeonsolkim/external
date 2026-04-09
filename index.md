---
layout: default
title: Abstraction
---

{% assign parent_categories = "English,Mathematics,Physics" | split: "," %}

{% for parent in parent_categories %}
  <section style="margin-bottom: 40px;">
    <h2 style="color: #000; padding-bottom: 10px; border-bottom: 2px solid #eee;">
      {{ parent }}
    </h2>

    {% comment %} 1. 해당 대분류에 속하는 모든 소분류 추출 {% endcomment %}
    {% assign sub_cats = "" | split: "" %}
    {% for post in site.posts %}
      {% if post.categories contains parent %}
        {% assign current_sub = post.categories[1] | default: "General" %}
        {% unless sub_cats contains current_sub %}
          {% assign sub_cats = sub_cats | push: current_sub %}
        {% endunless %}
      {% endif %}
    {% endfor %}
    
    {% comment %} 2. 소분류를 이름순(숫자순)으로 정렬 {% endcomment %}
    {% assign sub_cats = sub_cats | sort %}

    {% comment %} 3. 정렬된 소분류 순회하며 포스트 출력 {% endcomment %}
    {% for sub in sub_cats %}
      <div style="margin-left: 20px; margin-top: 25px;">
        <h3 style="color: #444; font-size: 1.1rem; border-left: 4px solid #0000001a; padding-left: 12px; margin-bottom: 15px;">
          {{ sub }}
        </h3>
        
        <ul class="custom-list">
          {% for post in site.posts %}
            {% comment %} 대분류와 소분류가 모두 일치하는 포스트만 출력 {% endcomment %}
            {% assign p_sub = post.categories[1] | default: "General" %}
            {% if post.categories[0] == parent and p_sub == sub %}
              <li>
                <a href="{{ site.baseurl }}{{ post.url }}" style="text-decoration: none; color: #555; font-weight: 500;">
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
  .custom-list li a:hover { text-decoration: underline; color: #000 !important; }
</style>