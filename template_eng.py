#!/usr/bin/env python3
"""Simple template engine with {{ var }}, {% for %}, {% if %}."""
import re

def render(template: str, context: dict) -> str:
    result = template
    # Process for loops
    for_re = re.compile(r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}', re.DOTALL)
    while for_re.search(result):
        def replace_for(m):
            var, collection, body = m.group(1), m.group(2), m.group(3)
            items = context.get(collection, [])
            parts = []
            for item in items:
                ctx = {**context, var: item}
                parts.append(render(body, ctx))
            return "".join(parts)
        result = for_re.sub(replace_for, result)
    # Process if blocks
    if_re = re.compile(r'\{%\s*if\s+(\w+)\s*%\}(.*?)(?:\{%\s*else\s*%\}(.*?))?\{%\s*endif\s*%\}', re.DOTALL)
    while if_re.search(result):
        def replace_if(m):
            cond = context.get(m.group(1))
            if cond:
                return render(m.group(2), context)
            return render(m.group(3) or "", context)
        result = if_re.sub(replace_if, result)
    # Variable substitution
    def replace_var(m):
        key = m.group(1).strip()
        parts = key.split(".")
        val = context
        for p in parts:
            if isinstance(val, dict): val = val.get(p, "")
            else: val = getattr(val, p, "")
        return str(val)
    result = re.sub(r'\{\{\s*(.+?)\s*\}\}', replace_var, result)
    return result

if __name__ == "__main__":
    tmpl = "Hello {{ name }}! {% for item in items %}{{ item }} {% endfor %}"
    print(render(tmpl, {"name": "World", "items": ["a", "b", "c"]}))

def test():
    assert render("Hello {{ name }}!", {"name": "World"}) == "Hello World!"
    assert render("{{ a.b }}", {"a": {"b": "deep"}}) == "deep"
    # For loop
    assert render("{% for x in items %}{{ x }},{% endfor %}", {"items": [1,2,3]}) == "1,2,3,"
    # If
    assert render("{% if show %}yes{% endif %}", {"show": True}) == "yes"
    assert render("{% if show %}yes{% endif %}", {"show": False}) == ""
    assert render("{% if show %}yes{% else %}no{% endif %}", {"show": False}) == "no"
    # Nested
    r = render("{% for x in items %}{% if x %}{{ x }}{% endif %}{% endfor %}", {"items": [1, 0, 3]})
    assert r == "13"
    # Missing
    assert render("{{ missing }}", {}) == ""
    print("  template_eng: ALL TESTS PASSED")
