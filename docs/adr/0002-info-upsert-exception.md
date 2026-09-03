# `Info` is an upsert, not a create/update/delete list like the other entities

The Portfolio is a singleton (one deployment = one dataset). `ProfessionalExperience`, `Education`, `Skill`, `Language`, and `Project` are genuine lists, so their Create/Update/Delete routes are correctly keyed by `{id}`. `Info` should only ever have one row, but nothing currently enforces that — resubmitting the form creates a second row instead of editing the first.

**Decision**: `POST /info` becomes an upsert — it updates the existing row if one is present, and creates it otherwise. There is no `/info/{id}/edit` or `/info/{id}/update`; `Info` does not follow the per-entity `{id}`-scoped pattern used by every other model.

**Consequence**: `Info` is deliberately the odd one out in the routing table. A future reader comparing it to `/education/{id}/update` should not "fix" it to match — the asymmetry reflects that Info models a singleton, not a list.

Because `Info`'s fields are nullable, `GET /form` now pre-fills the Info section with the existing row's values when one exists (empty when none does) — without that, a blank resubmission would silently null out previously-saved fields under the upsert.
