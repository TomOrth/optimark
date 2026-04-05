# Contributing

## Conventional Commits
Optimark uses Conventional Commits so the commit history and future changelog output stay easy to scan.

Use this format:

```text
type(scope): short summary
```

Scope is optional:

```text
type: short summary
```

Examples:
- `feat(frontend): add protected route gate`
- `fix(api): return 404 for missing assignment`
- `docs(adr): document backend uv workspace topology`
- `chore(ci): add commit message validation`

Supported types:
- `feat`
- `fix`
- `docs`
- `style`
- `refactor`
- `perf`
- `test`
- `build`
- `ci`
- `chore`
- `revert`

## Pull Requests
If you use squash merges, GitHub will usually use the PR title as the final commit message. Keep PR titles in Conventional Commit format too.

Local commits are checked with a `commit-msg` hook, and CI also validates commit messages and PR titles.
