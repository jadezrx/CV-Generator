## Agent skills

### Issue tracker

Issues live in GitHub Issues for `jadezrx/CV-Generator`, managed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

### `/implement` workflow

- At the end of every `/implement`, always finish with: `git push`, then verify with `gh issue view <number>` that the issue closed properly — if not, close it with `gh issue close`.
- Exception: for tickets #9 and #10 (and any future ticket touching authentication or public/manage routing), do **not** push and do **not** auto-close the issue — local commit only, then wait for explicit user confirmation before pushing.
