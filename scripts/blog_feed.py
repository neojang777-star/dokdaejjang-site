"""네이버 블로그 RSS를 읽어 index.html의 '블로그 최신 글' 영역을 갱신합니다.
GitHub Actions에서 하루 한 번 실행됩니다. 외부 라이브러리 없이 동작합니다."""
import re, sys, html, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

RSS = "https://rss.blog.naver.com/dokdaejjang.xml"
BLOG = "https://blog.naver.com/dokdaejjang"
COUNT = 3
START, END = "<!--BLOG:START-->", "<!--BLOG:END-->"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (dokdaejjang.kr blog feed)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def clean(text, limit):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[:limit].rstrip() + "…"

def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    items = []
    for it in root.iter("item"):
        title = clean(it.findtext("title"), 60)
        link = (it.findtext("link") or "").strip().split("?")[0]
        desc = clean(it.findtext("description"), 90)
        date = ""
        try:
            date = parsedate_to_datetime(it.findtext("pubDate")).strftime("%Y.%m.%d")
        except Exception:
            pass
        if title and link.startswith("https://blog.naver.com/"):
            items.append({"title": title, "link": link, "desc": desc, "date": date})
    return items[:COUNT]

def render(items):
    if not items:
        return '<p class="empty">블로그 글을 불러오는 중입니다.</p>'
    cards = "".join(
        f'<li><a href="{html.escape(i["link"])}" rel="noopener"><span class="date">{i["date"]}</span>'
        f'<b>{html.escape(i["title"])}</b>'
        + (f'<span class="desc">{html.escape(i["desc"])}</span>' if i["desc"] else "")
        + "</a></li>"
        for i in items)
    return f'<ul class="feed">{cards}</ul>'

def main(path="index.html"):
    try:
        items = parse(fetch(RSS))
    except Exception as e:
        print("RSS 읽기 실패:", e)
        return 0  # 실패해도 기존 목록 유지
    page = open(path, encoding="utf-8").read()
    if START not in page:
        print("표시 영역을 찾지 못했습니다.")
        return 1
    new = re.sub(re.escape(START) + ".*?" + re.escape(END), START + render(items) + END, page, flags=re.S)
    if new != page:
        open(path, "w", encoding="utf-8").write(new)
        print("갱신:", [i["title"] for i in items])
    else:
        print("변경 없음")
    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
