#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
연세대학교 경영대학 오퍼레이션 전공 홈페이지 정적 사이트 빌더.

  python3 build.py

를 실행하면 이 폴더에 index.html, faculty.html ... 이 새로 생성됩니다.
내용을 고치려면 아래 DATA 영역을 수정한 뒤 다시 실행하세요.
(HTML 파일을 직접 수정해도 되지만, 그 경우 build.py 는 다시 실행하지 마세요.)
"""
import io, os, re

OUT = os.path.dirname(os.path.abspath(__file__))

# ============================================================== helpers
def t(ko, en, tag="span", cls=""):
    """한/영 병기 요소. CSS 가 활성 언어만 보여줍니다."""
    c = (" " + cls).rstrip() if cls else ""
    return '<%s class="ko%s">%s</%s><%s class="en%s">%s</%s>' % (tag, c, ko, tag, tag, c, en, tag)

def write(name, html):
    with io.open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(html)
    print("  wrote %-16s %6.1f KB" % (name, len(html.encode("utf-8")) / 1024.0))

# ============================================================== svg assets
MARK = '''<svg class="brand__mark" viewBox="0 0 40 40" fill="none" aria-hidden="true">
<rect x="1" y="1" width="38" height="38" rx="11" fill="url(#bm)"/>
<circle cx="12.5" cy="13" r="3.1" fill="#fff" opacity=".95"/>
<circle cx="27.5" cy="13" r="3.1" fill="#C6A15B"/>
<circle cx="20" cy="27.5" r="3.1" fill="#fff" opacity=".95"/>
<path d="M12.5 13 27.5 13M12.5 13 20 27.5M27.5 13 20 27.5" stroke="#fff" stroke-opacity=".55" stroke-width="1.4"/>
<defs><linearGradient id="bm" x1="0" y1="0" x2="40" y2="40">
<stop stop-color="#00285A"/><stop offset="1" stop-color="#1E5299"/></linearGradient></defs></svg>'''

# 직접 그린 칼리지 고딕 건물 라인아트 (특정 사진의 복제가 아닌 창작 도안)
def _arch():
    """히어로 배경에 깔리는 건물 선 그림.
    연세대학교 본관인 언더우드관(1924년 준공, 사적 제276호)의 정면을 옮긴 것이다.
    3층 석조 건물 가운데에 5층 높이의 탑이 서 있고, 탑 꼭대기는 뾰족한 첨탑이 아니라
    성벽처럼 이가 빠진 평평한 난간이다. 정문은 튜더 아치이고 그 앞에 넓은 계단이 놓인다.
    창은 첨두형이 아니라 네모난 창이 일정한 간격으로 늘어선다."""
    G, BASE, EAVE, RIDGE = 372, 338, 196, 150      # 지면 · 밑단 · 처마 · 용마루
    L, R = 120, 1080                               # 건물 좌우 끝
    TL, TR = 510, 690                              # 중앙탑 좌우
    CAP, MERLON = 96, 78                           # 난간 윗선 · 이 빠진 부분 꼭대기

    d = [
        "M0 %d H1200" % G,                                             # 지면
        "M%d %d H%d" % (L, BASE, R),                                   # 밑단
        "M%d %d V%d M%d %d V%d" % (L, BASE, EAVE, R, BASE, EAVE),      # 양 끝 벽
        "M%d %d H%d M%d %d H%d" % (L, EAVE, TL, TR, EAVE, R),          # 처마
        "M%d %d L160 %d H%d" % (L, EAVE, RIDGE, TL),                   # 왼쪽 지붕
        "M%d %d L1040 %d H%d" % (R, EAVE, RIDGE, TR),                  # 오른쪽 지붕
        "M198 %d V%d M1002 %d V%d" % (BASE, EAVE, BASE, EAVE),         # 양 끝 돌출부
        "M%d %d V%d M%d %d V%d" % (TL, BASE, CAP, TR, BASE, CAP),      # 탑 좌우
        "M%d %d H%d" % (TL, CAP, TR),                                  # 난간 윗선
    ]
    # 성벽 모양 난간. 가운데 이가 정확히 x=600에 오도록 다섯 개를 놓는다.
    for x in (510, 549, 588, 627, 666):
        d.append("M%d %d V%d H%d V%d" % (x, CAP, MERLON, x + 24, CAP))
    d += [
        "M600 %d V48 M600 50 H618 V60 H600" % MERLON,                  # 깃대와 깃발
        "M516 120 H684",                                               # 탑 허리 띠
        "M566 %d V304 Q568 288 600 282 Q632 288 634 304 V%d" % (BASE, BASE),   # 정문 튜더 아치
        "M580 %d V308 Q582 298 600 294 Q618 298 620 308 V%d" % (BASE, BASE),   # 문틀
        "M588 214 V262 M612 214 V262",                                 # 정문 위 창 중간틀
        "M462 372 H738 M470 365 H730 M480 358 H720 M492 351 H708 M504 344 H696 M514 338 H686",  # 계단
        "M462 372 L514 338 M738 372 L686 338",                         # 계단 옆벽
    ]

    rects = []
    for x in (534, 589, 644):                                          # 탑 윗부분 창
        rects.append('<rect x="%d" y="136" width="22" height="50"/>' % x)
    rects.append('<rect x="566" y="214" width="68" height="48"/>')     # 정문 위 창
    for y in (206, 252, 298):                                          # 좌우 익동 3개 층
        for x in (150, 206, 262, 318, 374, 430, 744, 800, 856, 912, 968, 1024):
            rects.append('<rect x="%d" y="%d" width="26" height="32"/>' % (x, y))

    return ('<svg class="hero__arch" viewBox="0 0 1200 380" fill="none" aria-hidden="true">\n'
            ' <g stroke="#DCE7F7" stroke-width="1.5" stroke-linejoin="round" opacity=".9">\n'
            '  <path d="%s"/>\n'
            '  <circle cx="600" cy="106" r="8"/>\n'
            '  %s\n'
            ' </g>\n'
            '</svg>') % (" ".join(d), "".join(rects))


ARCH = _arch()

def net(cls):
    """공급망을 은유하는 노드-링크 애니메이션 배경."""
    import random
    random.seed(7)
    nodes = [(90,120),(250,70),(420,150),(560,60),(700,140),(860,80),(1010,160),(1130,90),
             (150,300),(320,250),(470,330),(620,260),(780,320),(930,250),(1080,320),
             (240,450),(400,500),(560,430),(730,490),(890,420),(1040,470)]
    edges = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(0,8),(1,9),(2,9),(3,11),(4,11),
             (5,13),(6,14),(8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(8,15),(10,16),
             (11,17),(12,18),(13,19),(14,20),(15,16),(16,17),(17,18),(18,19),(19,20),(2,10),(4,12)]
    ls = "".join('<line class="net-line" x1="%d" y1="%d" x2="%d" y2="%d" style="animation-delay:-%.1fs"/>'
                 % (nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1], (i % 9) * 1.6)
                 for i, (a, b) in enumerate(edges))
    ns = "".join('<circle class="net-node" cx="%d" cy="%d" r="3.4" style="animation-delay:-%.1fs"/>'
                 % (x, y, (i % 7) * .9) for i, (x, y) in enumerate(nodes))
    return ('<svg class="%s" viewBox="0 0 1200 560" preserveAspectRatio="xMidYMid slice" fill="none" aria-hidden="true">'
            '<g stroke="#8FC0FF" stroke-width="1" opacity=".45">%s</g>'
            '<g fill="#BFD9FF">%s</g></svg>') % (cls, ls, ns)

I = {
 "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M13 6l6 6-6 6"/></svg>',
 "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m3.5 7 8.5 6 8.5-6"/></svg>',
 "ext": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h5"/></svg>',
 "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m4 12.5 5 5L20 6.5"/></svg>',
 "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>',
 "theme": '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11Z"/></svg>',
 "burger": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
 "chain": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="9" width="6" height="6" rx="1.6"/><rect x="15.5" y="9" width="6" height="6" rx="1.6"/><path d="M8.5 12h7M12 12V4.5M9.5 6.8 12 4.3l2.5 2.5"/></svg>',
 "gear": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3.2"/><path d="M12 2.6v3M12 18.4v3M21.4 12h-3M5.6 12h-3M18.6 5.4l-2.1 2.1M7.5 16.5l-2.1 2.1M18.6 18.6l-2.1-2.1M7.5 7.5 5.4 5.4"/></svg>',
 "bulb": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 18h5M10 21h4"/><path d="M12 3a6 6 0 0 1 3.6 10.8c-.7.6-1.1 1.3-1.1 2.2h-5c0-.9-.4-1.6-1.1-2.2A6 6 0 0 1 12 3Z"/></svg>',
 "cube": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.8 20.5 7v10L12 21.2 3.5 17V7Z"/><path d="M3.5 7 12 11.4 20.5 7M12 11.4V21.2"/></svg>',
 "spark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.2 13.9 9l5.8 1.9-5.8 1.9L12 18.6l-1.9-5.8L4.3 10.9 10.1 9Z"/><path d="M18.5 3v3.4M20.2 4.7h-3.4"/></svg>',
 "ai": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="7.2" y="7.2" width="9.6" height="9.6" rx="1.6"/><path d="M10.2 3.4v3.8M13.8 3.4v3.8M10.2 16.8v3.8M13.8 16.8v3.8M3.4 10.2h3.8M3.4 13.8h3.8M16.8 10.2h3.8M16.8 13.8h3.8"/></svg>',
 "leaf": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 19.5C3 15 5 8.5 11 6.2c3-1.2 6-1.2 8.4-1.4.2 2.6.1 5.6-1.2 8.4-2.4 5.2-8.4 7.2-12.4 5.6"/><path d="M5.6 18.4C8 15 12 11.6 16.5 9.6"/></svg>',
 "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 20h17M6.5 20V12M11 20V6.5M15.5 20v-5.5M20 20V9.5"/></svg>',
 "cap": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2.8 8.6 12 4.4l9.2 4.2L12 12.8Z"/><path d="M6.5 10.8v4.6c0 1.5 2.5 2.8 5.5 2.8s5.5-1.3 5.5-2.8v-4.6M21.2 8.6v5.2"/></svg>',
 "mic": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="2.8" width="6" height="11" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3.2M9.2 21.2h5.6"/></svg>',
 "won": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7.5 7 17l5-8 5 8 4-9.5M2.6 11.4h18.8M2.6 14.2h18.8"/></svg>',
 "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3.2 9.8h17.6M3.2 14.2h17.6M12 3c2.6 3 2.6 15 0 18M12 3c-2.6 3-2.6 15 0 18"/></svg>',
 "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-5.4 7-11a7 7 0 1 0-14 0c0 5.6 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/></svg>',
 "book": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4.5h6a3 3 0 0 1 2 5.2V20a3.4 3.4 0 0 0-2-.8H4Z"/><path d="M20 4.5h-6a3 3 0 0 0-2 5.2V20a3.4 3.4 0 0 1 2-.8h6Z"/></svg>',
}

# ============================================================== chrome
NAV = [
    ("index.html",      "홈",        "Home"),
    ("faculty.html",    "전공 교수",  "Faculty"),
    ("admissions.html", "입학 안내",  "Admissions"),
    ("courses.html",    "교과목",     "Curriculum"),
    ("students.html",   "재학생",     "Students"),
    ("alumni.html",     "졸업생",     "Alumni"),
    ("seminars.html",   "세미나",     "Seminars"),
    ("news.html",       "소식",       "News"),
]

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E"
           "%3Crect width='40' height='40' rx='11' fill='%2300285A'/%3E"
           "%3Ccircle cx='12.5' cy='13' r='3.2' fill='white'/%3E"
           "%3Ccircle cx='27.5' cy='13' r='3.2' fill='%23C6A15B'/%3E"
           "%3Ccircle cx='20' cy='27.5' r='3.2' fill='white'/%3E%3C/svg%3E")

BOOT = ("document.documentElement.classList.add('js');"
        "(function(){try{var l=localStorage.getItem('omysb-lang');"
        "if(l)document.documentElement.setAttribute('data-lang',l);"
        "var t=localStorage.getItem('omysb-theme');"
        "if(t&&t!=='auto')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();")

def header(active):
    links = "".join(
        '<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == active else "", t(ko, en))
        for h, ko, en in NAV)
    return '''<a class="sr-only" href="#main">본문 바로가기</a>
<header class="hdr">
 <div class="wrap hdr__in">
  <a class="brand" href="index.html">
    <img class="brand__logo brand__logo--light" src="assets/img/brand/ysb-logo.png" alt="연세대학교 경영대학" width="208" height="64">
    <img class="brand__logo brand__logo--dark" src="assets/img/brand/ysb-logo-white.png" alt="" aria-hidden="true" width="208" height="64">
    <span class="brand__div" aria-hidden="true"></span>
    <span class="brand__txt">
    <span class="brand__ko">%s</span>
    <span class="brand__en">%s</span></span></a>
  <nav class="nav" aria-label="주 메뉴">%s</nav>
  <div class="tools">
   <div class="lang" role="group" aria-label="Language">
    <button type="button" data-lang-btn="ko" aria-pressed="true">KR</button>
    <button type="button" data-lang-btn="en" aria-pressed="false">EN</button>
   </div>
   <button type="button" class="iconbtn" data-theme-btn aria-label="다크 모드 전환">%s</button>
   <button type="button" class="iconbtn burger" data-burger aria-expanded="false" aria-label="메뉴 열기">%s</button>
  </div>
 </div>
</header>''' % (t("오퍼레이션 전공", "Operations Management"),
        t("Operations Management", "Yonsei School of Business"), links, I["theme"], I["burger"])

def footer():
    quick = "".join('<li><a href="%s">%s</a></li>' % (h, t(ko, en)) for h, ko, en in NAV[1:])
    return '''<footer class="ftr">
 <div class="wrap">
  <div class="ftr__top">
   <div>
    <div class="ftr__brand">
      <img class="ftr__logo" src="assets/img/brand/ysb-logo-footer.png" alt="연세대학교 경영대학" width="315" height="56">
      <span class="brand__txt">
      <span class="brand__ko">%s</span>
      <span class="brand__en">Operations Management, YSB</span></span></div>
    %s
    %s
   </div>
   <div>
    <h4>%s</h4>
    <ul>%s</ul>
   </div>
   <div>
    <h4>%s</h4>
    <ul>
     <li><a href="https://ysb.yonsei.ac.kr" target="_blank" rel="noopener">%s</a></li>
     <li><a href="https://graduate.yonsei.ac.kr" target="_blank" rel="noopener">%s</a></li>
     <li><a href="https://www.yonsei.ac.kr" target="_blank" rel="noopener">%s</a></li>
     <li><a href="mailto:seunghwan.jung@yonsei.ac.kr">%s</a></li>
    </ul>
   </div>
  </div>
  <div class="ftr__bot">
   <span>&copy; <span data-year-now>2026</span> %s</span>
   <span>%s</span>
  </div>
 </div>
</footer>''' % (
    t("오퍼레이션 전공", "Operations Management"),
    t("서울특별시 서대문구 연세로 50 연세대학교 경영대학", "50 Yonsei-ro, Seodaemun-gu, Seoul 03722, Republic of Korea", "p"),
    t("석·박사 과정 문의 · 정승환 교수 seunghwan.jung@yonsei.ac.kr",
      "M.S./Ph.D. inquiries · Prof. Seunghwan Jung, seunghwan.jung@yonsei.ac.kr", "p"),
    t("바로가기", "Explore"), quick,
    t("관련 링크", "Related"),
    t("연세대학교 경영대학", "Yonsei School of Business"),
    t("연세대학교 일반대학원", "Yonsei Graduate School"),
    t("연세대학교", "Yonsei University"),
    t("입학 문의 이메일", "Admissions e-mail"),
    t("연세대학교 경영대학 오퍼레이션 전공", "Operations Management, Yonsei School of Business"),
    t("본 페이지의 일러스트레이션은 본 전공에서 직접 제작한 것입니다.",
      "All illustrations on this site were created in-house."))

def asset_v(relpath):
    """스타일·스크립트 주소에 붙이는 내용 해시.
    파일을 고치면 주소가 바뀌어서, 새로고침만 해도 브라우저가 새 파일을 받는다.
    이게 없으면 file:// 로 열었을 때 예전 스크립트가 계속 살아 있다."""
    import hashlib
    with open(os.path.join(OUT, relpath), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def page(fname, title_ko, title_en, desc_ko, body, active=None):
    html = '''<!DOCTYPE html>
<html lang="ko" data-lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta name="theme-color" content="#00285A">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:type" content="website">
<link rel="icon" href="%s">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/pretendard-dynamic-subset.min.css">
<link rel="stylesheet" href="assets/css/site.css?v=%s">
<script>%s</script>
</head>
<body data-title-ko="%s" data-title-en="%s">
%s
<main id="main">
%s
</main>
%s
<script src="assets/js/site.js?v=%s"></script>
</body>
</html>
''' % (title_ko, desc_ko, title_ko, desc_ko, FAVICON, asset_v("assets/css/site.css"),
       BOOT, title_ko, title_en,
       header(active or fname), body, footer(), asset_v("assets/js/site.js"))
    write(fname, html)

def phead(crumb, h1_ko, h1_en, sub, desc_ko, desc_en):
    return '''<section class="phead">
 <div class="phead__bg"></div>
 <div class="wrap phead__in">
  %s
  <div class="sub">%s</div>
  %s
 </div>
</section>''' % (t(h1_ko, h1_en, "h1"), sub, t(desc_ko, desc_en, "p", "desc"))

# ============================================================== DATA

# 명단을 마지막으로 확인한 시점.  학기마다 build.py 를 손볼 때 함께 고친다.
LAST_REVIEWED_KO = "2026년 9월"
LAST_REVIEWED_EN = "September 2026"
CONTACT_MAIL = "seunghwan.jung@yonsei.ac.kr"
# ---- 교수진 (이름, 영문명, 이니셜, 직위ko/en, 관심분야ko/en, 이메일, 개인홈페이지, 사진파일)
FACULTY = [
 ("허대식","Daesik Hur","H","교수","Professor",
  "공급체인 구조 및 변화 전략, 글로벌 SCM 비교분석, 신제품 개발과 공급체인 통합전략",
  "Supply chain architecture and transformation strategy; comparative global SCM; integrating new product development with the supply chain",
  "dhur@yonsei.ac.kr","https://ysb.yonsei.ac.kr/ysb/faculty/full-time-professors.do?mode=view&amp;articleNo=21995","heo.jpg"),
 ("민순홍","Soonhong Min","M","교수","Professor",
  "지속가능성과 혁신, 공급사슬관리",
  "Sustainability and innovation; supply chain management",
  "sminscm@yonsei.ac.kr","https://ysb.yonsei.ac.kr/ysb/faculty/full-time-professors.do?mode=view&amp;articleNo=22035","min.jpg"),
 ("최선미","Sunmee Choi","C","교수","Professor",
  "서비스 운영관리, 수익경영",
  "Service operations management; revenue management",
  "sc128@yonsei.ac.kr","https://ysb.yonsei.ac.kr/ysb/faculty/full-time-professors.do?mode=view&amp;articleNo=21994","choi.jpg"),
 ("배성주","Sungjoo Bae","B","교수","Professor",
  "기술경영, 기술전략, 신제품 개발공정, 신서비스 개발 방법론, 제품 디자인 및 설계, 기술정책",
  "Technology management and strategy; new product development processes; new service development; product design; technology policy",
  "sjbae@yonsei.ac.kr","https://ysb.yonsei.ac.kr/ysb/faculty/full-time-professors.do?mode=view&amp;articleNo=22037","bae.jpg"),
 ("박승재","Seungjae Park","P","교수","Professor",
  "공급사슬관리, ESG 경영(탄소배출·공정무역·기업지배구조), 국제경영, 해외자회사",
  "Supply chain management; ESG (carbon emissions, fair trade, corporate governance); international business; foreign subsidiaries",
  "seung.park@yonsei.ac.kr","https://ysb.yonsei.ac.kr/ysb/faculty/full-time-professors.do?mode=view&amp;articleNo=22061","park.jpg"),
 ("정승환","Seunghwan Jung","J","부교수","Associate Professor",
  "오퍼레이션 데이터 애널리틱스, 데이터 기반 의사결정, 물류·수송, 소싱, 오퍼레이션 전략, 지속가능성",
  "Data analytics in OM; data-driven decision making; logistics and transportation; sourcing; operations strategy; sustainability",
  "seunghwan.jung@yonsei.ac.kr","https://ysb.yonsei.ac.kr/ysb/faculty/full-time-professors.do?mode=view&amp;articleNo=22087","jung.jpg"),
]
# ---- 교수 상시 활동 --------------------------------------------------
#
#  날짜가 지나도 낡지 않는 직함만 적습니다. 편집위원, 학회 임원, 센터장 같은 것입니다.
#  논문 게재나 수상처럼 시점이 있는 일은 여기가 아니라 NEWS 에 넣습니다.
#
#  한 분당 두 건까지만 두시기를 권합니다. 늘어날수록 관리가 밀립니다.
#  임기가 있는 직함(회장, 부회장)은 연도를 함께 적으세요. 임기가 끝나면 조용히 거짓이 됩니다.
#
#  형식  "교수 성함": [(국문, 영문), ...]
#  비어 있으면 카드에 아무것도 나오지 않습니다.
#
#  아래 내용은 연세대학교 경영대학 공식 교수 소개 페이지와 각 학회·학술지 공식 명단에서
#  확인한 것입니다. 출처는 항목마다 주석으로 달아 두었습니다. 게시 전에 한 번 확인해 주세요.
#
FACULTY_ROLES = {
    # 출처: 경영대학 교수 소개(articleNo=21995), Wiley JOM 편집위원 명단, 한국경영학회
    "허대식": [
        ("한국경영학회 부회장 (2021~현재)",
         "Vice President, Korean Academic Society of Business Administration (2021-present)"),
        ("Journal of Operations Management 부편집장 역임 (2018~2023)",
         "Associate Editor, Journal of Operations Management (2018-2023)"),
    ],
    # 출처: 경영대학 교수 소개(articleNo=22035), 한국생산운영관리학회 임원현황, 한국윤리경영학회 학회조직
    # 주의: 경영대학 페이지에는 윤리경영학회 회장이 현직처럼 적혀 있으나
    #       학회 공식 명단 기준 제19대(2025) 회장이고 현 회장은 제20대입니다. 역임으로 적었습니다.
    "민순홍": [
        ("한국생산운영관리학회 부회장",
         "Vice President, Korean Production and Operations Management Society"),
        ("한국윤리경영학회 제19대 회장 역임 (2025)",
         "19th President, Korean Academy of Business Ethics (2025)"),
    ],
    # 출처: 경영대학 교수 소개(articleNo=21994), Sage 편집위원 명단, 한국생산운영관리학회 임원현황
    "최선미": [
        ("Cornell Hospitality Quarterly 편집위원",
         "Editorial Board Member, Cornell Hospitality Quarterly"),
        ("한국생산운영관리학회 부회장",
         "Vice President, Korean Production and Operations Management Society"),
    ],
    # 출처: 경영대학 교수 소개(articleNo=22037)
    "배성주": [
        ("「기술혁신연구」 부편집장",
         "Associate Editor, Journal of Technology Innovation"),
        ("한국기술경영경제학회 이사 · 학술위원장",
         "Director and Chair of the Academic Committee, Korean Society for Technology Management and Economics"),
    ],
    # 출처: 경영대학 교수 소개(articleNo=22061), 한국생산운영관리학회 임원현황·편집위원회
    "박승재": [
        ("한국생산운영관리학회 이사 (2019~현재)",
         "Board Member, Korean Production and Operations Management Society (2019-present)"),
        ("한국생산관리학회지 편집위원 (2023~현재)",
         "Editorial Board Member, Korean Journal of Production and Operations Management (2023-present)"),
    ],
    # 출처: 경영대학 교수 소개(articleNo=22087), 한국경영학회 임원진
    "정승환": [
        ("한국생산운영관리학회 이사 (2023~현재)",
         "Board Member, Korean Production and Operations Management Society (2023-present)"),
        ("연세대학교 Global MBA 주임교수 (2025.9~현재)",
         "Director, Global MBA, Yonsei University (Sept. 2025-present)"),
    ],
}

# 연구실과 연락처. 연세대학교 경영대학 공식 교수 소개 페이지에서 확인한 값입니다.
FACULTY_CONTACT = {
    "허대식": ("경영관 524", "02-2123-5487"),
    "민순홍": ("경영관 521", "02-2123-6261"),
    "최선미": ("경영관 653", "02-2123-5479"),
    "배성주": ("경영관 613", "02-2123-6578"),
    "박승재": ("경영관 528", "02-2123-2546"),
    "정승환": ("경영관 649", "02-2123-5473"),
}

EMERITUS = [
 ("김기영","Ki-Young Kim","K","명예교수","Professor Emeritus",
  "현 삼일문화재단 이사장","Currently Chairman, Samil Foundation for Culture",
  "","https://ysb.yonsei.ac.kr/ysb/faculty/professor-emeritus.do?mode=view&amp;articleNo=22026","kimky.jpg",
  ("http://www.31cf.or.kr/intro/greet.asp", "삼일문화재단", "Samil Foundation")),
 ("김태현","Tae-Hyun Kim","K","명예교수","Professor Emeritus",
  "현 서울과학종합대학원(aSSIST) 총장","Currently President, aSSIST University",
  "","https://ysb.yonsei.ac.kr/ysb/faculty/professor-emeritus.do?mode=view&amp;articleNo=21993","kimth.jpg",
  ("https://www.assist.ac.kr/AssistIntroduction/Assist/president.php", "aSSIST", "aSSIST University")),
]

# ---- 재학생 (이름, 과정, 관심분야ko/en, 석사논문ko/en)
# 재학생.  (성명, 과정, 관심분야ko, en, 석사논문ko, en, 학력ko, 학력en)
#   학력  : 학부 졸업 학교와 전공. 졸업 연도는 넣지 않는다 (연령 추정을 막기 위함).
#           본인이 공개를 원하지 않으면 빈 문자열로 두면 화면에 나오지 않는다.
#   비어 있는 항목은 화면에 출력되지 않으므로 아는 것부터 채우면 된다.
# 재학생 연구 실적. 게재(확정) 논문과 학회 발표를 함께 싣는다.
# 발표까지 넣는 것은 박사과정 초기나 석사과정 학생도 실적을 보일 수 있게 하려는 것이다.
# 실적이 없는 학생은 아예 적지 않는다. 그러면 카드에 이 칸이 생기지 않는다.
# "실적 없음" 같은 빈 칸을 만들면 학생 사이에 대비만 두드러진다.
# 학기 초에 한 번 갱신한다.
#
#   "이름": [
#     ("pub",  "국문 표기", "영문 표기"),    게재 또는 게재 확정 논문
#     ("conf", "국문 표기", "영문 표기"),    학회 발표
#   ],
# 표기는 "저자 (연도). 제목. 학술지·학회명." 순서로 적는다. 영문이 따로 없으면 같은 문자열을 두 번 적는다.
STUDENT_WORK = {
    # ── 견본 ─────────────────────────────────────────────────────────────
    # 모양을 보여 주려고 넣은 가짜 항목이다. 실제 실적을 받으면 지우고 바꾼다.
    # 빌드할 때 [견본] 이 남아 있으면 경고가 뜬다. 게시 전에 반드시 지운다.
    "박지현": [
        ("pub",  "[견본] 박지현, 지도교수 (2026). 논문 제목. 학술지명, 권(호), 쪽.",
                 "[Sample] Park, J., Advisor (2026). Title of the paper. Journal, Vol(No), pp."),
        ("conf", "[견본] 박지현 (2026). 발표 제목. 학회명, 개최지.",
                 "[Sample] Park, J. (2026). Title of the talk. Conference, Location."),
    ],
    "김동진": [
        ("conf", "[견본] 김동진 (2026). 발표 제목. 학회명, 개최지.",
                 "[Sample] Kim, D. (2026). Title of the talk. Conference, Location."),
    ],
}

STUDENTS = [
 ("박지현","phd","지속가능 공급사슬관리, 조직생태학","Sustainable supply chain management; organizational ecology",
  "기계 학습과 RFM 모형을 이용한 고객 유형 분석: 문화예술 이용객을 대상으로",
  "Customer segmentation with machine learning and RFM models: evidence from arts and culture audiences",
  "", ""),
 ("부귀현","phd","","",
  "조직의 흡수역량이 혁신역량에 미치는 영향: 민첩성의 매개역할",
  "How absorptive capacity shapes innovation capability: the mediating role of agility",
  "", ""),
 ("김동진","ms","공급사슬관리, 군 물류체계 개선·최적화","Supply chain management; military logistics improvement and optimization","","", "", ""),
 ("이소현","ms","공급사슬관리, 공급망 리스크 관리, 물류","Supply chain management; supply chain risk management; logistics","","", "", ""),
 ("Yuhe Zeng","ms","","","","", "", ""),
 ("권진우","ms","","","","", "", ""),
 ("송미형","ms","","","","", "", ""),
 ("한지영","ms","","","","", "", ""),
 ("Hsin Lun Lee","ms","","","","", "", ""),
]

ADV = {"허대식":"Daesik Hur","민순홍":"Soonhong Min","최선미":"Sunmee Choi","배성주":"Sungjoo Bae",
       "박승재":"Seungjae Park","정승환":"Seunghwan Jung","김기영":"Ki-Young Kim","김태현":"Tae-Hyun Kim"}


# ============================================================== 영문 이름
# 영어 화면에서 세미나 연사, 졸업생, 재학생 이름을 로마자로 보여 준다.
# 키는 한글 이름이다. 표에 없는 이름은 영어 화면에서도 한글 그대로 나온다.
#
# NAMES_EN
#   본인이 쓰는 철자를 확인한 이름. 영어 화면에 그대로 나온다.
#   세미나 연사와 교수로 간 졸업생은 소속 기관 교수 페이지, Google Scholar,
#   ORCID 에서 확인했다.
#
# NAMES_EN_UNVERIFIED
#   확인하지 못해 관례 표기로 적어 둔 이름. 영어 화면에는 나오지 않는다.
#   본인에게 철자를 확인한 뒤 NAMES_EN 으로 옮기면 그때부터 나온다.
#   빌드할 때 남은 인원을 알려 준다.
#
#   확인 없이 내보내지 않는 이유가 있다. 표기법대로 옮기면 우리 전공 교수
#   일곱 분 중 네 분의 이름이 틀리게 나온다. 민순홍 교수는 Sunhong 이 아니라
#   Soonhong, 배성주 교수는 Seongju 가 아니라 Sungjoo 다. 이름을 틀리게 쓰는 것은
#   한글로 두는 것보다 나쁘다.
#
# 같은 한글 이름의 다른 사람이 있으면 (한글 이름, 소속 영문) 을 키로 따로 적는다.
# 세미나는 연사 소속을, 졸업생은 근무지 영문을 소속으로 본다.
NAMES_EN = {
    "강성":    "Sung Kang",            # https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearc
    "강세원":   "Sehwon Kang",          # https://skang.sogang.ac.kr/skang/
    "김기훈":   "Kihoon Kim",           # https://sites.google.com/view/kihoon
    "김보성":   "Bosung Kim",           # https://com.khu.ac.kr/biz_kor/user/bbs/BMSR00047/view.do?menuNo=14500199&boardId=395931
    "김상원":   "Sang Won Kim",         # https://www.business.kaist.edu/faculty/sk2559
    "김상조":   "Sangjo Kim",           # https://cob.sufe.edu.cn/en/Faculty/Resume/205
    "김성태":   "Seongtae Kim",         # https://www.aalto.fi/en/people/seongtae-kim
    "김송희":   "Song-Hee Kim",         # https://sites.google.com/view/songheekim
    "김수연":   "Sooyun Kim",           # https://orcid.org/0000-0001-5998-4110
    "김승범":   "Seungbeom Kim",        # https://doi.org/10.3390/su14031375
    "김우성":   "Woo-sung Kim",         # https://scholar.google.com/citations?user=g0gLfkYAAAAJ&hl=en
    "김유순":   "Yusoon Kim",           # https://business.oregonstate.edu/users/yusoon-kim
    "김은지":   "Eunji Kim",            # http://ejklike.github.io/
    "김정현":   "Jeunghyun Kim",        # https://sites.google.com/site/jeunghyunkim/
    "김종래":   "Jong-Rae Kim",         # https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearc
    "김지대":   "Ji-Dae Kim",           # https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearc
    "김창희":   "Changhee Kim",         # https://scholar.google.com/citations?user=yk-v1rsAAAAJ&hl=en
    "김헌":    "Heon Kim",             # https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearc
    "김효진":   "Hyojin Kim",           # https://www.emerald.com/ejim/article-abstract/27/1/233/1227355/Feeling-torn-The-conflict
    "노대훈":   "Daehoon Noh",          # https://biz.korea.ac.kr/eng/professor/professor_view?pinfo=_2fnyuCXPHilEM%2FIfArShg
    "노인준":   "In Joon Noh",          # https://scholar.google.com/citations?user=AGASNhgAAAAJ&hl=en
    "문성암":   "Seong-Am Moon",        # https://www.emerald.com/insight/content/doi/10.1108/13598540510624214/full/html
    "박민아":   "Minah Park",           # https://www.oberlin.edu/minah-park
    "박재혁":   "Jae-Hyuck Park",       # https://people.njit.edu/profile/jp2355
    "박준병":   "Jun-Byung Park",       # https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearc
    "박현우":   "Hyunwoo Park",         # https://mot.snu.ac.kr/snu__professor/%EB%B0%95%ED%98%84%EC%9A%B0/
    "배준현":   "Junhyun Bae",          # https://oakland.edu/business/faculty-staff-directory/junhyun-bae/
    "복준혁":   "Joonhyuk Bok",         # https://scholar.google.com/citations?hl=en&user=V98S1LoAAAAJ
    "서용원":   "Yong Won Seo",         # https://doi.org/10.1111/poms.12841
    "손범호":   "Bumho Son",            # https://bumhoson.github.io/
    "송다혜":   "Lina Song",            # https://linasong.com/about/
    "송주명":   "Ju Myung Song",        # https://www.uml.edu/myuml/submissions/2024/2024-06-18-17-42-09-umass-lowell-promotion-an
    "심재웅":   "Jaeung Sim",           # https://www.business.uconn.edu/person/jaeung-sim/
    "심정은":   "Jeongeun Sim",         # https://ris.snu.ac.kr/professors/%EC%8B%AC%EC%A0%95%EC%9D%80%EA%B5%90%EC%88%98/
    "오세진":   "Sei Jin Oh",           # https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearc
    "오재영":   "Jaeyoung Oh",          # https://www.cwu.edu/academics/colleges/college-business/finance-supply/supply-chain-mana
    "유창승":   "Changseung Yoo",       # https://www.mcgill.ca/desautels/changseung-chang-yoo
    "윤석준":   "Seokjun Youn",         # https://eller.arizona.edu/people/seokjun-youn
    "윤장원":   "Jang-Won Yoon",        # https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearc
    "윤재홍":   "Jae Hong Yoon",        # https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearc
    "윤지호":   "Jiho Yoon",            # https://scholar.google.com/citations?user=ou4XUfUAAAAJ&hl=en
    "이민경":   "Min Kyung Lee",        # https://hankamer.baylor.edu/person/min-kyung-lee
    "이수열":   "Su-Yol Lee",           # https://cba.jnu.ac.kr/cba/13908/subview.do
    "이승준":   "Seung Jun Lee",        # https://scholar.google.com/citations?hl=en&user=WjVE-V8AAAAJ
    "이연주":   "Yeonjoo Lee",          # https://directory.smeal.psu.edu/yvl5911
    "이인호":   "In Ho Lee",            # https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearc
    "이중희":   "Junghee Lee",          # https://mendoza.nd.edu/mendoza-directory/profile/junghee-lee/
    "이평수":   "Pyoungsoo Lee",        # https://pmc.ncbi.nlm.nih.gov/articles/PMC10531087/
    "이현석":   "Hyun Seok Lee",        # https://hyunseoklee.com/
    "인준환":   "Joonhwan In",          # https://www.emerald.com/jsm/article-abstract/34/6/833/252924/Social-media-engagement-ser
    "임종명":   "Jong Myeong Lim",      # https://scholar.google.com/citations?user=c7e0V7wAAAAJ&hl=en
    "정문원":   "Moonwon Chung",        # https://scholar.google.com/citations?hl=en&user=MUzOKmsAAAAJ
    "정병도":   "Byung Do Chung",       # https://sites.google.com/site/ysievcm/members/professor
    "정태현":   "Taehyun Jung",         # https://scholar.google.com/citations?user=80-deooAAAAJ&hl=en
    "조병주":   "Byung-Ju Cho",         # https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearc
    "조형찬":   "Hyungchan Cho",        # https://sites.google.com/umich.edu/chohc/
    "채상호":   "Sangho Chae",          # https://www.wbs.ac.uk/about/person/sangho-chae/
    "최지흥":   "Ji-Hung Choi",         # https://scholar.google.com/citations?hl=en&user=tWZbB7kAAAAJ
    "황우남":   "Woonam Hwang",         # https://sites.google.com/site/woonams/Home
}

NAMES_EN_UNVERIFIED = {
    # 조사했지만 철자를 확정하지 못한 분. 이유를 옆에 적었다.
    "김영대":   "Youngdai Kim",         # 연세대 소속은 맞으나 동명이인을 배제하지 못함
    "남현정":   "Hyun-Jung Nam",        # Hyun-Jung / Hyun-Jeong 두 표기가 섞여 있음
    "이규상":   "Kyu-Sang Lee",         # 목원대 소속으로 된 영문 표기를 찾지 못함
    "이상준":   "Sangjun Lee",          # 현재 연세대 교원 명단에서 찾지 못함
    "이철성":   "Cheolsung Lee",        # 우아한형제들 소속 공개 자료가 없음
    "이호창":   "Hochang Lee",          # 가천대 소속 영문 표기를 찾지 못함. 경희대 이호창 교수와 다른 분
    "조석환":   "Sok-Hwan Cho",         # Sok-Hwan / Suk-Whan 등 연도마다 철자가 다름
    # 공개 자료가 없어 조사하지 않은 졸업생과 재학생. 관례 표기일 뿐이다.
    "권진우":   "Jinu Kwon",
    "김경순":   "Gyeongsun Kim",
    "김동진":   "Dongjin Kim",
    "김원소":   "Wonso Kim",
    "김지혜":   "Jihye Kim",
    "김탁경":   "Takgyeong Kim",
    "김태교":   "Taegyo Kim",
    "김형호":   "Hyeongho Kim",
    "류광정":   "Gwangjeong Ryu",
    "박정수":   "Jeongsu Park",
    "박정훈":   "Jeonghun Park",
    "박지현":   "Jihyeon Park",
    "박채원":   "Chaewon Park",
    "부귀현":   "Gwihyeon Bu",
    "서용기":   "Yonggi Seo",
    "손지원":   "Jiwon Son",
    "송미형":   "Mihyeong Song",
    "안민정":   "Minjeong Ahn",
    "안충영":   "Chungyeong Ahn",
    "양기훈":   "Gihun Yang",
    "양다은":   "Daeun Yang",
    "이동희":   "Donghui Lee",
    "이문일":   "Munil Lee",
    "이성현":   "Seonghyeon Lee",
    "이세진":   "Sejin Lee",
    "이소현":   "Sohyeon Lee",
    "이수민":   "Sumin Lee",
    "이영신":   "Yeongsin Lee",
    "이은지":   "Eunji Lee",
    "이청헌":   "Cheongheon Lee",
    "임세환":   "Sehwan Lim",
    "임현민":   "Hyeonmin Lim",
    "장유주":   "Yuju Jang",
    "전양수":   "Yangsu Jeon",
    "전준배":   "Junbae Jeon",
    "정대훈":   "Daehun Jung",
    "정주아":   "Jua Jung",
    "정현기":   "Hyeongi Jung",
    "조영재":   "Yeongjae Cho",
    "조혁진":   "Hyeokjin Cho",
    "조효원":   "Hyowon Cho",
    "주재이":   "Jaei Joo",
    "주천우":   "Cheonu Joo",
    "최범수":   "Beomsu Choi",
    "최종철":   "Jongcheol Choi",
    "한지영":   "Jiyeong Han",
    "함진영":   "Jinyeong Ham",
    "황선일":   "Seonil Hwang",
}

# 확인 안 된 이름까지 영어 화면에 내보내려면 True. 게시 전에는 False 로 둔다.
SHOW_UNVERIFIED_NAMES = False


def ename(ko, ctx=None):
    """영어 화면에 쓸 이름 문자열. 확인된 영문이 없으면 한글 그대로 돌려준다."""
    if ko in ADV:                       # 우리 교수진은 교수 소개 페이지 철자를 따른다
        return ADV[ko]
    tables = (NAMES_EN, NAMES_EN_UNVERIFIED) if SHOW_UNVERIFIED_NAMES else (NAMES_EN,)
    for table in tables:
        if ctx and (ko, ctx) in table:
            return table[(ko, ctx)]
    for table in tables:
        if ko in table:
            return table[ko]
    return ko


def pname(ko, ctx=None):
    """사람 이름을 한/영 두 벌로 낸다. ctx 는 동명이인을 가를 소속(영문)."""
    en = ename(ko, ctx)
    return t(ko, en) if en != ko else ko


def speaker(ko, rko, ren, ctx=None):
    """세미나 연사 이름과 직함. 한국어는 '노대훈 교수', 영어는 'Prof. Daehoon Noh'.
    Prof. 처럼 이름 앞에 오는 직함이 아니면 영어에서는 'Name, Team Lead' 로 뒤에 붙인다."""
    en = ename(ko, ctx)
    en_full = ("%s %s" % (ren, en)) if ren in ("Prof.", "Dr.") else ("%s, %s" % (en, ren))
    return t("%s %s" % (ko, rko), en_full)

# ---- 졸업생 (이름, 졸업연도, 지도교수, 논문주제ko, en, 근무지ko, en)
ALUMNI_MS = [
 ("조효원",2026,"민순홍","","","",""),
 ("박정수",2026,"허대식","","","",""),
 ("안민정",2026,"정승환","","","UCLA 경영대학원 박사과정","Ph.D. student, UCLA Anderson School of Management"),
 ("L. Jin",2026,"민순홍","인적자원 지향성","Human resource orientation","古茗(Good me)","Good Me (Guming)"),
 ("손지원",2026,"허대식","ESG 디커플링","ESG decoupling","아성다이소","Daiso Asung"),
 ("H. Yan",2025,"정승환","시장 경쟁","Market competition","SK하이닉스","SK hynix"),
 ("이세진",2025,"허대식","ESG 디커플링","ESG decoupling","대한민국 해군","ROK Navy"),
 ("임세환",2025,"민순홍","물류서비스 품질","Logistics service quality","대한민국 공군","ROK Air Force"),
 ("이동희",2024,"정승환","마이크로 풀필먼트 · 수요예측","Micro-fulfillment; demand forecasting","EY한영","EY Korea"),
 ("이성현",2024,"민순홍","공급사슬 적응성과 직원경험","Supply chain adaptability and employee experience","로지스올컨설팅","Logisall Consulting"),
 ("M. Kozaiym",2023,"허대식","디지털 전환","Digital transformation","대원강업","Daewon Kangup"),
 ("조영재",2023,"민순홍","전투기 성능개량","Fighter aircraft performance upgrades","대한민국 공군","ROK Air Force"),
 ("정대훈",2022,"박승재","공정무역","Fair trade","University of Florida 박사과정","Ph.D. student, University of Florida"),
 ("이청헌",2022,"민순홍","ESG 경영","ESG management","삼정KPMG","KPMG Korea"),
 ("전준배",2022,"민순홍","COVID-19와 재택근무","COVID-19 and remote work","대한민국 공군","ROK Air Force"),
 ("주재이",2022,"배성주","기술경영","Technology management","삼일회계법인","Samil PwC"),
 ("조혁진",2022,"허대식","디지털 전환","Digital transformation","대한민국 해군 평택함대","ROK Navy, Pyeongtaek Fleet"),
 ("최범수",2022,"허대식","책임있는 공급사슬관리","Responsible supply chain management","세흥인쇄","Sehung Printing"),
 ("양다은",2020,"민순홍","공급사슬 통합","Supply chain integration","CJ대한통운","CJ Logistics"),
 ("임현민",2020,"허대식","공급사슬 민첩성","Supply chain agility","SK네트웍스","SK Networks"),
 ("장유주",2020,"민순홍","서비스 산업","Service industries","ASUS Korea","ASUS Korea"),
 ("양기훈",2020,"민순홍","공급사슬과 조직문화 · 공급사슬 적응성","Supply chain and organizational culture; supply chain adaptability","대한민국 공군","ROK Air Force"),
 ("이연주",2019,"최선미","옴니채널","Omnichannel","Penn State University 조교수","Assistant Professor, Penn State University"),
 ("함진영",2019,"허대식","행동적 공급사슬관리","Behavioral supply chain management","LG CNS","LG CNS"),
 ("이영신",2019,"허대식","성과기반 군수(PBL)","Performance-based logistics","대한민국 공군","ROK Air Force"),
 ("김지혜",2019,"민순홍","사회적 책임활동","Corporate social responsibility","연세우유","Yonsei Milk"),
 ("이은지",2017,"허대식","친환경 공급사슬관리","Green supply chain management","삼성경제연구소","Samsung Economic Research Institute"),
 ("정주아",2017,"민순홍","공급사슬 조화","Supply chain alignment","이베스트투자증권","eBEST Investment & Securities"),
 ("주천우",2016,"민순홍","","","삼성전자","Samsung Electronics"),
 ("김경순",2016,"민순홍","친환경 경영","Environmental management","LIG넥스원","LIG Nex1"),
 ("이수민",2015,"민순홍","친환경 경영","Environmental management","현대글로비스","Hyundai Glovis"),
 ("복준혁",2010,"허대식","공급망 통합","Supply chain integration","동북재경대학 교수","Professor, Dongbei University of Finance and Economics"),
 ("서용기",2006,"김태현","공급계약의 동적 특성","Dynamics of supply contracts","로지스올그룹 부회장","Vice Chairman, Logisall Group"),
]
ALUMNI_PHD = [
 ("박채원",2026,"배성주","","","",""),
 ("박민아",2020,"배성주","","","Oberlin College 조교수","Assistant Professor, Oberlin College"),
 ("김효진",2019,"허대식","","","건국대학교 경영학과 교수","Professor, Konkuk University"),
 ("김수연",2019,"최선미","","","한밭대학교 경영학과 교수","Professor, Hanbat National University"),
 ("최종철",2019,"허대식","","","대한민국 육군본부","ROK Army Headquarters"),
 ("정현기",2013,"김태현","","","대한민국 공군본부","ROK Air Force Headquarters"),
 ("김영대",2011,"김태현","","","연세대학교 정경·창업대학원 교수","Professor, Yonsei University"),
 ("황선일",2010,"허대식","","","한국해양수산개발원 부연구위원","Associate Research Fellow, Korea Maritime Institute"),
 ("김원소",2010,"김태현","","","Bain & Company 컨설턴트","Consultant, Bain & Company"),
 ("이문일",2010,"김태현","","","",""),
 ("이인호",2010,"김태현","","","웅지세무대학교 교수","Professor, Woongji Accounting & Tax College"),
 ("김형호",2008,"김태현","","","현대종합금속 사장","President, Hyundai Welding"),
 ("박정훈",2008,"김태현","","","로지스올컨설팅 대표","CEO, Logisall Consulting"),
 ("이호창",2007,"김태현","","","가천대학교 산업경영공학과 교수","Professor, Gachon University"),
 ("문성암",1999,"김태현","","","국방대학교 국방관리학과 교수","Professor, Korea National Defense University"),
 ("김헌",1998,"김기영","","","천안대학교 경영학과 교수","Professor, Cheonan University"),
 ("김종래",1996,"김기영","","","조선대학교 산업공학과 교수","Professor, Chosun University"),
 ("조석환",1995,"김기영","","","평택대학교 경영학과 교수","Professor, Pyeongtaek University"),
 ("김지대",1995,"김기영","","","충북대학교 경영학과 교수","Professor, Chungbuk National University"),
 ("전양수",1995,"김기영","","","",""),
 ("윤장원",1994,"김기영","","","우석대학교 경영학과 교수","Professor, Woosuk University"),
 ("김탁경",1993,"김기영","","","",""),
 ("박준병",1992,"김기영","","","한밭대학교 경영학과 교수","Professor, Hanbat National University"),
 ("윤재홍",1991,"김기영","","","동아대학교 경영학과 교수","Professor, Dong-A University"),
 ("강성",1990,"김기영","","","전주대학교 경영학부 교수","Professor, Jeonju University"),
 ("오세진",1990,"김기영","","","강남대학교 경영학부 교수","Professor, Kangnam University"),
 ("김태교",1989,"김기영","","","한국항공우주산업(KAI)","Korea Aerospace Industries (KAI)"),
 ("이규상",1989,"김기영","","","목원대학교 경영학과 교수","Professor, Mokwon University"),
 ("안충영",1986,"김기영","","","",""),
 ("조병주",1985,"김기영","","","아주대학교 경영학과 교수","Professor, Ajou University"),
 ("류광정",1984,"김기영","","","",""),
]


# ---- 지원자가 자주 묻는 질문 -------------------------------------------
#
#  학교 규정에 따라 바뀌는 것(등록금 액수, 전형 일정, 어학 요건)은 여기에 쓰지 마세요.
#  그런 항목은 낡으면 단순한 방치가 아니라 오정보가 됩니다. 대학원 공지로 링크만 거세요.
#  한 번 써 두면 낡지 않는 질문만 남깁니다.
#
#  형식 (질문ko, 질문en, 답변ko, 답변en)
#
FAQ = [
 ("학부 전공이 경영학이 아니어도 지원할 수 있나요?",
  "Can I apply if my undergraduate major was not business?",
  "무관합니다. 인문·사회, 공학, 자연과학 등 다양한 배경의 학생이 함께 공부하고 있습니다. "
  "필요한 지식은 대학원 수업에서 처음부터 배웁니다. 오히려 서로 다른 배경이 연구의 출발점이 되는 경우가 많습니다.",
  "It does not matter. Students here come from the humanities, social sciences, engineering, and the natural sciences. "
  "Everything you need is taught from the ground up in our graduate courses, and a different background is often where a research question starts."),

 ("연구 주제를 아직 정하지 못했습니다. 지원해도 될까요?",
  "I have not settled on a research topic yet. Should I still apply?",
  "괜찮습니다. 대부분의 학생이 입학 후 수업과 세미나를 거치며 주제를 좁혀 갑니다. "
  "지금 필요한 것은 확정된 주제가 아니라 파고들고 싶은 질문입니다.",
  "That is fine. Most students narrow their topic during their first terms, through coursework and the seminar series. "
  "What we look for is not a finished topic but a question you want to dig into."),

 ("수업은 어떤 언어로 진행되나요?",
  "What language are the courses taught in?",
  "모든 수업은 한국어로 진행합니다. 다만 읽는 논문은 국제 학술지의 영문 논문이므로, "
  "영문 독해는 꾸준히 연습해 두시면 좋습니다.",
  "All courses are taught in Korean. The readings, however, are English-language articles from international journals, "
  "so it helps to keep practising academic reading in English."),

 ("등록금과 생활비는 어떻게 마련하나요?",
  "How do students cover tuition and living costs?",
  "수업 조교 장학금은 등록금을 면제하며, BK21 장학금 수혜자는 매 학기 선발합니다. "
  "진행 중인 연구과제에 연구보조원으로 참여하는 방법도 있습니다. "
  "금액과 신청 요건은 해마다 달라지므로 일반대학원 장학 안내를 함께 확인해 주시기 바랍니다.",
  "A teaching assistantship waives tuition, and BK21 stipends are awarded each semester. "
  "Students can also join funded research projects as research assistants. "
  "Amounts and eligibility change from year to year, so please also check the Graduate School's funding pages."),

 ("직장과 병행할 수 있나요?",
  "Can I study while working full time?",
  "석사과정에는 재직 중 학업을 병행한 사례가 있으나, 교과목이 주간에 개설되므로 일정 조율이 필요합니다. "
  "박사과정의 경우 연구에 전념하는 전일제 학업을 권합니다.",
  "Some master's students have done so, but classes meet during the day, so it takes arranging. "
  "For the doctoral program we recommend full-time study."),

 ("지도교수는 어떻게 정해지나요?",
  "How is a thesis advisor assigned?",
  "연구 관심 분야가 좁혀지면서 자연스럽게 정해집니다. "
  "지원 전에 관심 분야가 가까운 교수님께 메일로 먼저 문의하셔도 좋습니다.",
  "It follows from your research interests as they take shape. "
  "You are also welcome to write to a faculty member whose work is close to yours before you apply."),
]


# ---- 소식 (Highlights) -------------------------------------------------
#
#  여기 올리는 것
#    - 교수, 재학생, 졸업생을 가리지 않고 한 목록에 함께 올린다.
#      호칭이 이미 대상을 구분해 준다. "허대식 교수", "박채원 박사과정", "이연주 동문".
#    - 수상과 임용, 논문 게재와 연구과제 선정, 전공 차원의 변화.
#
#  여기 올리지 않는 것
#    - 세미나 개별 회차. SEMINARS 에 넣으면 세미나 페이지에 자동으로 들어간다.
#    - 연도만 아는 사실. 졸업생 표에 넣는다.
#    - 학사 공지와 장학 공지. 일반대학원과 경영대학이 이미 담당한다.
#
#  형식 (사건월, 분류, 국문 한 줄, 영문 한 줄, 링크)
#    사건월 : "YYYY-MM". 정확한 날짜를 몰라도 되도록 월까지만 쓴다.
#    분류   : NEWS_CATS 의 키. 빈 문자열이면 배지가 나오지 않는다.
#    영문   : 비워 두어도 된다. 비면 영어 화면에도 국문이 그대로 나온다.
#    링크   : 사이트 안 페이지나 외부 원문 주소. 없으면 빈 문자열.
#
NEWS_CATS = {
    "honor":   ("수상 · 임용", "Honors &amp; Appointments"),
    "research": ("연구 · 논문", "Research"),
    "program": ("전공 소식", "Program"),
}

NEWS = [
 ("2026-09", "program",
  "오퍼레이션 전공 홈페이지를 새로 열었습니다. 교수진과 입학 안내, 교과목, 재학생과 졸업생 현황, 세미나 기록을 한곳에 모았습니다.",
  "Our new program website is live, bringing together faculty, admissions, curriculum, current students, alumni, and the seminar archive.",
  ""),
 ("2026-09", "program",
  "2027학년도 전기 석·박사 신입생을 모집합니다. 원서접수는 2026년 10월 7일부터 14일까지입니다.",
  "Applications for Spring 2027 M.S. and Ph.D. admission are open from October 7 to 14, 2026.",
  "admissions.html"),
 ("2026-06", "program",
  "2026학년도 1학기 초청 세미나 시리즈를 마쳤습니다. 3월 노대훈 교수부터 6월 조형찬 교수까지 열 차례 열렸습니다.",
  "The spring 2026 invited seminar series concluded after ten talks, from Prof. Daehun Roh in March to Prof. Hyungchan Cho in June.",
  "seminars.html"),
 ("2026-04", "research",
  "Thomas Y. Choi 교수(Arizona State University)가 초청 세미나에서 발표했습니다.",
  "Prof. Thomas Y. Choi (Arizona State University) gave a talk in our invited seminar series.",
  "seminars.html"),
 ("2026-08", "honor",
  "2026년 8월 박사 한 명과 석사 세 명이 학위를 받았습니다. 박채원(지도교수 배성주), "
  "조효원(지도교수 민순홍), 박정수(지도교수 허대식), 안민정(지도교수 정승환).",
  "One doctoral and three master's students received their degrees in August 2026: "
  "박채원 (advisor: Sungjoo Bae), 조효원 (advisor: Soonhong Min), "
  "박정수 (advisor: Daesik Hur), and 안민정 (advisor: Seunghwan Jung).",
  "alumni.html"),
 ("2026-02", "honor",
  "2026년 2월 석사 두 명이 학위를 받았습니다. 손지원(지도교수 허대식), L. Jin(지도교수 민순홍).",
  "Two students received their M.S. degrees in February 2026: Jiwon Son (advisor: Daesik Hur) and L. Jin (advisor: Soonhong Min).",
  "alumni.html"),
]

MONTHS_EN = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]

