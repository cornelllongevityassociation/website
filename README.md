# Cornell Longevity Association — website

The club's public site. Static HTML, hosted free on GitHub Pages.

**Editing the site's text does not require any coding.** All of it lives in
plain Markdown and YAML files in [`content/`](content/). See
**[EDITING.md](EDITING.md)** — that is the guide for everyone who just wants to
add an event, fill a position, or reword a page.

---

## How it works

```
content/     ← every word on the site (Markdown + YAML). Edit these.
templates/   ← the HTML page structure
assets/      ← stylesheet, favicon, photos
build.py     ← reads content/ + templates/ and writes _site/
_site/       ← the generated site. Never edit; never committed.
```

`build.py` turns each `content/*.md` file into one page and pulls the shared
lists (`team.yml`, `events.yml`, …) into every template that needs them.

Pushing to `main` triggers
[`.github/workflows/deploy.yml`](.github/workflows/deploy.yml), which builds the
site and publishes it. A change committed from the GitHub web editor is live in
about a minute.

## Design

The palette, type, and the hero artwork all come from the club's title slide:
warm charcoal `#383735`, cream `#E9E5DD`, a marigold rule `#EFA83B`, and the
refracted spectrum running blue → green → yellow → gold → coral. The hero is a
scalable SVG rebuild of that slide rather than an image, so it stays sharp at
any size. The spectrum also appears as the thin strip above the footer and as
the per-card accent colours.

Colours are defined once as CSS custom properties at the top of
`assets/css/site.css`.

## Running it locally

Optional — you only need this to preview changes before pushing.

```bash
pip install -r requirements.txt
python build.py --serve
```

Then open <http://localhost:8000>. Re-run the command after each edit.

To build without serving:

```bash
python build.py
```

## First-time setup on GitHub

This only has to be done once, by someone with admin access to the repository:

1. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
2. Push to `main` (or use **Actions → Deploy site → Run workflow**).
3. The URL appears under Settings → Pages.

If the site is served from `https://<org>.github.io/website/`, leave
`base_url: /website` in `content/site.yml` as it is. If you later add a custom
domain, put the domain in a file named `CNAME` at the root of the repository and
blank out `base_url`.

## Notes

- Pages are flat `.html` files with relative links, so the site works from a
  project subpath, a custom domain, or even opened straight from disk.
- `_site/` is generated and git-ignored — GitHub Actions builds it on every push.
- A blank value in `content/` renders as nothing, so deleting an optional line
  will never break the build.
