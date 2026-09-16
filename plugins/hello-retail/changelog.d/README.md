# changelog.d — release notes, one file per PR

Changed something under `plugins/hello-retail/`? Add **a new file here**, named after your
branch: `changelog.d/script-loading-triage.md`. Do not edit `CHANGELOG.md` — the Release
workflow writes that file, and editing it is what used to make every second PR conflict.

A fragment is nothing but `###` sections and their bullets:

```markdown
### Fixed

- `search-qa` no longer reports a false FAIL on price parity for shops that lazy-load prices.

### Changed

- `recom-developer` writes new designs as REVIEW drafts instead of leaving them unassigned,
  so they show up in the dashboard's draft list.
```

Only `### Added`, `### Changed`, `### Fixed` and `### Removed`, and only the ones that apply.
No `##` version heading, no title, no prose outside a bullet.

Write for whoever installs the plugin: name the skill in backticks, say what is different in
its *behaviour*, two sentences at most. No file paths, PR numbers, commit SHAs or customer
data. Skip pure refactors and typo fixes — if nothing is different for the user, add no file.
The full house style is in `CLAUDE.md` → "Release notes".

See what the next release will say:

```
npm run changelog
```

On merge, the Release workflow folds every fragment here into `CHANGELOG.md` under the
version it publishes, deletes the fragments, and uses that section as the GitHub Release
body. This README stays.
