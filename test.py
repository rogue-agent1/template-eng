from template_eng import render
assert render("Hello {{ name }}!", {"name": "World"}) == "Hello World!"
r = render("{% for item in items %}{{ item }} {% endfor %}", {"items": ["a","b","c"]})
assert "a" in r and "b" in r and "c" in r
r2 = render("{% if show %}yes{% else %}no{% endif %}", {"show": True})
assert r2.strip() == "yes"
print("Template engine tests passed")