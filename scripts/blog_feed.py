"""네이버 블로그 RSS를 읽어 data/blog.json에 저장하고, 메인·소식 페이지의 목록을 갱신합니다.
GitHub Actions에서 하루 한 번 실행됩니다. 외부 라이브러리 없이 동작합니다."""
import re, sys, os, json, html, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feed_render import render_all

RSS = "https://rss.blog.naver.com/dokdaejjang.xml"
KEEP = 20

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (dokdaejjang.kr blog feed)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def clean(text, limit):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return text if len(text) <= limit else text[:limit].rstrip() + "…"

def parse(xml_bytes):
    items = []
    for it in ET.fromstring(xml_bytes).iter("item"):
        title = clean(it.findtext("title"), 60)
        link = (it.findtext("link") or "").strip().split("?")[0]
        desc = clean(it.findtext("description"), 90)
        try: d = parsedate_to_datetime(it.findtext("pubDate")).strftime("%Y.%m.%d")
        except Exception: d = ""
        if title and link.startswith("https://blog.naver.com/"):
            items.append({"title": title, "link": link, "desc": desc, "date": d})
    return items[:KEEP]

def main(index_path="index.html"):
    root = os.path.dirname(os.path.abspath(index_path))
    try:
        items = parse(fetch(RSS))
        if items:
            json.dump(items, open(f"{root}/data/blog.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("블로그 글:", [i["title"] for i in items[:5]])
    except Exception as e:
        print("RSS 읽기 실패, 기존 목록 유지:", e)
    print("갱신된 파일:", render_all(root) or "없음")
    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
