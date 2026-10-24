"""블로그 글(data/blog.json)과 주요 안내(news.json)로 메인·블로그 최신 글 페이지 목록을 그립니다.
blog_feed.py(매일 자동)와 build_news.py(소식 추가 시) 둘 다 이 파일을 씁니다."""
import json, re, html, os
from datetime import date, datetime

BLOG = "https://blog.naver.com/dokdaejjang"
HOME_BLOG, PAGE_BLOG = 4, 10
REL = ' rel="noopener"'

def _d(s):  # "2026.10.09" or "2026-10-09" -> date
    try: return datetime.strptime(s.replace("-", ".")[:10], "%Y.%m.%d").date()
    except Exception: return None

def load(root):
    news = json.load(open(f"{root}/news/news.json", encoding="utf-8"))
    try: blog = json.load(open(f"{root}/data/blog.json", encoding="utf-8"))
    except Exception: blog = []
    return news, blog

def notices(news):
    out = [{"date": n["date"].replace("-", "."), "cat": n["category"], "title": n["title"],
            "desc": n["summary"], "href": f'/news/{n["slug"]}/', "ext": False} for n in news]
    out.sort(key=lambda x: x["date"], reverse=True)
    return out

def news_cards(items):
    if not items: return '<p class="empty">현재 주요 안내가 없습니다.</p>'
    li = "".join(f'<li><a href="{html.escape(i["href"])}"{REL if i["ext"] else ""}>'
                 f'<span class="date">{i["date"]} · {html.escape(i["cat"])}</span><b>{html.escape(i["title"])}</b>'
                 + (f'<span class="desc">{html.escape(i["desc"])}</span>' if i["desc"] else "") + "</a></li>" for i in items)
    return f'<ul class="feed">{li}</ul>'

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
    items = notices(news)
    changed = []
    for path, parts in [(f"{root}/index.html", {"BLOG": blog_cards(blog[:HOME_BLOG])}),
                        (f"{root}/news/index.html", {"NEWS": news_cards(items), "BLOG": blog_cards(blog[:PAGE_BLOG])})]:
        if not os.path.exists(path): continue
        s = open(path, encoding="utf-8").read(); t = s
        for k, v in parts.items(): t = _put(t, k, v)
        if t != s:
            open(path, "w", encoding="utf-8").write(t); changed.append(path)
    return changed