# ---- 세미나 (연도 -> [(월.일, 성함, 직함ko, 직함en, 소속ko, 소속en)])
P = ("교수", "Prof.")
SEMINARS = [
 (2026, [
  ("3.13","노대훈",P[0],P[1],"고려대학교","Korea University"),
  ("4.3","남현정",P[0],P[1],"덕성여자대학교","Duksung Women's University"),
  ("4.23","Thomas Y. Choi",P[0],P[1],"Arizona State University","Arizona State University"),
  ("4.24","이승준",P[0],P[1],"중앙대학교","Chung-Ang University"),
  ("5.1","이연주",P[0],P[1],"The Pennsylvania State University","The Pennsylvania State University"),
  ("5.21","채상호",P[0],P[1],"Warwick Business School","Warwick Business School"),
  ("5.29","박재혁",P[0],P[1],"New Jersey Institute of Technology","New Jersey Institute of Technology"),
  ("6.5","김유순",P[0],P[1],"Oregon State University","Oregon State University"),
  ("6.12","임종명",P[0],P[1],"University of Miami","University of Miami"),
  ("6.19","조형찬",P[0],P[1],"Arizona State University","Arizona State University"),
 ]),
 (2025, [
  ("3.14","이평수",P[0],P[1],"경기대학교","Kyonggi University"),
  ("3.21","심재웅",P[0],P[1],"University of Connecticut","University of Connecticut"),
  ("3.28","김정현",P[0],P[1],"고려대학교","Korea University"),
  ("5.2","심정은",P[0],P[1],"서울대학교","Seoul National University"),
  ("5.16","황우남",P[0],P[1],"KAIST","KAIST"),
  ("5.23","손범호",P[0],P[1],"중앙대학교","Chung-Ang University"),
  ("6.13","김보성",P[0],P[1],"경희대학교","Kyung Hee University"),
  ("9.5","김상조",P[0],P[1],"Shanghai University of Finance and Economics","Shanghai University of Finance and Economics"),
  ("9.24","Constantin Blome",P[0],P[1],"Stockholm School of Economics","Stockholm School of Economics"),
  ("10.24","김우성",P[0],P[1],"건국대학교","Konkuk University"),
  ("11.14","박현우",P[0],P[1],"서울대학교","Seoul National University"),
  ("11.28","이철성","팀장","Team Lead","배달의민족","Woowa Brothers"),
  ("12.12","노인준",P[0],P[1],"고려대학교","Korea University"),
 ]),
 (2024, [
  ("3.8","이상준",P[0],P[1],"연세대학교","Yonsei University"),
  ("3.29","정문원",P[0],P[1],"Cleveland State University","Cleveland State University"),
  ("4.12","이중희",P[0],P[1],"University of Notre Dame","University of Notre Dame"),
  ("5.3","문성암",P[0],P[1],"국방대학교","Korea National Defense University"),
  ("5.10","윤석준",P[0],P[1],"University of Arizona","University of Arizona"),
  ("5.10","최지흥",P[0],P[1],"Eastern Michigan University","Eastern Michigan University"),
  ("5.17","이수열",P[0],P[1],"전남대학교","Chonnam National University"),
  ("5.31","배준현",P[0],P[1],"Oakland University","Oakland University"),
 ]),
 (2023, [
  ("3.10","김우성",P[0],P[1],"건국대학교","Konkuk University"),
  ("4.7","정태현",P[0],P[1],"한양대학교","Hanyang University"),
  ("4.28","최지흥",P[0],P[1],"Eastern Michigan University","Eastern Michigan University"),
  ("5.10","김성태",P[0],P[1],"Aalto University","Aalto University"),
  ("5.19","노인준",P[0],P[1],"Penn State University","Penn State University"),
  ("5.25","정승환",P[0],P[1],"연세대학교","Yonsei University"),
  ("6.9","송주명",P[0],P[1],"University of Massachusetts Lowell","University of Massachusetts Lowell"),
 ]),
 (2022, [
  ("1.27","박승재",P[0],P[1],"연세대학교","Yonsei University"),
  ("2.25","정승환",P[0],P[1],"연세대학교","Yonsei University"),
  ("3.18","김창희",P[0],P[1],"인천대학교","Incheon National University"),
  ("4.8","채상호",P[0],P[1],"Tilburg University","Tilburg University"),
  ("4.29","김은지",P[0],P[1],"중앙대학교","Chung-Ang University"),
  ("5.6","김송희",P[0],P[1],"서울대학교","Seoul National University"),
  ("5.13","강세원",P[0],P[1],"서강대학교","Sogang University"),
  ("5.20","이민경",P[0],P[1],"Baylor University","Baylor University"),
  ("5.27","유창승",P[0],P[1],"McGill University","McGill University"),
  ("6.3","김기훈",P[0],P[1],"고려대학교","Korea University"),
 ]),
 (2021, [
  ("4.2","인준환",P[0],P[1],"UNIST","UNIST"),
  ("4.9","송다혜",P[0],P[1],"University College London","University College London"),
  ("4.16","이현석",P[0],P[1],"고려대학교","Korea University"),
  ("4.30","김상원",P[0],P[1],"KAIST","KAIST"),
  ("5.7","윤지호",P[0],P[1],"중앙대학교","Chung-Ang University"),
  ("5.12","박승재",P[0],P[1],"연세대학교","Yonsei University"),
  ("5.14","김효진",P[0],P[1],"계명대학교","Keimyung University"),
  ("5.21","김보성",P[0],P[1],"부산대학교","Pusan National University"),
  ("6.4","오재영",P[0],P[1],"Central Washington University","Central Washington University"),
  ("11.15","정승환",P[0],P[1],"연세대학교","Yonsei University"),
 ]),
 (2019, [
  ("3.8","허대식",P[0],P[1],"연세대학교","Yonsei University"),
  ("3.22","정병도",P[0],P[1],"연세대학교","Yonsei University"),
  ("4.5","서용원",P[0],P[1],"중앙대학교","Chung-Ang University"),
  ("4.19","김승범",P[0],P[1],"홍익대학교","Hongik University"),
  ("5.10","Wenbo Yan",P[0],P[1],"National University of Singapore","National University of Singapore"),
  ("5.17","이승준",P[0],P[1],"중앙대학교","Chung-Ang University"),
  ("6.7","박승재",P[0],P[1],"연세대학교","Yonsei University"),
 ]),
]
SEMINAR_TOTAL = sum(len(v) for _, v in SEMINARS)

