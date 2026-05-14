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
    color: #000 !important;
    font-size: 1.8rem !important;
    font-style: bold;
    padding-bottom: 9px;
    border-bottom: 0.6px solid #959595;
  }

  .category-heading {
    margin-top: 18px;
    color: #222 !important ;
    font-weight: 500;
  }

  .category-heading.depth-1 {
    margin-top: 30px;
    font-size: 1.3rem !important;
  }

  .category-section > .category-block.depth-1:first-of-type .category-heading.depth-1 {
    margin-top: 0;
  }

  .category-block.depth-1 > .category-block.depth-2:first-of-type > .category-heading.depth-2 {
    margin-top: -20px !important;
  }

  .category-block.depth-2,
  .category-block.depth-3,
  .category-block.depth-4,
  .category-block.depth-5 {
    margin-left: 22px;
  }

  .category-heading.depth-2 {
    font-size: 1rem;
    margin-top: -10px;
  }

  .category-heading.depth-3,
  .category-heading.depth-4,
  .category-heading.depth-5,
  .category-heading.depth-6 {
    display: inline-block;
    font-size: 1rem;
    margin-left: 22px;
  }

  .post-list {
    list-style-type: none;
    padding-left: 0;
    margin-top: -17px !important ;
    margin-bottom: 12px;
    margin-left: 22px;
  }

  .post-list li {
    margin-bottom: 8px;
    margin-top: -0.5rem !important ;
  }

  .post-link {
    text-decoration: none !important;
    color: blue !important;
    transition: color 0.2s ease;
    font-size: 1rem; 
  }

  .post-link:hover {
    text-decoration: underline !important;
  }
</style>
