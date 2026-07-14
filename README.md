# Blink Social — Discovery Pre-Work forms

Branded client discovery questionnaires, hosted on GitHub Pages, collecting into one shared
Google Sheet. Each brand is one folder here and gets its own public link. Answers land on a
per-brand tab in the Sheet, and blewis@jackreiley.com gets an email on every submission.

Live form URL pattern: `https://vthokiebrett.github.io/blink-pre-work/<brand-slug>/`

---

## Adding a new brand (the recurring process)

1. **Finalize the questions** (in Claude Cowork). Cowork writes the brand file for you:
   `brands/<brand-slug>.json`. You do not hand-write it.

2. **Build the form:**
   ```
   python3 build.py brands/<brand-slug>.json
   ```
   This creates `<brand-slug>/index.html`, fully styled, with the shared endpoint baked in.

3. **Publish:**
   ```
   ./publish.sh "<brand-slug>"        # builds, commits, pushes, prints the live URL
   ```
   or manually:
   ```
   git add -A && git commit -m "Add <brand-slug> pre-work" && git push
   ```

4. **Send the client the link.** The Google Sheet tab named after the brand is created
   automatically the first time someone submits. No Google setup per brand.

To change a live brand's questions later: edit its `brands/<slug>.json`, run step 2, then step 3.

---

## One-time setup (already done, for reference)

- **Google Sheet:** created once. `google-apps-script.gs` (in the design handoff) is pasted into
  its Apps Script editor and deployed as a Web app (Execute as Me, Access Anyone). The `/exec`
  URL from that deployment is set once in `build.py` as `SHARED_ENDPOINT`, so every brand form
  reuses it. To rotate it, change `SHARED_ENDPOINT` and rebuild all brands: `python3 build.py --all`.
- **GitHub Pages:** this repo (`blink-pre-work`, public) serves Pages from `main` / root.

---

## Brand file format (`brands/<slug>.json`)

Cowork generates this; reference only.

| Field | Meaning |
|---|---|
| `slug` | URL folder + build output folder. Lowercase, hyphens. |
| `form_name` | The brand name. Becomes the Google Sheet tab and the `_form` value. |
| `client_name` | Shown in the dark client tag and footer. |
| `cover_lede` | One line under the title. |
| `howto_title`, `howto_paras` | The "how to use" intro. |
| `est_time_html` | The estimated-time pill (HTML allowed for `&nbsp;` / `·`). |
| `ready` | List of `{ "a": bold line, "b": sub line }` for "before you start". |
| `sections` | List of sections, each `{ num, title, subtitle, time, questions[] }`. |
| `questions` | Each `{ id, name, text, help, tag, min_height }`. `name` must be unique (e.g. `q1_1`). `tag` optional (e.g. `↗ Look this up first`). |
| `closing_kicker`, `closing_title`, `closing_body` | The thank-you page. |

The Google Sheet columns are generated automatically from each question as `"<id> <text>"`, so the
Sheet is self-documenting — you never maintain a separate label list.

---

## Files

| Path | What |
|---|---|
| `build.py` | Generator: brand file → `<slug>/index.html`. `--all` rebuilds every brand. |
| `publish.sh` | Build + commit + push + print URL. |
| `template/head.css` | Inlined design tokens + page styles. |
| `template/doc-page.js` | Print/PDF pagination component (inlined into each form). |
| `template/app.js` | Form logic (autosave, submit, CSV). Placeholders injected at build. |
| `brands/*.json` | One file per brand. |
| `<slug>/index.html` | Built, hosted form. Do not edit by hand — rebuild instead. |
| `extract_es.py` | One-time seed of the first brand file from the original handoff. Not used going forward. |

Fonts (Space Grotesk, Inter) load from Google Fonts at view time, so a live connection is needed
to render the exact type — always true for a hosted link.
