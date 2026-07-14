#!/usr/bin/env python3
"""
Blink pre-work form generator.

Turns a brand file (brands/<slug>.json) into a self-contained, hosted-ready
questionnaire at <slug>/index.html. Fonts load from Google Fonts; the design
tokens, page CSS, pagination component (doc-page.js) and form logic are inlined.

Usage:
    python3 build.py brands/everyday-scaries.json
    python3 build.py --all          # rebuild every brand in brands/

The shared Google Apps Script /exec URL is set ONCE below and baked into every
form, so a new brand never needs its own Google setup.
"""
import json, os, sys, glob, html

HERE = os.path.dirname(os.path.abspath(__file__))

# ── The one shared endpoint for every brand form. Set after deploying the Apps Script. ──
SHARED_ENDPOINT = "https://script.google.com/macros/s/AKfycbzJL-ndyFgppx5YciRzy6UU2m87CytJCC_BVgGeII6X0yPoqhjLSCog9bNw-mA_zpd9Jw/exec"

FONT_LINKS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap">'
)
PLACEHOLDER = "Type your answer…"


def esc(s):
    """Escape text going into element content (matches how browsers read the source)."""
    return html.escape(str(s), quote=False)


def read(path):
    with open(os.path.join(HERE, path), "r", encoding="utf-8") as f:
        return f.read()


def inline_js(s):
    """Neutralize any literal </script> so an inline <script> block isn't closed early."""
    import re
    return re.sub(r"</(script)", r"<\\/\1", s, flags=re.I)


def build_labels(sections):
    """Single source of truth for the JS LABELS map + Sheet columns."""
    labels = {"completed_by": "Completed by", "date": "Date"}
    for sec in sections:
        for q in sec["questions"]:
            labels[q["name"]] = "{} {}".format(q["id"], q["text"]).strip()
    return labels


def render_question(q):
    tag = q.get("tag") or ""
    tag_html = ' <span class="qtag">{}</span>'.format(esc(tag)) if tag else ""
    return (
        '        <div class="q">\n'
        '          <div class="qhead"><span class="qid">{id}</span>'
        '<span class="qtext">{text}{tag}</span></div>\n'
        '          <p class="qhelp">{help}</p>\n'
        '          <textarea class="answer" name="{name}" style="min-height:{mh}px" '
        'placeholder="{ph}"></textarea>\n'
        '        </div>'
    ).format(
        id=esc(q["id"]), text=esc(q["text"]), tag=tag_html,
        help=esc(q["help"]), name=esc(q["name"]),
        mh=int(q.get("min_height", 110)), ph=esc(PLACEHOLDER),
    )


def render_section(sec):
    qs = "\n".join(render_question(q) for q in sec["questions"])
    return (
        '      <section class="sec">\n'
        '        <div class="secband">\n'
        '          <div class="secnum">{num}</div>\n'
        '          <div class="secmeta">\n'
        '            <div class="sectitle">{title}</div>\n'
        '            <div class="secsub">{subtitle}</div>\n'
        '          </div>\n'
        '          <div class="sectime">{time}</div>\n'
        '        </div>\n\n{qs}\n'
        '      </section>'
    ).format(
        num=esc(sec["num"]), title=esc(sec["title"]),
        subtitle=esc(sec.get("subtitle", "")), time=esc(sec.get("time", "")), qs=qs,
    )


