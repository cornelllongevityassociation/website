# Editing the website

Everything visible on the site lives in the **`content/`** folder. You do not
need to touch HTML, CSS, or Python to change any of the words, people, or
events.

You can edit these files two ways:

- **On github.com** (easiest) — open the file, click the pencil ✏️, make your
  change, and click *Commit changes*. The site rebuilds and goes live in about
  a minute.
- **On your computer** — edit the files in any text editor, then commit and
  push.

---

## Which file do I edit?

| I want to change… | Edit this file |
| --- | --- |
| Club name, tagline, nav links, email, social links, footer | `content/site.yml` |
| Homepage headline, intro, section headings, calls to action | `content/home.md` |
| The About page essay text, section headings | `content/about.md` |
| The numbered "Goals of the club" list | `content/goals.yml` |
| The three branches and their bullet points | `content/branches.yml` |
| The three core values | `content/values.yml` |
| E-board members and their roles | `content/team.yml` |
| Faculty advisors | `content/advisors.yml` |
| Events | `content/events.yml` |
| The "Upcoming goals" timeline | `content/roadmap.yml` |
| The Join Us page | `content/join.md` |
| Page banners (headline + subtitle at the top of each page) | the matching `.md` file |

---

## The two file types

### `.yml` files — lists of things

YAML is just `label: value`, one per line. Indentation matters — use **spaces,
never tabs**, and keep items lined up with the ones already there.

A list item starts with `- `:

```yaml
- name: Scientific Research
  accent: gold
  summary: >-
    Sharing and discussing the longevity research happening inside
    Cornell's own labs.
```

The `>-` means "the text on the following indented lines is one paragraph".
Use it for anything longer than a few words; it keeps lines short and readable.

**If a value contains a colon followed by a space, or starts with `#`, wrap it
in quotes:**

```yaml
title: "Longevity: what comes next"
```

### `.md` files — pages with prose

Each page file has two parts. The block between the `---` lines is settings
(headings, buttons, banner text). Everything after the closing `---` is the
page's body, written in Markdown:

```markdown
---
title: About
banner_heading: About the club
---

## A heading

A paragraph. **Bold** and *italic* work, and so do
[links](https://example.com) and bullet lists:

- first point
- second point
```

---

## Common tasks

### Fill an open e-board position

In `content/team.yml`, find the role and put the name after `holder:`.

```yaml
- role: Events Coordinator
  holder: Jamie Rivera        # was blank
```

The card stops saying "Position open" and the role disappears from the
"Open positions" list on the Join Us page — both update automatically.

### Add someone's photo

1. Put the image in `assets/img/team/` (a square crop around 400×400 works best).
2. Point at it in `content/team.yml`:

```yaml
  photo: team/jamie-rivera.jpg
```

Leave `photo:` blank and the site shows their initials in a circle instead —
which looks perfectly fine, so there is no rush.

### Add an event

In `content/events.yml`, add a block. There are two commented-out examples in
the file you can copy — delete the leading `# ` from each line.

```yaml
- title: Speaker Q&A — Aging Research at Cornell
  date: 2026-10-22
  time: 6:00 – 7:00 PM
  location: Biotechnology Building 101
  branch: Scientific Research
  link: https://forms.gle/your-rsvp-form
  description: >-
    A conversation with a Cornell lab working on the biology of aging.
```

`date` must be `YYYY-MM-DD`. Everything else is optional.

Events move from **Upcoming** to **Past events** on their own once the date
passes — you never have to move them by hand. When there are no upcoming
events, the page shows a friendly placeholder instead.

### Add a new e-board role

Copy an existing block in `content/team.yml`. `group:` decides which heading it
appears under — reuse an existing group name (`Leadership`, `Operations`,
`Branch Representatives`) or invent a new one, which will create a new section.

### Add or rename a page in the navigation

Edit the `nav:` list in `content/site.yml`. To add a genuinely new page you also
need a new `content/<name>.md` file; ask whoever set the site up, or copy
`content/branches.md` as a starting point.

### Change the colours

Don't, if you can avoid it — the palette is taken directly from the club's
title slide. If you must, the colours are defined once at the top of
`assets/css/site.css` under `:root`.

Card accents are chosen per item with `accent:`, which accepts:
`gold`, `green`, `blue`, `coral`, `yellow`.

---

## Rules of thumb

- **Leaving a value blank is safe.** `photo:` with nothing after it, or a
  deleted optional line, renders as nothing — never as an error or the word
  "None".
- **Deleting a whole item is safe.** Remove an advisor, a value, or a branch and
  the layout re-flows.
- **Adding items is safe.** A fourth branch or a fifth value will lay out fine.
- **Apostrophes are fine** in normal text. Only quote a value if it contains
  `: ` or begins with `#`.

## If the site doesn't update

Go to the **Actions** tab of the repository. A red ✗ next to the most recent run
means the build failed — click it to see why. It is almost always a YAML
indentation mistake, and the error names the file and line. Fix that line and
the site rebuilds itself.
