# Docs Site Content Roadmap

Tracks what's still missing or placeholder on the public docs site (`website/`), grouped by
what unblocks it. Update this alongside the site as items land — check items off or delete them
once done rather than letting it drift out of sync with the actual design.

## Blocking: needed before the site can go public at all

- [ ] **Push this repo to GitHub** and enable Pages (Settings → Pages → Source: "GitHub
      Actions"). The deploy workflow (`.github/workflows/deploy-docs.yml`) is already scaffolded
      and inert until this happens.
- [ ] **Fill in the real GitHub Pages URL** in `website/docusaurus.config.ts` — `url`,
      `organizationName`, and (if deploying to a project-page subpath) `baseUrl`. Currently
      placeholders.

## Near-term: fills in placeholders already on the live pages today

- [ ] **Design files download** (`website/docs/design-files.md` → Downloads section) — once the
      repo is public, publish gerbers/BOM/pick-and-place/STEP as a GitHub Release and link it
      here instead of the current "not yet available" placeholder.
- [ ] **Schematic PDF** (`website/docs/design-files.md` → Schematic section) — export and link a
      clean schematic PDF.
- [ ] **Current consumption numbers** (`website/docs/overview.md` → Power → Current consumption)
      — currently "not yet characterized." Fill in once bring-up/bench measurements exist,
      ideally broken out by state (deep sleep, Wi-Fi active, charging, etc.) the way PowerFeather-
      style hardware docs typically do — use real bring-up measurements rather than estimating.
- [ ] **Real board photos** — the site currently uses `kicad-cli`-rendered CAD images
      (`website/static/img/board-top.png` / `board-bottom.png`). Swap in or supplement with actual
      assembled-board photography once a unit exists.

## Later: new content, not just filling gaps

- [ ] **Getting Started guide** — first power-up steps, flashing firmware over native USB, LED
      status meanings, connecting a battery pack for the first time. This is genuinely new
      content (a "Guides" category alongside the existing "Hardware" one), not adapted from
      anything currently in `docs/`.
- [ ] **Physical dimensions & mounting page** — exact board outline dimensions and mounting-hole
      positions for enclosure/mechanical design. Not yet extracted from the PCB file.
- [ ] **Errata / hardware revision history** — currently only Rev A exists, so there's nothing to
      track yet, but this page should exist before a Rev B happens so changes have somewhere to
      land.
- [ ] **FAQ expansion** — `website/docs/notes.md` currently reflects known-gotchas identified
      during design review; real usage will surface more.

## Open decisions (not urgent, but worth deciding before the site gets wide traffic)

- Whether the site's own original prose needs an explicit license statement (separate from the
  Espressif CC BY-SA credit already on the Attribution page, which only covers that one vendored
  library, not writing original to this site).
- Whether to add site search (e.g. Algolia DocSearch) — only really useful once the site is
  public and indexed.
