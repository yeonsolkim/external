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
  .category-section {
    margin-bottom: 48px;
  }

  .category-root {
    color: #000;
    font-size: 1.8rem !important;
    padding-bottom: 9px;
    border-bottom: 2px solid #eee;
  }

  .category-block {
    margin-top: 18px;
  }

  .category-block.depth-1 {
    margin-left: 10px;
  }

  .category-block.depth-2 {
    margin-left: 22px;
  }

  .category-block.depth-3 {
    margin-left: 34px;
  }

  .category-block.depth-4,
  .category-block.depth-5,
  .category-block.depth-6 {
    margin-left: 42px;
  }

  .category-heading {
    margin-top: 18px;
    margin-bottom: 10px;
    color: #222;
    font-weight: 500;
  }

  .category-heading.depth-1 {
    font-size: 1.1rem;
    padding-left: 12px;
    border-left: 3px solid #ddd;
  }

  .category-heading.depth-2 {
    font-size: 0.95rem;
    color: #555;
    padding-left: 10px;
    border-left: 2px solid #eee;
  }

  .category-heading.depth-3,
  .category-heading.depth-4,
  .category-heading.depth-5,
  .category-heading.depth-6 {
    display: inline-block;
    font-size: 0.85rem;
    color: #666;
    background: #f6f6f6;
    border-radius: 6px;
    padding: 3px 8px;
  }

  .post-list {
    list-style-type: none;
    padding-left: 0;
    margin-top: 8px;
    margin-bottom: 12px;
  }

  .post-list.depth-1 {
    margin-left: 24px;
  }

  .post-list.depth-2 {
    margin-left: 32px;
  }

  .post-list.depth-3,
  .post-list.depth-4,
  .post-list.depth-5,
  .post-list.depth-6 {
    margin-left: 38px;
  }

  .post-list li {
    margin-bottom: 8px;
  }

  .post-link {
    text-decoration: none !important;
    color: #414141d3 !important;
    transition: color 0.2s ease;
  }

  .post-link:hover {
    text-decoration: underline !important;
  }
</style>
