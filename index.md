---
layout: default
title: Representations
---

{% assign parent_categories = "Mathematics,Physics,English,Reading" | split: "," %}

{% for parent in parent_categories %}
  <section class="category-section">
    <h2 class="category-root">
      {{ parent | escape }}
    </h2>

    {% include category_tree.html posts=site.posts path=parent depth=1 %}
  </section>
{% endfor %}