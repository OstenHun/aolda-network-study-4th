"""Apply the hosted workspace to generated copies, keeping lesson sources intact."""
from html import escape, unescape
from pathlib import PurePosixPath
import json
import posixpath
import re


GROUPS = {
    'ssh-top-down': 'VM·SSH 준비', 'week-01': '1주차 · 요청과 응답',
    'week-02': '2주차 · IPv4와 서브넷', 'week-03': '3주차 · LAN과 다음 홉',
    'week-04': '4주차 · TCP (본문 일부)', 'week-06': '6주차 · HTTP (본문 일부)',
}
NAV = {
    'ssh-top-down': [('index', '학습 안내'), ('lesson', 'VM·SSH 접속 교재'), ('questions', '내 접속 기록'), ('sources', '공식 참고자료')],
    'week-01': [('index', '학습 안내'), ('concepts', '개념 교재'), ('linux', 'Linux 실습'), ('worksheet', '팀 활동'), ('review', '복습 문제'), ('answers', '해설')],
    'week-02': [('index', '학습 안내'), ('worksheet', '함께 찾을 질문'), ('articles', '함께 찾아보기'), ('essentials', '핵심 개념'), ('concepts', '개념 교재'), ('linux', '기존 VM 실습'), ('review', '복습 문제'), ('answers', '분리 해설')],
    'week-03': [('index', '학습 안내'), ('recall', '복습 진단'), ('lan-mac', 'LAN·MAC'), ('next-hop', '다음 홉'), ('arp', 'ARP·캐시'), ('icmp', 'ICMP·ping'), ('linux', 'Linux 실험'), ('worksheet', '함께 설명'), ('review', '복습 문제'), ('answers', '해설')],
}


def page_title(html):
    title = re.search(r'<h1\b[^>]*>([\s\S]*?)</h1>', html)
    if not title:
        title = re.search(r'<title>([\s\S]*?)</title>', html)
    return unescape(re.sub(r'<[^>]+>', '', title[1])).strip()


