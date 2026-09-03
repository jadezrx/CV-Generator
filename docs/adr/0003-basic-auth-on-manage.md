# HTTP Basic Auth protects `/manage`

ADR-0001 makes `/` the public, shareable portfolio view. Existing-entry management (Modifier/Supprimer) lives at `/manage`; creating new entries stays at `/form`, kept separate rather than merged into `/manage`. No route in this app has ever had authentication. Left that way, `/manage` and `/form` would let anyone who discovers or guesses either URL edit, delete, or add to the portfolio's data — a real risk once `/` is a link meant to be shared (e.g. with recruiters), and `/manage` stays linked from it.

**Decision**: Protect both `/manage` and `/form`, and every route under them (edit forms, create/update/delete routes), with HTTP Basic Auth. It's the minimal mechanism available without adding a session/login system, user model, or password storage.

**Considered and rejected**: session-based login with a user model and password hashing (disproportionate for a single-operator tool); leaving `/manage` unauthenticated (rejected once `/` — and its link to `/manage` — became public by design, per ADR-0001/Q8).