# ---- 연구 분야
# 제목에 쓰는 우리말·영문 수사. AREAS 길이가 바뀌면 제목도 같이 바뀐다.
KO_NUM = {3:"세", 4:"네", 5:"다섯", 6:"여섯", 7:"일곱", 8:"여덟", 9:"아홉", 10:"열"}
EN_NUM = {3:"Three", 4:"Four", 5:"Five", 6:"Six", 7:"Seven", 8:"Eight", 9:"Nine", 10:"Ten"}

AREAS = [
 ("chain","공급사슬 경영","Supply Chain Management",
  "구매 및 협력업체 전략, 물류와 유통채널 관리, 공급망 전체를 아우르는 통합적 경영을 연구합니다.",
  "Sourcing and supplier strategy, logistics and distribution channels, and the integrated management of end-to-end supply networks."),
 ("gear","프로세스 설계와 개선","Process Design & Improvement",
  "고객이 원하는 제품과 서비스를 만들어 내는 전환 프로세스를 설계하고 개선하는 방법을 연구합니다.",
  "Designing and improving the transformation processes through which firms create the goods and services customers want."),
 ("bulb","기술경영과 신제품 혁신","Technology & Innovation Management",
  "기술전략과 연구개발 관리에서 신제품·신서비스의 개발 방법론과 제품 설계에 이르는 혁신의 과정을 연구합니다.",
  "From technology strategy and R&D management to development methodology and product design for new products and services."),
 ("spark","서비스 오퍼레이션","Service Operations",
  "서비스 전달 프로세스, 수요·공급 조정, 수익경영 등 서비스 기업의 운영 문제를 연구합니다.",
  "Service delivery processes, demand-supply coordination, and revenue management in service firms."),
 ("ai","인공지능과 오퍼레이션","AI and Operations",
  "생성형 AI와 머신러닝을 제품 개발과 공급사슬 의사결정에 적용하는 문제를 연구합니다.",
  "Applying generative AI and machine learning to product development and supply chain decisions."),
 ("leaf","지속가능경영과 ESG","Sustainability & ESG",
  "탄소배출, 공정무역, 기업지배구조 등 공급사슬의 지속가능성 문제를 실증적으로 분석합니다.",
  "Empirical work on carbon emissions, fair trade, governance, and other sustainability questions in supply chains."),
]

