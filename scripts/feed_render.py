"""블로그 글(data/blog.json)과 주요 안내(news.json)로 메인·주요 안내·블로그 최신 글 목록을 그립니다.
blog_feed.py(매일 자동)와 build_news.py(소식 추가 시) 둘 다 이 파일을 씁니다."""
import json, re, html, os
from datetime import date, datetime

BLOG = "https://blog.naver.com/dokdaejjang"
HOME_NOTICE, HOME_BLOG, PAGE_BLOG = 3, 4, 10
REL = ' rel="noopener"'

def _d(s):  # "2026.10.09" or "2026-10-09" -> date
    try: return datetime.strptime(s.replace("-", ".")[:10], "%Y.%m.%d").date()
    except Exception: return None

def load(root):
    news = json.load(open(f"{root}/news/news.json", encoding="utf-8"))
    try: blog = json.load(open(f"{root}/data/blog.json", encoding="utf-8"))
    except Exception: blog = []
    return news, blog

def notices(news, today):
    out = []
    for n in news:
        end = _d(n.get("end", "")) if n.get("end") else None
        out.append({"date": n["date"].replace("-", "."), "cat": n["category"], "title": n["title"], "desc": n["summary"],
                    "href": f'/news/{n["slug"]}/', "img": (f'/news/{n["slug"]}/{n["image"]}' if n.get("image") else ""),
                    "closed": bool(end and today > end)})
    out.sort(key=lambda x: x["date"], reverse=True)
    out.sort(key=lambda x: x["closed"])  # 진행 중인 안내가 먼저
    return out

def notice_cards(items):
    if not items: return '<p class="empty">현재 주요 안내가 없습니다.</p>'
    cards = []
    for i in items:
        badge = '<span class="badge closed">마감</span>' if i["closed"] else '<span class="badge">진행 중</span>'
        img = f'<img src="{i["img"]}" alt="" loading="lazy">' if i["img"] else ""
        cls = ' class="is-closed"' if i["closed"] else ""
        cards.append(f'<li{cls}><a href="{html.escape(i["href"])}">{img}<div>'
                     f'<span class="date">{badge}{i["date"]} · {html.escape(i["cat"])}</span><b>{html.escape(i["title"])}</b>'
                     f'<span class="desc">{html.escape(i["desc"])}</span></div></a></li>')
    return '<ul class="notices">' + "".join(cards) + '</ul>'

def blog_cards(blog):
    if not blog: return '<p class="empty">블로그 글을 불러오는 중입니다.</p>'
    li = "".join(f'<li><a href="{html.escape(b["link"])}" rel="noopener"><span class="date">{b["date"]}</span>'
                 f'<b>{html.escape(b["title"])}</b>' + (f'<span class="desc">{html.escape(b["desc"])}</span>' if b.get("desc") else "") + "</a></li>"
                 for b in blog)
    return f'<ul class="feed">{li}</ul>'

def _put(s, key, content):
    a, b = f"<!--{key}:START-->", f"<!--{key}:END-->"
    return re.sub(re.escape(a) + ".*?" + re.escape(b), lambda m: a + content + b, s, flags=re.S) if a in s else s

def render_all(root, today=None):
    today = today or date.today()
    news, blog = load(root)
    items = notices(news, today)
    changed = []
    for path, parts in [(f"{root}/index.html", {"NEWS": notice_cards(items[:HOME_NOTICE]), "BLOG": blog_cards(blog[:HOME_BLOG])}),
                        (f"{root}/notice/index.html", {"NEWS": notice_cards(items)}),
                        (f"{root}/news/index.html", {"BLOG": blog_cards(blog[:PAGE_BLOG])})]:
        if not os.path.exists(path): continue
        s = open(path, encoding="utf-8").read(); t = s
        for k, v in parts.items(): t = _put(t, k, v)
        if t != s:
            open(path, "w", encoding="utf-8").write(t); changed.append(path)
    return changed
