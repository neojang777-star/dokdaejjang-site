"""news/news.json으로 학원 소식 목록·개별 페이지와 메인 페이지 소식 영역을 만듭니다."""
import json, re, html, os, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SITE = "https://dokdaejjang.kr"; NAME = "장독대국어논술학원"
START, END = "<!--NEWS:START-->", "<!--NEWS:END-->"
news = json.load(open(f"{ROOT}/news/news.json", encoding="utf-8"))
news.sort(key=lambda n: n["date"], reverse=True)
tpl = open(f"{ROOT}/sajik/index.html", encoding="utf-8").read()
HEAD = tpl[:tpl.index("<main>") + 6]; FOOT = tpl[tpl.index("</main>"):]
def head(title, desc, path, ld):
    h = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", HEAD)
    for k in ['name="description"', 'property="og:description"']:
        h = re.sub(rf'({k} content=")[^"]*', lambda m: m.group(1) + html.escape(desc), h)
    h = re.sub(r'(property="og:title" content=")[^"]*', lambda m: m.group(1) + html.escape(title), h)
    h = h.replace(f"{SITE}/sajik/", f"{SITE}{path}")
    return re.sub(r'<script type="application/ld\+json">.*?</script>',
                  lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', h, flags=re.S)
def dot(d): return d.replace("-", ".")
def card(n):
    return (f'<li><a href="/news/{n["slug"]}/"><span class="date">{dot(n["date"])} · {html.escape(n["category"])}</span>'
            f'<b>{html.escape(n["title"])}</b><span class="desc">{html.escape(n["summary"])}</span></a></li>')
EMPTY = '<p class="empty">새 소식을 준비하고 있습니다.</p>'
# list page
lst = "<ul class=\"feed\">" + "".join(card(n) for n in news) + "</ul>" if news else EMPTY
ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"학원 소식 | {NAME}", "url": SITE + "/news/"}
body = f'''
<div class="hero"><div class="wrap" style="grid-template-columns:1fr"><div>
<p class="crumb"><a href="/">{NAME}</a> / 학원 소식</p>
<h1 class="slogan" style="font-size:clamp(32px,4.6vw,54px)">학원 소식</h1>
<p class="lead">설명회, 개강, 특강 등 장독대국어논술학원의 새 소식을 알려 드립니다.</p></div></div></div>
<section><div class="wrap">{lst}</div></section>
'''
os.makedirs(f"{ROOT}/news", exist_ok=True)
open(f"{ROOT}/news/index.html", "w", encoding="utf-8").write(head(f"학원 소식 | {NAME}", "장독대국어논술학원 사직점·명지점의 설명회, 개강, 특강 소식입니다.", "/news/", ld) + body + FOOT)
# item pages
for n in news:
    rows = "".join(f"<tr><th>{html.escape(k)}</th><td>{html.escape(v)}</td></tr>" for k, v in n.get("facts", []))
    paras = "".join(f"<p>{html.escape(p)}</p>" for p in n.get("body", []))
    img = (f'<figure class="poster"><img src="/news/{n["slug"]}/{n["image"]}" alt="{html.escape(n["title"])} 포스터" loading="lazy"></figure>' if n.get("image") else "")
    ev = n.get("event")
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "NewsArticle", "headline": n["title"], "datePublished": n["date"], "inLanguage": "ko",
         "author": {"@type": "Organization", "name": NAME}, "mainEntityOfPage": f"{SITE}/news/{n['slug']}/"}]}
    if ev: ld["@graph"].append(ev)
    if n.get("event2"): ld["@graph"].append(n["event2"])
    body = f'''
<div class="hero"><div class="wrap" style="grid-template-columns:1fr"><div>
<p class="crumb"><a href="/">{NAME}</a> / <a href="/news/">학원 소식</a></p>
<p class="date">{dot(n["date"])} · {html.escape(n["category"])}</p>
<h1 class="slogan" style="font-size:clamp(30px,4.2vw,50px)">{html.escape(n["title"])}</h1>
<p class="lead">{html.escape(n["summary"])}</p>
{n.get("cta","")}</div></div></div>
<section><div class="wrap"><div class="newsbody">
<div>{('<div class="scroll"><table class="tbl"><tbody>' + rows + '</tbody></table></div>') if rows else ''}{paras}</div>{img}
</div><p style="margin-top:28px"><a class="more" href="/news/">학원 소식 전체 보기</a></p></div></section>
'''
    os.makedirs(f"{ROOT}/news/{n['slug']}", exist_ok=True)
    open(f"{ROOT}/news/{n['slug']}/index.html", "w", encoding="utf-8").write(head(f"{n['title']} | {NAME}", n["summary"], f"/news/{n['slug']}/", ld) + body + FOOT)
# home block
home = f"{ROOT}/index.html"; s = open(home, encoding="utf-8").read()
block = ("<ul class=\"feed\">" + "".join(card(n) for n in news[:3]) + "</ul>") if news else EMPTY
s = re.sub(re.escape(START) + ".*?" + re.escape(END), START + block + END, s, flags=re.S)
open(home, "w", encoding="utf-8").write(s)
# sitemap
sm = f"{ROOT}/sitemap.xml"; x = open(sm, encoding="utf-8").read()
x = re.sub(r'  <url><loc>https://dokdaejjang.kr/news/[^<]*</loc>.*?</url>\n', "", x)
add = f"  <url><loc>{SITE}/news/</loc><lastmod>{news[0]['date'] if news else '2026-10-15'}</lastmod></url>\n" + "".join(
    f"  <url><loc>{SITE}/news/{n['slug']}/</loc><lastmod>{n['date']}</lastmod></url>\n" for n in news)
x = x.replace("</urlset>", add + "</urlset>"); open(sm, "w", encoding="utf-8").write(x)
print("news:", len(news))