METHODS = [
 ("행동과학 조사방법론","Behavioral research methods"),
 ("통계 분석 (회귀분석·다변량분석·구조방정식)","Statistics (regression, multivariate analysis, SEM)"),
 ("수리계획법 등 최적화 기법","Mathematical programming and optimization"),
 ("데이터 애널리틱스와 머신러닝","Data analytics and machine learning"),
]


# ============================================================== 졸업생 추천 글
# 졸업생이 직접 쓴 글이다. 본인의 글이므로 문장을 다듬지 않고 받은 그대로 싣는다.
# 새 글을 받으면 아래 목록에 dict 하나를 더 붙이면 된다.
#   name     (국문 이름, 영문 이름)
#   meta     (국문 한 줄, 영문 한 줄)  졸업 시기와 현재 소속
#   excerpt  홈 화면에 짧게 실을 문단들. 첫 번째 글만 홈에 나온다.
#   letter   졸업생 페이지에 실을 전문
# 영문은 본인이 쓴 것이 있으면 그것을, 없으면 번역하되 본인 확인을 받는다.
TESTIMONIALS = [
 dict(
  name=('이청헌', 'Cheongheon Lee'),
  meta=('2022년 2월 석사 졸업 &middot; 現 삼정KPMG',
        'M.S. 2022 &middot; now at KPMG Korea'),
  # 홈 화면에 짧게 싣는 부분
  excerpt=[
   ('OM은 가치의 흐름에 대한 학문이라 생각합니다. 그렇기에 모든 기업과 조직에 적용할 수 있는 범용성을 가지면서, 동시에 다양한 지식과 경험이 영감의 원천이 될 수 있으리라 봅니다.',
    'I came to think of OM as the study of how value flows. That makes it general enough to apply to any organization, while letting all kinds of knowledge and experience become a source of insight.'),
   ('앞으로의 OM 신입생분들도 경영학의 지평을 넓히면서 자신만의 경쟁력을 만들고, 나아가 새로운 커리어의 전환점을 맞을 수 있으리라 기대합니다.',
    'I hope the students who come next will widen the horizon of business research, build something that is theirs alone, and find a turning point in their careers.'),
  ],
  # 졸업생 페이지에 싣는 전문
  letter=[
   ('안녕하세요, 이청헌입니다. 저는 문과대 학부 전공과 일용·계약직·스타트업 등의 경험적 배경을 바탕으로, 전공 과정을 이해하고 연구를 수행하면서 ESG 관련 논문으로 석사 과정을 마쳤습니다. 현재는 이때의 배움의 연장선에서 지속가능성 컨설턴트로 근무하고 있습니다.',
    "My name is Cheongheon Lee. I came from a humanities background and a working history of day jobs, contract work, and startups. I finished my master's with a thesis on ESG, and I now work as a sustainability consultant, which is a direct continuation of what I learned here."),
   ('2년의 석사 기간 동안의 제 짧은 식견에서 OM(Operations Management)은 가치의 흐름에 대한 학문이라 생각합니다. 그렇기에 모든 기업과 조직에 적용할 수 있는 범용성을 가지면서, 동시에 다양한 지식과 경험이 영감의 원천이 될 수 있으리라 봅니다.',
    'In the two years of the program I came to see Operations Management as the study of how value flows. That makes it general enough to apply to any firm or organization, and it means that all kinds of knowledge and experience can become a source of insight.'),
   ('얼핏 경영학과 다소 동떨어져 보이는 학문적·업무적 분야가 OM과 경영학의 경계를 넓혀온 수많은 연구들을 기억합니다.',
    'I remember the many studies in which fields that look far removed from business research turned out to widen the boundary of OM.'),
   ('앞으로의 OM 신입생분들도 경영학의 지평을 넓히면서 자신만의 경쟁력을 만들고, 나아가 새로운 커리어의 전환점을 맞을 수 있으리라 기대합니다.',
    'I hope the students who come next will widen that horizon too, build something that is theirs alone, and find a turning point in their own careers.'),
  ],
 ),
]


