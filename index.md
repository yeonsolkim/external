---
layout: default
title: Semantics
---

{% assign preferred_categories = "Mathematics,Physics,English,Reading" | split: "," %}
{% assign discovered_categories = "" | split: "" %}

{% for post in site.posts %}
  {% assign raw_path = post.category_path | default: post.categories %}
  {% if raw_path %}
    {% assign path_string = raw_path | join: "|" %}
    {% assign top_category = path_string | split: "|" | first | strip %}
    {% if top_category != "" %}
      {% unless discovered_categories contains top_category %}
        {% assign discovered_categories = discovered_categories | push: top_category %}
      {% endunless %}
    {% endif %}
  {% endif %}
{% endfor %}

{% assign extra_categories = "" | split: "" %}
{% for category in discovered_categories %}
  {% unless preferred_categories contains category %}
    {% assign extra_categories = extra_categories | push: category %}
  {% endunless %}
{% endfor %}

{% assign extra_categories = extra_categories | sort %}
{% assign parent_categories = preferred_categories | concat: extra_categories %}

{% for parent in parent_categories %}
  <section class="category-section">
    <h2 class="category-root">
      {{ parent | escape }}
    </h2>

    {% include category_tree.html posts=site.posts path=parent depth=1 %}
  </section>
{% endfor %}
