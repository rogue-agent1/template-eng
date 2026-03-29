#!/usr/bin/env python3
"""template_eng - Simple template engine with variables, loops, and conditionals."""
import sys, re

def render(template, context):
    result = template
    # conditionals: {% if var %}...{% endif %}
    def replace_if(m):
        var = m.group(1).strip()
        body = m.group(2)
        val = _resolve(var, context)
        return body if val else ""
    result = re.sub(r"\{%\s*if\s+(.+?)\s*%\}(.*?)\{%\s*endif\s*%\}", replace_if, result, flags=re.DOTALL)
    # loops: {% for item in list %}...{% endfor %}
    def replace_for(m):
        var = m.group(1).strip()
        iterable_name = m.group(2).strip()
        body = m.group(3)
        items = _resolve(iterable_name, context)
        if not items:
            return ""
        parts = []
        for item in items:
            ctx = dict(context)
            ctx[var] = item
            parts.append(render(body, ctx))
        return "".join(parts)
    result = re.sub(r"\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}", replace_for, result, flags=re.DOTALL)
    # variables: {{ var }}
    def replace_var(m):
        var = m.group(1).strip()
        val = _resolve(var, context)
        return str(val) if val is not None else ""
    result = re.sub(r"\{\{\s*(.+?)\s*\}\}", replace_var, result)
    return result

def _resolve(key, context):
    parts = key.split(".")
    val = context
    for p in parts:
        if isinstance(val, dict):
            val = val.get(p)
        elif hasattr(val, p):
            val = getattr(val, p)
        else:
            return None
    return val

def test():
    # simple variable
    assert render("Hello {{ name }}!", {"name": "World"}) == "Hello World!"
    # conditional
    t = "{% if show %}visible{% endif %}"
    assert render(t, {"show": True}) == "visible"
    assert render(t, {"show": False}) == ""
    # loop
    t2 = "{% for x in items %}{{ x }} {% endfor %}"
    assert render(t2, {"items": ["a", "b", "c"]}) == "a b c "
    # nested access
    assert render("{{ user.name }}", {"user": {"name": "Alice"}}) == "Alice"
    # combined
    t3 = "Users: {% for u in users %}{{ u }}{% endfor %}"
    assert render(t3, {"users": ["A", "B"]}) == "Users: AB"
    print("OK: template_eng")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: template_eng.py test")
