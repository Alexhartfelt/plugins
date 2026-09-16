### Added

- `hello-retail-knowledge` answers "Hello Retail is not working" tickets with a script-loading
  walk: is the `<head>` snippet there, does the script load in the Network tab, and the usual
  reasons it does not (consent categories, blockers, JS-deferring optimizers, a theme update
  that dropped the snippet), and it names whose action each outcome is — a missing snippet is an
  ask to the customer to install it, with the snippet, the install guide and a re-check once they
  confirm. `qa-checklists` makes that the first Setup & Data check and stops the run there when the
  script is missing.
