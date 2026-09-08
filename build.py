#!/usr/bin/env python3
"""
Build the Cornell Longevity Association website.

Reads plain Markdown + YAML from content/, renders the templates in templates/,
and writes a finished static site to _site/.

    python build.py             # build once into _site/
    python build.py --serve     # build, then serve on http://localhost:8000

Nothing in this file needs to be edited to change the words on the site — all
of the text lives in content/. See EDITING.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml
from markupsafe import Markup
from jinja2 import ChainableUndefined, Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"
OUTPUT = ROOT / "_site"

# Icons are cycled through in order for each repeating card group.
BRANCH_ICONS = ["flask", "palette", "briefcase", "compass", "spark"]
VALUE_ICONS = ["scales", "handshake", "heart", "compass", "spark"]
JOIN_ICONS = ["users", "spark", "flask", "handshake", "mic", "compass"]

SOCIAL_LABELS = {
    "instagram": "Instagram",
    "linkedin": "LinkedIn",
    "github": "GitHub",
    "twitter": "X",
    "x": "X",
    "youtube": "YouTube",
    "discord": "Discord",
}

FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def blankify(value):
    """Turn empty YAML values into empty strings.

    A key left blank in content/ (``photo:`` with nothing after it) parses as
    None, which would otherwise render as the literal word "None" on the page.
    Empty strings stay falsy, so `{% if %}` checks keep working.
    """
    if value is None:
        return ""
    if isinstance(value, dict):
        return {k: blankify(v) for k, v in value.items()}
    if isinstance(value, list):
        return [blankify(v) for v in value]
    return value


def load_yaml(name: str, default=None):
    """Read a YAML file from content/. Missing files fall back to `default`."""
    path = CONTENT / name
    if not path.exists():
        return default if default is not None else {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return default if default is not None else {}
    return blankify(data)


def load_page(name: str) -> dict:
    """Read a Markdown file with YAML front matter from content/."""
    path = CONTENT / name
    raw = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(raw)
    if not match:
        raise SystemExit(
            f"{path.relative_to(ROOT)}: missing the '---' front matter block at the top."
        )
    meta = blankify(yaml.safe_load(match.group(1)) or {})
    body = match.group(2).strip()
    meta["body_html"] = Markup(
        markdown.markdown(body, extensions=["extra", "sane_lists", "smarty"])
    ) if body else ""
    meta.setdefault("title", path.stem.title())
    return meta


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return slug or "item"


def initials(name: str | None) -> str:
    if not name:
        return "?"
    parts = [p for p in re.split(r"\s+", name.strip()) if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


# --------------------------------------------------------------------------
# Shaping content for the templates
# --------------------------------------------------------------------------

def prepare_events(raw, today: dt.date):
    """Split events into upcoming and past, each sorted sensibly."""
    upcoming, past = [], []
    for item in raw or []:
        entry = dict(item)
        date = entry.get("date")
        if isinstance(date, str):
            try:
                date = dt.date.fromisoformat(date.strip())
            except ValueError:
                raise SystemExit(
                    f"content/events.yml: '{entry.get('title', '?')}' has an unreadable "
                    f"date {date!r}. Use YYYY-MM-DD."
                )
        if isinstance(date, dt.datetime):
            date = date.date()
        if not isinstance(date, dt.date):
            raise SystemExit(
                f"content/events.yml: '{entry.get('title', '?')}' is missing a date."
            )
        entry["date"] = date
        entry["month"] = date.strftime("%b")
        entry["day"] = date.strftime("%-d") if sys.platform != "win32" else str(date.day)
        entry["year"] = date.strftime("%Y")
        entry["is_past"] = date < today
        (past if entry["is_past"] else upcoming).append(entry)

    upcoming.sort(key=lambda e: e["date"])
    past.sort(key=lambda e: e["date"], reverse=True)
    return upcoming, past


def prepare_team(raw):
    """Group e-board entries by `group`, preserving file order, and add initials."""
    members, groups, open_roles = [], [], []
    seen: dict[str, list] = {}

    for item in raw or []:
        m = dict(item)
        m["initials"] = initials(m.get("holder"))
        m["slug"] = slugify(m.get("role", ""))
        members.append(m)
        if not m.get("holder"):
            open_roles.append(m)
        group = m.get("group") or "Team"
        if group not in seen:
            seen[group] = []
            groups.append(group)
        seen[group].append(m)

    return members, [(g, seen[g]) for g in groups], open_roles


def prepare_socials(raw: dict | None):
    out = []
    for key, url in (raw or {}).items():
        if not url:
            continue
        out.append({
            "key": key,
            "icon": key if key in {"instagram", "linkedin", "github"} else "link",
            "label": SOCIAL_LABELS.get(key, key.title()),
            "url": url,
        })
    return out


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def build() -> int:
    today = dt.date.today()

    site = load_yaml("site.yml")
    branches = [dict(b, slug=slugify(b.get("name", ""))) for b in load_yaml("branches.yml", [])]
    values = load_yaml("values.yml", [])
    goals = load_yaml("goals.yml", [])
    advisors = [dict(a, initials=initials(a.get("name"))) for a in load_yaml("advisors.yml", [])]
    roadmap = load_yaml("roadmap.yml", [])

    members, team_groups, open_roles = prepare_team(load_yaml("team.yml", []))
    upcoming_events, past_events = prepare_events(load_yaml("events.yml", []), today)

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=True,
        # Missing optional keys render as empty rather than breaking the build,
        # so deleting a line from content/ is always safe.
        undefined=ChainableUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals.update(
        site=site,
        branches=branches,
        values=values,
        goals=goals,
        advisors=advisors,
        roadmap=roadmap,
        team=members,
        team_groups=team_groups,
        open_roles=open_roles,
        rep_lookup={m["role"]: m for m in members},
        upcoming_events=upcoming_events,
        past_events=past_events,
        socials=prepare_socials(site.get("social")),
        branch_icons=BRANCH_ICONS,
        value_icons=VALUE_ICONS,
        join_icons=JOIN_ICONS,
        year=today.year,
    )

    # Every content/*.md becomes one page. index.html comes from home.md.
    pages = []
    for md in sorted(CONTENT.glob("*.md")):
        page = load_page(md.name)
        page["source"] = md.name
        page["url"] = "index.html" if md.stem == "home" else f"{md.stem}.html"
        page["template"] = f"{page.get('template', 'page')}.html"
        pages.append(page)

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    for page in pages:
        template = env.get_template(page["template"])
        html = template.render(page=page, pages=pages)
        (OUTPUT / page["url"]).write_text(html, encoding="utf-8")
        print(f"  built  {page['url']:<16} from content/{page['source']}")

    shutil.copytree(ASSETS, OUTPUT / "assets")

    # Tell GitHub Pages not to run this through Jekyll.
    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")

    for extra in ("CNAME", "robots.txt"):
        src = ROOT / extra
        if src.exists():
            shutil.copy2(src, OUTPUT / extra)

    print(f"\n  {len(pages)} pages -> {OUTPUT.relative_to(ROOT)}/")
    return 0


def serve(port: int) -> None:
    import http.server

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(OUTPUT), **kw)

        def log_message(self, *a):  # keep the console quiet
            pass

    # Threading matters: browsers hold keep-alive connections open, and a
    # single-threaded server would stall every later request behind them.
    class Server(http.server.ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    with Server(("", port), Handler) as httpd:
        print(f"\n  Serving http://localhost:{port}  (Ctrl+C to stop)\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--serve", action="store_true", help="serve the site after building")
    parser.add_argument("--port", type=int, default=8000, help="port for --serve (default 8000)")
    args = parser.parse_args()

    print("\nBuilding Cornell Longevity Association site\n")
    code = build()
    if args.serve and code == 0:
        serve(args.port)
    raise SystemExit(code)
