import json, re, os, html
SITE="https://dokdaejjang.kr"; NAME="장독대국어논술학원"
BR={"sajik":dict(name="사직점",addr="부산광역시 연제구 종합운동장로 26, 대운빌딩 2층·8층",tel="051-504-3578",tellabel="중고등 051-504-3578",telraw="0515043578"),
    "myeongji":dict(name="명지점",addr="부산광역시 강서구 명지국제8로 271, 8층",tel="051-207-3578",tellabel="051-207-3578",telraw="0512073578")}
def load_tpl(ROOT):
    tpl=open(f"{ROOT}/school/sajikjung/index.html").read()
    return tpl[:tpl.index("<main>")+6], tpl[tpl.index("</main>"):]
def faq_html(items): return "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in items)
def faq_ld(items): return {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in items]}
def set_meta(h,title,desc):
    h=re.sub(r"<title>.*?</title>",f"<title>{html.escape(title)}</title>",h)
    h=re.sub(r'(name="description" content=")[^"]*',lambda m:m.group(1)+html.escape(desc),h)
    h=re.sub(r'(property="og:title" content=")[^"]*',lambda m:m.group(1)+html.escape(title),h)
    h=re.sub(r'(property="og:description" content=")[^"]*',lambda m:m.group(1)+html.escape(desc),h)
    return h
def set_ld(h,ld):
    return re.sub(r'<script type="application/ld\+json">.*?</script>',lambda m:'<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False)+'</script>',h,count=1,flags=re.S)
def ld_for(slug,headline,school,faq,br,date):
    b=BR[br]
    return {"@context":"https://schema.org","@graph":[
      {"@type":"Article","headline":headline,"datePublished":date,"inLanguage":"ko","author":{"@type":"Person","name":"장양우"},
       "publisher":{"@id":SITE+"/#org","name":NAME},"about":[f"{school} 국어 시험","국어 내신 대비"],"mainEntityOfPage":f"{SITE}/school/{slug}/"},
      {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":NAME,"item":SITE+"/"},
        {"@type":"ListItem","position":2,"name":b["name"],"item":f"{SITE}/{br}/"},
        {"@type":"ListItem","position":3,"name":f"{school} 국어 시험 분석","item":f"{SITE}/school/{slug}/"}]},
      faq_ld(faq)]}
def hero(school,title,lead,br):
    b=BR[br]
    return f"""
<div class="hero"><div class="wrap" style="grid-template-columns:1fr">
<div><p class="crumb"><a href="/">{NAME}</a> / <a href="/{br}/">{b["name"]}</a> / {school}</p>
<h1 class="slogan" style="font-size:clamp(32px,4.6vw,54px)">{title}</h1>
<p class="lead">{lead}</p>
<div class="cta"><a class="btn solid" href="tel:{b["telraw"]}">{school} 내신반 상담 {b["tel"]}</a><a class="btn" href="/{br}/">{b["name"]} 안내</a></div></div>
</div></div>"""
def ban(school,fee,br):
    b=BR[br]
    return f"""
<section><div class="wrap"><h2>장독대 {school} 내신반</h2><div class="branches"><div class="branch"><dl>
<dt>지점</dt><dd>{b["name"]}, {b["addr"]}</dd><dt>운영</dt><dd>시험 기간에 {school} 내신반을 별도 시간표로 운영</dd>
<dt>교재</dt><dd>자체 교재</dd><dt>클리닉</dt><dd>수~금 오후 3시~10시 중 학생별 지정</dd></dl></div>
<div class="branch"><dl><dt>상담</dt><dd>{b["tellabel"]}</dd><dt>교습비</dt><dd>{fee}</dd><dt>입학</dt><dd>진단 테스트 후 반 배정</dd></dl></div></div></div></section>"""
HIGH="고등A 월 30만 원, 고등B 월 35만 원"; MID="중등 월 23만 원"
def steps(items):
    return '<ol class="steps">'+"".join(f"<li><b>{a}</b><span>{b}</span></li>" for a,b in items)+"</ol>"