def render_body(b):
    client = b["client_name"]
    ready = "\n".join(
        '          <li><span class="ri-a">{}</span><span class="ri-b">{}</span></li>'.format(
            esc(it["a"]), esc(it["b"])) for it in b.get("ready", [])
    )
    paras = "\n".join('    <p>{}</p>'.format(esc(p)) for p in b.get("howto_paras", []))
    sections = "\n".join(render_section(s) for s in b["sections"])
    footer_left = b.get("footer_left_html",
                        '<span class="dot"></span>Blink Social · Discovery Pre-Work')
    footer_right = esc(b.get("footer_right", "{} · Confidential".format(client)))
    return (
        '<doc-page size="letter" orientation="portrait" margin="0.7in">\n\n'
        '  <div slot="footer" class="foot">\n'
        '    <span>{footer_left}</span>\n'
        '    <span>{footer_right}</span>\n'
        '  </div>\n\n'
        '  <form autocomplete="off">\n'
        '  <!-- COVER -->\n'
        '  <div class="cover-kicker"><span class="dot"></span>{kicker}</div>\n'
        '  <h1 class="cover-title">{title_html}</h1>\n'
        '  <p class="cover-lede">{lede}</p>\n'
        '  <div class="client-tag"><span class="cl-lbl">{client_label}</span>'
        '<span class="cl-name">{client}</span></div>\n'
        '  <div class="coverfields">\n'
        '    <label class="cf"><span>Completed by</span>'
        '<input type="text" name="completed_by" placeholder="Your name"></label>\n'
        '    <label class="cf"><span>Date</span>'
        '<input type="text" name="date" placeholder="MM / DD / YYYY"></label>\n'
        '  </div>\n\n'
        '  <div class="howto">\n'
        '    <div class="block-label">{howto_label}</div>\n'
        '    <h2>{howto_title}</h2>\n'
        '{paras}\n'
        '    <span class="esttime">{est_time}</span>\n'
        '  </div>\n\n'
        '  <div class="ready">\n'
        '    <div class="block-label" style="margin-bottom:0">{ready_label}</div>\n'
        '    <ul>\n{ready}\n    </ul>\n'
        '  </div>\n\n'
        '  <!-- SECTIONS -->\n\n{sections}\n\n'
        '  <!-- CLOSING -->\n'
        '  <div class="closing">\n'
        '    <div class="ok">{closing_kicker}</div>\n'
        '    <h2>{closing_title}</h2>\n'
        '    <p>{closing_body}</p>\n'
        '    <div class="rule"></div>\n'
        '    <div class="actionbar">\n'
        '      <button type="button" class="btn btn-primary" id="submitBtn">Submit to Blink</button>\n'
        '      <button type="button" class="btn btn-ghost" id="downloadBtn">Download a copy (CSV)</button>\n'
        '      <button type="button" class="btn btn-ghost" id="clearBtn">Clear my answers</button>\n'
        '    </div>\n'
        '    <div class="savenote" id="saveNote">Your answers save automatically in this browser.</div>\n'
        '  </div>\n\n'
        '  </form>\n'
        '</doc-page>'
    ).format(
        footer_left=footer_left, footer_right=footer_right,
        kicker=b.get("cover_kicker_html", "BLINK SOCIAL &nbsp;·&nbsp; DISCOVERY PRE-WORK"),
        title_html=b.get("cover_title_html", "Client<br>Questionnaire"),
        lede=esc(b["cover_lede"]),
        client_label=esc(b.get("client_label", "Client")), client=esc(client),
        howto_label=esc(b.get("howto_label", "How to use this document")),
        howto_title=esc(b.get("howto_title", "")), paras=paras,
        est_time=b.get("est_time_html", ""),
        ready_label=esc(b.get("ready_label", "Before you start — have these ready")),
        ready=ready, sections=sections,
        closing_kicker=esc(b.get("closing_kicker", "That's everything we need")),
        closing_title=esc(b.get("closing_title", "Thank you.")),
        closing_body=esc(b.get("closing_body", "")),
    )


def render_submitted(b):
    """Branded confirmation page the form redirects to after a successful submit."""
    tpl = read("template/submitted.html")
    title = esc(b.get("title", "{} — Discovery Pre-Work".format(b["client_name"])))
    return (tpl.replace("{{TITLE}}", title)
               .replace("{{CLIENT_NAME}}", esc(b["client_name"])))


def render_app_js(b):
    slug = b["slug"]
    js = read("template/app.js")
    labels = build_labels(b["sections"])
    js = js.replace("__FORM_NAME__", json.dumps(b["form_name"], ensure_ascii=False))
    js = js.replace("__ENDPOINT__", json.dumps(SHARED_ENDPOINT))
    js = js.replace("__STORAGE_KEY__",
                    json.dumps(b.get("storage_key", "blink-prework-{}-v1".format(slug))))
    js = js.replace("__LABELS__", json.dumps(labels, ensure_ascii=False, indent=4))
    return js


def build_brand(brand_path):
    b = json.loads(read(brand_path))
    for req in ("slug", "form_name", "client_name", "cover_lede", "sections"):
        if req not in b:
            raise SystemExit("Brand file {} is missing required field: {}".format(brand_path, req))

    head_css = read("template/head.css")
    doc_page_js = inline_js(read("template/doc-page.js"))
    app_js = inline_js(render_app_js(b))
    title = esc(b.get("title", "{} — Discovery Pre-Work".format(b["client_name"])))

    page = (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>{title}</title>\n{fonts}\n<style>\n{css}\n</style>\n</head>\n<body>\n"
        "{body}\n<script>\n{docpage}\n</script>\n<script>\n{app}\n</script>\n</body>\n</html>\n"
    ).format(title=title, fonts=FONT_LINKS, css=head_css,
             body=render_body(b), docpage=doc_page_js, app=app_js)

    out_dir = os.path.join(HERE, b["slug"])
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)

    # Confirmation page at <slug>/submitted/index.html
    sub_dir = os.path.join(out_dir, "submitted")
    os.makedirs(sub_dir, exist_ok=True)
    with open(os.path.join(sub_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_submitted(b))

    nq = sum(len(s["questions"]) for s in b["sections"])
    connected = "connected" if SHARED_ENDPOINT.startswith("http") else "NOT connected (placeholder endpoint)"
    print("Built {}/index.html  ({} sections, {} questions, {})".format(
        b["slug"], len(b["sections"]), nq, connected))
    return out_path


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    if argv[0] == "--all":
        paths = sorted(glob.glob(os.path.join(HERE, "brands", "*.json")))
        if not paths:
            raise SystemExit("No brand files in brands/")
        for p in paths:
            build_brand(os.path.relpath(p, HERE))
    else:
        build_brand(argv[0])


if __name__ == "__main__":
    main(sys.argv[1:])
