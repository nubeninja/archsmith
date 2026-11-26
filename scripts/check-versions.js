// Fails if package.json, plugin.json and marketplace.json disagree on the version.
// With a tag argument (v1.2.3 or refs/tags/v1.2.3) it also checks the tag matches.
'use strict';
const read = (f) => JSON.parse(require('node:fs').readFileSync(f, 'utf8'));
const versions = {
  'package.json': read('package.json').version,
  '.claude-plugin/plugin.json': read('.claude-plugin/plugin.json').version,
  '.claude-plugin/marketplace.json': read('.claude-plugin/marketplace.json').plugins[0].version,
};
const tag = (process.argv[2] || '').replace(/^refs\/tags\/v?/, '').replace(/^v/, '');
if (tag) versions['git tag'] = tag;
const unique = new Set(Object.values(versions));
if (unique.size !== 1) {
  console.error('version mismatch:', versions);
  process.exit(1);
}
console.log(`all versions are ${[...unique][0]}`);
