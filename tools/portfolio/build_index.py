"""Build the portfolio home page (index.html) from the project list below.

Usage, from the repository root:  python3 tools/portfolio/build_index.py

Each project row: (name, description, tags, preview, demo URL, docs URL, source URL[, extra links]).
preview is "img:<name>" for assets/thumbs/<name>.webp (480x300) or "icon:<id>" for an icon from ICONS.
None for a URL renders an em dash ("not available").
"""

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G = "https://github.com/neuroanimal/"
P = "https://neuroanimal.github.io/"
T = "https://github.com/neuroanimal/neuroanimal.github.io/tree/master/"

# (name, description, tags, thumb-or-icon, demo, docs, source)
APPS = [
 ("Paleoscript", "Medieval broad-nib handwriting generator (LOGO-style pen) and scan analysis for Polona manuscripts.",
  "TypeScript · canvas · image analysis", "img:paleoscript", P+"paleoscript/", G+"paleoscript#readme", G+"paleoscript"),
 ("Camera OCR in the browser", "No-build, modular camera OCR: staged overlays, pen/scanner modes, receipt-oriented cleanup and line accumulation (Tesseract.js).",
  "JavaScript · ES modules · Tesseract.js · camera API", "img:camera_ocr", P+"ocr_in_browser/skill-bill-modular/",
  T+"ocr_in_browser/skill-bill-modular#readme", T+"ocr_in_browser/skill-bill-modular"),
 ("Job offers from Kraków BIP and job boards", "Daily scraper of public-sector and job-board offers for two career profiles (culture &amp; arts, data &amp; AI): availability history, profile matching, salaries, HTML reports with a district map and filters.",
  "Python · requests · BeautifulSoup · data pipeline", "img:bip_krk", P+"bip_krk/", G+"bip_krk#readme", G+"bip_krk"),
 ("CV Scoring Engine", "Explainable scoring of CVs, cover letters and job offers (PL/EN) without LLMs: 62 metrics, InDesign-aware PDF extraction with OCR, recruiter screening verdict, calibration on real outcomes.",
  "Python · PyMuPDF · Tesseract · scikit-learn · BM25 · NLP", "img:cvscore", P+"candidate-score/",
  G+"candidate-score/tree/master/cv-scoring-system#readme", G+"candidate-score"),
 ("Skill Bill - mobile app", "Expo / React Native app: resumable parallel upload of photos and videos from iPhone, and offline verification by content (MD5) before deleting from the phone.",
  "TypeScript · Expo · React Native", "icon:phone", None, G+"skill-bill#readme", G+"skill-bill"),
 ("Skill Bill - server", "Receives chunked, resumable uploads over ngrok or pulls over the phone hotspot; files every item by capture date and GPS place; EXIF / QuickTime parsers without dependencies.",
  "Python · Flask · EXIF · Nominatim", "icon:server", None, G+"skill-bill-srv#readme", G+"skill-bill-srv"),
 ("AI chat sessions report", "One interactive HTML report of all AI chat sessions stored locally by kiro-cli and other tools, across their different storage formats.",
  "Python · SQLite · JSONL", "icon:chat", None, G+"kiro-self-reporting#readme", G+"kiro-self-reporting"),
 ("AI Platform", "Modular, extensible AI / DS / ML platform: traditional and modern AI, NLP, OCR, ML, DL, LLM, GenAI, agents.",
  "Python · architecture", "icon:layers", None, G+"ai_platform#readme", G+"ai_platform"),
 ("OCR Platform", "Cross-platform OCR application (work in progress).", "Flutter · Dart", "icon:scan", None, None, T+"ocr_platform"),
 ("OTA App Test", "Over-the-air update test application.", "C++ · Flutter", "icon:update", None, P+"test_ota_app/", G+"test_ota_app"),
]
INFL = ("Plotly", "dashboard_01_plotly_kaleido"), ("Altair", "dashboard_03_altair"), ("Bokeh", "dashboard_04_bokeh"), \
       ("Great Tables", "dashboard_05_great_tables_summary"), ("Segments", "dashboard_05_great_tables_segments"), ("D3.js", "dashboard_08_d3_js")
