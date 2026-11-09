# -*- coding: utf-8 -*-
"""Build a single RTL Persian PDF-ready HTML from the Docker course markdown files."""
import re, pathlib, markdown
from pygments.formatters import HtmlFormatter

BASE = pathlib.Path(__file__).resolve().parent.parent
BUILD = BASE / "build"

CHAPTERS = [
    ("README.md", "شروع دوره"),
    ("01-what-why.md", "فصل ۱ — داکر چیست و چرا"),
    ("02-install.md", "فصل ۲ — نصب و hello-world"),
    ("03-run-containers.md", "فصل ۳ — اجرای کانتینرها"),
    ("04-images.md", "فصل ۴ — ایمیج‌ها و Docker Hub"),
    ("05-inside-containers.md", "فصل ۵ — داخل کانتینر و دیباگ"),
    ("06-dockerfile.md", "فصل ۶ — اولین Dockerfile"),
    ("07-optimize.md", "فصل ۷ — multi-stage و کاهش حجم"),
    ("08-compose.md", "فصل ۸ — Docker Compose"),
    ("09-volumes.md", "فصل ۹ — داده ماندگار"),
    ("10-networking.md", "فصل ۱۰ — شبکه کانتینرها"),
    ("11-dev-workflow.md", "فصل ۱۱ — استک Next.js + Postgres 🚀"),
    ("12-push-deploy.md", "فصل ۱۲ — push و دپلوی"),
    ("13-cheatsheet.md", "فصل ۱۳ — چیت‌شیت و گلاساری"),
]

ANCHOR = {fn: f"ch{i:02d}" for i, (fn, _) in enumerate(CHAPTERS)}
LINK_RE = re.compile(r"\]\((\.?/?)([\w\-]+\.md)([#\w\-]*)\)")

MD_EXT = ["tables", "fenced_code", "codehilite", "md_in_html", "attr_list", "sane_lists"]
MD_CFG = {"codehilite": {"guess_lang": False}}


def preprocess(text: str) -> str:
    def repl(m):
        target, frag = m.group(2), m.group(3) or ""
        if target in ANCHOR:
            return f"](#{ANCHOR[target]}{frag})"
        return m.group(0)
    text = LINK_RE.sub(repl, text)
    text = re.sub(r"```mermaid\n(.*?)```", lambda m: f'<div class="mermaid">\n{m.group(1)}</div>', text, flags=re.S)
    text = text.replace("<details>", '<details markdown="1" open>')
    text = text.replace("<summary>", '<summary markdown="span">')
    return text


def render_chapter(fn: str, idx: int) -> str:
    raw = (BASE / fn).read_text(encoding="utf-8")
    body = markdown.markdown(preprocess(raw), extensions=MD_EXT, extension_configs=MD_CFG)
    return f'<section class="chapter" id="ch{idx:02d}">{body}</section>'


