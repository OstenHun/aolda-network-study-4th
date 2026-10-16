# 아올다 4기 네트워크 스터디

요약: 질문을 함께 찾고 설명과 실습으로 확인하는 네트워크 학습 사이트다. 공개 교재·실습·화면 원본을 관리하며, GitHub Actions가 검사와 빌드를 수행한 뒤 GitHub Pages에 게시한다.

## 학습 사이트

[네트워크 스터디 시작하기](https://ostenhun.github.io/aolda-network-study-4th/)

VM·SSH 준비, 1주차 요청과 응답, 2주차 IPv4·서브넷, 3주차 LAN·MAC·ARP·ICMP와 4주차 TCP·UDP 교재·실습을 제공한다. 6주차 HTTP는 본문 일부이며, 자료 제작이 참가자의 실제 학습·실습 완료를 뜻하지 않는다.

## 소스와 빌드

Python 3.12 이상과 Node.js 22.22 이상을 사용한다. CI는 Node.js 24를 사용하며 Astro 버전은 잠금 파일로 고정한다.

```sh
npm ci --ignore-scripts
npm test
npm run build
python -m http.server 8000 --directory dist
```

브라우저에서 `http://localhost:8000`을 연다. 저장소를 새로 내려받아도 내부 문서·기존 ZIP·ChatGPT Sites 계정 없이 같은 사이트를 만들 수 있다.

| 위치 | 역할 |
| --- | --- |
| `content/` | 공개 교재 Markdown, 페이지 HTML 원본, 실습 코드와 예제 캡처 |
| `config/site.json` | 과정·메뉴·홈 연결과 새 교재의 입력/출력 경로 |
| `astro/` | 새 Markdown 교재의 HTML·목차 생성 |
| `tools/templates/study-home.html` | 학습 홈 원본 |
| `tools/study_site_theme.py` | 공통 탐색·현재 위치·검색 색인 생성 |
| `tools/study-site.css`, `tools/study-site.js` | 공통 디자인과 브라우저 동작 |
| `tools/build-site.py` | 공개 소스 검사·링크/앵커 확인·정적 파일 생성 |
| `.github/workflows/pages.yml` | 변경 검사와 Pages 자동 배포 |
| `dist/` | 생성물. Git에 넣지 않고 Actions에서 생성 |

공개 화면의 정본은 이 저장소다. 기존 주차의 HTML·Markdown은 그대로 유지한다. 다음에 제작하는 교재는 Markdown 한 벌을 Astro로 변환하며 HTML을 따로 작성하지 않는다. 공통 탐색·검색은 빌드할 때 생성하므로 각 교재에 직접 넣지 않는다. Python은 기존 페이지 보존·공통 조립·공개 정보와 링크 검사를 맡는다.

[새 교재 작성 안내](docs/AUTHORING.md)에 Markdown 양식과 과정 등록 예시, 복습 답안·링크·검사 방법을 정리했다. 4주차부터 이 경로로 제작하며 새 주차의 기본으로 사용한다. 기존 1주차 교재와 학습 기능은 보존한다.

## 수정과 게시

작은 수정은 `main`에 반영하고 큰 수정은 브랜치와 PR로 검토한다. PR에서는 공개 정보와 링크를 검사하며, `main` 반영 후 검사에 통과하면 Pages에 배포한다. 화면 변경은 데스크톱·모바일에서 한국어 줄바꿈, 키보드 조작, 검색·실습·답안 다운로드를 확인한다.

[운영·공개 범위](docs/OPERATIONS.md)에서 자료 추가, 게시 확인과 복구 절차를 확인한다. 내용의 기술 근거는 각 교재의 공식 출처를 따른다.

[공식 로고 사용](docs/BRAND.md)에 헤더·푸터·홈·파비콘의 자산 출처와 표시 기준을 정리했다.
