#!/usr/bin/env python3
"""One-time: parse the original Everyday Scaries source form into brands/everyday-scaries.json.
Run once to seed the first brand file. Future brand files are authored in Cowork, not extracted."""
import re, json, os, html

SRC = ("/Users/brettlewis/Documents/Software/BlinkUiPrototype/"
       "design_handoff_discovery_form/Everyday Scaries - Discovery Pre-Work.html")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brands", "everyday-scaries.json")

src = open(SRC, "r", encoding="utf-8").read()


def unesc(s):
    return html.unescape(s).strip()


def one(pat, s=src, flags=re.S):
    m = re.search(pat, s, flags)
    return m.group(1).strip() if m else None


brand = {"slug": "everyday-scaries", "form_name": "Everyday Scaries"}
brand["storage_key"] = "blink-es-discovery-prework-v1"  # keep original key so in-progress drafts survive
brand["title"] = "Everyday Scaries — Discovery Pre-Work"

# Cover
brand["cover_kicker_html"] = one(r'<div class="cover-kicker"><span class="dot"></span>(.*?)</div>')
brand["cover_title_html"] = one(r'<h1 class="cover-title">(.*?)</h1>')
brand["cover_lede"] = unesc(one(r'<p class="cover-lede">(.*?)</p>'))
brand["client_label"] = one(r'<span class="cl-lbl">(.*?)</span>')
brand["client_name"] = one(r'<span class="cl-name">(.*?)</span>')

# How-to
howto = one(r'<div class="howto">(.*?)</div>\s*<div class="ready">')
brand["howto_label"] = unesc(re.search(r'<div class="block-label">(.*?)</div>', howto, re.S).group(1))
brand["howto_title"] = unesc(re.search(r'<h2>(.*?)</h2>', howto, re.S).group(1))
brand["howto_paras"] = [unesc(p) for p in re.findall(r'<p>(.*?)</p>', howto, re.S)]
brand["est_time_html"] = re.search(r'<span class="esttime">(.*?)</span>', howto, re.S).group(1).strip()

# Ready
ready = one(r'<div class="ready">(.*?)</div>\s*<!-- SECTIONS')
brand["ready_label"] = unesc(re.search(r'<div class="block-label"[^>]*>(.*?)</div>', ready, re.S).group(1))
brand["ready"] = [{"a": unesc(a), "b": unesc(b)} for a, b in
                  re.findall(r'<li><span class="ri-a">(.*?)</span><span class="ri-b">(.*?)</span></li>', ready, re.S)]

# Sections
sections = []
for sec_html in re.findall(r'<section class="sec">(.*?)</section>', src, re.S):
    sec = {
        "num": re.search(r'<div class="secnum">(.*?)</div>', sec_html, re.S).group(1).strip(),
        "title": unesc(re.search(r'<div class="sectitle">(.*?)</div>', sec_html, re.S).group(1)),
        "subtitle": unesc(re.search(r'<div class="secsub">(.*?)</div>', sec_html, re.S).group(1)),
        "time": re.search(r'<div class="sectime">(.*?)</div>', sec_html, re.S).group(1).strip(),
        "questions": [],
    }
    # each question chunk: from <div class="q"> to its </textarea>
    for q_html in re.findall(r'<div class="q">(.*?)</textarea>', sec_html, re.S):
        qid = re.search(r'<span class="qid">(.*?)</span>', q_html, re.S).group(1).strip()
        qhead = re.search(r'<div class="qhead">(.*?)</div>', q_html, re.S).group(1)
        qtext_block = re.search(r'<span class="qtext">(.*)</span>', qhead, re.S).group(1)
        tag_m = re.search(r'<span class="qtag">(.*?)</span>', qtext_block, re.S)
        tag = unesc(tag_m.group(1)) if tag_m else ""
        text = unesc(re.sub(r'<span class="qtag">.*?</span>', '', qtext_block, flags=re.S))
        help_txt = unesc(re.search(r'<p class="qhelp">(.*?)</p>', q_html, re.S).group(1))
        ta = re.search(r'<textarea class="answer" name="(.*?)"[^>]*min-height:(\d+)px', q_html, re.S)
        sec["questions"].append({
            "id": qid, "name": ta.group(1), "text": text, "help": help_txt,
            "tag": tag, "min_height": int(ta.group(2)),
        })
    sections.append(sec)
brand["sections"] = sections

# Closing
closing = one(r'<div class="closing">(.*?)</div>\s*</form>')
brand["closing_kicker"] = unesc(re.search(r'<div class="ok">(.*?)</div>', closing, re.S).group(1))
brand["closing_title"] = unesc(re.search(r'<h2>(.*?)</h2>', closing, re.S).group(1))
brand["closing_body"] = unesc(re.search(r'<p>(.*?)</p>', closing, re.S).group(1))
footer = one(r'<div slot="footer"[^>]*>(.*?)</div>')
brand["footer_right"] = unesc(re.findall(r'<span>([^<]*)</span>', footer)[-1])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(brand, f, ensure_ascii=False, indent=2)

nq = sum(len(s["questions"]) for s in sections)
print("Wrote {}  ({} sections, {} questions)".format(OUT, len(sections), nq))
assert len(sections) == 6 and nq == 16, "expected 6 sections / 16 questions, got {}/{}".format(len(sections), nq)
print("client:", brand["client_name"], "| footer_right:", brand["footer_right"])
