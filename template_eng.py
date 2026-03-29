#!/usr/bin/env python3
"""template_eng - Minimal template engine with variables, loops, and conditionals."""
import sys, re

def render(template, context):
    result = template
    result = _for_loops(result, context)
    result = _if_blocks(result, context)
    result = _vars(result, context)
    return result

def _vars(t, ctx):
    def repl(m):
        key = m.group(1).strip()
        val = _resolve(key, ctx)
        return str(val) if val is not None else ""
    return re.sub(r"\{\{\s*(.+?)\s*\}\}", repl, t)

def _resolve(key, ctx):
    parts = key.split(".")
    val = ctx
    for p in parts:
        if isinstance(val, dict) and p in val:
            val = val[p]
        else:
            return None
    return val

def _for_loops(t, ctx):
    pattern = r"\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}"
    def repl(m):
        var, lst_name, body = m.group(1), m.group(2), m.group(3)
        lst = ctx.get(lst_name, [])
        return "".join(render(body, {**ctx, var: item}) for item in lst)
    return re.sub(pattern, repl, t, flags=re.DOTALL)

def _if_blocks(t, ctx):
    pattern = r"\{%\s*if\s+(.+?)\s*%\}(.*?)(?:\{%\s*else\s*%\}(.*?))?\{%\s*endif\s*%\}"
    def repl(m):
        cond, then, els = m.group(1), m.group(2), m.group(3) or ""
        val = _resolve(cond.strip(), ctx)
        return render(then, ctx) if val else render(els, ctx)
    return re.sub(pattern, repl, t, flags=re.DOTALL)

def test():
    assert render("Hello {{ name }}!", {"name": "World"}) == "Hello World!"
    assert render("{{ a.b }}", {"a": {"b": 42}}) == "42"
    t = "{% for item in items %}{{ item }} {% endfor %}"
    assert render(t, {"items": ["a", "b", "c"]}) == "a b c "
    t2 = "{% if show %}yes{% else %}no{% endif %}"
    assert render(t2, {"show": True}) == "yes"
    assert render(t2, {"show": False}) == "no"
    assert render("{{ missing }}", {}) == ""
    print("template_eng: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: template_eng.py --test")
