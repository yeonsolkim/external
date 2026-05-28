---
layout: default
title: External
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

<script>
(function () {
  function formatEditedTime(dateString) {
    const edited = new Date(dateString);
    const now = new Date();

    if (Number.isNaN(edited.getTime())) {
      return null;
    }

    const diffMs = now - edited;
    const minute = 60 * 1000;
    const hour = 60 * minute;
    const day = 24 * hour;

    if (diffMs < 0) {
      return "edited just now";
    }

    if (diffMs < minute) {
      return "edited just now";
    }

    const minutes = Math.floor(diffMs / minute);
    if (minutes < 60) {
      return "edited " + minutes + " " + (minutes === 1 ? "minute" : "minutes") + " ago";
    }

    const hours = Math.floor(diffMs / hour);
    if (hours < 24) {
      return "edited " + hours + " " + (hours === 1 ? "hour" : "hours") + " ago";
    }

    const days = Math.floor(diffMs / day);
    if (days < 7) {
      return "edited " + days + " " + (days === 1 ? "day" : "days") + " ago";
    }

    return "edited on " + edited.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric"
    });
  }

  document.querySelectorAll(".post-edited-time").forEach(function (el) {
    const editedAt = el.getAttribute("data-edited-at");
    const text = formatEditedTime(editedAt);

    if (text) {
      el.textContent = text;
    }
  });
})();
</script>

<style>
  .post-edited-time {
    margin-left: 8px;
    color: #767676a8;
    font-size: 0.8rem;
    font-weight: 300 !important;
    white-space: nowrap;
  }

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
    border-bottom: 0.6px solid #c6c6c6;
  }

  .category-root {
    color: #000 !important;
    font-size: 1rem !important;
    border-bottom-color: #6e6e6e !important;
    font-weight: 600 !important;
  }

  .category-heading {
    color: #000000c0 !important;
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
    line-height: 1.4;
  }

  .post-link:hover .post-title {
    text-decoration: underline;
  }
</style>