---
layout: default
title: Abstraction
---

{% comment %} 1. 모든 카테고리를 중복 없이 추출하여 부모 카테고리 리스트 생성 {% endcomment %}
{% assign parent_categories = "English,Math,Physics" | split: "," %}

{% for parent in parent_categories %}
  <section style="margin-bottom: 50px;">
    <h2 style="color: #000; padding-bottom: 10px;">
      {{ parent }}
    </h2>
    <hr>
    {% comment %} 2. 해당 부모 카테고리에 속한 글들을 가져와서 자식 카테고리로 그룹화 {% endcomment %}
    {% assign posts = site.categories[parent] %}
    {% assign grouped_sub = posts | group_by: "categories" %}

    {% for group in grouped_sub %}
      {% comment %} 3. 부모 카테고리 이름 자체를 제외한 나머지(자식) 이름만 추출 {% endcomment %}
      {% assign sub_name = group.name | replace: parent, "" | replace: '[', '' | replace: ']', '' | replace: '"', '' | replace: ',', '' | strip %}

      <div style="margin-left: 20px; margin-top: 20px;">
        <h3 style="color: #444; font-size: 1.2rem; border-left: 4px solid #eee;">
          {% if sub_name == "" %} General {% else %} {{ sub_name | capitalize }} {% endif %}
        </h3>
        
        <ul class="custom-list">
          {% for post in group.items %}
            <li>
              <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
              <span style="color: #999; font-size: 0.85em;">- {{ post.date | date: "%B %d, %Y" }}</span>
            </li>
          {% endfor %}
        </ul>
      </div>
    {% endfor %}
  </section>
{% endfor %}

<style>
  .custom-list { list-style-type: disc !important; padding-left: 20px; }
  .custom-list li::marker { color: #000; font-size: 0.8em; }
  .custom-list li { margin-bottom: 8px; }
</style>