def testimonial_excerpt(tm):
    """홈 화면용. 발췌 문단과 서명만 싣는다."""
    return ('<div class="tquote">\n'
            + "".join("     %s\n" % t(ko, en, "p") for ko, en in tm["excerpt"])
            + '     <div class="tquote__by"><span>%s%s</span></div>\n'
              % (t("<b>%s</b>" % tm["name"][0], "<b>%s</b>" % tm["name"][1]),
                 t("<span>%s</span>" % tm["meta"][0], "<span>%s</span>" % tm["meta"][1]))
            + '    </div>')


def testimonial_letters():
    """졸업생 페이지용. 추천 글을 모두 전문으로 싣는다."""
    out = []
    for i, tm in enumerate(TESTIMONIALS):
        gap = "" if i == 0 else ";margin-top:28px"
        out.append('<div class="tquote rv" style="max-width:820px%s">\n' % gap
                   + "".join("   %s\n" % t(ko, en, "p") for ko, en in tm["letter"])
                   + '   <div class="tquote__by"><span>%s%s</span></div>\n'
                     % (t("<b>%s</b>" % tm["name"][0], "<b>%s</b>" % tm["name"][1]),
                        t("<span>%s</span>" % tm["meta"][0], "<span>%s</span>" % tm["meta"][1]))
                   + '  </div>')
    return "\n  ".join(out)

# ============================================================== components
def fcard(f, delay=0, show_roles=False):
    ko, en, ini, rko, ren, iko, ien, mail, url, photo = f[:10]
    extra = f[10] if len(f) > 10 else None
    chips = ""
    if mail:
        chips += '<a class="chip" href="mailto:%s">%s%s</a>' % (mail, I["mail"], t("이메일", "E-mail"))
    if url:
        chips += '<a class="chip" href="%s" target="_blank" rel="noopener">%s%s</a>' % (
            url, I["ext"], t("개인 홈페이지", "Homepage"))
    if extra:
        chips += '<a class="chip" href="%s" target="_blank" rel="noopener">%s%s</a>' % (
            extra[0], I["ext"], t(extra[1], extra[2]))
    where = ""
    if ko in FACULTY_CONTACT:
        room, tel = FACULTY_CONTACT[ko]
        where = ('<p class="fcard__where">%s<span>%s</span></p>'
                 % (I["pin"], t("%s &middot; %s" % (room, tel),
                                "%s &middot; %s" % (room.replace("경영관", "Business Hall"), tel))))
    roles = ""
    if show_roles:
        rs = FACULTY_ROLES.get(ko, [])
        if rs:
            roles = '<ul class="fcard__roles">%s</ul>' % "".join(
                "<li>%s%s</li>" % (I["check"], t(rko, ren)) for rko, ren in rs)
    return '''<article class="fcard rv" data-delay="%d">
 <div class="fcard__ph"><img src="assets/img/faculty/%s" alt="" loading="lazy" onerror="this.remove()"><span class="fcard__ini">%s</span></div>
 <div class="fcard__b">
  %s
  %s
  %s
  %s
  %s
  <div class="fcard__f">%s</div>
 </div>
</article>''' % (delay, photo, ini,
                 t(ko, en, "div", "fcard__name"),
                 t(rko, ren, "div", "fcard__role"),
                 t(iko, ien, "p", "fcard__int"), where, roles, chips)

def seminar_list(items, limit=None):
    rows = ""
    for d, nm, rko, ren, ako, aen in (items[:limit] if limit else items):
        rows += ('<li><span class="d">%s</span><span class="who">%s</span>%s</li>'
                 % (d, speaker(nm, rko, ren, aen), t(ako, aen, "span", "aff")))
    return '<ul class="tl">%s</ul>' % rows

def faq_block():
    """답이 낡지 않는 질문만 모은 아코디언. JS 없이 details 로만 동작한다."""
    rows = ""
    for i, (qko, qen, ako, aen) in enumerate(FAQ):
        rows += ('<details class="faq__i rv"%s data-delay="%d"><summary>%s</summary>%s</details>'
                 % (" open" if i == 0 else "", min(i, 4) * 50,
                    t(qko, qen, "span", "faq__q"), t(ako, aen, "p", "faq__a")))
    return '<div class="faq">%s</div>' % rows


def news_row(item):
    ym, cat, ko, en, url = item
    y, m = ym.split("-")
    date = t("%s. %s." % (y, int(m)), "%s %s" % (MONTHS_EN[int(m) - 1], y),
             "time", "news__d").replace("<time ", '<time datetime="%s" ' % ym)
    tag = ""
    if cat:
        tag = '<span class="news__tag">%s</span>' % t(NEWS_CATS[cat][0], NEWS_CATS[cat][1])
    # 영문이 없으면 영어 화면에도 국문을 그대로 보여준다. 누락보다 낫다.
    body = t(ko, en) if en else t(ko, '<span lang="ko">%s</span>' % ko)
    if url:
        ext = url.startswith("http")
        body = '<a href="%s"%s>%s%s</a>' % (
            url, ' target="_blank" rel="noopener"' if ext else "",
            body, I["ext"] if ext else I["arrow"])
    return '<li>%s%s<span class="news__t">%s</span></li>' % (date, tag, body)


def news_block(limit=5):
    """홈에 붙는 소식 블록. 최근 몇 건만 보여 주고 전체는 news.html 에 둔다."""
    if not NEWS:
        return ""
    items = sorted(NEWS, key=lambda x: x[0], reverse=True)[:limit]
    return '<ul class="news rv">%s</ul>' % "".join(news_row(x) for x in items)


def area_cards():
    out = ""
    for i, (ic, ko, en, dko, den) in enumerate(AREAS):
        out += ('<article class="card card--hover rv" data-delay="%d"><div class="card__ico">%s</div>%s%s</article>'
                % (i * 70, I[ic], t(ko, en, "h3"), t(dko, den, "p")))
    return out

# ============================================================== index
def build_index():
    stats = [
        (len(FACULTY), "전임 교수", "Faculty members"),
        (len(STUDENTS), "재학 대학원생", "Current graduate students"),
        (len(ALUMNI_MS) + len(ALUMNI_PHD), "석·박사 졸업생", "M.S. &amp; Ph.D. alumni"),
        (SEMINAR_TOTAL, "초청 연구 세미나", "Invited research seminars"),
    ]
    strip = "".join(
        '<div class="stat"><div class="stat__n" data-count="%d">%d</div>%s</div>'
        % (n, n, t(ko, en, "div", "stat__l")) for n, ko, en in stats)

    why = [
        ("chart", "OM · Business Analytics 융합전공", "OM x Business Analytics",
         "2020년 1학기부터 BA 융합과정을 운영합니다. 필수 6과목 포함 36학점을 이수하면 융합전공 학위를 받습니다.",
         "Since spring 2020 we have offered a joint track with Business Analytics: 36 credits including six required BA courses."),
        ("won", "장학 제도", "Financial support",
         "교수 1인당 수업 조교 장학금(등록금 면제), 매 학기 BK 장학금, 관정·용운·배정 등 외부 장학금을 안내합니다.",
         "A teaching-assistant scholarship (full tuition) per faculty member, BK21 stipends each semester, plus external fellowships."),
        ("mic", "연구 세미나 시리즈", "Research seminar series",
         "국내외 주요 대학의 연구자를 초빙하여 매 학기 세미나를 개최합니다. 학생은 이를 통해 최신 연구 동향을 파악하고 자신의 연구 주제를 구체화합니다.",
         "Each semester we host scholars from leading universities at home and abroad, helping students find and sharpen their own topics."),
    ]
    whyc = "".join(
        '<article class="card card--hover rv" data-delay="%d"><div class="card__ico">%s</div>%s%s</article>'
        % (i * 70, I[ic], t(ko, en, "h3"), t(dko, den, "p"))
        for i, (ic, ko, en, dko, den) in enumerate(why))

    meth = "".join('<li>%s%s</li>' % (I["check"], t(ko, en)) for ko, en in METHODS)

    acad = [("이연주", "Penn State University"), ("박민아", "Oberlin College"),
            ("김효진", "건국대학교|Konkuk University"), ("김수연", "한밭대학교|Hanbat National University"),
            ("정대훈", "University of Florida"), ("복준혁", "동북재경대학|Dongbei Univ. of Finance & Economics")]
    acad_html = ""
    for nm, aff in acad:
        ko, en = (aff.split("|") + [aff])[:2] if "|" in aff else (aff, aff)
        acad_html += '<li>%s<span><b>%s</b> &middot; %s</span></li>' % (I["cap"], nm, t(ko, en))

    body = '''
<section class="hero">
 <div class="hero__bg"><div class="hero__grad"></div><div class="hero__photo"></div><div class="hero__veil"></div></div>
 %s
 %s
 <div class="wrap hero__in">
  <div class="eyebrow rv">%s</div>
  %s
  %s
  <div class="hero__cta rv" data-delay="180">
   <a class="btn btn--light" href="admissions.html">%s%s</a>
   <a class="btn btn--ghost" href="faculty.html">%s</a>
  </div>
  <div class="hero__meta rv" data-delay="260">
   %s %s
  </div>
 </div>
</section>

<section class="strip"><div class="wrap"><div class="strip__in">%s</div>%s</div></section>

<section class="sec">
 <div class="wrap">
  <div class="split">
   <div>
    %s
    %s
    %s
   </div>
   <div class="rv" data-delay="120">
    <div class="card" style="padding:32px">
     %s
     <ul class="flist" style="margin-top:18px">%s</ul>
     <p style="margin-top:24px;padding-top:20px;border-top:1px solid var(--line-soft);color:var(--muted);font-size:14px">%s</p>
    </div>
   </div>
  </div>
 </div>
</section>

<section class="sec sec--soft">
 <div class="wrap">
  <div class="sechead">
   %s
   %s
  </div>
  <div class="grid g3">%s</div>
 </div>
</section>

<section class="sec">
 <div class="wrap">
  <div class="sechead sechead--row">
   <div>
    %s
   </div>
   <a class="btn btn--outline rv" href="admissions.html">%s%s</a>
  </div>
  <div class="grid g3">%s</div>
 </div>
</section>

<section class="sec sec--soft">
 <div class="wrap">
  <div class="sechead sechead--row">
   <div>
    %s
    %s
   </div>
   <a class="btn btn--outline rv" href="faculty.html">%s%s</a>
  </div>
  <div class="fac">%s</div>
 </div>
</section>

<section class="sec">
 <div class="wrap">
  <div class="split">
   <div>
    %s
    %s
    <div class="rv" style="margin-top:26px"><a class="btn btn--outline" href="seminars.html">%s%s</a></div>
   </div>
   <div class="rv" data-delay="120">%s</div>
  </div>
 </div>
</section>

<section class="sec sec--soft" id="highlights">
 <div class="wrap">
  <div class="sechead sechead--row">
   <div>
    %s
    %s
   </div>
   <a class="btn btn--outline rv" href="news.html">%s%s</a>
  </div>
  %s
 </div>
</section>

<section class="sec">
 <div class="wrap">
  <div class="split">
   <div class="rv">
    %s
    %s
    <ul class="flist" style="margin-top:24px">%s</ul>
    <div style="margin-top:28px"><a class="btn btn--outline" href="alumni.html">%s%s</a></div>
   </div>
   <div class="rv" data-delay="120">
    %s
   </div>
  </div>
 </div>
</section>

<section class="sec sec--tight">
 <div class="wrap">
  <div class="cta rv">
   <div class="cta__in">
    %s
    %s
    <div class="cta__row">
     <a class="btn btn--light" href="admissions.html">%s%s</a>
     <a class="btn btn--ghost" href="mailto:seunghwan.jung@yonsei.ac.kr">%s%s</a>
    </div>
   </div>
  </div>
 </div>
</section>
''' % (
 ARCH, net("hero__net"),
 t("연세대학교 경영대학 &middot; 석사 / 박사 과정",
   "Yonsei School of Business &middot; M.S. / Ph.D. Programs"),
 ('<h1 class="rv" data-delay="80">%s<span class="accent ko">가치의 흐름을 설계하는&nbsp;학문</span>'
  '<span class="accent en">Designing how value flows</span></h1>'
  % t("오퍼레이션 전공", "Operations Management", "span")),
 t("본 전공은 고객이 원하는 제품과 서비스를 만들어 내는 기업의 전환 프로세스를 설계하고 관리하며 개선하는 방법을 연구합니다. 신제품 개발에서 구매·생산·물류를 거쳐 공급망 전체의 통합적 경영에 이르는 영역이 연구 대상입니다.",
   "We study how firms design, manage, and improve the transformation processes that create the goods and services customers want, from new product development through sourcing, production, and logistics, to the integrated management of the entire supply network.",
   "p", "lede rv"),
 t("석·박사 과정 안내", "Admissions"), I["arrow"],
 t("전공 교수 소개", "Meet the faculty"),
 t("2027학년도 전기 석사 · 박사 모집", "Admissions for Spring 2027", "span"),
 t("OM &middot; Business Analytics 융합전공", "Joint track with Business Analytics", "span"),
 strip,
 t("%s 기준" % LAST_REVIEWED_KO, "As of %s" % LAST_REVIEWED_EN, "p", "strip__as"),
 t("첫 박사 학위자를 배출한 해, <em>1984</em>년",
   "Our first doctorate, <em>1984</em>", "h2", "lead-quote"),
 t("연세대학교 경영대학 오퍼레이션 전공 홈페이지입니다. 지금은 전임 교수 %d명이 박사과정 %d명과 석사과정 %d명을 지도하고 있고, 2019년 이후 국내외 연구자를 초청해 %d차례 세미나를 열었습니다."
   % (len(FACULTY), sum(1 for x in STUDENTS if x[1] == "phd"), sum(1 for x in STUDENTS if x[1] == "ms"), SEMINAR_TOTAL),
   "This is the Operations Management area at Yonsei School of Business. Six faculty members currently advise three doctoral and nine master's students, and we have hosted %d research seminars since 2019."
   % SEMINAR_TOTAL,
   "p", "body-copy"),
 t("Operations Management(운영관리) 분야에서는 고객이 원하는 제품과 서비스를 창출하는 기업의 전환 프로세스(transformation process)를 설계·관리·개선하는 방법을 연구합니다. 신제품 및 신서비스의 설계와 혁신, 생산 및 서비스 전달 프로세스의 구축, 구매 및 물류 프로세스 등 가치사슬 전반에 걸쳐 연구하며, 최근에는 공급업체 및 유통·판매업체와의 전략적 협업을 통한 공급망 전체의 통합적 경영으로 연구 범위가 확대되었습니다.",
   "Operations Management asks how firms actually get things made and delivered. We work on new product development, sourcing and production, logistics, and service delivery. In recent years the field has widened from single firms to whole supply networks.",
   "p", "body-copy"),
 t("연구방법론", "Research methods", "h3"), meth,
 t("학부 전공은 무관합니다. 필요한 지식은 대학원 수업에서 처음부터 배울 수 있습니다.",
   "Your undergraduate major does not matter. Everything you need is taught from the ground up in our graduate courses."),
 t("%s 갈래의 <span class=\"thin\">연구 분야</span>" % KO_NUM[len(AREAS)],
   "%s lines of <span class=\"thin\">inquiry</span>" % EN_NUM[len(AREAS)], "h2"),
 t("구매와 협력업체 전략에서 지속가능성까지, 가치사슬 전반을 다룹니다.",
   "From sourcing and supplier strategy to sustainability, across the whole value chain.", "p", "dek"),
 area_cards(),
 t("이곳에서 공부하는 방식", "What studying here looks like", "h2"),
 t("입학 안내 자세히 보기", "See admissions"), I["arrow"], whyc,
 t("전공 교수진", "Our faculty", "h2"),
 t("여섯 분의 전임 교수와 두 분의 명예교수가 함께합니다.",
   "Six full-time faculty members and two professors emeriti.", "p", "dek"),
 t("전체 보기", "View all"), I["arrow"],
 "".join(fcard(f, i * 60) for i, f in enumerate(FACULTY)),
 t("매 학기 열리는 <span class=\"thin\">연구 세미나</span>", "A seminar <span class=\"thin\">every few weeks</span>", "h2"),
 t("본 전공은 국내외 주요 대학의 연구자를 초빙하여 연구 발표 시리즈를 운영합니다. 석·박사 과정 학생은 이를 통해 최신 연구 동향을 파악하고 자신의 연구 주제를 선정·발전시킵니다.",
   "We invite scholars from leading universities in Korea and abroad. For our graduate students the series is where research trends become visible and dissertation topics take shape.",
   "p", "body-copy"),
 t("전체 일정 보기", "All seminars"), I["arrow"],
 seminar_list(SEMINARS[0][1][-6:]),
 t("소식", "Highlights", "h2"),
 t("교수와 학생, 졸업생의 소식을 한곳에 모았습니다.",
   "News from our faculty, students, and alumni in one place.", "p", "dek"),
 t("전체 소식 보기", "All news"), I["arrow"],
 news_block(),
 t("졸업 후 <span class=\"thin\">진로</span>", "Where our graduates <span class=\"thin\">go</span>", "h2"),
 t("졸업생들은 국내외 기업의 프로세스 설계와 공급사슬 관리, 컨설팅, 연구소, 그리고 학계로 진출합니다. 학계로 진출한 동문들은 국내외 대학에서 연구와 교육을 이어가고 있습니다.",
   "Our graduates work in process design and supply chain management at Korean and multinational firms, in consulting, in research institutes, and in academia, in Korea and abroad.",
   "p", "body-copy"),
 acad_html,
 t("졸업생 현황 보기", "Alumni placements"), I["arrow"],
 testimonial_excerpt(TESTIMONIALS[0]),
 t("열정을 갖춘 석·박사 과정 학생을 모집합니다",
   "We are looking for students with a genuine appetite for research", "h2"),
 t("입학을 위해 필요한 지식은 대학원 수업에서 처음부터 배울 수 있습니다. 학부 전공은 무관합니다. 필요한 것은 주요 연구 분야에 대한 열정입니다.",
   "Everything you need is taught from the beginning in our graduate courses, whatever you majored in. What we ask for is enthusiasm for the questions we work on.",
   "p"),
 t("입학 안내 보기", "Admissions"), I["arrow"],
 t("입학 문의 메일 보내기", "E-mail us"), I["mail"],
)
    page("index.html",
         "연세대학교 경영대학 오퍼레이션 전공 | 석사 · 박사 과정",
         "Operations Management, Yonsei School of Business | M.S. &amp; Ph.D. Programs",
         "연세대학교 경영대학 오퍼레이션(Operations Management) 전공 석·박사 과정 공식 홈페이지. 공급사슬, 서비스 오퍼레이션, 기술경영, 지속가능경영 연구와 대학원 입학 안내.",
         body)

