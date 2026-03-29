#!/usr/bin/env python3
"""Simple template engine (Jinja-like subset). Zero dependencies."""
import re, sys

def render(template, context):
    result = template
    # Variable substitution {{ var }}
    result = re.sub(r"\{\{\s*(.+?)\s*\}\}", lambda m: _eval_expr(m.group(1), context), result)
    # For loops {% for x in items %}...{% endfor %}
    result = _process_for(result, context)
    # If blocks {% if cond %}...{% endif %}
    result = _process_if(result, context)
    return result

def _eval_expr(expr, ctx):
    parts = expr.split(".")
    val = ctx
    for p in parts:
        m2 = re.match(r"(\w+)\[(\d+)\]", p)
        if m2:
            val = val[m2.group(1)][int(m2.group(2))]
        elif isinstance(val, dict):
            val = val.get(p, "")
        else:
            val = getattr(val, p, "")
    if expr.endswith("|upper"): return str(val).upper()
    if expr.endswith("|lower"): return str(val).lower()
    if expr.endswith("|title"): return str(val).title()
    return str(val)

def _process_for(template, ctx):
    pattern = r"\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}"
    def replacer(m):
        var, collection, body = m.group(1), m.group(2), m.group(3)
        items = ctx.get(collection, [])
        result = []
        for item in items:
            inner_ctx = dict(ctx)
            inner_ctx[var] = item
            result.append(render(body, inner_ctx))
        return "".join(result)
    return re.sub(pattern, replacer, template, flags=re.DOTALL)

def _process_if(template, ctx):
    pattern = r"\{%\s*if\s+(.+?)\s*%\}(.*?)(?:\{%\s*else\s*%\}(.*?))?\{%\s*endif\s*%\}"
    def replacer(m):
        cond, true_block, false_block = m.group(1), m.group(2), m.group(3) or ""
        val = _eval_expr(cond, ctx)
        if val and val != "False" and val != "0" and val != "" and val != "None":
            return render(true_block, ctx)
        return render(false_block, ctx)
    return re.sub(pattern, replacer, template, flags=re.DOTALL)

if __name__ == "__main__":
    import json, argparse
    p = argparse.ArgumentParser(description="Template engine")
    p.add_argument("template")
    p.add_argument("-d", "--data", required=True)
    args = p.parse_args()
    with open(args.template) as f: tmpl = f.read()
    with open(args.data) as f: ctx = json.load(f)
    print(render(tmpl, ctx))
