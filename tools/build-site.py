"""Assemble legacy pages and Astro lessons, then validate the final public site."""
from pathlib import Path, PurePosixPath
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
import shutil
import struct
import os
import subprocess

from study_site_theme import apply_theme
from site_catalog import read_catalog, validate_catalog, home_courses, local_path
from lesson_html import LessonHTML

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
MD_LINK = re.compile(r'\[[^\]]*\]\(([^\s)]+)(?:\s+"[^\"]*")?\)')
HEAD = '<meta name="robots" content="noindex,nofollow">'
ALLOWED_SUFFIXES = {".html", ".md", ".txt", ".py", ".sh", ".mts", ".pcapng", ".svg"}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = set()
        self.duplicate_ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])
        if attrs.get("id"):
            if attrs['id'] in self.ids:
                self.duplicate_ids.add(attrs['id'])
            self.ids.add(attrs["id"])


def resolve(name, href):
    url = urlsplit(href)
    if url.scheme or url.netloc:
        return None
    if url.path.startswith("/"):
        raise ValueError(f"{name}: root path breaks project Pages URLs")
    if not url.path:
        return name
    parts = list(PurePosixPath(name).parent.parts)
    for part in unquote(url.path).split("/"):
        if part == "..":
            if not parts:
                raise ValueError(f"{name}: link escapes site")
            parts.pop()
        elif part not in ("", "."):
            parts.append(part)
    return "/".join(parts)


def check_capture(data):
    """Accept only metadata-free loopback IPv4 packets in the teaching capture."""
    offset = 0
    packets = 0
    while offset < len(data):
        kind, size = struct.unpack_from("<II", data, offset)
        block = data[offset:offset + size]
        if size < 12 or size % 4 or len(block) != size or struct.unpack_from("<I", block, size - 4)[0] != size:
            raise ValueError("Invalid teaching capture block")
        if kind == 0x0A0D0D0A:
            if size != 28:
                raise ValueError("Capture section metadata must be removed")
        elif kind == 1:
            if size != 20 or struct.unpack_from("<H", block, 8)[0] != 0:
                raise ValueError("Unexpected capture interface or metadata")
        elif kind == 6:
            length = struct.unpack_from("<I", block, 20)[0]
            packet = block[28:28 + length]
            if size != 32 + ((length + 3) // 4) * 4:
                raise ValueError("Capture packet metadata must be removed")
            if packet[:4] != b"\x02\x00\x00\x00" or packet[4] >> 4 != 4:
                raise ValueError("Expected loopback IPv4 teaching packet")
            if packet[16:24] != bytes([127, 0, 0, 1]) * 2:
                raise ValueError("Teaching capture contains non-loopback addresses")
            packets += 1
        else:
            raise ValueError("Unexpected capture block")
        offset += size
    if not packets:
        raise ValueError("Teaching capture has no packets")
    return packets


def check_public_sources():
    # This covers the repository source, not just files served by Pages.
    patterns = {
        "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        "GitHub credential": r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})",
        "API credential": r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}",
        "local user path": r"(?i)[A-Z]:[\\/]Users[\\/][^\s<>]+|/ho" + r"me/[^/\s]+/",
        "internal service": r"https?://(?:console\.aolda\.net|(?:app\.)?notion\.(?:com|so))",
        "email address": r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
    }
    files = [ROOT / name for name in ('README.md', 'AGENTS.md', 'package.json', 'package-lock.json', 'astro.config.mjs') if (ROOT / name).exists()]
    for folder in ("content", "tools", "docs", ".github", "config", "astro", "tests"):
        for path in (ROOT / folder).rglob('*'):
            if path.is_symlink():
                raise ValueError('Public source cannot contain symbolic links')
            if path.is_file() and '__pycache__' not in path.parts:
                files.append(path)
    for path in files:
        if path.is_symlink():
            raise ValueError('Public source cannot contain symbolic links')
        if path.suffix == ".pcapng":
            check_capture(path.read_bytes())
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in patterns.items():
            if re.search(pattern, text):
                raise ValueError(f"{path.relative_to(ROOT)}: {label}")
    return len(files)


def collect_content():
    payload = {}
    for path in CONTENT.rglob("*"):
        if path.is_symlink():
            raise ValueError("Public content cannot contain symbolic links")
        if path.is_file():
            if path.suffix not in ALLOWED_SUFFIXES:
                raise ValueError(f"Unexpected public input: {path.name}")
            payload[path.relative_to(CONTENT).as_posix()] = path.read_bytes()
    return payload


