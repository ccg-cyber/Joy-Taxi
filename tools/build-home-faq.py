#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add FAQPage structured data to the two homepages, built FROM the questions already
on the page.

Google requires the marked-up answer to match what a visitor actually reads, so the
schema is parsed out of the <details> blocks rather than written by hand beside them:
edit a question on the page, re-run this, and the schema follows. It cannot drift.

    python3 tools/build-home-faq.py

Idempotent: the block it writes is marked, and a re-run replaces it.
"""
import io, os, re, json, html, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK_OPEN  = '<!-- FAQ schema, generated from the questions above by tools/build-home-faq.py -->'
BLOCK_RE   = re.compile(re.escape(MARK_OPEN) + r'\n<script type="application/ld\+json">.*?</script>\n', re.S)

TARGETS = {
    'index.html':    'https://joytaxi.cierp.uk/',
    'ar/index.html': 'https://joytaxi.cierp.uk/ar/',
}


def text_of(frag):
    """Visible text of an HTML fragment: drop tags, unescape entities, collapse space."""
    t = re.sub(r'<[^>]+>', '', frag)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def faqs(src):
    out = []
    for m in re.finditer(r'<details>\s*<summary>(.*?)</summary>\s*(.*?)\s*</details>', src, re.S):
        q, a = text_of(m.group(1)), text_of(m.group(2))
        if q and a:
            out.append((q, a))
    return out


def build(path, url):
    p = os.path.join(ROOT, path)
    src = io.open(p, encoding='utf-8').read()
    qa = faqs(src)
    if not qa:
        sys.exit('%s: found no <details> FAQ blocks' % path)

    graph = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        '@id': url + '#faq',
        'inLanguage': 'ar' if path.startswith('ar/') else 'en',
        'mainEntity': [
            {'@type': 'Question', 'name': q,
             'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qa
        ],
    }
    block = (MARK_OPEN + '\n<script type="application/ld+json">\n'
             + json.dumps(graph, ensure_ascii=False, indent=2)
             + '\n</script>\n')

    src, n = BLOCK_RE.subn(block, src)
    if not n:
        # First run: sit it immediately before the closing </body>.
        anchor = '</body>'
        if src.count(anchor) != 1:
            sys.exit('%s: need exactly one </body>' % path)
        src = src.replace(anchor, block + anchor)
    io.open(p, 'w', encoding='utf-8').write(src)
    return len(qa), ('replaced' if n else 'inserted')


if __name__ == '__main__':
    for path, url in TARGETS.items():
        n, how = build(path, url)
        print('  %-16s %d questions %s' % (path, n, how))
