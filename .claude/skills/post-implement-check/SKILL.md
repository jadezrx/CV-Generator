---
name: post-implement-check
description: Use once implementation work for a ticket/issue in this repo is functionally finished — checks that the commit is pushed and the tracking issue is closed before considering the ticket done. Trigger on "I'm done with this ticket", "issue X is implemented", "ready to wrap up", "finished issue #N", or any indication that coding work for a specific ticket has concluded. Do not trigger for general git status questions, mid-implementation checks, or tickets you have not been told are finished.
---

# Post-implement git hygiene

A ticket is not done when the code works — it is done when the commit is pushed and the tracking issue reflects that.

## Do this, in order

1. Run `git status`. If it reports the branch ahead of `origin/main`, run `git push`.
2. Run `gh issue view <ticket-number>`. If it is still OPEN, close it: `gh issue close <ticket-number>`.
3. Exception — do not push or close automatically if the ticket touches authentication, access control, public-facing routing, secrets/credentials, or anything the user has explicitly flagged as sensitive. In that case: commit locally only, report what's pending, and wait for explicit confirmation before push/close.

## Done when

`git status` shows no commits ahead of `origin` for this ticket (or an explicit, named exception), and `gh issue view <ticket-number>` shows CLOSED (or an explicit, named exception) — not just "I committed it."

## Reference — what counts as sensitive

Anything touching: authentication/authorization, secrets or environment credentials, or public routing changes affecting what unauthenticated users can reach. When in doubt, ask rather than assume it's routine.