def apply_theme(payload, root):
    payload['assets/study-site.css'] = (root / 'tools/study-site.css').read_bytes()
    payload['assets/study-site.js'] = (root / 'tools/study-site.js').read_bytes()
    searchable = []
    for name, data in payload.items():
        if not name.endswith('.html') or name == 'index.html':
            continue
        # Compatibility redirects are reachable but don't duplicate search results.
        if 'http-equiv="refresh"' in data.decode():
            continue
        group = next((label for key, label in GROUPS.items() if f'/{key}/' in name), '실습 준비')
        headings = re.findall(r'<h[23]\b[^>]*>([\s\S]*?)</h[23]>', data.decode())
        keywords = unescape(re.sub(r'<[^>]+>', '', ' '.join(headings)))
        searchable.append({'title': page_title(data.decode()), 'group': group, 'path': name, 'keywords': keywords})
    searchable.sort(key=lambda item: (item['group'], item['path']))

    for name, data in list(payload.items()):
        if not name.endswith('.html'):
            continue
        html = data.decode()
        if 'http-equiv="refresh"' in html:
            continue
        current_group = next((key for key in GROUPS if f'/{key}/' in name), None)

        def href(target):
            return posixpath.relpath(target, str(PurePosixPath(name).parent))

        def link(target, label, extra=''):
            current = ' aria-current="page"' if target == name else ''
            return f'<a href="{escape(href(target), quote=True)}"{current}{extra}>{label}</a>'

        sidebar = link('index.html', '학습 홈')
        sidebar += '<span class="sidebar-group-title">시작하기 전에</span>'
        sidebar += link('materials/ssh-top-down/index.html', 'VM·SSH 접속 준비')
        if current_group == 'ssh-top-down':
            sidebar += '<div class="sidebar-children">' + ''.join(link(f'materials/ssh-top-down/{stem}.html', label) for stem, label in NAV['ssh-top-down'][1:]) + '</div>'
        sidebar += '<span class="sidebar-group-title">공통 과정</span>'
        for number, key, title in [('01', 'week-01', '요청과 응답'), ('02', 'week-02', 'IPv4와 서브넷'), ('03', 'week-03', 'LAN과 다음 홉')]:
            sidebar += '<div class="sidebar-week">' + link(f'materials/{key}/index.html', f'<span>{number}</span> {title}')
            if current_group == key:
                sidebar += '<div class="sidebar-children">' + ''.join(link(f'materials/{key}/{stem}.html', label) for stem, label in NAV[key][1:]) + '</div>'
            sidebar += '</div>'
        sidebar += '<span class="sidebar-group-title">후속 개념 · 본문 일부</span>'
        sidebar += link('materials/week-04/concepts.html', '04 · TCP와 RTT')
        sidebar += link('materials/week-06/concepts.html', '06 · HTTP 연결 재사용')
        sidebar += '<span class="sidebar-group-title">다시 찾아보기</span>'
        sidebar += link('materials/week-01/concept-index.html', '전체 개념 색인')
        sidebar += link('materials/week-01/interview-references.html', '면접·개발 참고자료')
        sidebar += '<div class="sidebar-foot">질문 → 함께 탐색 → 설명 → 확인<br>아올다 4기 네트워크 스터디</div>'
        topbar = '<a class="study-skip" href="#main">본문으로 건너뛰기</a><header class="study-topbar"><a class="study-logo" href="' + href('index.html') + '"><span class="study-logo-mark" aria-hidden="true">a/</span>아올다<small>네트워크 스터디 · 4기</small></a><div class="study-top-actions"><button class="study-search-trigger" type="button" aria-haspopup="dialog">자료 검색 <kbd aria-hidden="true">/</kbd></button><button class="study-menu" type="button" aria-expanded="false" aria-controls="study-sidebar">학습 메뉴</button></div></header><nav id="study-sidebar" class="study-sidebar" aria-label="전체 학습 경로">' + sidebar + '</nav>'
        breadcrumb = ''
        if name != 'index.html':
            breadcrumb = '<nav class="study-breadcrumb" aria-label="현재 위치">' + link('index.html', '학습 홈') + '<span aria-hidden="true">/</span>'
            if current_group:
                index = f'materials/{current_group}/index.html'
                group_label = escape(GROUPS[current_group])
                breadcrumb += (link(index, group_label) if index in payload else '<span>' + group_label + '</span>') + '<span aria-hidden="true">/</span>'
            breadcrumb += '<span>' + escape(page_title(html)) + '</span></nav>'
        index = [{'title': p['title'], 'group': p['group'], 'keywords': p['keywords'], 'href': href(p['path'])} for p in searchable]
        search_data = json.dumps(index, ensure_ascii=False).replace('<', '\\u003c')
        search = '<dialog class="study-search-dialog" aria-labelledby="study-search-title"><div class="search-heading"><label id="study-search-title" for="study-search-input">공개 학습 자료 찾기</label><button class="search-close" type="button">닫기 <span aria-hidden="true">Esc</span></button></div><div class="search-field"><input id="study-search-input" type="search" autocomplete="off" placeholder="주차나 개념 이름으로 검색"></div><div class="search-status" role="status" aria-live="polite"></div><div class="search-results"></div></dialog><script type="application/json" id="study-search-data">' + search_data + '</script><script src="' + href('assets/study-site.js') + '" defer></script>'
        # Replace only the old generated global-home strip; preserve lesson DOM/scripts.
        html = re.sub(r'<div style="padding:10px 20px;[^\"]*"><a href="[^\"]*">스터디 학습 홈</a></div>', '', html, count=1)
        if not re.search(r'\bid="main"', html):
            html = re.sub(r'<main\b', '<main id="main"', html, count=1)
        html = re.sub(r'<body([^>]*)>', lambda match: '<body class="study-site"' + match[1] + '>' + topbar + '<div class="study-workspace">' + breadcrumb, html, count=1)
        html = html.replace('</body>', '<div class="study-bottom"><span>아올다 4기 · 함께 배우는 네트워크</span>' + link('materials/week-01/concept-index.html', '개념 색인 ↗') + '</div></div>' + search + '</body>')
        html = html.replace('</head>', '<link rel="stylesheet" href="' + href('assets/study-site.css') + '"></head>', 1)
        payload[name] = html.encode()