CSS = """
@font-face { font-family:'Vazirmatn'; src:url('fonts/Vazirmatn-Regular.ttf') format('truetype'); font-weight:400; }
@font-face { font-family:'Vazirmatn'; src:url('fonts/Vazirmatn-Medium.ttf') format('truetype'); font-weight:500; }
@font-face { font-family:'Vazirmatn'; src:url('fonts/Vazirmatn-Bold.ttf') format('truetype'); font-weight:700; }
@font-face { font-family:'JetBrains Mono'; src:url('fonts/JetBrainsMono-Regular.ttf') format('truetype'); font-weight:400; }
@font-face { font-family:'JetBrains Mono'; src:url('fonts/JetBrainsMono-Bold.ttf') format('truetype'); font-weight:700; }

@page { size: A4; margin: 16mm 13mm 18mm 13mm; }

:root {
  --ink:#0f1f17; --muted:#5f6f66; --line:#dde7e1;
  --primary:#047857; --primary-soft:#ecfdf5;
  --accent:#b45309; --accent-soft:#fffbeb;
  --green:#059669; --green-soft:#ecfdf5;
  --amber:#b45309; --amber-soft:#fffbeb;
  --rose:#be123c; --rose-soft:#fff1f2;
  --code-bg:#0b2920; --code-ink:#e2e8f0;
}
* { box-sizing:border-box; }
html { -webkit-print-color-adjust:exact; print-color-adjust:exact; }
body {
  direction:rtl; text-align:right;
  font-family:'Vazirmatn', Tahoma, sans-serif;
  color:var(--ink); font-size:11.2pt; line-height:2;
  margin:0; padding:0;
}

/* cover */
.cover {
  page-break-after:always; height:250mm;
  display:flex; flex-direction:column; justify-content:center; align-items:center;
  text-align:center; color:#fff; border-radius:14px; padding:20mm;
  background:linear-gradient(135deg,#052e22 0%,#047857 50%,#0d9488 100%);
}
.cover .badge { background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.35);
  padding:4px 18px; border-radius:999px; font-size:10pt; letter-spacing:.3px; }
.cover h1 { font-size:30pt; line-height:1.6; margin:14px 0 6px; border:none; color:#fff; background:none; }
.cover h2 { font-size:14pt; font-weight:500; color:#d1fae5; border:none; margin:0; }
.cover .stack { display:flex; gap:10px; margin-top:26px; flex-wrap:wrap; justify-content:center; }
.cover .stack span { background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.3);
  border-radius:10px; padding:6px 16px; font-size:10.5pt; }
.cover .foot { margin-top:40px; font-size:9.5pt; opacity:.85; }

/* toc */
.toc { page-break-after:always; }
.toc h1 { border:none; }
.toc ol { list-style:none; padding:0; counter-reset:toc; }
.toc li { counter-increment:toc; border-bottom:1px dashed var(--line);
  padding:9px 2px; display:flex; justify-content:space-between; align-items:baseline; }
.toc a { text-decoration:none; color:var(--ink); font-weight:500; }
.toc li::before { content:counter(toc); background:var(--primary-soft); color:var(--primary);
  font-weight:700; border-radius:8px; width:30px; height:30px; display:inline-flex;
  align-items:center; justify-content:center; margin-left:14px; flex:none; }
.toc li .desc { color:var(--muted); font-size:9.5pt; }

/* chapters / headings */
.chapter { page-break-before:always; }
h1 {
  font-size:19pt; color:#fff; background:linear-gradient(90deg,#065f46,#059669);
  padding:14px 22px; border-radius:12px; line-height:1.7;
  margin:0 0 18px; page-break-after:avoid;
}
h2 {
  color:var(--primary); font-size:14.5pt; margin:26px 0 10px;
  padding-right:12px; border-right:4px solid var(--primary); line-height:1.8;
  page-break-after:avoid;
}
h3 { color:var(--accent); font-size:12.5pt; margin:20px 0 8px; page-break-after:avoid; }
p { margin:8px 0; }
strong { color:#064e3b; }
a { color:var(--primary); text-decoration:none; }

/* lists */
ul, ol { padding-right:1.6em; padding-left:0; margin:8px 0; }
li { margin:3px 0; }
li::marker { color:var(--primary); font-weight:700; }
input[type="checkbox"] { accent-color:var(--primary); }

/* tables */
table { border-collapse:collapse; width:100%; margin:12px 0; font-size:10pt;
  border-radius:10px; overflow:hidden; page-break-inside:avoid; }
th { background:linear-gradient(90deg,#065f46,#059669); color:#fff; font-weight:700; }
th, td { border:1px solid #d3e4dc; padding:6px 10px; text-align:right; vertical-align:top; }
tbody tr:nth-child(even) { background:#f6faf8; }

/* code */
pre, code, kbd { font-family:'JetBrains Mono','Vazirmatn',Consolas,monospace; direction:ltr; }
code { background:#ecfdf5; color:#047857; padding:1px 6px; border-radius:5px;
  font-size:8.8pt; unicode-bidi:embed; }
pre { background:var(--code-bg); color:var(--code-ink); direction:ltr; text-align:left;
  padding:13px 16px; border-radius:12px; overflow-x:hidden; font-size:8.6pt;
  line-height:1.65; margin:10px 0; border:1px solid #134e4a; page-break-inside:avoid; }
pre code { background:none; color:inherit; padding:0; font-size:inherit; }
.codehilite { background:var(--code-bg); border-radius:12px; margin:10px 0; page-break-inside:avoid; }
.codehilite pre { margin:0; border:none; }
.codehilite .k,.codehilite .kd,.codehilite .kn,.codehilite .ow { color:#6ee7b7; }
.codehilite .s,.codehilite .s1,.codehilite .s2,.codehilite .sd { color:#fde68a; }
.codehilite .n,.codehilite .na,.codehilite .nx { color:#e2e8f0; }
.codehilite .nf { color:#a5f3fc; }
.codehilite .mi,.codehilite .mf { color:#fda4af; }
.codehilite .o,.codehilite .p { color:#94a3b8; }
.codehilite .nb,.codehilite .nv { color:#5eead4; }
.codehilite .err { color:#e2e8f0; background:none; border:none; }
.codehilite .c,.codehilite .c1,.codehilite .cm,.codehilite .cp { color:#6ee7b7 !important; font-style:italic; }
.codehilite .nt { color:#f0abfc; }
.codehilite .nd { color:#a5f3fc; }

/* blockquotes */
blockquote {
  margin:12px 0; padding:10px 16px; border-radius:12px;
  border-right:5px solid var(--primary); background:var(--primary-soft);
  page-break-inside:avoid;
}
blockquote p { margin:4px 0; }
blockquote p:first-child { font-weight:500; }
blockquote:has(> p:first-child strong:contains("⚠")) { background:var(--amber-soft); border-right-color:var(--amber); }
blockquote:has(> p:first-child strong:contains("🚨")) { background:var(--rose-soft); border-right-color:var(--rose); }
blockquote:has(> p:first-child strong:contains("💡")) { background:var(--green-soft); border-right-color:var(--green); }
blockquote:has(> p:first-child strong:contains("🔑")) { background:var(--green-soft); border-right-color:var(--green); }
blockquote:has(> p:first-child strong:contains("🎯")) { background:var(--primary-soft); border-right-color:var(--primary); }
blockquote:has(> p:first-child strong:contains("⭐")) { background:var(--accent-soft); border-right-color:var(--accent); }

/* hr, details */
hr { border:none; border-top:2px dashed var(--line); margin:22px 0; }
details { background:#f6faf8; border:1px solid var(--line); border-radius:10px;
  padding:8px 14px; margin:10px 0; page-break-inside:avoid; }
summary { cursor:pointer; font-weight:700; color:var(--green); }

/* mermaid */
.mermaid {
  background:#fff; border:1px solid var(--line); border-radius:12px;
  padding:10px; margin:12px 0; text-align:center; page-break-inside:avoid;
  display:flex; justify-content:center;
}
.mermaid svg { max-width:100%; height:auto; }

del { color:var(--muted); }
em { color:#134e4a; }
"""

