---
---
<head>
  <title>Index of /</title>
</head>

<body>
  <h1>Index of /</h1>
  <ul>
 .  {% for f in site.static_files %}
....  {% if f.extpath = '.zip' %}
 ..    <li><a href="{{ site.baseurl | escape }}{{ f.path | escape }}">{{ f.path | escape }}</a> </li>
 .. . {% endif %}
.   {% endfor %}
  </ul>
</body>
