# Set up Mohamed Waleed's GitHub profile

This is a real GitHub profile README package for **Mishostrange**. Everything displayed by README.md is Markdown, compatible HTML, a local SVG, PNG, or animated GIF. There is no JavaScript, iframe, website deployment, or third-party statistics image service.

## Publish

1. Create or open the public repository **Mishostrange/Mishostrange**. A public repository whose name matches the username is required for a profile README.
2. Upload the contents of this folder to the repository root, including the hidden `.github` folder. If a profile already exists, merge these files with it rather than replacing valuable content.
3. Commit to your default branch. In **Actions → Update profile**, run the workflow manually once. On a fresh repository, uploading the workflow and scripts also triggers a run.
4. The job requires `contents: write` only for committing generated files. If your account or organization restricts workflow writes, allow them for this repository. Branch protection may require reviewing and merging generated updates separately; this workflow never bypasses protection or force pushes.
5. Open [your profile](https://github.com/Mishostrange) and check the terminal, ASCII reveal, skills, and activity section. GitHub image caching can delay visible asset updates.

Schedule: daily at **04:17 UTC**. Manual runs are available. Schedule triggers run on the default branch and GitHub can delay or disable schedules in inactive public repositories. Push triggers are restricted to generator/configuration inputs. Generated commits cannot trigger a loop; only changed generated files are staged and committed.

## Configuration

`profile.json` contains the supplied username and configurable ASCII source, columns, frame count, frame rate, and random seed. `PROFILE_USERNAME` can override the username. For an unconfigured `YOUR_GITHUB_USERNAME` placeholder, the generator can infer the owner from `GITHUB_REPOSITORY` only when the repository is an actual `username/username` profile repo.

Project descriptions come directly from the supplied brief. `project_repositories` is a record of verified links (null means none supplied/verified). It does not automatically modify the README: after verifying a public repository exists and matches the described project, add its Markdown link to the corresponding project manually and update the record. Do not substitute guessed repository names. The football platform remains a concept unless evidence establishes a different status.

No personal portrait or reference recording was supplied. The included source is an original, fictional geometric cyber sentinel, explicitly labeled as such. To use a personal photo, place a source image inside assets, update `ascii.source`, and regenerate. Change the illustration disclaimer in `generate_ascii.py` and the README alt text only if that photo is actually your portrait. Do not commit a portrait you do not intend to publish.

## Local regeneration

Use Python 3.12 or later:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build.py --offline
python -m unittest discover -s tests -v
python scripts/validate.py
```

`--offline` builds visuals and uses a saved data snapshot when available. A first offline build displays unavailable statistics, not sample counts. For an API refresh, run `python scripts/build.py` without `--offline`. The workflow passes its temporary `GITHUB_TOKEN` as `GH_TOKEN`. Do not put tokens in configuration files, README, command arguments, or commits.

Public REST statistics can work without authentication, subject to a much lower rate limit. GraphQL is the preferred contribution source and requires an authenticated token. The workflow uses its built-in token for public queries. Without a token or when GraphQL fails, the generator reads the public GitHub calendar HTML. This fallback verifies a complete contiguous year, exact per-day tooltip counts, color levels, and an aggregate total before accepting the data. If GitHub changes the markup or either source cannot be verified, contributions become unavailable rather than estimated. No private repositories, event payloads, or secret data are fetched or stored. The calendar reflects GitHub's visibility and the user's contribution privacy settings.

```sh
python scripts/generate_terminal.py
python scripts/generate_ascii.py --source assets/cyber-source.png --columns 92 --frames 54 --fps 12
python scripts/generate_ascii.py --source assets/cyber-source.png --output assets/sentinel.webp
python scripts/generate_stats.py
```

The ASCII generator preserves source proportions using the font cell aspect ratio, converts luminance through a character ramp, reveals seeded falling-code transitions, and exports optimized GIF or animated WebP. GIF is used in the README for broad compatibility. Fixed palette and seed avoid color flicker and make regeneration deterministic. Source Code Pro is bundled under its embedded SIL Open Font License; see assets/fonts/LICENSE.txt.

## Data accuracy and failure behavior

- Repository count: public count from `/users/Mishostrange`.
- Stars: summed stars received by all public owned repositories, including forks.
- Languages: code bytes from each public owned non-fork repository's `/languages` endpoint. The displayed top six percentages are shares of those top six, not claims about personal proficiency.
- Contributions: `contributionsCollection.contributionCalendar` from GitHub GraphQL, or the strictly validated public GitHub calendar as a fallback; a rolling-year total, never a fabricated lifetime total. The snapshot records the source in `calendar_status`.
- Streak: consecutive nonzero calendar days, measured in UTC from the date of the snapshot, using yesterday if today is still empty. Limited to the calendar window; private activity visibility and GitHub's accounting rules apply.
- Recent activity: the last five returned public events. Events can be delayed, and GitHub does not provide an exhaustive activity history through this endpoint.

All network calls have timeouts; API retries are bounded and the public-calendar fallback makes one request. A failed core REST refresh retains the previous username-matched snapshot with a **STALE** label and its original timestamp. Without a snapshot, values are dashes. If both calendar sources fail validation, contribution data is unavailable. No tokens or API response bodies are logged. `assets/github-data.json` contains only normalized public data and a fetch timestamp.

## Compatibility and maintenance

Images have bounded widths and scale down within GitHub's content area. Skill cards wrap naturally rather than relying on a fixed-width table. Dark self-contained image panels are readable on both GitHub themes; surrounding Markdown follows the user's selected theme. Text alternatives and expandable static versions accompany animations. The terminal and ASCII GIFs loop smoothly with a final hold; contributions use a scanner accent that does not alter counts. `contribution-animation.svg` is an optional SMIL variant; README uses GIF because SVG animation support can differ between image renderers.

External actions are pinned to full verified commit SHAs for checkout v5.0.0 and setup-python v6.0.0. Review and update pins and Pillow deliberately. No pull-request event executes this write job. Authentication is scoped to the API generation step and the final Git push, with checkout credential persistence disabled. A concurrent human push causes a normal non-fast-forward rejection, preserving remote work; rerun after inspecting the change.

## Verification limits

`scripts/validate.py` verifies local references, SVG XML, complete GIF decoding, file budgets, and the lack of active content in the README. Unit tests exercise contribution streak boundaries, API failure retention, pagination, and escaping. These checks cannot prove GitHub's live image proxy behavior or a workflow run before uploading. Final verification is opening the published profile and checking a successful Actions run.

Official references: [GitHub profile README](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme), [GraphQL contribution calendar](https://docs.github.com/en/graphql/reference/objects#contributioncalendar), [checkout v5.0.0](https://github.com/actions/checkout/releases/tag/v5.0.0), [setup-python v6.0.0](https://github.com/actions/setup-python/releases/tag/v6.0.0).
