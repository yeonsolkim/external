---
layout: default
title: Abstraction
---

{% assign parent_categories = "English,Mathematics,Physics" | split: "," %}

{% for parent in parent_categories %}
  <section style="margin-bottom: 40px;">
    <h2 style="color: #000; padding-bottom: 10px; border-bottom: 2px solid #eee;">
      {{ parent }}
    </h2>

    
    {% assign sub_cats = "" | split: "" %}
    {% for post in site.posts %}
      {% if post.categories contains parent %}
        {% assign current_sub = post.categories[1] | default: "General" %}
        {% unless sub_cats contains current_sub %}
          {% assign sub_cats = sub_cats | push: current_sub %}
        {% endunless %}
      {% endif %}
    {% endfor %}
    
    {% assign sub_cats = sub_cats | sort %}

    {% for sub in sub_cats %}
      <div style="margin-left: 20px; margin-top: 25px;">
        <h3 style="color: #444; font-size: 1.1rem; border-left: 4px solid #0000001a; padding-left: 12px; margin-bottom: 15px;">
          {{ sub }}
        </h3>
        
        <ul class="custom-list">
         {% assign sorted_posts = site.posts | sort: "title" %}

          {% for post in sorted_posts %}
           {% assign p_sub = post.categories[1] | default: "General" %}
            {% if post.categories[0] == parent and p_sub == sub %}
              <li>
                <a href="{{ site.baseurl }}{{ post.url }}" class="post-link">
                {{ post.title }}
                </a>
              </li>
            {% endif %}
           {% endfor %}
        </ul>
      </div>
    {% endfor %}
  </section>
{% endfor %}

<style>
  .custom-list { list-style-type: disc !important; padding-left: 20px; margin-left: 20px; }
  .custom-list li::marker { color: #00000000; font-size: 0.7em; }
  .custom-list li { margin-bottom: 10px; }
  .custom-list li a:hover { text-decoration: underline; color: #000 !important; }
  .post-link {
    text-decoration: none !important; 
    color: #666 !important; 
    font-weight: 500;
    transition: color 0.2s ease;
  }
  .post-link:hover { 
    text-decoration: underline !important; 
    color: #000 !important; 
  }
</style>