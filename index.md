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
    {% assign posts = site.categories[parent] %}
    {% assign grouped_sub = posts | group_by: "categories" %}

    {% for group in grouped_sub %}
      {% assign sub_name = group.name | replace: parent, "" | replace: '[', '' | replace: ']', '' | replace: '"', '' | replace: ',', '' | strip %}

      <div style="margin-top: 20px;">
        <h3 style="color: #444; font-size: 1.2rem; border-left: 4px solid #eee; padding-left: 10px;">
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
  .custom-list { list-style-type: disc !important; padding-left: 35px; }
  .custom-list li::marker { color: #00000064; font-size: 0.8em; }
  .custom-list li { margin-bottom: 8px; }
</style>