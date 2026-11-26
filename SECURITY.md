# Security policy

## Reporting a vulnerability

Please use GitHub's private reporting: **Security > Report a vulnerability** on https://github.com/nubeninja/archsmith. Do not open a public issue. Expect a first reply within 5 working days.

## Supported versions

Only the latest published version gets fixes.

## What the project does to stay safe

- No runtime dependencies. The npm package has no `postinstall` or other lifecycle scripts; the installer only runs when you call `npx archsmith install`.
- Every CI run: CodeQL (JavaScript, Python, Actions), Trivy (vulnerabilities, secrets, misconfiguration, fails on HIGH/CRITICAL), gitleaks over full history, zizmor on the workflows, and dependency review on pull requests. A weekly scheduled scan also runs.
- All third-party GitHub Actions are pinned to commit SHAs and kept current by Dependabot (with a 7-day cooldown).
- Workflows default to no permissions and grant them per job.
- Releases publish through npm trusted publishing (OIDC) with provenance. No long-lived npm token is stored in the repo.