INFL_LINKS = "".join(f'<a href="{P}finance/inflation/report/{f}.html">{n}</a>' for n, f in INFL)
DATA = [
 ("Inflation in Poland", "GUS and NBP data pipeline with the same dashboard built in six visualisation libraries.",
  "Python · Plotly · Altair · Bokeh · Great Tables · D3.js", "img:inflation", P+"finance/inflation/report/dashboard_08_d3_js.html",
  None, T+"finance/inflation", INFL_LINKS),
 ("Fuel prices vs Brent oil and USD/PLN", "Brent crude, exchange rate, retail vs wholesale diesel prices and margin analysis.",
  "Python · Plotly · pandas", "img:fuel", P+"war/us_ir/", None, T+"war"),
 ("Iris - exploratory data analysis report", "Reproducible analytical report (Polish).", "Quarto · Python", "img:iris",
  P+"markdown/PA07/iris_report.html", None, T+"markdown"),
 ("SARS-CoV-2 in Poland, Feb-Apr 2020", "Diagrams of tests, cases, recoveries and deaths: cumulative values, daily velocity and acceleration.",
  "data analysis · charts", "img:sars2", P+"virus/sars2/", None, T+"virus"),
 ("Blood groups and population genetics", "ABO / Rh allele frequencies against Global25 PCA population averages.",
  "Python · pandas · matplotlib", "icon:dna", None, None, T+"gen/blood"),
]
NOTES = [
 ("Neural networks from basics", "Activation and loss functions, tensors, training loops.", "Python · PyTorch", "icon:network", None, None, T+"nn"),
 ("OCR with PyTorch", "OCR model notebook on an insurance-document dataset.", "Python · PyTorch", "icon:scan", None, None, T+"ocr"),
 ("LLM agents", "Experiments with the OpenAI API and Google ADK agents.", "Python · LLM · agents", "icon:robot", None, None, T+"agent"),
 ("Visualisation of ML functions", "Seaborn plots and LaTeX figures of regression loss functions.", "Python · seaborn · LaTeX", "icon:chart", None, None, T+"visual"),
 ("Notebook code extractor", "Extracts code cells from Jupyter notebooks into scripts.", "Bash", "icon:terminal", None, None, T+"ipynb2py"),
]

def visual(spec, name, demo):
    """Preview cell: screenshot linked to the demo, or an icon tile."""
    kind, key = spec.split(":")
    if kind == "img":
        img = f'<img src="assets/thumbs/{key}.webp" width="480" height="300" loading="lazy" alt="Screenshot of {html.escape(html.unescape(name))}">'
        return f'<a class="thumb" href="{demo}" tabindex="-1" aria-hidden="true">{img}</a>'
    return f'<span class="thumb icon-tile" aria-hidden="true"><svg><use href="#i-{key}"/></svg></span>'

def link(url, label, icon, none_label):
    """Link cell with an icon, or an em dash when the resource does not exist."""
    if not url:
        return f'<td class="link"><span class="none" aria-label="{none_label}">—</span></td>'
    return f'<td class="link"><a href="{url}"><svg aria-hidden="true"><use href="#i-{icon}"/></svg>{label}</a></td>'

def rows(items):
    """Table rows for a list of projects."""
    out = []
    for it in items:
        name, desc, tags, vis, demo, docs, src = it[:7]
        extra = f'\n      <div class="multi">{it[7]}</div>' if len(it) > 7 else ""
        demo_label = "Demo reports" if name in ("CV Scoring Engine", "Job offers from Kraków BIP and job boards") else "Live demo"
        out.append(f'''<tr>
  <td class="vis">{visual(vis, name, demo)}</td>
  <td><div class="name">{name}</div>
      <div class="desc">{desc}</div>
      <div class="tags">{tags}</div>{extra}</td>
  {link(demo, demo_label, "play", "no live demo")}
  {link(docs, "Docs", "book", "no documentation")}
  {link(src, "Source", "code", "")}
</tr>''')
    return "\n".join(out)

