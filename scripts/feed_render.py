"""학원 소식(news.json)과 블로그 글(data/blog.json)을 합쳐 메인·소식 페이지 목록을 그립니다.
blog_feed.py(매일 자동)와 build_news.py(소식 추가 시) 둘 다 이 파일을 씁니다."""
import json, re, html, os
from datetime import date, datetime

BLOG = "https://blog.naver.com/dokdaejjang"
# 블로그 제목에 이 단어가 있으면 '학원 소식'에도 자동으로 올립니다.
NOTICE_WORDS = ["설명회", "세미나", "개강", "특강", "모집", "휴원", "휴강", "개원", "공지", "안내", "입학", "레벨테스트"]
NOTICE_DAYS = 60   # 최근 60일 안의 글만 소식으로 올림
HOME_NEWS, HOME_BLOG, PAGE_BLOG = 3, 3, 6
REL = ' rel="noopener"'

def _d(s):  # "2026.10.09" or "2026-10-09" -> date
    try: return datetime.strptime(s.replace("-", ".")[:10], "%Y.%m.%d").date()
    except Exception: return None

def load(root):
    news = json.load(open(f"{root}/news/news.json", encoding="utf-8"))
    try: blog = json.load(open(f"{root}/data/blog.json", encoding="utf-8"))
    except Exception: blog = []
    return news, blog

def is_notice(item, today):
    d = _d(item.get("date", ""))
    if not d or (today - d).days > NOTICE_DAYS: return False
    return any(w in item["title"] for w in NOTICE_WORDS)

def merged_news(news, blog, today):
    linked = {n.get("blog") for n in news if n.get("blog")}
    out = [{"date": n["date"].replace("-", "."), "cat": n["category"], "title": n["title"],
            "desc": n["summary"], "href": f'/news/{n["slug"]}/', "ext": False} for n in news]
    for b in blog:
        if b["link"] in linked or not is_notice(b, today): continue
        out.append({"date": b["date"], "cat": "블로그 공지", "title": b["title"], "desc": b.get("desc", ""), "href": b["link"], "ext": True})
    out.sort(key=lambda x: x["date"], reverse=True)
    return out

def news_cards(items):
    if not items: return '<p class="empty">새 소식을 준비하고 있습니다.</p>'
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
    items = merged_news(news, blog, today)
    changed = []
    for path, parts in [(f"{root}/index.html", {"NEWS": news_cards(items[:HOME_NEWS]), "BLOG": blog_cards(blog[:HOME_BLOG])}),
                        (f"{root}/news/index.html", {"NEWS": news_cards(items), "BLOG": blog_cards(blog[:PAGE_BLOG])})]:
        if not os.path.exists(path): continue
        s = open(path, encoding="utf-8").read(); t = s
        for k, v in parts.items(): t = _put(t, k, v)
        if t != s:
            open(path, "w", encoding="utf-8").write(t); changed.append(path)
    return changed
