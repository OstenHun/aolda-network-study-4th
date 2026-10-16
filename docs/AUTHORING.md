# 새 교재 작성 안내

요약: 기존 주차의 화면과 동작을 보존한다. 다음 제작 교재는 Markdown과 과정 등록 정보로 HTML·목차·메뉴·검색을 생성하고 공개 정보·링크·앵커를 검사한다. 빌드만으로 배포하지 않는다.

## 제작 순서

새 주차는 Astro로 제작하는 것을 기본으로 한다. 기존 정상 교재는 필요한 변경 범위에서 유지하며 이 결정을 일괄 이전으로 확대하지 않는다.

1. 실제 제작할 주차나 심화 모듈의 범위를 정한다. 미제작 전체 주차를 빈 화면으로 만들지 않는다.
2. `tools/templates/lesson.md` 또는 `review.md`를 필요한 `content/materials/` 폴더로 복사해 작성한다. 첫 H1 다음에 `요약:` 한 문장을 1~200자로 쓴다. 제목·요약을 별도 설정에 중복 입력하지 않는다.
3. `config/site.json`에 과정과 페이지를 등록한다. 기존 과정에 추가할 때는 `lessons`만 추가한다. HTML 출력 경로는 기존 파일과 겹칠 수 없다.
4. 아래 검사와 실제 화면·기능 확인을 마친다. 배포는 별도 승인 범위로 진행한다.

## 과정과 페이지 등록 예시

다음은 설정 형식을 설명하는 예시다. 해당 자료를 실제로 작성한 뒤 기존 배열에 항목을 추가한다. 번호·상태·주제는 실제 제작 범위에 맞춘다.

`groups`에 들어가는 과정:

```json
{
  "id": "week-05",
  "label": "5주차 · DNS",
  "prefix": "materials/week-05/",
  "entry": "materials/week-05/concepts.html",
  "section": "common",
  "number": "05",
  "sidebar_title": "DNS",
  "nav": [],
  "home": {
    "title": "5주차 · 이름으로 서버 찾기",
    "description_html": "DNS · 캐시 · 조건 변경",
    "tag": "교재 · 복습",
    "arrow": "→"
  }
}
```

`lessons`에 들어가는 페이지:

```json
[
  {"id":"week05-concepts","source":"materials/week-05/CONCEPTS.md","output":"materials/week-05/concepts.html","group":"week-05","kind":"lesson","label":"개념 교재"},
  {"id":"week05-review","source":"materials/week-05/REVIEW.md","output":"materials/week-05/review.html","group":"week-05","kind":"review","label":"복습 문제"},
  {"id":"week05-answers","source":"materials/week-05/ANSWERS.md","output":"materials/week-05/answers.html","group":"week-05","kind":"lesson","label":"분리 해설"}
]
```

페이지 등록 순서가 하위 메뉴 순서다. 제목은 Markdown H1에서 읽고 메뉴에는 `label`을 쓴다. 새 페이지를 `nav`에 다시 적을 필요는 없다. 기존 HTML만 별도로 연결할 때 `nav`에 `path`·`label`을 넣는다. `documents`는 기존 Markdown과 HTML의 대응표이며 새 교재는 자동 등록한다.

후속 심화는 과정의 `section`을 `advanced`로, `number`를 `S01` 등의 표시로 정한다. 같은 페이지 생성·검색·검사를 사용한다. `partial`은 기존 본문 일부를 표시하는 구분이며 완료된 주차로 바꾸지 않는다. `home`은 홈에 노출할 실제 자료가 있을 때 추가한다. 설명은 일반 문장을 쓰고 필요한 경우에만 `keep-phrase` span을 사용한다.

## 링크·목차·복습 답안

- H2·H3로 목차를 자동 생성한다. Astro의 제목 앵커를 사용하며 기존 수동 HTML의 앵커는 바꾸지 않는다. 안정된 짧은 앵커가 필요하면 본문에 `<span id="rtt"></span>`처럼 명시하고 중복을 피한다.
- 새 Markdown에서 `[분리 해설](ANSWERS.md)`처럼 원문 기준 상대 링크를 쓴다. 등록된 교재는 생성된 `.html`로 연결한다. 기존 교재는 `documents` 대응표를 사용한다. HTML 화면 링크도 상대 경로로 쓸 수 있다.
- 원문 다운로드는 `<a download href="CONCEPTS.md">교재 원본</a>`처럼 명시한다. 각 새 교재 하단에도 원본 다운로드를 제공한다. 코드 블록 속 링크 문자열은 바꾸지 않는다.
- `kind: "review"`는 `## Q1. 질문` 또는 `### Q1. 질문` 형태의 고유 번호마다 입력칸을 붙인다. 답안 다운로드·저장 확인·수정 후 이동 경고는 기존 복습 방식과 같다. 입력은 서버나 브라우저 저장소에 자동 저장하지 않는다. 해설은 별도 `lesson` 페이지로 작성한다.
- Markdown 표에는 가로 스크롤을 붙인다. 공통 CSS와 16px 본문·한국어 어절 줄바꿈을 적용한다. 새 대화형 모형은 별도 구현·검증 대상이며 Astro가 학습 기능을 자동으로 만들어 주지는 않는다.

## 로컬 검사와 미리보기

```sh
npm ci --ignore-scripts
npm test
npm run build
python -m http.server 8000 --directory dist
```

`http://localhost:8000`에서 연다. 정적 파일의 상대 경로를 사용하므로 실제 Pages 하위 경로에서도 같은 연결을 유지한다. 검수할 때는 하위 경로를 포함한 로컬 경로에서도 깊은 링크·새로고침·목차·검색·메뉴·원본/답안 다운로드를 확인한다.

빌드는 공개 소스와 캡처 형식, 중복 출력·경로 이탈, 존재하지 않는 내부 링크·HTML 앵커, 새 교재의 중복 ID·복습 번호를 검사한다. 검사 실패를 무시해 게시하지 않는다. 외부 URL의 현재 응답·기술 내용의 정확성·실제 실습·화면 읽기는 별도로 확인한다.

자동 테스트는 실제 Astro로 비공개 심화 예시 네 페이지를 만들고 중첩 `index.html`·공통 홈·메뉴·검색·다운로드·링크 변환을 확인한다. 시험 입력은 특정 주차 본문에 의존하지 않으며 실제 교재가 늘어도 함께 검사한다. 동시에 기존 페이지의 본문·스타일·스크립트가 변하지 않는지 검사한다. 예시는 메모리에서만 넣으므로 정상 `dist/`나 학습 메뉴에 게시되지 않는다.

## 변경 경계

기존 1주차는 Astro로 옮기지 않는다. 4주차 실제 제작에서는 기존 일부 초안의 Markdown을 이어 쓰고 대응 수동 HTML 두 개만 제거해 같은 공개 경로를 Astro로 생성한다. 새 교재와 이 전환 대상에 Astro를 사용하고 Python은 나머지 기존 파일 조립과 검사를 유지한다. 수동 HTML이 남아 있으면 등록 출력과 충돌하므로 빌드가 실패한다. 생성된 HTML·임시 `.astro-input/`·`.astro-output/`·`dist/`는 수정하거나 커밋하지 않는다. 공통 디자인·동작을 바꿀 때는 기존 페이지를 포함해 회귀 확인한다.

잠금 파일을 커밋하고 설치는 `npm ci --ignore-scripts`로 재현한다. 원격 CI와 배포 상태는 로컬 검사 결과와 구별한다. `main`에 push하면 기존 Pages 워크플로가 배포하므로 배포 승인이 없을 때는 push하지 않는다.