PYGMENTS_CSS = HtmlFormatter(style="default").get_style_defs(".codehilite")

COVER = """
<section class="cover">
  <div class="badge">آموزش صفر تا صد — نسخه سپتامبر ۲۰۲۶</div>
  <h1>Docker<br/>از صفر مطلق تا دپلوی واقعی</h1>
  <h2>بسته‌بندی، اجرا و توزیع پروژه‌های Next.js در کانتینر</h2>
  <div class="stack">
    <span>Docker Engine 29</span><span>Dockerfile</span><span>Multi-stage</span>
    <span>Compose v2</span><span>Volumes</span><span>Deploy on VPS</span>
  </div>
  <div class="foot">۱۳ فصل · استک کامل Next.js + PostgreSQL + Prisma · تمرین با جواب · ۱۲ ارور کلاسیک</div>
</section>
"""

DESCS = {
    "README.md": "نقشه دوره و زمین تمرین",
    "01-what-why.md": "image/container/registry، کانتینر vs VM",
    "02-install.md": "Docker Desktop، WSL2، تأیید سلامت",
    "03-run-containers.md": "run، -p، logs، ps، چرخه عمر",
    "04-images.md": "pull، تگ‌ها، لایه‌ها، Alpine",
    "05-inside-containers.md": "exec -it، env، inspect، چرخه دیباگ",
    "06-dockerfile.md": "FROM/COPY/RUN/CMD، کش لایه‌ها",
    "07-optimize.md": "multi-stage، omit=dev، کاهش حجم",
    "08-compose.md": "YAML، up/down، استک api+db",
    "09-volumes.md": "named volume، bind mount، بکاپ",
    "10-networking.md": "DNS داخلی، hostname سرویس‌ها",
    "11-dev-workflow.md": "Next.js + Postgres + Prisma در عمل",
    "12-push-deploy.md": "push، GHCR، VPS، امنیت",
    "13-cheatsheet.md": "مرور سریع + ۱۲ ارور کلاسیک",
}


def build_toc() -> str:
    items = []
    for i, (fn, title) in enumerate(CHAPTERS):
        items.append(f'<li><a href="#ch{i:02d}">{title}</a><span class="desc">{DESCS.get(fn, "")}</span></li>')
    return f'<section class="toc"><h1>فهرست مطالب</h1><ol>{"".join(items)}</ol></section>'


def main():
    parts = [COVER, build_toc()]
    for i, (fn, _) in enumerate(CHAPTERS):
        parts.append(render_chapter(fn, i))
    html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl"><head><meta charset="utf-8"/>
<title>دوره Docker</title>
<style>{CSS}
{PYGMENTS_CSS}
</style></head>
<body>{''.join(parts)}
<script src="mermaid.min.js"></script>
<script>mermaid.initialize({{ startOnLoad:true, theme:'base',
  themeVariables: {{ fontFamily:'Vazirmatn, Tahoma', fontSize:'13px',
    primaryColor:'#ecfdf5', primaryBorderColor:'#047857', primaryTextColor:'#0f1f17',
    lineColor:'#64748b', secondaryColor:'#fffbeb', tertiaryColor:'#f6faf8' }},
  flowchart: {{ htmlLabels:true, curve:'basis' }} }});</script>
</body></html>"""
    out = BUILD / "course.html"
    out.write_text(html, encoding="utf-8")
    print("OK -> course.html (" + str(round(len(html)/1024)) + " KB)")


if __name__ == "__main__":
    main()
