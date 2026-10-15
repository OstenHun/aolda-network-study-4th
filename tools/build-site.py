"""Build the public learning site using only this repository and Python stdlib."""
from pathlib import Path, PurePosixPath
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, quote
import json
import re
import shutil
import struct

from study_site_theme import apply_theme

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
OUT = ROOT / "dist"
MD_LINK = re.compile(r'\[[^\]]*\]\(([^\s)]+)(?:\s+"[^\"]*")?\)')
FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#07548e"/><path d="M8 9h16M8 16h16M8 23h16M8 9v14" stroke="white" stroke-width="3"/></svg>'
HEAD = '<meta name="robots" content="noindex,nofollow"><link rel="icon" type="image/svg+xml" href="data:image/svg+xml,' + quote(FAVICON, safe='') + '">'
ALLOWED_SUFFIXES = {".html", ".md", ".txt", ".py", ".sh", ".mts", ".pcapng"}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])
        if attrs.get("id"):
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
    files = [ROOT / "README.md", ROOT / "AGENTS.md"]
    for folder in ("content", "tools", "docs", ".github"):
        files.extend(p for p in (ROOT / folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    for path in files:
        if path.suffix == ".pcapng":
            check_capture(path.read_bytes())
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in patterns.items():
            if re.search(pattern, text):
                raise ValueError(f"{path.relative_to(ROOT)}: {label}")
    return len(files)


def build():
    source_count = check_public_sources()
    payload = {}
    for path in CONTENT.rglob("*"):
        if path.is_symlink():
            raise ValueError("Public content cannot contain symbolic links")
        if path.is_file():
            if path.suffix not in ALLOWED_SUFFIXES:
                raise ValueError(f"Unexpected public input: {path.name}")
            payload[path.relative_to(CONTENT).as_posix()] = path.read_bytes()
    home = (ROOT / "tools/templates/study-home.html").read_text(encoding="utf-8")
    payload["index.html"] = home.replace("__HEAD__", HEAD).encode()
    apply_theme(payload, ROOT)
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
    if OUT.is_symlink() or OUT.resolve() != ROOT / "dist":
        raise ValueError("Output must be the repository dist folder")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    payload[".nojekyll"] = b""
    for name, data in payload.items():
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(json.dumps({"source_files_checked": source_count, "public_files": len(payload), "html_pages": len(pages), "local_links_checked": links}, ensure_ascii=False))


if __name__ == "__main__":
    build()
