---
layout: default
title: Index of /addons
---
<h1>Index of /addons</h1>
<pre>
{% for f in site.static_files %}
  {% if f.path contains '/addons' and f.extname == '.zip' %}
    <a href="{{ site.baseurl | escape }}{{ f.path | escape }}">{{ f.path | escape }}</a>
  {% endif %}
{% endfor %}
</pre>
