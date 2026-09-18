# changelog.d — release notes, one file per PR

Changed something under `plugins/hello-retail-unmanaged/`? Add **a new file here**, named after
your branch: `changelog.d/pages-input-filters.md`. Do not edit `CHANGELOG.md` — the Release
workflow writes that file, and editing it is what used to make every second PR conflict.

A fragment is nothing but `###` sections and their bullets:

```markdown
### Fixed

- `pages-api` no longer tells you to omit `format`; the endpoint defaults to HTML, so a custom
  frontend must send `"json"` on every request.

### Changed

- `tracking-user-id` now covers what to do when a shopper revokes consent after already having
  a `hello_retail_id` cookie, not just the never-consented case.
```

Only `### Added`, `### Changed`, `### Fixed` and `### Removed`, and only the ones that apply.
No `##` version heading, no title, no prose outside a bullet.

Write for whoever installs the plugin: name the skill in backticks, say what is different in
its *behaviour*, two sentences at most. No file paths, PR numbers, commit SHAs or customer
data. Skip pure refactors and typo fixes — if nothing is different for the user, add no file.
The full house style is in `CLAUDE.md` → "Release notes".

See what the next release will say:

```
node scripts/changelog.mjs preview hello-retail-unmanaged
```

On merge, the Release workflow folds every fragment here into `CHANGELOG.md` under the
version it publishes, deletes the fragments, and uses that section as the GitHub Release
body. This README stays.