def table(rows,head=None):
    th=("<thead><tr>"+"".join(f"<th>{x}</th>" for x in head)+"</tr></thead>") if head else ""
    tr="".join("<tr><th>"+r[0]+"</th>"+"".join(f"<td>{c}</td>" for c in r[1:])+"</tr>" for r in rows)
    return f'<div class="scroll"><table class="tbl">{th}<tbody>{tr}</tbody></table></div>'
def two(left,right): return f'<div class="two"><div>{left}</div><div>{right}</div></div>'
def h3(t,first=False): return f'<h3 style="margin:{"0" if first else "20px"} 0 8px">{t}</h3>'
def new_page(ROOT,school,slug,br,title,desc,h1,lead,sections,faq,prep,fee,headline,date):
    HEAD,FOOT=load_tpl(ROOT)
    h=set_meta(HEAD,title,desc).replace("/school/sajikjung/",f"/school/{slug}/")
    h=set_ld(h,ld_for(slug,headline,school,faq,br,date))
    body=hero(school,h1,lead,br)+sections+f'\n<section class="alt"><div class="wrap"><h2>기말고사를 위한 준비 포인트</h2>{steps(prep)}</div></section>'+ban(school,fee,br)+f'\n<section class="faq"><div class="wrap"><h2>{school} 국어 자주 묻는 질문</h2>{faq_html(faq)}</div></section>\n'
    os.makedirs(f"{ROOT}/school/{slug}",exist_ok=True)
    open(f"{ROOT}/school/{slug}/index.html","w").write(h+body+FOOT)
def update_page(ROOT,slug,title,desc,h1,lead,renames,insert_html,add_faq,headline):
    p=f"{ROOT}/school/{slug}/index.html"; s=open(p).read()
    s=set_meta(s,title,desc)
    s=re.sub(r'(<h1 class="slogan"[^>]*>).*?(</h1>)',lambda m:m.group(1)+h1+m.group(2),s,count=1)
    s=re.sub(r'(<p class="lead">).*?(</p>)',lambda m:m.group(1)+lead+m.group(2),s,count=1)
    for a,b in renames: s=s.replace(a,b)
    i=s.find('<h2>기말고사를 위한 준비 포인트</h2>'); i=s.rfind('<section',0,i)
    s=s[:i]+insert_html+s[i:]
    d=json.loads(re.search(r'ld\+json">(.*?)</script>',s,re.S).group(1))
    d["@graph"][0]["headline"]=headline
    faq=d["@graph"][2]["mainEntity"]
    for q,a in add_faq:
        faq.append({"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}})
        k=s.rfind('</details>')+len('</details>'); s=s[:k]+f"<details><summary>{q}</summary><p>{a}</p></details>"+s[k:]
    s=set_ld(s,d); open(p,"w").write(s)
def link_chip(ROOT,school,slug,files):
    for f in files:
        p=f"{ROOT}/{f}"; s=open(p).read()
        s=s.replace(f"<li>{school}</li>",f'<li class="has-page"><a href="/school/{slug}/">{school} 시험 분석</a></li>'); open(p,"w").write(s)
def sitemap(ROOT,slug,date):
    p=f"{ROOT}/sitemap.xml"; s=open(p).read()
    s=re.sub(rf'  <url><loc>{SITE}/school/{slug}/</loc>.*?</url>\n',"",s)
    s=s.replace("</urlset>",f"  <url><loc>{SITE}/school/{slug}/</loc><lastmod>{date}</lastmod></url>\n</urlset>"); open(p,"w").write(s)
def llms(ROOT,slug,line):
    p=f"{ROOT}/llms.txt"; s=open(p).read()
    s=re.sub(rf"- [^\n]*{SITE}/school/{slug}/\n","",s)
    s=s.replace("\n\n## 대표원장",f"\n- {line}: {SITE}/school/{slug}/\n\n## 대표원장",1); open(p,"w").write(s)
