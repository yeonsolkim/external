---
layout: default
title: External
index_page: true
---

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

{% assign parent_categories = discovered_categories | sort %}

{% for parent in parent_categories %}
  <section class="category-section">
    <h2 class="category-root">
      {{ parent | strip_category_order_prefix | escape }}
    </h2>

    {% include category_tree.html posts=site.posts path=parent depth=1 max_depth=1 link_subcategories=true %}
  </section>
{% endfor %}