# ============================================================== faculty
def build_faculty():
    body = phead("Faculty", "전공 교수 소개", "Faculty",
                 t("전임 교수 6명 · 명예교수 2명", "Six faculty members, two emeriti"),
                 "연세대학교 경영대학 오퍼레이션 전공 교수진입니다. 각 교수의 상세 이력과 연구 내용은 개인 홈페이지에서 확인하실 수 있습니다.",
                 "The Operations Management faculty at Yonsei School of Business. Fuller profiles are available on each professor's own page.")
    body += '''
<section class="sec">
 <div class="wrap">
  <div class="sechead">%s</div>
  <div class="fac">%s</div>
 </div>
</section>
<section class="sec sec--soft">
 <div class="wrap">
  <div class="sechead">%s%s</div>
  <div class="fac">%s</div>
 </div>
</section>
''' % (t("전임 교수", "Full-time faculty", "h2"),
       "".join(fcard(f, i * 60, show_roles=True) for i, f in enumerate(FACULTY)),
       t("명예교수", "Professors emeriti", "h2"),
       t("본 전공의 오늘을 만든 두 분의 명예교수입니다.",
         "Two emeriti who built the area into what it is today.", "p", "dek"),
       "".join(fcard(f, i * 60) for i, f in enumerate(EMERITUS)))
    page("faculty.html",
         "전공 교수 소개 | 연세대 경영대학 오퍼레이션 전공",
         "Faculty | Operations Management, Yonsei School of Business",
         "연세대학교 경영대학 오퍼레이션 전공 교수진 소개와 연구 관심 분야.", body)

# ============================================================== admissions
def build_admissions():
    careers = [
     ("cube", "기업", "Industry",
      "국내 및 다국적 기업의 프로세스 디자인 및 관리, 호텔·레스토랑·병원 등 서비스 경영, 신제품개발, 구매, 물류 및 유통, 글로벌 공급사슬관리, 시스템 통합 등",
      "Process design and management, service management in hotels, restaurants, and hospitals, new product development, sourcing, logistics and distribution, global supply chain management, and systems integration."),
     ("gear", "컨설팅", "Consulting",
      "국내외 컨설팅업체에서 프로세스 개선, 서비스 경영, 신제품 개발 등의 분야를 담당하는 컨설턴트",
      "Consultants at Korean and global firms working on process improvement, service management, and new product development."),
     ("book", "연구직", "Research institutes",
      "대기업 경영·경제 연구소 및 국책 연구소의 연구원",
      "Researchers at corporate economic research centers and government-funded research institutes."),
     ("cap", "학계", "Academia",
      "국내외 박사과정 진학 후 교수직 및 연구직 진출",
      "Ph.D. study in Korea or abroad, then faculty and research positions."),
    ]
    ccards = "".join(
      '<article class="card card--hover rv" data-delay="%d"><div class="card__ico">%s</div>%s%s</article>'
      % (i * 70, I[ic], t(ko, en, "h3"), t(dko, den, "p"))
      for i, (ic, ko, en, dko, den) in enumerate(careers))

    prep = [
      ("경영학 및 인문·사회과학(경제학·사회학·심리학) 기초 지식",
       "Basic grounding in business and the social sciences (economics, sociology, psychology)"),
      ("기초 통계 및 통계 패키지 활용법 (SPSS 등)",
       "Introductory statistics and a statistical package such as SPSS"),
      ("영문 학술 문헌 독해 및 국문·영문 논리적 작문 연습",
       "Reading academic English, and writing clear arguments in both English and Korean"),
    ]
    prep_html = "".join('<li>%s%s</li>' % (I["check"], t(ko, en)) for ko, en in prep)

    sch = [
      ("조교 장학금", "Teaching assistantship",
       "교수 1인당 수업 조교 장학금 한 명 (등록금 면제)", "One TA position per faculty member, with full tuition waived.", ""),
      ("BK21 장학금", "BK21 fellowship",
       "매 학기 1~2명 이상 선발 가능", "One to two students selected each semester, sometimes more.",
       "https://youtu.be/U1eb2KotO2o"),
      ("외부 장학금", "External fellowships",
       "관정 장학금, 용운 장학금, 배정 장학금 등", "Kwanjeong, Yongwoon, Baejeong, and other external programs.",
       "https://graduate.yonsei.ac.kr/graduate/board/notice.do?mode=list&srCategoryId1=225"),
    ]
    sch_html = ""
    for i, (ko, en, dko, den, link) in enumerate(sch):
        extra = ('<div style="margin-top:16px"><a class="chip" href="%s" target="_blank" rel="noopener">%s%s</a></div>'
                 % (link, I["ext"], t("자세히 보기", "Learn more"))) if link else ""
        sch_html += ('<article class="card card--hover rv" data-delay="%d">%s%s%s</article>'
                     % (i * 70, t(ko, en, "h3"), t(dko, den, "p"), extra))

    body = phead("Admissions", "석·박사 과정 입학 안내", "Admissions",
                 t("2027학년도 전기 · 2027년 3월 입학", "Spring 2027 entry"),
                 "본 전공에서는 열정을 갖춘 석·박사 학생들을 모집하고 있습니다. 필요한 지식은 대학원 수업에서 처음부터 새로 배울 수 있으며, 학부 전공은 무관합니다.",
                 "We are recruiting master's and doctoral students with a real appetite for research. Whatever you studied as an undergraduate, the knowledge you need is taught from the beginning in our graduate courses.")
    body += '''
<section class="sec">
 <div class="wrap">
  <div class="split">
   <div>
    %s
    %s
    <ul class="flist rv" style="margin-top:22px">%s</ul>
   </div>
   <div class="rv" data-delay="120">
    <div class="card" style="padding:32px">
     %s
     %s
     <ul class="flist" style="margin-top:18px">%s</ul>
    </div>
   </div>
  </div>
 </div>
</section>

<section class="sec sec--soft">
 <div class="wrap">
  <div class="sechead">
   %s
   %s
  </div>
  <div class="grid g4">%s</div>
 </div>
</section>

<section class="sec">
 <div class="wrap">
  <div class="split">
   <div class="rv">
    %s
    %s
    <div style="margin-top:26px"><a class="btn btn--outline" href="courses.html">%s%s</a></div>
   </div>
   <div class="rv" data-delay="120">
    <div class="card" style="padding:32px">
     <div class="card__ico">%s</div>
     %s
     %s
    </div>
   </div>
  </div>
 </div>
</section>

<section class="sec sec--soft">
 <div class="wrap">
  <div class="sechead sechead--row">
   <div>%s</div>
   <a class="btn btn--outline rv" href="https://graduate.yonsei.ac.kr/graduate/academic/scholarship.do" target="_blank" rel="noopener">%s%s</a>
  </div>
  <div class="grid g3">%s</div>
 </div>
</section>

<section class="sec" id="faq">
 <div class="wrap">
  <div class="sechead">
   %s
   %s
  </div>
  %s
  <p class="note rv" style="margin-top:28px">%s <a href="https://graduate.yonsei.ac.kr/graduate/admission/general_schedule.do" target="_blank" rel="noopener">%s</a></p>
 </div>
</section>

<section class="sec sec--tight">
 <div class="wrap">
  <div class="cta rv">
   %s
   <div class="cta__in">
    %s
    %s
    <div class="cta__row">
     <a class="btn btn--light" href="mailto:seunghwan.jung@yonsei.ac.kr">%s%s</a>
     <a class="btn btn--ghost" href="alumni.html#letter">%s</a>
    </div>
   </div>
  </div>
 </div>
</section>
''' % (
 t("주요 연구 분야", "What we work on", "h2"),
 t("공급사슬 관리, 서비스 관리, 기술경영, 인공지능, ESG와 지속가능 경영, 공급사슬 애널리틱스를 중심으로 연구합니다.",
   "Supply chain management, service management, technology management, artificial intelligence, ESG and sustainability, and supply chain analytics.",
   "p", "dek"),
 "".join('<li>%s%s</li>' % (I["check"], t(ko, en)) for _, ko, en, _, _ in AREAS),
 t("입학을 위해 필요한 지식", "What you need to bring", "h3"),
 t("주요 연구 분야에 대한 열정 하나면 충분합니다. 나머지 지식은 대학원 수업에서 처음부터 배웁니다. 다만 아래 항목을 미리 준비해 두면 시작이 한결 수월합니다.",
   "Enthusiasm for the questions above is the requirement. Everything else is taught from scratch. Still, the following make the first year easier.",
   "p", "dek"),
 prep_html,
 t("졸업 후 진로", "Where our graduates go", "h2"),
 t("본 전공에서 석사 30명과 박사 30명이 학위를 받았습니다. 이 가운데 20명은 대학에 교수로 재직하고 있으며, 나머지는 기업과 컨설팅, 연구기관, 군 등에 진출하였습니다.",
   "Thirty master's and thirty doctoral students have graduated from the area. Twenty of them now teach at universities; the rest work in industry, consulting, research institutes, and the armed forces.",
   "p", "dek"),
 ccards,
 t("Business Analytics 융합전공", "A joint track with Business Analytics", "h2"),
 t("최근 학계와 실무에서 급속히 주목받는 Business Analytics 역량을 갖추도록 2020년 1학기부터 BA 융합 과정을 운영하고 있습니다. OM 전공의 졸업 요건을 충족하면서 BA 전공 필수 6과목을 포함해 총 36학점(방법론 9학점 포함)을 이수하면 'OM / BA 융합전공' 학위를 받습니다.",
   "Since spring 2020 we have run a joint track with Business Analytics. Students who meet the OM degree requirements and complete 36 credits, including six required BA courses and nine credits of methods, receive the joint OM / BA degree.",
   "p", "body-copy"),
 t("교과목 자세히 보기", "See the curriculum"), I["arrow"],
 I["chart"],
 t("BA 전공 필수 과목", "Required BA courses", "h3"),
 t("Business Analytics 1 &middot; Business Analytics 2 &middot; Data Management for BA &middot; Web &amp; Text Analytics &middot; AI for Business &middot; BA Capstone",
   "Business Analytics 1 &middot; Business Analytics 2 &middot; Data Management for BA &middot; Web &amp; Text Analytics &middot; AI for Business &middot; BA Capstone", "p"),
 t("장학 제도", "Scholarships and funding", "h2"),
 t("대학원 장학 안내", "Graduate school funding"), I["ext"],
 sch_html,
 t("자주 묻는 질문", "Frequently asked questions", "h2"),
 t("지원을 앞두고 가장 많이 받는 질문과 답을 정리했습니다.",
   "The questions we are asked most often by prospective students.", "p", "dek"),
 faq_block(),
 t("전형 일정과 어학 요건, 등록금처럼 해마다 바뀌는 사항은 연세대학교 일반대학원 공고를 확인해 주시기 바랍니다.",
   "For items that change each year, such as the application timeline, language requirements, and tuition, please refer to the Yonsei Graduate School announcements."),
 t("일반대학원 입시 안내", "Graduate School admissions"),
 net("cta__net"),
 t("석·박사 과정 문의", "Contact us", "h2"),
 t("오퍼레이션 전공 석·박사 과정에 대한 문의는 정승환 교수(seunghwan.jung@yonsei.ac.kr)에게 연락 주시기 바랍니다.",
   "For questions about the M.S. and Ph.D. programs, please contact Prof. Seunghwan Jung at seunghwan.jung@yonsei.ac.kr.", "p"),
 t("메일 보내기", "Send an e-mail"), I["mail"],
 t("졸업생 추천 글 읽기", "Read an alumnus's letter"),
)
    page("admissions.html",
         "석·박사 과정 입학 안내 | 연세대 경영대학 오퍼레이션 전공",
         "Admissions | Operations Management, Yonsei School of Business",
         "연세대 경영대학 오퍼레이션 전공 석사·박사 과정 입학 안내, 진로, 장학금, BA 융합전공 정보.", body)

# ============================================================== courses
# 전공 교과목 (원본 사이트 교과목 표 기준): 과목명ko, 과목명en, 학점, 설명ko, 설명en
COURSES = [
 ("OM 워크샵", "OM Workshop", "1.5",
  "교내외 교수·강사 초빙 강의 등을 통한 대학원생의 연구 역량 증진을 목적으로 합니다.",
  "Builds the research capability of graduate students through invited lectures by faculty and speakers from inside and outside the university."),
 ("OM 프로세미나", "OM Proseminar", "1.5",
  "Operations Management 분야의 석사·박사과정 학생들이 모여 각자의 연구 주제를 발표하고 토론합니다. 또한 필요에 따라 학계와 산업계의 연사를 초청하여 강의와 토론을 진행함으로써 학생들이 이 분야의 다양한 주제를 접할 수 있도록 합니다.",
  "Master's and doctoral students in Operations Management gather to present and discuss their own research topics. Speakers from academia and industry are also invited, so that students encounter the full range of topics in the field."),
 ("OM/SCM 연구방법론", "OM/SCM Research Methodology", "3",
  "연구 설계와 방법론 전반을 다루는 대학원 세미나입니다. 공급사슬·오퍼레이션 분야의 대학원생이 연구 아이디어 생성에서 이론과 모형 개발, 연구 설계, 자료 수집과 분석, 그리고 논문 출판에 이르는 과정을 폭넓게 접하도록 설계되었습니다. 학술적 글쓰기와 저널 출판의 윤리 문제도 함께 다룹니다. 매주 다루는 주제는 그 자체로 한 과목이 될 만한 것으로, 해당 영역으로 들어가는 입구 역할을 합니다. 통계 과목이 아니라 연구방법론 과목이므로 통계에 대한 기초 지식은 전제합니다. 최종 산출물은 학술대회, 되도록 국제 학술대회에서 발표할 수 있는 수준의 연구 제안서입니다.",
  "A graduate seminar surveying research design and methods. It introduces students in supply chain and operations management to the whole arc of research, from idea generation to theory and model development, research design, data collection and analysis, and publication. Academic writing and the ethics of journal publication are also discussed. Each weekly topic could constitute a course in itself and serves as an entry point to that area. This is not a statistics course but a methodology course, so familiarity with statistics is assumed. The exit criterion is a research proposal presentable at an academic conference, preferably an international one."),
 ("전략적 구매관리", "Strategic Purchasing Management", "3",
  "구매 및 공급 관리 분야의 주요 연구 주제를 소개하고, 대학원생이 이 분야에서 출판 가능한 연구 논문을 쓸 수 있도록 준비시키는 과목입니다. 수강 후 학생들은 (1) 공급 관리가 기업 경쟁력에 기여하는 방식과 공급사슬 관리에서의 역할을 이해하고, (2) 공급 관리의 최신 연구 이슈에 익숙해지며, (3) 문제 정의, 문헌 연구, 모형 개발, 연구방법 선택으로 이어지는 연구 과정을 직접 경험합니다.",
  "Introduces the major research topics in purchasing and supply management and prepares graduate students to write publishable papers in the field. On completing the course students should be able to: learn how supply management contributes to corporate competitiveness and understand its role in supply chain management; familiarize themselves with up-to-date research issues in supply management; and experience the research process from problem identification, literature review, and model development through the selection of research methods."),
 ("기술혁신세미나", "Technology Innovation Seminar", "3",
  "본 과목은 경영대학 석사·박사과정 학생을 대상으로, 기술혁신 관련 연구 논문과 서적을 바탕으로 이 분야의 기초 개념을 정립하고 현재의 연구 동향을 소개합니다. 전반부에는 기술혁신의 기초개념인 Schumpeterian Competition and Industry Dynamics, Patterns of Technological Change, Firm Failures, Science and Technology, Market Demand and Diffusion 등을 다루고, 후반부에서는 조금 더 미시적인 시각에서 Modularity, Standards and Networks, Knowledge and Capabilities, Learning and Problem-Solving, Development of New Products and Processes 등을 다룹니다.",
  "For master's and doctoral students in the School of Business, this seminar builds the foundational concepts of technological innovation from research articles and books and surveys the current research landscape. The first half covers Schumpeterian competition and industry dynamics, patterns of technological change, firm failures, science and technology, and market demand and diffusion. The second half takes a more micro view: modularity, standards and networks, knowledge and capabilities, learning and problem-solving, and the development of new products and processes."),
 ("기술전략세미나", "Technology Strategy Seminar", "3",
  "경영대학과 기술경영협동과정에 재학 중인 석사·박사 과정 학생을 대상으로, 기술전략과 관련된 연구 논문과 관련 서적을 바탕으로 이 분야의 기초 개념들을 정립하고 현재의 연구 분야를 소개합니다. 기술전략의 기초개념인 Modularity, Standards and Networks, Knowledge and Capabilities, Learning and Problem-Solving, Development of New Products and Processes 등을 다룹니다.",
  "For master's and doctoral students in the School of Business and in the interdisciplinary technology management program, this seminar establishes the foundational concepts of technology strategy from research articles and books and surveys current research areas, covering modularity, standards and networks, knowledge and capabilities, learning and problem-solving, and the development of new products and processes."),
 ("생산 및 운영관리세미나", "Production &amp; Operations Management Seminar", "3",
  "본 과목은 생산 및 운영관리의 다양한 주제를 이해하고, 이를 바탕으로 연구 제안서(research proposal)를 완성하는 데 목적이 있습니다. 주요 주제는 재고 관리, 채찍효과, 글로벌 공급사슬관리, 지속가능 공급사슬관리 등입니다.",
  "The aim is to understand a range of topics in production and operations management and, on that basis, to complete a research proposal. Main topics include inventory management, the bullwhip effect, global supply chain management, and sustainable supply chain management."),
 ("서비스 경영 &ndash; 생산과 운영관리", "Service Management &ndash; Production &amp; Operations", "3",
  "서비스 부문은 경제에서 가장 빠르게 성장하는 영역으로 국가 경제 성장에 큰 기회를 제공하며, 동시에 지속가능한 경쟁력의 원천이기도 합니다. 그럼에도 서비스 고유의 경영 문제에 대한 연구는 최근까지 충분하지 않았습니다. 이 수업에서 학생들은 서비스 경영이 학문적으로 어떻게 발전해 왔고 현재의 연구 주제가 무엇인지 배우며, 나아가 서비스 경영의 한 영역을 선택해 그 분야의 연구 제안서를 발전시킬 기회를 갖습니다.",
  "As the fastest-growing sector of the economy, services offer tremendous opportunities for national economic growth, and the service dimensions of business offer equally large opportunities for sustainable competitiveness. Yet until recently there has been little research on the management issues unique to services. In this course students learn how the field of service management has developed academically and what its current research topics are, and have the opportunity to choose an area of service management and develop a research proposal in it."),
]