def section(sid, title, icon, items):
    """One titled section with its borderless table."""
    return f'''<section aria-labelledby="{sid}">
<h2 id="{sid}"><svg aria-hidden="true"><use href="#i-{icon}"/></svg>{title}</h2>
<table>
<thead class="sr-only"><tr><th scope="col">Preview</th><th scope="col">Project</th><th scope="col">Live demo</th><th scope="col">Documentation</th><th scope="col">Source code</th></tr></thead>
<tbody>
{rows(items)}
</tbody>
</table>
</section>'''

# Icons: simple 24x24 stroke glyphs (drawn for this page, no external icon set)
ICONS = {
 "play": '<circle cx="12" cy="12" r="9"/><path d="M10 8.5l5.5 3.5-5.5 3.5z" fill="currentColor"/>',
 "book": '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5"/>',
 "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M13.5 4l-3 16"/>',
 "apps": '<rect x="3" y="3" width="7.5" height="7.5" rx="1.5"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="1.5"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="1.5"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.5"/>',
 "chart": '<path d="M3 21h18"/><rect x="5" y="11" width="3" height="7"/><rect x="10.5" y="6" width="3" height="12"/><rect x="16" y="13" width="3" height="5"/>',
 "flask": '<path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2.2h12.4a1.5 1.5 0 0 0 1.3-2.2L14 9V3"/><path d="M7 15h10"/>',
 "phone": '<rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M10.5 18.5h3"/><path d="M12 7v6M9.5 10.5L12 13l2.5-2.5"/>',
 "server": '<rect x="3.5" y="4" width="17" height="6.5" rx="1.5"/><rect x="3.5" y="13.5" width="17" height="6.5" rx="1.5"/><path d="M7 7.25h.01M7 16.75h.01M11 7.25h6M11 16.75h6"/>',
 "chat": '<path d="M4 5h16v10H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
 "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/><path d="M3 17.5l9 5 9-5" opacity=".6"/>',
 "scan": '<path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><path d="M8 9h8M8 12h8M8 15h5"/>',
 "update": '<path d="M20 12a8 8 0 1 1-2.3-5.7"/><path d="M20 4v4h-4"/><path d="M12 8v5l3 2"/>',
 "dna": '<path d="M7 3c0 6 10 6 10 12 0 3-2 5-2 6M17 3c0 6-10 6-10 12 0 3 2 5 2 6"/><path d="M8.5 7h7M8.5 17h7M10 12h4"/>',
 "network": '<circle cx="5" cy="6" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="19" cy="18" r="2"/><path d="M7 6.8l3.2 4M7 17.2l3.2-4M13.8 11.2L17 6.8M13.8 12.8L17 17.2"/>',
 "robot": '<rect x="4.5" y="8" width="15" height="11" rx="3"/><path d="M12 4v4M9 13h.01M15 13h.01M9.5 16.5h5"/><circle cx="12" cy="3.5" r="1"/>',
 "terminal": '<rect x="3" y="4.5" width="18" height="15" rx="2"/><path d="M7 10l3 2.5L7 15M12.5 15H17"/>',
 "github": '<path d="M9 19c-4 1.3-4-2-5.5-2.5M14.5 21v-3.4a3 3 0 0 0-.8-2.3c2.7-.3 5.6-1.3 5.6-6a4.6 4.6 0 0 0-1.3-3.2 4.3 4.3 0 0 0-.1-3.2s-1-.3-3.4 1.3a11.6 11.6 0 0 0-6 0C6.1 2.6 5.1 2.9 5.1 2.9a4.3 4.3 0 0 0-.1 3.2A4.6 4.6 0 0 0 3.7 9.3c0 4.6 2.8 5.6 5.5 6a3 3 0 0 0-.8 2.3V21"/>',
}


def main():
    """Render the template into index.html."""
    sprite = "\n".join(f'  <symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
    page = (Path(__file__).parent / "index.template.html").read_text(encoding="utf-8")
    page = page.replace("@@SPRITE@@", sprite)
    page = page.replace("@@SECTIONS@@", "\n\n".join([
        section("apps", "Applications &amp; tools", "apps", APPS),
        section("data", "Data analysis &amp; dashboards", "chart", DATA),
        section("notes", "Experiments &amp; notes", "flask", NOTES)]))
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print("rows:", len(APPS) + len(DATA) + len(NOTES))


if __name__ == "__main__":
    main()
