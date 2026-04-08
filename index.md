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
    {% comment %} 해당 부모 카테고리에 속한 모든 포스트 가져오기 {% endcomment %}
    {% assign posts = site.categories[parent] %}

    {% comment %} 1. 소분류들만 따로 모으기 (String 형태로 변환하여 처리) {% endcomment %}
    {% capture sub_string %}{% for post in posts %}{{ post.categories[1] | default: "General" }}|{% endfor %}{% endcapture %}
    {% assign sub_cats = sub_string | split: "|" | uniq | sort %}

    {% comment %} 2. 추출된 소분류 순회 {% endcomment %}
    {% for sub in sub_cats %}
      {% if sub == "" %}{% continue %}{% endif %}
      
      <div style="margin-left: 20px; margin-top: 25px;">
        <h3 style="color: #444; font-size: 1.1rem; border-left: 4px solid #eee; padding-left: 12px; margin-bottom: 15px;">
          {% comment %} Title Case 적용: 1. grammatical meaning -> 1. Grammatical Meaning {% endcomment %}
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