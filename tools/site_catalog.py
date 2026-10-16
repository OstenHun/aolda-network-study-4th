"""Shared course metadata and new-lesson source contracts."""
from html import escape
from pathlib import PurePosixPath
import copy
import json
import re


def local_path(value, suffix=None):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_./-]+', value):
        raise ValueError(f'Invalid site path: {value!r}')
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ('', '.', '..') for part in value.split('/')) or path.as_posix() != value:
        raise ValueError(f'Path must stay inside the site: {value}')
    if suffix and path.suffix != suffix:
        raise ValueError(f'Expected {suffix} path: {value}')
    return value


def read_catalog(root):
    path = root / 'config/site.json'
    if path.is_symlink():
        raise ValueError('Course metadata cannot be a symbolic link')
    return json.loads(path.read_text(encoding='utf-8'))


def lesson_text(data):
    text = data.decode('utf-8-sig').replace('\r\n', '\n')
    match = re.match(r'\A# ([^\n]+)\n+요약: ([^\n]+)\n', text)
    if not match or not match[1].strip() or not 1 <= len(match[2].strip()) <= 200:
        raise ValueError('A lesson needs one opening H1 and a summary of 1–200 characters')
    return match[1].strip(), match[2].strip(), text[match.end():].lstrip('\n')


def validate_catalog(catalog, payload):
    catalog = copy.deepcopy(catalog)
    groups = {}
    prefixes = []
    for group in catalog['groups']:
        key = group['id']
        if not re.fullmatch(r'[a-z0-9-]+', key) or key in groups:
            raise ValueError(f'Duplicate or invalid course ID: {key}')
        local_path(group['prefix'].rstrip('/'))
        if not group['prefix'].endswith('/') or any(group['prefix'].startswith(p) or p.startswith(group['prefix']) for p in prefixes):
            raise ValueError('Course prefixes must be distinct directories')
        prefixes.append(group['prefix'])
        local_path(group['entry'], '.html')
        if not group['entry'].startswith(group['prefix']):
            raise ValueError('Course entry must be inside its prefix')
        if group['section'] not in ('preparation', 'common', 'partial', 'advanced'):
            raise ValueError('Unknown course section')
        for page in group.get('nav', []):
            local_path(page['path'], '.html')
        description = group.get('home', {}).get('description_html', '')
        plain = description.replace('<span class="keep-phrase">', '').replace('</span>', '')
        if '<' in plain or '>' in plain:
            raise ValueError('Home description permits only keep-phrase spans')
        groups[key] = group
    outputs = set()
    ids = set()
    sources = set()
    for page in catalog['lessons']:
        if not re.fullmatch(r'[a-z0-9-]+', page['id']) or page['id'] in ids:
            raise ValueError('Lesson IDs must be unique lowercase names')
        ids.add(page['id'])
        local_path(page['source'], '.md')
        local_path(page['output'], '.html')
        if page['source'] in sources or page['output'] in outputs or page['output'] in payload:
            raise ValueError('A lesson cannot overwrite an existing source or output')
        sources.add(page['source'])
        outputs.add(page['output'])
        if page['source'] not in payload or page['group'] not in groups:
            raise ValueError('Lesson source or course is missing')
        group = groups[page['group']]
        if not page['output'].startswith(group['prefix']):
            raise ValueError('Lesson output must be inside its course')
        if page.get('kind', 'lesson') not in ('lesson', 'review'):
            raise ValueError('Only lesson and review pages are supported')
        page['kind'] = page.get('kind', 'lesson')
        title, summary, body = lesson_text(payload[page['source']])
        page.update(title=title, summary=summary, body=body, group_label=group['label'])
        questions = re.findall(r'^#{2,3} (Q\d+)\b([^\n]*)$', body, re.M) if page['kind'] == 'review' else []
        if page['kind'] == 'review' and (not questions or len({q[0] for q in questions}) != len(questions)):
            raise ValueError('A review needs unique Q1, Q2, … question headings')
        page['questions'] = [{'id': key, 'label': key + rest} for key, rest in questions]
        nav = group.setdefault('nav', [])
        if not any(item['path'] == page['output'] for item in nav):
            nav.append({'path': page['output'], 'label': page.get('label', title)})
    available = set(payload) | outputs
    for group in groups.values():
        if group['entry'] not in available or any(item['path'] not in available for item in group.get('nav', [])):
            raise ValueError(f'Course contains a missing page: {group["id"]}')
    for source, output in catalog['documents'].items():
        local_path(source, '.md')
        local_path(output, '.html')
        if source not in payload or output not in available:
            raise ValueError('Document mapping contains a missing source or output')
    catalog['documents'].update({page['source']: page['output'] for page in catalog['lessons']})
    return catalog


def numbers_text(numbers):
    values = sorted(int(n) for n in numbers)
    runs = []
    for value in values:
        if runs and value == runs[-1][-1] + 1:
            runs[-1].append(value)
        else:
            runs.append([value])
    return '·'.join(f'{run[0]}~{run[-1]}' if len(run) >= 3 else '·'.join(map(str, run)) for run in runs)


def home_courses(catalog):
    rows = []
    for group in catalog['groups']:
        home = group.get('home')
        if not home:
            continue
        extra = ' prep-row' if group['section'] == 'preparation' else ''
        rows.append('    <a class="course-row' + extra + '" href="' + group['entry'] + '"><span class="course-number">' + escape(group['number']) + '</span><div><h3>' + escape(home['title']) + '</h3><p>' + home['description_html'] + '</p></div><span class="course-tag">' + escape(home['tag']) + '</span><span class="row-arrow" aria-hidden="true">' + escape(home.get('arrow', '→')) + '</span></a>')
    partial = [group for group in catalog['groups'] if group['section'] == 'partial']
    if partial:
        rows.append('    <div class="partial-chapters"><span>먼저 읽을 수 있는 후속 개념</span>' + ''.join('<a href="' + group['entry'] + '">' + escape(group['home_partial_title']) + ' <span>본문 일부 ↗</span></a>' for group in partial) + '</div>')
    common = [g['number'] for g in catalog['groups'] if g['section'] == 'common' and g['number'].isdigit()]
    parts = []
    if common:
        parts.append(numbers_text(common) + '주차 자료')
    if partial:
        parts.append(numbers_text([g['number'] for g in partial]) + '주차 본문 일부')
    if any(g['section'] == 'advanced' for g in catalog['groups']):
        parts.append('후속 심화 자료')
    rows.append('    <p class="availability-note">' + '와 '.join(parts) + '를 공개하고 있습니다. 자료 공개는 개인의 실습·학습 완료를 뜻하지 않습니다.</p>')
    return '\n'.join(rows)