def generated_folder(name):
    path = ROOT / name
    if path.is_symlink() or path.resolve() != ROOT / name:
        raise ValueError('Generated folders must stay inside this repository')
    if path.exists():
        shutil.rmtree(path)
    path.mkdir()
    return path


def astro_lessons(catalog):
    if not catalog['lessons']:
        return {}
    input_folder = generated_folder('.astro-input')
    (input_folder / 'static').mkdir()
    output_folder = generated_folder('.astro-output')
    manifest = []
    for lesson in catalog['lessons']:
        metadata = '\n'.join(key + ': ' + json.dumps(lesson[key], ensure_ascii=False) for key in ('title', 'summary'))
        (input_folder / (lesson['id'] + '.md')).write_text('---\n' + metadata + '\n---\n\n' + lesson['body'], encoding='utf-8')
        manifest.append({key: value for key, value in lesson.items() if key != 'body'})
    (input_folder / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')
    cli = ROOT / 'node_modules/astro/bin/astro.mjs'
    node = shutil.which('node')
    if not node or not cli.is_file():
        raise ValueError('Install Node.js 22.22+ and run npm ci before generating lessons')
    environment = dict(os.environ, ASTRO_TELEMETRY_DISABLED='1', NO_COLOR='1')
    run = subprocess.run([node, str(cli), 'build'], cwd=ROOT, env=environment, capture_output=True, text=True, encoding='utf-8', timeout=120)
    if run.returncode:
        raise ValueError('Astro build failed:\n' + run.stdout + run.stderr)
    generated = {}
    for path in output_folder.rglob('*'):
        if path.is_symlink():
            raise ValueError('Astro output cannot contain symbolic links')
        if path.is_file():
            name = path.relative_to(output_folder).as_posix()
            local_path(name)
            generated[name] = path.read_bytes()
    expected = {page['id'] + '.html' for page in catalog['lessons']}
    if {name for name in generated if name.endswith('.html')} != expected:
        raise ValueError('Astro did not produce exactly the registered lesson pages')
    for lesson in catalog['lessons']:
        name = lesson['output']
        raw = generated.pop(lesson['id'] + '.html')
        generated[name] = LessonHTML(raw.decode(), lesson, catalog['documents'], resolve).rendered().encode()
        page = Page(generated[name].decode())
        if page.duplicate_ids:
            raise ValueError(f'{name}: duplicate anchors {sorted(page.duplicate_ids)}')
    generated['assets/lesson.css'] = (ROOT / 'tools/lesson.css').read_bytes()
    if any(page['kind'] == 'review' for page in catalog['lessons']):
        generated['assets/lesson-answers.js'] = (ROOT / 'tools/lesson-answers.js').read_bytes()
    return generated


def make_payload(catalog=None, content=None):
    payload = collect_content() if content is None else dict(content)
    catalog = validate_catalog(read_catalog(ROOT) if catalog is None else catalog, payload)
    generated = astro_lessons(catalog)
    if set(payload) & set(generated):
        raise ValueError('Generated assets cannot overwrite existing public files')
    payload.update(generated)
    home = (ROOT / "tools/templates/study-home.html").read_text(encoding="utf-8")
    payload["index.html"] = home.replace("__HEAD__", HEAD).replace('__COURSE_PATH__', home_courses(catalog)).encode()
    apply_theme(payload, ROOT, catalog)
    return payload


def validate_links(payload):
    pages = {name: Page(data.decode()) for name, data in payload.items() if name.endswith(".html")}
    links = 0
    for name, data in payload.items():
        if name.endswith(".html"):
            refs = pages[name].links
        elif name.endswith(".md"):
            refs = MD_LINK.findall(data.decode())
        else:
            continue
        for href in refs:
            target = resolve(name, href)
            if target is None:
                continue
            links += 1
            if target not in payload:
                raise ValueError(f"{name}: missing link {href}")
            fragment = unquote(urlsplit(href).fragment)
            if target in pages and fragment and fragment not in pages[target].ids:
                raise ValueError(f"{name}: missing anchor {href}")
    return len(pages), links


def build():
    source_count = check_public_sources()
    payload = make_payload()
    pages, links = validate_links(payload)
    output = generated_folder('dist')
    payload[".nojekyll"] = b""
    for name, data in payload.items():
        local_path(name)
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(json.dumps({"source_files_checked": source_count, "public_files": len(payload), "html_pages": pages, "local_links_checked": links}, ensure_ascii=False))


if __name__ == "__main__":
    build()