# 학위 이수 요건 (ODI-OM 석·박사 내규 기준): 구분ko, 구분en, 내용ko, 내용en, 이수ko, 이수en
REQ_MS = [
 ("방법론 1", "Methods 1", "연구조사방법론", "Research Methodology", "필수", "Required"),
 ("방법론 2", "Methods 2", "수리통계학 또는 행동과학통계방법론, 혹은 지도교수가 승인한 그에 준하는 과목",
  "Mathematical Statistics or Behavioral Science Statistics, or an equivalent course approved by the advisor", "필수", "Required"),
 ("방법론 3", "Methods 3", "경영자료처리, 실험설계방법, 시뮬레이션, 질적연구방법, 혹은 지도교수 지정 과목",
  "Business Data Processing, Experimental Design, Simulation, Qualitative Research Methods, or a course designated by the advisor", "택 1", "Choose 1"),
 ("전공", "Major", "생산관리, 구매관리, 서비스운영관리, Supply Chain Management, 기술경영세미나 등 전공 과목",
  "Production Management, Purchasing Management, Service Operations Management, Supply Chain Management, Technology Management Seminar, and other major courses", "택 4", "Choose 4"),
 ("세미나", "Seminar", "OM 프로세미나 (1.5학점) + OM 워크샵 (1.5학점)", "OM Proseminar (1.5 cr.) + OM Workshop (1.5 cr.)",
  "1학기 청강 · 2~3학기 수강 · 4학기 청강 원칙", "Audit in term 1, take for credit in terms 2 and 3, audit in term 4"),
 ("학부보충", "Undergraduate make-up", "마케팅 · 매니지먼트 · 회계학 중 택 2, 그리고 비지정 2과목",
  "Two courses from marketing, management, or accounting, plus two unspecified courses",
  "12학점 · 졸업학점에서 제외", "12 credits, excluded from the degree total"),
 ("연구윤리", "Research ethics", "온라인 연구윤리 교육", "Online research ethics course", "Pass / Non-pass", "Pass / Non-pass"),
]
REQ_PHD = [
 ("방법론 1", "Methods 1", "연구조사방법론", "Research Methodology", "필수", "Required"),
 ("방법론 2", "Methods 2", "수리통계학 또는 행동과학통계방법론, 혹은 그에 준하는 과목",
  "Mathematical Statistics or Behavioral Science Statistics, or an equivalent course", "필수", "Required"),
 ("방법론 3 · 4", "Methods 3 &amp; 4", "경영자료처리, 실험설계방법, 시뮬레이션, 질적연구방법, 혹은 지도교수 지정 과목",
  "Business Data Processing, Experimental Design, Simulation, Qualitative Research Methods, or a course designated by the advisor", "택 2", "Choose 2"),
 ("전공", "Major", "생산관리, 구매관리, 서비스운영관리, Supply Chain Management, 기술경영세미나 등 전공 과목",
  "Production Management, Purchasing Management, Service Operations Management, Supply Chain Management, Technology Management Seminar, and other major courses", "택 3~5", "Choose 3 to 5"),
 ("전공 관련", "Related field", "MIS · 매니지먼트 · 마케팅 과목 중 지도교수가 지정한 전공 관련 과목",
  "Courses in MIS, management, or marketing designated by the advisor", "택 0~2", "Choose 0 to 2"),
 ("세미나", "Seminar", "OM 프로세미나 (1.5학점) + OM 워크샵 (1.5학점)", "OM Proseminar (1.5 cr.) + OM Workshop (1.5 cr.)",
  "수강하지 않는 학기에도 지속 청강 (예심·본심 학기 제외)", "Audited continuously even in terms not taken for credit, except the proposal and defense terms"),
 ("연구윤리", "Research ethics", "온라인 연구윤리 교육", "Online research ethics course", "Pass / Non-pass", "Pass / Non-pass"),
]

def build_courses():
    # --- 교과목 목록
    clist = ""
    for i, (ko, en, cr, dko, den) in enumerate(COURSES):
        clist += ('<li class="rv" data-delay="%d"><div><div class="cname">%s</div>'
                  '<span class="badge ccr">%s%s</span></div>%s</li>'
                  % ((i % 4) * 60, t(ko, en, "span"), cr, t("학점", " credits", "span"),
                     t(dko, den, "p", "cdesc")))

    def reqtable(rows):
        trs = "".join('<tr><td class="nm">%s</td><td>%s</td><td class="yr">%s</td></tr>'
                      % (t(a, b), t(c, d), t(e, f)) for a, b, c, d, e, f in rows)
        return ('<div class="tablewrap"><div class="tablescroll"><table>'
                '<thead><tr><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody>'
                '</table></div></div>' % (t("구분", "Category"), t("과목", "Course"),
                                          t("이수", "Requirement"), trs))

    exam_ms = [
        ("시험 시간 120분", "120 minutes"),
        ("응시 자격은 24학점 이수 (방법론·통계 9학점 포함, 학부보충 제외)",
         "Eligible after 24 credits, including nine credits of methods and statistics and excluding make-up courses"),
        ("합격 기준 80점", "Pass mark of 80"),
        ("응시 2회 제한, 교수회의가 불가피한 사정을 인정하면 1회 추가",
         "Two attempts, with one more if the faculty meeting recognises unavoidable circumstances"),
    ]
    grad_ms = [
        ("국내외 학회에서 연구 논문 발표, 또는 국내 등재후보지 이상 학회지 논문 게재 확정(acceptance)",
         "A conference presentation at home or abroad, or acceptance in a journal listed as a KCI candidate or above"),
        ("해외 유학을 준비하는 학생은 지도교수 승인 하에 SCOPUS급 이상 해외 학회지 투고를 장려",
         "Students preparing to study abroad are encouraged, with the advisor's approval, to submit to a SCOPUS-indexed international journal"),
    ]
    exam_phd = [
        ("전공 120분, 부전공 60분", "120 minutes for the major, 60 for the minor"),
        ("합격 기준 80점", "Pass mark of 80"),
        ("응시 3회 제한, 교수회의가 불가피한 사정을 인정하면 1회 추가",
         "Three attempts, with one more if the faculty meeting recognises unavoidable circumstances"),
    ]
    grad_phd = [
        ("1년차 연구논문과 2년차 연구논문을 제출·발표해 OM 교수회의에서 pass 등급을 받아야 예심 신청 가능",
         "A first-year and a second-year research paper must be submitted, presented, and passed by the OM faculty meeting before the proposal defense"),
        ("1년차 논문은 2개 학기, 2년차 논문은 4개 학기 수료 후 제출 (1학기 입학 4월 말, 2학기 입학 9월 말)",
         "The first-year paper is due after two terms and the second-year paper after four, by end of April for spring entrants and end of September for fall entrants"),
        ("주저자 또는 공저자로 SCOPUS급 이상 해외 학회지 논문 게재 확정(acceptance)",
         "Acceptance of a paper in a SCOPUS-indexed international journal as lead or co-author"),
    ]
    def li(items):
        return "".join('<li>%s%s</li>' % (I["check"], t(ko, en)) for ko, en in items)

    body = phead("Curriculum", "교과목 소개", "Curriculum",
                 t("석사 30학점 · 박사 36학점",
                   "30 credits (M.S.) &middot; 36 credits (Ph.D.)"),
                 "오퍼레이션 전공의 개설 교과목과 석·박사 이수 요건, 그리고 Business Analytics 융합전공을 소개합니다.",
                 "What we offer, what each degree requires, and the joint track with Business Analytics.")

    body += ('<section class="sec sec--soft"><div class="wrap">'
             '<div class="sechead">%s%s</div>'
             '<ul class="clist">%s</ul></div></section>'
             % (t("전공 교과목", "Course list", "h2"),
                t("오퍼레이션 전공에서 개설하는 교과목입니다. 수업은 한국어로 진행하며, 읽기 자료는 주로 국제 학술지의 영문 논문입니다.",
                  "The courses offered by the Operations Management area. Classes are taught in Korean, and most readings are English-language articles from international journals.",
                  "p", "dek"),
                clist))

    body += ('<section class="sec"><div class="wrap">'
             '<div class="sechead">%s%s</div>'
             '<div class="grid" style="gap:48px">'
             '<div class="rv"><h3 class="reqh">%s<span class="badge">%s</span></h3>%s%s</div>'
             '<div class="rv" data-delay="100"><h3 class="reqh">%s<span class="badge badge--gold">%s</span></h3>%s%s</div>'
             '</div><div class="note rv" style="margin-top:28px">%s</div></div></section>'
             % (t("석·박사 이수 요건", "What each degree requires", "h2"),
                t("아래는 ODI-OM 석·박사 내규에 따른 이수 요건입니다.",
                  "The requirements below follow the ODI-OM degree regulations.", "p", "dek"),
                t("석사과정", "M.S. program", "span"), t("30학점", "30 credits", "span"), reqtable(REQ_MS),
                t("방법론 9학점과 전공 필수 9~12학점을 포함해 졸업학점 30학점을 이수합니다. 학부보충 12학점은 졸업학점에서 제외됩니다.",
                  "Thirty credits in total, including nine credits of methods and nine to twelve credits of required major courses. The twelve credits of undergraduate make-up work are excluded from that total.",
                  "p", "reqnote"),
                t("박사과정", "Ph.D. program", "span"), t("36학점", "36 credits", "span"), reqtable(REQ_PHD),
                t("석사학위 과정에서 취득한 학점은 박사과정 졸업학점으로 인정되지 않습니다. 지도교수 또는 전공 주임교수가 학사지도 후 필요하다고 판단하면 36학점을 초과해 이수합니다. OM 석사과정에서 전공과목을 모두 이수한 경우에는 전공과 전공 관련 과목을 합해 5과목을 이수합니다.",
                  "Credits earned in a master's program do not count toward the doctoral total. If the advisor or the area chair judges it necessary after academic counselling, students take more than 36 credits. Students who completed all major courses in our own M.S. program take five courses in total across the major and related fields.",
                  "p", "reqnote"),
                t("<b>안내</b> &middot; 위 요건은 ODI-OM 석·박사 내규를 정리한 것입니다. 최종 기준은 경영대학이 공지하는 전공별 석·박사 내규 원문입니다.",
                  "<b>Note</b> &middot; This is a summary of the ODI-OM degree regulations. The official text published by the School of Business governs.")))

    body += ('<section class="sec sec--soft"><div class="wrap">'
             '<div class="sechead">%s%s</div>'
             '<div class="grid g2" style="gap:18px;align-items:start">'
             '<article class="card rv"><div class="card__ico">%s</div>%s<ul class="flist" style="margin-top:16px">%s</ul>'
             '<div style="margin-top:24px;padding-top:20px;border-top:1px solid var(--line-soft)">%s<ul class="flist" style="margin-top:14px">%s</ul></div></article>'
             '<article class="card rv" data-delay="100"><div class="card__ico">%s</div>%s<ul class="flist" style="margin-top:16px">%s</ul>'
             '<div style="margin-top:24px;padding-top:20px;border-top:1px solid var(--line-soft)">%s<ul class="flist" style="margin-top:14px">%s</ul></div></article>'
             '</div></div></section>'
             % (t("종합시험과 졸업 요건", "Comprehensive exam and thesis requirements", "h2"),
                t("두 과정 모두 종합시험을 거치며, 졸업 전 연구 성과를 요구합니다.",
                  "Both degrees require a comprehensive examination and a research output before graduation.", "p", "dek"),
                I["book"], t("석사과정 종합시험", "M.S. comprehensive exam", "h3"), li(exam_ms),
                t("석사 졸업 요건", "M.S. thesis requirement", "h4"), li(grad_ms),
                I["cap"], t("박사과정 종합시험", "Ph.D. comprehensive exam", "h3"), li(exam_phd),
                t("박사 졸업 요건", "Ph.D. thesis requirement", "h4"), li(grad_phd)))

    body += ('<section class="sec"><div class="wrap"><div class="split">'
             '<div class="rv">%s%s%s'
             '<div style="margin-top:26px;display:flex;gap:10px;flex-wrap:wrap">'
             '<a class="btn btn--outline" href="https://ysb.yonsei.ac.kr/ysb/ms-phd/curriculum.do" target="_blank" rel="noopener">%s%s</a>'
             '<a class="btn btn--outline" href="https://sites.google.com/site/isatyonsei/%%EC%%86%%8C%%EA%%B0%%9C%%EC%%9D%%98-%%EA%%B8%%80/%%EA%%B3%%BC%%EB%%AA%%A9-%%EC%%86%%8C%%EA%%B0%%9C" target="_blank" rel="noopener">%s%s</a>'
             '</div></div>'
             '<div class="rv" data-delay="120"><div class="card" style="padding:32px">%s'
             '<ul class="flist" style="margin-top:18px">%s</ul></div></div></div></div></section>'
             % (t("OM &middot; Business Analytics <span class=\"thin\">융합전공</span>",
                  "The OM x Business Analytics <span class=\"thin\">joint track</span>", "h2"),
                t("본 전공은 학생들이 Business Analytics(BA) 역량을 갖추도록 2020년도 1학기부터 BA 융합 과정을 운영하고 있습니다.",
                  "To give students the analytics skills that both research and practice now demand, we have run a joint track with Business Analytics since spring 2020.",
                  "p", "body-copy"),
                t("OM 전공의 졸업 요건을 충족하고 BA 전공 필수 과목 6개를 포함하여 총 36학점(방법론 9학점 포함)을 이수한 학생은 'OM / BA 융합전공' 학위를 받습니다.",
                  "Students who satisfy the OM degree requirements and complete 36 credits, including the six required BA courses and nine credits of methods, graduate with the joint OM / BA degree.",
                  "p", "body-copy"),
                t("경영대학 학사 안내", "School of Business academic info"), I["ext"],
                t("BA 과목 소개 (IS 전공)", "BA course descriptions"), I["ext"],
                t("BA 전공 필수 6과목", "The six required BA courses", "h3"),
                "".join('<li>%s<span>%s</span></li>' % (I["check"], c)
                        for c in ["Business Analytics 1", "Business Analytics 2", "Data Management for BA",
                                  "Web &amp; Text Analytics", "AI for Business", "BA Capstone"])))

    page("courses.html",
         "교과목 소개 | 연세대 경영대학 오퍼레이션 전공",
         "Curriculum | Operations Management, Yonsei School of Business",
         "오퍼레이션 전공 교과목, 석·박사 이수 요건, 종합시험과 졸업 요건, OM / Business Analytics 융합전공 안내.", body)

