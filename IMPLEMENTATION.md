# Implementation and verification

Built for **Mishostrange** from the profile owner's supplied brief. No existing local repository or Git remote was present; all deliverables were created in a new folder without overwriting existing work. The reference recording and a personal portrait were not attached, so the ASCII visual is an original generic cyber sentinel, explicitly labeled as fictional.

## Delivered

- GitHub-compatible README with a terminal header, ASCII reveal, six skill cards, four project descriptions, statistics, contributions, and recent-activity block.
- Terminal GIF: sequential typing, cursor blink, subtle glow, final hold, and static PNG/SVG fallbacks.
- ASCII GIF: source image, aspect-preserving character conversion, seeded matrix reveal, fixed palette, and static PNG. Generator supports GIF/WebP export and a replacement source photo.
- Contribution GIF: authentic daily cells with a cyan/green scanner accent; static PNG/SVG and optional animated SVG.
- Public GitHub API statistics, a normalized data snapshot, graceful unavailable/stale handling, and a strict public-calendar fallback when GraphQL is unavailable.
- Daily/manual workflow, full-SHA action pins, scoped credentials, default-branch restriction, concurrency control, changed-file commits, and no generated-commit loop.
- Setup instructions, bundled licensed font, asset validator, and ten data-handling tests.

## Verified data

The delivered snapshot contains **21 public repositories**, **1 received star**, and **36 contributions in GitHub's rolling-year public calendar**. The 366 dated calendar cells were parsed from GitHub and their sum matched its displayed total. Language sizes came from public non-fork repository language endpoints; no profile statistics were invented. Empty public events are shown as no returned recent events, rather than fictional activity.

The BMO link was verified against the public [BMO11 README](https://github.com/Mishostrange/BMO11). The other three project descriptions remain unlinked because matching public repositories were not established. The football platform is explicitly a project concept. Supplied project descriptions and the owner's stated role are not presented as independently certified accomplishments.

## Local validation

Ten tests passed for streak boundaries, repository pagination, language counting, API failures, snapshot identity, text escaping, calendar totals, calendar alignment, and changed/incomplete calendar markup. All fourteen referenced README images exist. SVG XML and safety checks passed. Every GIF frame decoded successfully, all GIFs loop, and each is below the 3 MB per-file budget.

Approximate animation sizes: terminal 68 KiB, ASCII reveal 845 KiB, contribution scanner 28 KiB. Combined animation payload is below 1 MiB. Python generators ran successfully using Pillow 12.3.0. A static visual contact sheet accompanies the package for review; it is not a second website.

## Remaining deployment step

This package has not been pushed to GitHub. Upload its contents, including `.github`, to the public **Mishostrange/Mishostrange** repository root and run **Actions → Update profile**. Live GitHub rendering, image-cache behavior, and the hosted workflow require verification after uploading. The scripts and workflow are included and tested locally; no claim is made that the hosted workflow has already run.
