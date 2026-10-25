"""news/news.json으로 학원 소식 목록·개별 페이지와 메인 페이지 소식 영역을 만듭니다."""
import json, re, html, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feed_render import render_all
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
lst = "<!--NEWS:START--><!--NEWS:END-->"
ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"블로그 최신 글 | {NAME}", "url": SITE + "/news/"}
body = f'''
<div class="hero"><div class="wrap" style="grid-template-columns:1fr"><div>
<p class="crumb"><a href="/">{NAME}</a> / 블로그 최신 글</p>
<h1 class="slogan" style="font-size:clamp(32px,4.6vw,54px)">블로그 최신 글</h1>
<p class="lead">장독대국어논술학원 네이버 블로그의 최신 글을 모아 보실 수 있습니다.</p></div></div></div>
<section><div class="wrap"><!--BLOG:START--><!--BLOG:END--><a class="more" href="https://blog.naver.com/dokdaejjang" rel="noopener">네이버 블로그 바로가기</a></div></section>
'''
os.makedirs(f"{ROOT}/news", exist_ok=True)
open(f"{ROOT}/news/index.html", "w", encoding="utf-8").write(head(f"블로그 최신 글 | {NAME}", "장독대국어논술학원 네이버 블로그 최신 글입니다.", "/news/", ld) + body + FOOT)
# notice list page
nld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"주요 안내 | {NAME}", "url": SITE + "/notice/"}
nbody = f'''
<div class="hero"><div class="wrap" style="grid-template-columns:1fr"><div>
<p class="crumb"><a href="/">{NAME}</a> / 주요 안내</p>
<h1 class="slogan" style="font-size:clamp(32px,4.6vw,54px)">주요 안내</h1>
<p class="lead">설명회, 특별반 모집, 개강 등 장독대국어논술학원의 주요 안내입니다.</p></div></div></div>
<section><div class="wrap"><!--NEWS:START--><!--NEWS:END--></div></section>
'''
os.makedirs(f"{ROOT}/notice", exist_ok=True)
open(f"{ROOT}/notice/index.html", "w", encoding="utf-8").write(head(f"주요 안내 | {NAME}", "장독대국어논술학원 사직점·명지점의 설명회, 특별반 모집, 개강 안내입니다.", "/notice/", nld) + nbody + FOOT)
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
<p class="crumb"><a href="/">{NAME}</a> / <a href="/notice/">주요 안내</a></p>
<p class="date">{dot(n["date"])} · {html.escape(n["category"])}</p>
<h1 class="slogan" style="font-size:clamp(30px,4.2vw,50px)">{html.escape(n["title"])}</h1>
<p class="lead">{html.escape(n["summary"])}</p>
{n.get("cta","")}</div></div></div>
<section><div class="wrap"><div class="newsbody">
<div>{('<div class="scroll"><table class="tbl"><tbody>' + rows + '</tbody></table></div>') if rows else ''}{paras}</div>{img}
</div><p style="margin-top:28px"><a class="more" href="/notice/">주요 안내 전체 보기</a></p></div></section>
'''
    os.makedirs(f"{ROOT}/news/{n['slug']}", exist_ok=True)
    open(f"{ROOT}/news/{n['slug']}/index.html", "w", encoding="utf-8").write(head(f"{n['title']} | {NAME}", n["summary"], f"/news/{n['slug']}/", ld) + body + FOOT)
# sitemap
sm = f"{ROOT}/sitemap.xml"; x = open(sm, encoding="utf-8").read()
x = re.sub(r'  <url><loc>https://dokdaejjang.kr/(news|notice)/[^<]*</loc>.*?</url>\n', "", x)
add = f"  <url><loc>{SITE}/notice/</loc><lastmod>{news[0]['date'] if news else '2026-10-25'}</lastmod></url>\n" + f"  <url><loc>{SITE}/news/</loc><lastmod>{news[0]['date'] if news else '2026-10-15'}</lastmod></url>\n" + "".join(
    f"  <url><loc>{SITE}/news/{n['slug']}/</loc><lastmod>{n['date']}</lastmod></url>\n" for n in news)
x = x.replace("</urlset>", add + "</urlset>"); open(sm, "w", encoding="utf-8").write(x)
print("news:", len(news), "render:", render_all(ROOT))