# ============================================================== students
def reviewed_note():
    """명단이 언제 확인된 것인지 밝히고, 정정 요청 창구를 연다.
    표가 낡더라도 사이트가 사실과 다른 말을 하지 않게 하는 장치."""
    return '''<p class="note rv" style="margin-top:34px">%s <a href="mailto:%s">%s</a></p>''' % (
        t("위 명단은 <b>%s</b>에 확인한 내용입니다. 사실과 다른 부분이 있으면 알려주시면 바로 고치겠습니다." % LAST_REVIEWED_KO,
          "This list reflects information confirmed in <b>%s</b>. If anything is out of date, please let us know and we will correct it." % LAST_REVIEWED_EN),
        CONTACT_MAIL, t("정보 수정 요청", "Request a correction"))


def build_students():
    cards = ""
    for i, st in enumerate(STUDENTS):
        nm, deg, iko, ien, tko, ten = st[:6]
        eko, een = (st[6], st[7]) if len(st) > 7 else ("", "")
        badge = t("박사과정", "Ph.D. student", "span", "badge badge--gold") if deg == "phd" else t("석사과정", "M.S. student", "span", "badge")
        interest = t(iko, ien, "div", "scard__i") if iko else t("연구 관심 분야 준비 중", "Research interests to be announced", "div", "scard__i")
        # 출신 학교. 아직 모으는 중이라 대부분 비어 있다. 칸이 있다는 것이
        # 보여야 채워 넣을 수 있으므로, 비었을 때도 자리를 남겨 둔다.
        # STUDENTS 의 마지막 두 칸을 채우면 그 값이 그대로 들어간다.
        edu = '<div class="scard__e">%s %s</div>' % (
            I["cap"],
            t(eko, een) if eko else t("출신 학교 미기재", "Prior degree not listed",
                                      "span", "scard__blank"))
        thesis = ('<div class="scard__t">%s %s</div>' % (t("<b>석사 논문</b>", "<b>M.S. thesis</b>"), t(tko, ten))) if tko else ""
        work = ""
        entries = STUDENT_WORK.get(nm, [])
        if entries:
            order = {"pub": 0, "conf": 1}
            label = {"pub": ("논문", "Paper"), "conf": ("발표", "Talk")}
            work = '<ul class="scard__work">%s</ul>' % "".join(
                '<li><span class="scard__k">%s</span><span>%s</span></li>'
                % (t(*label[k]), t(ko_, en_))
                for k, ko_, en_ in sorted(entries, key=lambda e: order.get(e[0], 9)))
        cards += '''<article class="scard rv" data-item data-tags="%s" data-delay="%d">
 <div class="scard__hd"><span class="scard__n">%s</span>%s</div>
 %s
 %s
 %s
 %s
</article>''' % (deg, (i % 3) * 60, pname(nm), badge, interest, edu, thesis, work)

    body = phead("Students", "재학생 현황", "Current students",
                 t("박사과정 %d명 · 석사과정 %d명" % (sum(1 for x in STUDENTS if x[1] == "phd"),
                                              sum(1 for x in STUDENTS if x[1] == "ms")),
                   "%d doctoral and %d master's students" % (sum(1 for x in STUDENTS if x[1] == "phd"),
                                                             sum(1 for x in STUDENTS if x[1] == "ms"))),
                 "본 전공 석·박사 과정에 재학 중인 학생의 연구 관심 분야입니다.",
                 "The research interests of the students currently enrolled in our master's and doctoral programs.")
    body += '''
<section class="sec">
 <div class="wrap">
  <div class="grid g2">%s</div>
  %s
 </div>
</section>
''' % (cards, reviewed_note())
    page("students.html",
         "재학생 현황 | 연세대 경영대학 오퍼레이션 전공",
         "Current students | Operations Management, Yonsei School of Business",
         "오퍼레이션 전공 석·박사 과정 재학생의 연구 관심 분야 소개.", body)

# ============================================================== alumni
def placement_summary():
    """박사 졸업생 중 대학에 자리 잡은 인원을 데이터에서 직접 센다.
    손으로 적은 숫자는 반드시 뒤처지므로 세지 말고 계산한다."""
    academic = [a for a in ALUMNI_PHD + ALUMNI_MS if "교수" in a[5] or "Professor" in a[6]]
    stats = [
        (len(ALUMNI_MS) + len(ALUMNI_PHD), "석·박사 배출", "M.S. and Ph.D. graduates"),
        (len(ALUMNI_PHD), "박사 학위", "Ph.D. degrees"),
        (len(ALUMNI_MS), "석사 학위", "M.S. degrees"),
        (len(academic), "대학 교수 임용", "faculty appointments"),
    ]
    cells = "".join(
        '<div class="pstat"><div class="pstat__n" data-count="%d">%d</div>%s</div>' % (n, n, t(ko, en, "div", "pstat__l"))
        for n, ko, en in stats)
    return '''<div class="pgrid rv">%s</div>''' % cells


def build_alumni():
    # 박사과정은 논문 주제를 아직 모으지 못했다. 30행이 전부 줄표가 되면
    # 칸이 비었다는 사실만 크게 보이므로, 그럴 때는 열 자체를 내린다.
    # 주제를 채워 넣으면 show_topic=True 로 되돌리면 된다.
    def rows(data, tag, show_topic=True):
        out = ""
        for nm, yr, adv, tko, ten, pko, pen in data:
            place = t(pko, pen) if pko else '<span style="color:var(--muted)">&mdash;</span>'
            topic = ""
            if show_topic:
                topic = '<td>%s</td>' % (t(tko, ten) if tko
                                         else '<span style="color:var(--muted)">&mdash;</span>')
            out += ('<tr data-item data-tags="%s"><td class="nm">%s</td><td class="yr">%d</td>'
                    '<td class="yr">%s</td>%s<td>%s</td></tr>'
                    % (tag, pname(nm, pen), yr, t(adv, ADV.get(adv, adv)), topic, place))
        return out

    def block(title_ko, title_en, data, tag, show_topic=True):
        cols = [t("이름", "Name"), t("졸업 연도", "Year"), t("지도교수", "Advisor")]
        if show_topic:
            cols.append(t("논문 주제", "Thesis topic"))
        cols.append(t("근무지", "Placement"))
        head = '<thead><tr>%s</tr></thead>' % "".join("<th>%s</th>" % c for c in cols)
        return '''<div class="ygroup rv" data-group>
 <h3>%s<span class="cnt">%d</span></h3>
 <div class="tablewrap"><div class="tablescroll"><table>%s<tbody>%s</tbody></table></div></div>
</div>''' % (t(title_ko, title_en, "span"), len(data), head, rows(data, tag, show_topic))

    body = phead("Alumni", "졸업생 현황", "Alumni",
                 t("1984년 첫 박사 배출 이후 %d명" % (len(ALUMNI_MS) + len(ALUMNI_PHD)),
                   "%d graduates since the first Ph.D. in 1984" % (len(ALUMNI_MS) + len(ALUMNI_PHD))),
                 "본 전공에서 석사 %d명과 박사 %d명이 학위를 받았습니다. 이 가운데 %d명은 대학에 교수로 재직하고 있으며, 나머지는 기업과 컨설팅, 연구기관, 군 등에 진출하였습니다."
                 % (len(ALUMNI_MS), len(ALUMNI_PHD),
                    sum(1 for a in ALUMNI_MS + ALUMNI_PHD if "교수" in a[5] or "Professor" in a[6])),
                 "%d master's and %d doctoral students have come through. %d now teach at universities; the rest are in industry, consulting, research institutes, and the armed forces."
                 % (len(ALUMNI_MS), len(ALUMNI_PHD),
                    sum(1 for a in ALUMNI_MS + ALUMNI_PHD if "교수" in a[5] or "Professor" in a[6])))
    body += '''
<section class="sec" data-scope="alumni">
 <div class="wrap">
  <div class="toolbar rv">
   <label class="search">%s<input type="search" data-search data-ph-ko="이름 · 주제 · 근무지 검색" data-ph-en="Search name, topic, or employer" placeholder="이름 · 주제 · 근무지 검색" aria-label="Search"></label>
   <div class="segs">
    <button class="seg" type="button" data-filter="all" aria-pressed="true">%s</button>
    <button class="seg" type="button" data-filter="ms" aria-pressed="false">%s</button>
    <button class="seg" type="button" data-filter="phd" aria-pressed="false">%s</button>
   </div>
  </div>
  %s
  %s
  %s
  <div class="empty" data-empty style="display:none">%s</div>
  %s
 </div>
</section>

<section class="sec sec--soft" id="letter">
 <div class="wrap">
  <div class="sechead">
   %s
   %s
  </div>
  %s
 </div>
</section>
''' % (I["search"], t("전체", "All"), t("석사과정", "M.S."), t("박사과정", "Ph.D."),
       placement_summary(),
       block("석사과정", "M.S. program", ALUMNI_MS, "ms"),
       block("박사과정", "Ph.D. program", ALUMNI_PHD, "phd", show_topic=False),
       t("검색 결과가 없습니다.", "No matching records."),
       reviewed_note(),
       t("졸업생 추천 글", "In an alumnus's words" if len(TESTIMONIALS) == 1 else "In our alumni's words", "h2"),
       (t("최근 졸업생이 후배들에게 남긴 글입니다.", "A recent graduate writing to those who come next.", "p", "dek")
        if len(TESTIMONIALS) == 1 else
        t("졸업생들이 후배들에게 남긴 글입니다.", "Graduates writing to those who come next.", "p", "dek")),
       testimonial_letters())
    page("alumni.html",
         "졸업생 현황 | 연세대 경영대학 오퍼레이션 전공",
         "Alumni | Operations Management, Yonsei School of Business",
         "오퍼레이션 전공 석·박사 졸업생의 논문 주제와 진로 현황, 그리고 졸업생 추천 글.", body)

# ============================================================== news
def build_news():
    items = sorted(NEWS, key=lambda x: x[0], reverse=True)
    years = []
    for it in items:
        y = int(it[0][:4])
        if not years or years[-1][0] != y:
            years.append((y, []))
        years[-1][1].append(it)

    group_tpl = ('<div class="ygroup rv">\n'
                 ' <h3>%s<span class="cnt">%d %s</span></h3>\n'
                 ' <ul class="news">%s</ul>\n'
                 '</div>')
    groups = "".join(group_tpl % (t("%d년" % y, "%d" % y, "span"), len(rows),
                                  t("건", "items", "span"),
                                  "".join(news_row(r) for r in rows))
                     for y, rows in years)

    body = phead("News", "소식", "News",
                 t("교수 · 학생 · 졸업생 소식 %d건" % len(NEWS),
                   "%d items from faculty, students, and alumni" % len(NEWS)),
                 "오퍼레이션 전공 구성원의 수상과 임용, 연구 성과, 학위 수여, 전공 행사 소식입니다.",
                 "Honors and appointments, research, degrees, and program news from across the area.")
    body += ('\n<section class="sec">\n <div class="wrap">\n  %s\n </div>\n</section>\n' % groups)
    page("news.html",
         "소식 | 연세대 경영대학 오퍼레이션 전공",
         "News | Operations Management, Yonsei School of Business",
         "연세대 경영대학 오퍼레이션 전공 교수, 학생, 졸업생 소식.", body)


# ============================================================== seminars
def build_seminars():
    segs = '<button class="seg" type="button" data-filter="all" aria-pressed="true">%s</button>' % t("전체", "All")
    segs += "".join('<button class="seg" type="button" data-filter="y%d" aria-pressed="false">%d</button>' % (y, y)
                    for y, _ in SEMINARS)
    groups = ""
    for y, items in SEMINARS:
        lis = "".join(
            '<li data-item data-tags="y%d"><span class="d">%s</span><span class="who">%s</span>%s</li>'
            % (y, d, speaker(nm, rko, ren, aen), t(ako, aen, "span", "aff"))
            for d, nm, rko, ren, ako, aen in items)
        groups += '''<div class="ygroup rv" data-group>
 <h3>%s<span class="cnt">%d %s</span></h3>
 <ul class="tl">%s</ul>
</div>''' % (t("%d년 세미나 시리즈" % y, "%d Seminar Series" % y, "span"), len(items),
             t("회", "talks", "span"), lis)

    body = phead("Seminars", "연구 세미나 시리즈", "Research seminar series",
                 t("2019년 이후 %d회" % SEMINAR_TOTAL, "%d talks since 2019" % SEMINAR_TOTAL),
                 "본 전공은 국내외 주요 대학의 연구자를 초빙하여 연구 세미나 시리즈를 운영하고 있습니다. 석·박사 과정 학생은 세미나를 통해 최신 연구 동향을 파악하고 연구 주제를 선정·발전시킵니다.",
                 "We invite scholars from leading universities in Korea and abroad to present their work. For our graduate students, the series is where current research becomes visible and dissertation topics take shape.")
    body += '''
<section class="sec" data-scope="seminars">
 <div class="wrap">
  <div class="toolbar rv">
   <label class="search">%s<input type="search" data-search data-ph-ko="발표자 · 소속 검색" data-ph-en="Search speaker or affiliation" placeholder="발표자 · 소속 검색" aria-label="Search"></label>
   <div class="segs">%s</div>
  </div>
  %s
  <div class="note rv" style="margin-top:8px">%s</div>
  <div class="empty" data-empty style="display:none">%s</div>
 </div>
</section>
''' % (I["search"], segs, groups,
       t("<b>2020년</b> &middot; COVID-19으로 인해 세미나 시리즈가 취소되었습니다.",
         "<b>2020</b> &middot; the seminar series was cancelled because of COVID-19."),
       t("검색 결과가 없습니다.", "No matching seminars."))
    page("seminars.html",
         "연구 세미나 시리즈 | 연세대 경영대학 오퍼레이션 전공",
         "Research Seminar Series | Operations Management, Yonsei School of Business",
         "연세대 경영대학 오퍼레이션 전공이 초빙한 국내외 연구자의 세미나 목록.", body)

def guard():
    """AI가 쓴 티가 나는 표현이 다시 섞여 들어왔는지 확인한다.
    나중에 문구를 손볼 때 원래대로 돌아가는 것을 막기 위한 장치."""
    import glob as _glob
    import unicodedata as _ud
    patterns = {
        "이모지": None,
        "em dash(—)": "—",
        "세계 최고": "세계 최고",
        "최선을 다": "최선을 다",
        "다양한 분야에서": "다양한 분야에서",
        "delve": "delve",
        "seamless": "seamless",
        "elevate": "elevate",
        "robust": "robust",
    }
    found = {}
    for f in sorted(_glob.glob(os.path.join(OUT, "*.html"))):
        h = open(f, encoding="utf-8").read()
        for label, pat in patterns.items():
            n = (len([c for c in h if _ud.category(c) == "So" and ord(c) > 0x2100])
                 if pat is None else h.lower().count(pat.lower()))
            if n:
                found.setdefault(os.path.basename(f), []).append("%s %d" % (label, n))
    if found:
        print("  [확인 필요] AI 티 표현이 발견되었습니다")
        for f, hits in found.items():
            print("    %-16s %s" % (f, ", ".join(hits)))
    else:
        print("  표현 점검 통과")


# 제목 자리에 종결형 문장이 다시 들어오지 않았는지 확인한다.
# 국내 대학 사이트에서 h1·h2·h3는 거의 예외 없이 명사구이고, 종결형 문장은
# 카드나 맨 아래 CTA 한 곳에만 쓴다. 아래 한 줄은 그 한 곳으로 의도한 것이다.
HEADING_SENTENCE_OK = ["열정을 갖춘 석·박사 과정 학생을 모집합니다"]


def guard_headings():
    import glob as _glob
    import re as _re
    pat = _re.compile(r"<(h[1-4])\b[^>]*>(.*?)</\1>", _re.S)
    tag = _re.compile(r"<[^>]+>")
    end = _re.compile(r"(니다|나요\?|하세요|한다는 것|해요|있으신가)")
    found = []
    for f in sorted(_glob.glob(os.path.join(OUT, "*.html"))):
        h = open(f, encoding="utf-8").read()
        for m in pat.finditer(h):
            if 'class="en' in m.group(0):
                continue
            txt = tag.sub("", m.group(2)).strip()
            if txt and end.search(txt) and txt not in HEADING_SENTENCE_OK:
                found.append((os.path.basename(f), m.group(1), txt[:60]))
    if found:
        print("  [확인 필요] 제목이 종결형 문장입니다 (명사구로 바꾸세요)")
        for f, t_, txt in found:
            print("    %-16s %s  %s" % (f, t_, txt))
    else:
        print("  제목 점검 통과")


# ============================================================== main
if __name__ == "__main__":
    print("building…")
    build_index()
    build_faculty()
    build_admissions()
    build_courses()
    build_students()
    build_alumni()
    build_seminars()
    build_news()
    print("done. %d seminars, %d alumni." % (SEMINAR_TOTAL, len(ALUMNI_MS) + len(ALUMNI_PHD)))
    guard()
    guard_headings()
    samples = sum(1 for es in STUDENT_WORK.values() for e in es if "[견본]" in e[1])
    if samples:
        print("  [지울 것] 견본 연구 실적 %d건이 재학생 카드에 나옵니다 (STUDENT_WORK). 게시 전에 지우세요." % samples)
    if NAMES_EN_UNVERIFIED:
        print("  [확인할 것] 영문 이름 철자 %d명 (NAMES_EN_UNVERIFIED)" % len(NAMES_EN_UNVERIFIED))
    blank = [x[0] for x in STUDENTS if not x[6]]
    if blank:
        print("  [채울 것] 출신 학교 %d명: %s" % (len(blank), ", ".join(blank)))
