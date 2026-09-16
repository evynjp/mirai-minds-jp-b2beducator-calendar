from pathlib import Path
import re

EVENT_RE = re.compile(r"BEGIN:VEVENT\n(.*?)\nEND:VEVENT", re.S)
URL_RE = re.compile(r"(?m)^URL:(.+)$")
DESC_RE = re.compile(r"(?m)^DESCRIPTION:(.*)$")


def escape_text(value: str) -> str:
    return value.replace('\\', '\\\\').replace(',', '\\,').replace(';', '\\;')


def normalize_event(match: re.Match) -> str:
    body = match.group(1)
    url_match = URL_RE.search(body)
    desc_match = DESC_RE.search(body)
    if not url_match or not desc_match:
        return match.group(0)

    url = url_match.group(1).strip()
    desc = desc_match.group(1)
    if url in desc:
        return match.group(0)

    fallback_domains = ('doris.school', 'visit.doris.school')
    label = 'Source listing (fallback)' if any(domain in url for domain in fallback_domains) else 'More information / source'
    addition = f"\\n{label}: {escape_text(url)}"
    new_desc = f"DESCRIPTION:{desc}{addition}"
    body = body[:desc_match.start()] + new_desc + body[desc_match.end():]
    return f"BEGIN:VEVENT\n{body}\nEND:VEVENT"


def normalize_file(path: Path) -> bool:
    original = path.read_text(encoding='utf-8')
    updated = EVENT_RE.sub(normalize_event, original)
    if updated != original:
        path.write_text(updated, encoding='utf-8')
        return True
    return False


changed = []
for path in sorted(Path('_includes').glob('events*.ics')):
    if normalize_file(path):
        changed.append(str(path))

if changed:
    print('Updated source links in descriptions:')
    for path in changed:
        print(f' - {path}')
else:
    print('No calendar link normalization changes needed.')
