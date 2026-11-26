# Releasing archsmith to npm

Two channels ship from this repo: the Claude Code plugin marketplace (no build; users track the git repo) and the npm package `archsmith`. The npm package is a copy of `bin/`, `skills/`, `agents/`, `commands/` and `.claude-plugin/`.

## One-time setup

1. **Claim the name.** `archsmith` is free on npm (checked 2026-11-26). If you prefer a scope, rename to `@nubeninja/archsmith` in `package.json` (needs an npm org) and update the README commands.
2. **First publish, by hand.** npm trusted publishing can only be configured for a package that already exists:
   ```
   npm login            # account with 2FA
   npm publish --access public
   ```
3. **Enable trusted publishing.** npmjs.com > package `archsmith` > Settings > Trusted Publisher > GitHub Actions: owner `nubeninja`, repo `archsmith`, workflow `release.yml`, environment `npm`. Then set "Require two-factor authentication and disallow tokens" so only the workflow can publish.
4. **GitHub settings.**
   - Settings > Environments > create `npm`; add required reviewers and restrict to tags `v*`.
   - Settings > Branch protection on `main`: require PR, the `CI` and `Security` checks, no force-push.
   - Settings > Code security: enable Dependabot alerts, secret scanning with push protection, private vulnerability reporting.
   - Settings > Rules: protect tags `v*` from deletion and update.

## Each release

1. Bump the version in **all three**: `package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`. CI (`npm run check:versions`) fails if they differ.
2. PR into `develop`, then `main`. Wait for CI and Security to pass.
3. Tag and push from `main`:
   ```
   git tag -s v0.3.0 -m "v0.3.0" && git push origin v0.3.0
   ```
4. The `Release` workflow checks the tag equals the manifest versions, runs tests, waits for approval on the `npm` environment, publishes with provenance, and creates the GitHub release with generated notes.
5. Verify:
   ```
   npm view archsmith version
   npm audit signatures            # inside a project that installed it
   npx archsmith@latest install --project   # smoke test in a scratch folder
   ```

## Rollback

- Within 72 hours a version can be unpublished; otherwise `npm deprecate archsmith@<bad> "use <good>"` and release a fixed patch version. Never reuse a version number.
- Plugin marketplace users get the repo's default branch, so revert on `main` as well.

## Notes

- Versioning: semver. New commands or options are minor; behaviour changes to existing commands are major once past 1.0.
- The weekly Security run catches new CVEs and rule updates between releases.
