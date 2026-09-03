# CV-Generator

A single-page portfolio/CV builder: one person's data (profile, experience, education, skills, languages, projects) entered through a form and rendered as a portfolio page.

## Language

**Portfolio**:
The complete, singular set of CV data managed by one deployment: one `Info` record plus all `ProfessionalExperience`, `Education`, `Skill`, `Language`, and `Project` entries. There is exactly one Portfolio per deployment — no multi-profile or multi-user support.
_Avoid_: Profile (as a synonym for the whole dataset — reserve "profile" for `Info` specifically if needed), CV (used loosely in conversation, but "Portfolio" is the canonical term in code and routes).
