# -*- coding: utf-8 -*-
"""메일에 첨부할 수 있는 압축본을 만든다.

구글은 .js 파일을 첨부에서 막는다. 압축 안에 들어 있어도 똑같이 막는다.
그래서 site.js 를 각 페이지 안에 직접 넣고 파일 자체는 빼서 담는다.
보이는 것과 동작은 원본과 같다.

    python3 build.py && python3 package_mail.py
"""
import io, os, re, zipfile, unicodedata, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = ["index.html", "faculty.html", "admissions.html", "courses.html",
         "students.html", "alumni.html", "seminars.html"]
ASSETS = ["assets/css/site.css",
          "assets/img/brand/yonsei-seal.png", "assets/img/brand/ysb-logo-footer.png",
          "assets/img/brand/ysb-logo-white.png", "assets/img/brand/ysb-logo.png"]
ASSETS += ["assets/img/faculty/%s.jpg" % n for n in
           ("bae", "choi", "heo", "jung", "kimky", "kimth", "min", "park")]

README = u"""연세대학교 경영대학 오퍼레이션 전공 홈페이지 (시안)


index.html 을 두 번 누르면 브라우저에서 열립니다.
서버나 인터넷 연결은 필요 없습니다.

오른쪽 위 KR / EN 단추로 영문판을 볼 수 있고,
그 옆 단추를 누르면 어두운 화면으로 바뀝니다.


정승환  seunghwan.jung@yonsei.ac.kr
"""


def build(stamp=None):
    stamp = stamp or datetime.date.today().strftime("%Y%m%d")
    name = unicodedata.normalize("NFC", u"연세대_오퍼레이션전공_홈페이지_%s" % stamp)
    stage = os.path.join(HERE, "_mail", name)
    shutil.rmtree(os.path.join(HERE, "_mail"), ignore_errors=True)

    js = io.open(os.path.join(HERE, "assets/js/site.js"), encoding="utf-8").read()
    tag = re.compile(r'<script src="assets/js/site\.js[^"]*"></script>')

    for p in PAGES:
        html = io.open(os.path.join(HERE, p), encoding="utf-8").read()
        assert len(tag.findall(html)) == 1, p
        html = tag.sub(lambda _: "<script>\n%s\n</script>" % js, html)
        out = os.path.join(stage, p)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        io.open(out, "w", encoding="utf-8").write(html)

    for a in ASSETS:
        dst = os.path.join(stage, a)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(HERE, a), dst)

    io.open(os.path.join(stage, "README.txt"), "w", encoding="utf-8").write(README)

    zpath = os.path.join(HERE, "_mail", name + ".zip")
    n = 0
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dp, dn, fn in os.walk(stage):
            dn.sort(); fn.sort()
            for f in fn:
                if f == ".DS_Store":
                    continue
                full = os.path.join(dp, f)
                arc = unicodedata.normalize("NFC", os.path.join(name, os.path.relpath(full, stage)))
                z.write(full, arc); n += 1
    print("  %s  (%d개 파일, %.0f KB)" % (os.path.basename(zpath), n, os.path.getsize(zpath) / 1024.0))
    return zpath


if __name__ == "__main__":
    print("메일용 압축본 만드는 중…")
    build()
