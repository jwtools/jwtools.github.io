---
---
<head>
  <title>Index of /</title>
</head>

<body>
  <h1>Index of /</h1>
  <ul>
    {% for f in site.static_files %}
    <li><a href="{{ site.baseurl | escape }}{{ f.path | escape }}">{{ f.path | escape }}</a> </li>
    {% endfor %}
  </ul>
</body>
