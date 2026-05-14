---
layout: default
title: Abstraction
---

{% assign parent_categories = "English,Mathematics,Physics" | split: "," %}

{% for parent in parent_categories %}
  <section class="category-section">
    <h2 class="category-root">
      {{ parent | escape }}
    </h2>

    {% include category_tree.html posts=site.posts path=parent depth=1 %}
  </section>
{% endfor %}

<style>
  .category-root,
  .category-heading,
  .post-list li {
    box-sizing: border-box;
    min-height: 42px;
    line-height: 1.4;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 10px;
    padding-bottom: 10px;
    border-bottom: 0.6px solid #d0d0d0;
  }

  .category-root {
    color: #000 !important;
    font-size: 1rem !important;
    border-bottom-color: #6e6e6e;
    font-weight: 600 !important;
  }

  .category-heading {
    color: #000000ab !important;
    font-size: 1rem !important;
  }

  .category-block {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    margin-left: 22px;
  }

  .post-list {
    list-style-type: none;
    padding-left: 0;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
  }

  .post-list li {
    margin-left: 22px;
  }

  .post-link {
    text-decoration: none !important;
    color: blue !important;
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.4;
  }

  .post-link:hover {
    text-decoration: underline !important;
  }
</style>