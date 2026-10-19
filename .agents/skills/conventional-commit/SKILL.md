---
name: conventional-commit
description: Prompt and workflow for generating conventional commit messages. Use when writing commit messages to keep them standardized and in line with the Conventional Commits specification.
---

# Conventional Commit

Generate standardized, descriptive commit messages per the Conventional Commits
specification.

## Workflow

1. Run `git status` to review changed files.
2. Run `git diff` or `git diff --cached` to inspect changes.
3. Stage changes with `git add <file>`.
4. Construct the commit message using the structure below.
5. Commit: `git commit -m "type(scope): description"`.

## Message structure

```
type(scope): description

[optional body]

[optional footer]
```

- **type** (required) — one of:
  `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`,
  `chore`, `revert`
- **scope** (optional, recommended) — the area affected, in parentheses
- **description** (required) — short, imperative summary ("add", not "added")
- **body** (optional) — more detailed explanation
- **footer** (optional) — `BREAKING CHANGE: details`, or issue references

## Examples

```
feat(parser): add ability to parse arrays
fix(ui): correct button alignment
docs: update README with usage instructions
refactor: improve performance of data processing
chore: update dependencies
feat!: send email on registration (BREAKING CHANGE: email service required)
```

Reference: https://www.conventionalcommits.org/en/v1.0.0/#specification
