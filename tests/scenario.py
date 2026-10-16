"""Unpublished authoring examples injected into the in-memory site input."""
import copy


def authoring_example(builder):
    catalog = copy.deepcopy(builder.read_catalog(builder.ROOT))
    content = builder.collect_content()
    prefix = 'materials/authoring-example/'
    content[prefix + 'INDEX.md'] = '''# 비공개 심화 시험 홈

요약: index.html 경로와 심화 등록의 연결을 확인하는 비공개 입력이다.

## 읽기 순서

[교재](CONCEPTS.md) → [복습](REVIEW.md) → [해설](ANSWERS.md).
'''.encode()
    # Keep this fixture independent of a course's growing set of sibling links.
    content[prefix + 'CONCEPTS.md'] = '''# TCP 연결 비용 읽기

요약: 연결 수립의 왕복 시간과 메시지 수를 구별하는 비공개 시험 입력이다.

<span id="rtt"></span>

## 연결 준비

계산 모형을 읽고 [분리 해설](ANSWERS.md)로 확인한다.
'''.encode()
    content[prefix + 'ANSWERS.md'] = '''# 연결 비용 해설

요약: 비공개 시험 문항의 계산 가정을 확인한다.

## 조건 확인

[교재](CONCEPTS.md#rtt)로 돌아간다.
'''.encode()
    content[prefix + 'REVIEW.md'] = '''# TCP 연결 비용 복습

요약: RTT와 서버 상태를 구별해 설명하고 조건을 바꿔 확인한다. 답안은 개인 파일로 내려받으며 자동 저장되거나 제출되지 않는다.

## Q1. 왕복 시간과 메시지 수

왕복 시간이 100ms일 때, 세 메시지로 연결하는 과정을 세 번의 왕복이라고 설명할 수 있는가? [RTT 교재](CONCEPTS.md#rtt)에서 근거를 찾는다.

## Q2. 비대칭 경로

보내는 편도 지연이 30ms, 돌아오는 편도가 70ms인 경우를 설명한다. 계산과 실제 관찰을 구별한다.

| 확인 대상 | 판단 근거 |
| --- | --- |
| 클라이언트 | 응답을 받는 시점 |
| 서버 | 마지막 ACK를 받는 시점 |

## 다시 확인하기

[분리 해설](ANSWERS.md)과 비교하고, <a download href="CONCEPTS.md">교재 원본</a>도 보관할 수 있다. 값 1~3의 범위와 아래 코드 원문은 변환 중 유지돼야 한다.

```html
<a href="ANSWERS.md">코드 예시</a>
```
'''.encode()
    catalog['groups'].append({
        'id': 'authoring-example', 'label': 'TCP 연결 비용',
        'prefix': prefix, 'entry': prefix + 'index.html',
        'section': 'advanced', 'number': '예시', 'sidebar_title': 'TCP 연결 비용',
        'nav': [], 'home': {'title': 'TCP 연결 비용 읽기', 'description_html': 'RTT · 조건 변경 · 설명과 복습', 'tag': '교재 · 복습', 'arrow': '→'}
    })
    for source, output, kind, label in [('INDEX', 'index', 'lesson', '시험 홈'), ('CONCEPTS', 'concepts', 'lesson', '개념 교재'), ('REVIEW', 'review', 'review', '복습 문제'), ('ANSWERS', 'answers', 'lesson', '분리 해설')]:
        catalog['lessons'].append({'id': 'example-' + output, 'source': prefix + source + '.md', 'output': prefix + output + '.html', 'group': 'authoring-example', 'kind': kind, 'label': label})
    return catalog, content
