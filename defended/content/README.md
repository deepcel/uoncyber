# Training module content

The training modules live here as Markdown files, one file per module, so they are versioned in git
and can be loaded into any database with one command.

```
content/modules/
  01-introduction-to-cyber-security.md
  02-cyber-security-attacks-and-threats.md
  03-security-domains.md
  04-mitigation-and-defensive-controls.md
  05-prevention-best-practices-zero-trust.md
  pathway.md                      <- the pathway that groups the modules, in file-name order
```

## Loading the modules

From the `defended/` folder, with the virtual environment active and the database migrated:

```
python manage.py migrate
python manage.py load_modules --dry-run     # check the files, change nothing
python manage.py load_modules               # create or update the modules
```

- New modules are owned by the first ADMIN user. Use `--owner <username>` to choose someone else.
  If there is no admin yet, run `python manage.py createsuperuser` first.
- Modules are loaded as PUBLISHED. Use `--draft` to load them as drafts.
- If a module with the same `slug` already exists but was made by hand in the app, the command stops
  without changing anything, because loading would replace that module's sections. Change the slug
  in the file to load alongside it, or add `--force` to overwrite it.
- It is safe to run again after editing a file: modules are matched by `slug` and updated in place.
  Learners keep their section progress, and quiz questions that already appear in someone's results
  are deactivated (not deleted) when changed, so past results stay intact.

## File format

~~~markdown
---
title: Introduction to Cyber Security
slug: introduction-to-cyber-security       # unique, lowercase-with-hyphens; never change it once loaded
category: Fundamentals
summary: One line shown on the module card.
pass_mark: 80                              # optional settings below
estimated_minutes: 40
---

Module description: plain text shown on the module page.

## 1.1 First section title
Each "## " heading starts a new section, shown as its own page.
Section text is Markdown: **bold**, lists, [links](https://example.com), tables, ### sub-headings,
and images with ![alt text](https://example.com/picture.png).

A YouTube link on its own line becomes an embedded video.

### Try it: an exercise
Interactive tasks go in the section, with the answer hidden behind a "Show answer" button:

```answer
1. Confidentiality
2. Integrity
```

## 1.2 Next section
...

# Knowledge check

### Question text goes here?
- [ ] A wrong choice
- [x] The right choice
- [ ] Another wrong choice
Explanation: Optional; shown to learners after they submit.
~~~

Quiz rules: every question needs at least two choices and at least one `[x]`. One `[x]` makes a
single-answer question; several make a multiple-answer question (all correct choices must be picked).

Optional front-matter settings: `pass_mark`, `estimated_minutes`, `max_attempts`,
`time_limit_minutes`, `questions_per_attempt`, `shuffle_questions` (true/false),
`self_enroll_allowed` (true/false).

`<!-- comments -->` are for reviewers and are never shown to learners. Search for `REVIEW:` to find
content questions that still need a decision.
