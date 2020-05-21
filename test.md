---
---
<head>
  <title>Index of /</title>
</head>

<body>
  <h1>Index of /</h1>
    {% for f in site.static_files %}
      {% if f.extname == '.zip' and f.path contains 'addons' %}
        <p><a href="{{ site.baseurl | escape }}{{ f.path | escape }}">{{ f.path | escape }}</a></p>
      {% endif %}
    {% endfor %}
</body>
