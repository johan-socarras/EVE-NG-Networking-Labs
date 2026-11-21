#!/usr/bin/env python3
"""Checks this repository with the standard library only.

- Every relative link and image in the Markdown files points at a file that exists,
  and every #anchor at a heading of the page it links to.
- Every PNG holds only the image itself: no text chunks, so no capture time and no
  program name travel with a screenshot.
- No EVE-NG lab export (.unl) and no archive (.zip) is committed: an export embeds
  every startup-config, and in a troubleshooting lab that is the answer.
- Every secret in a configuration is replaced by <REDACTED>.
- Every IPv4 address is private (RFC 1918), documentation-only (RFC 5737) or loopback, or is
  a netmask or wildcard mask.

Run it from the root of the repository: python3 .github/scripts/check-repo.py
"""
import ipaddress
import re
import struct
import subprocess
import sys
from pathlib import Path

LINK = re.compile(r'!?\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
HTML_LINK = re.compile(r'<(?:a|img)\b[^>]*?\b(?:href|src)="([^"]+)"')
HEADING = re.compile(r'^#{1,6}\s+(.*)$', re.M)
FENCE = re.compile(r'```.*?```', re.S)
SECRET = re.compile(r'\b(secret|password|md5|key-string|pre-shared-key|authentication-key|community)'
                    r'\s+(?:\d\s+)?(\S+)', re.I)
IPV4 = re.compile(r'(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])')
ALLOWED = [ipaddress.ip_network(n) for n in (
    '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16',               # RFC 1918
    '192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24',          # RFC 5737
    '127.0.0.0/8', '224.0.0.0/24',                                # loopback, link-local multicast
)]


def tracked(*patterns):
    out = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', *patterns],
                         capture_output=True, text=True, check=True).stdout
    return [Path(line) for line in out.splitlines() if Path(line).exists()]


def slug(heading):
    """The anchor GitHub gives a heading: lower case, punctuation dropped, spaces to hyphens."""
    text = re.sub(r'[`*_]', '', heading.strip().lower())
    return re.sub(r'[^\w\- ]', '', text).replace(' ', '-')


def check_links():
    pages = tracked('*.md')
    anchors = {p: {slug(h) for h in HEADING.findall(FENCE.sub('', p.read_text(encoding='utf-8')))} for p in pages}
    problems, count = [], 0
    for page in pages:
        text = FENCE.sub('', page.read_text(encoding='utf-8'))
        for target in LINK.findall(text) + HTML_LINK.findall(text):
            if re.match(r'[a-z][a-z0-9+.-]*:', target):
                continue  # http, https, mailto: not checked here
            count += 1
            path, _, anchor = target.partition('#')
            dest = (page.parent / path) if path else page
            if not dest.exists():
                problems.append(f'{page}: {target} does not exist')
            elif anchor and dest.suffix == '.md':
                known = anchors.get(Path(*dest.resolve().relative_to(Path.cwd().resolve()).parts))
                if known is not None and anchor not in known:
                    problems.append(f'{page}: {target} has no such heading')
    print(f'{count} relative links and images in {len(pages)} pages')
    return problems


def check_images():
    problems = []
    images = tracked('*.png')
    for image in images:
        data = image.read_bytes()
        if data[:8] != b'\x89PNG\r\n\x1a\n':
            problems.append(f'{image}: not a PNG file')
            continue
        pos, chunks = 8, set()
        while pos + 8 <= len(data):
            length, kind = struct.unpack('>I4s', data[pos:pos + 8])
            chunks.add(kind.decode('latin-1'))
            pos += 12 + length
        extra = chunks - {'IHDR', 'IDAT', 'IEND', 'PLTE', 'tRNS'}
        if extra or pos != len(data):
            problems.append(f'{image}: carries more than the image ({", ".join(sorted(extra)) or "trailing data"})')
    print(f'{len(images)} PNG images')
    return problems


def check_exports():
    found = tracked('*.unl', '*.zip')
    print(f'{len(found)} lab exports or archives')
    return [f'{f}: lab exports and archives are not published' for f in found]


def config_lines():
    """Configuration text: every .txt file, and the fenced blocks of the Markdown pages."""
    for f in tracked('*.txt'):
        for n, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
            yield f, n, line
    for f in tracked('*.md'):
        text = f.read_text(encoding='utf-8')
        for block in FENCE.finditer(text):
            first = text.count('\n', 0, block.start()) + 1
            for k, line in enumerate(block.group(0).splitlines()):
                yield f, first + k, line


def check_secrets():
    problems, count = [], 0
    for f, n, line in config_lines():
        for m in SECRET.finditer(line):
            count += 1
            if m.group(2) != '<REDACTED>':
                problems.append(f'{f}:{n}: secret not redacted ({m.group(1)})')
    print(f'{count} secret fields checked')
    return problems


def is_mask(ip):
    value = int(ip)
    inverse = value ^ 0xFFFFFFFF
    return (inverse & (inverse + 1)) == 0 or (value & (value + 1)) == 0


def check_addresses():
    problems, seen = [], set()
    for f in tracked('*.md', '*.txt'):
        for n, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
            for raw in IPV4.findall(line):
                try:
                    ip = ipaddress.IPv4Address(raw)
                except ValueError:
                    continue  # a version string such as 15.2.4.0, not an address
                seen.add(ip)
                if not any(ip in net for net in ALLOWED) and not is_mask(ip):
                    problems.append(f'{f}:{n}: {ip} is neither private nor documentation-only')
    print(f'{len(seen)} distinct IPv4 addresses')
    return problems


if __name__ == '__main__':
    found = check_links() + check_images() + check_exports() + check_secrets() + check_addresses()
    for line in found:
        print(f'::error::{line}')
    sys.exit(1 if found else 0)
