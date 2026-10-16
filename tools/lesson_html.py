"""Adapt Astro's new HTML to existing site links, tables and review controls."""
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import PurePosixPath
from urllib.parse import urlsplit, unquote, quote, urlunsplit
import posixpath
import re


def relative_url(page, target, query='', fragment=''):
    path = posixpath.relpath(target, str(PurePosixPath(page).parent))
    return urlunsplit(('', '', quote(path, safe='/.-_'), query, fragment))


class LessonHTML(HTMLParser):
    def __init__(self, text, lesson, documents, resolve):
        super().__init__(convert_charrefs=True)
        self.text = text
        self.lesson = lesson
        self.documents = documents
        self.resolve = resolve
        self.edits = []
        self.lines = [0]
        self.lines.extend(match.end() for match in re.finditer('\n', text))
        self.in_article = False
        self.question = None
        self.question_level = 0
        self.heading = None
        self.heading_text = []
        self.questions = {q['id']: q['label'] for q in lesson['questions']}
        self.seen = set()
        self.feed(text)
        if set(self.questions) != self.seen:
            raise ValueError('Review question headings did not render as expected')

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def finish_question(self, offset):
        if not self.question:
            return
        key = self.question
        label = escape(self.questions[key], quote=True)
        field = f'<div class="answer-box"><label for="answer-{key}">{label} — 답과 근거</label><textarea id="answer-{key}" data-answer="{label} — 답과 근거" rows="5" placeholder="내 답과 판단 근거를 적으세요."></textarea></div>'
        self.edits.append((offset, offset, field))
        self.question = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        offset = self.position()
        raw = self.get_starttag_text()
        if tag == 'article':
            self.in_article = True
        if self.in_article and re.fullmatch('h[2-6]', tag):
            level = int(tag[1])
            if self.question and level <= self.question_level:
                self.finish_question(offset)
            self.heading, self.heading_text = level, []
        if self.in_article and 'save-bar' in attrs.get('class', '').split():
            self.finish_question(offset)
        if self.in_article and tag == 'table':
            self.edits.append((offset, offset, '<div class="table-scroll" role="region" tabindex="0" aria-label="가로로 스크롤할 수 있는 표">'))
        for attr in ('href', 'src'):
            value = attrs.get(attr)
            if not value:
                continue
            url = urlsplit(value)
            target = None
            if url.path.startswith('/aolda-network-study-4th/_astro/'):
                target = url.path.removeprefix('/aolda-network-study-4th/')
            elif tag == 'a' and self.in_article and 'data-site-link' not in attrs and not url.scheme and not url.netloc and url.path:
                source = self.resolve(self.lesson['source'], value)
                target = source if 'download' in attrs else self.documents.get(source, source)
            if target is None:
                continue
            new_value = relative_url(self.lesson['output'], target, url.query, url.fragment)
            match = re.search(r'\b' + attr + r'\s*=\s*([\"\'])(.*?)\1', raw, re.S)
            if not match:
                raise ValueError('Generated URL attributes must be quoted')
            self.edits.append((offset + match.start(2), offset + match.end(2), escape(new_value, quote=True)))

    def handle_endtag(self, tag):
        offset = self.position()
        if self.in_article and tag == 'table':
            self.edits.append((offset + len('</table>'), offset + len('</table>'), '</div>'))
        if self.in_article and self.heading and tag == f'h{self.heading}':
            label = unescape(''.join(self.heading_text)).strip()
            match = re.match(r'(Q\d+)\b', label)
            if match and match[1] in self.questions:
                key = match[1]
                if key in self.seen:
                    raise ValueError('Duplicate rendered review question')
                self.seen.add(key)
                self.question, self.question_level = key, self.heading
            self.heading = None
        if tag == 'article':
            self.finish_question(offset)
            self.in_article = False

    def handle_data(self, data):
        if self.heading:
            self.heading_text.append(data)

    def rendered(self):
        text = self.text
        for start, end, value in sorted(self.edits, reverse=True):
            text = text[:start] + value + text[end:]
        return text
