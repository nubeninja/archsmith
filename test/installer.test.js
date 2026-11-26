'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { run } = require('../bin/archsmith.js');

const env = () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'archsmith-'));
  const logs = [];
  return { home, cwd: home, out: (m) => logs.push(m), err: (m) => logs.push(m), logs };
};

test('installs the skill for claude by default', () => {
  const e = env();
  assert.strictEqual(run(['install'], e), 0);
  assert.ok(fs.existsSync(path.join(e.home, '.claude/skills/archsmith/SKILL.md')));
  assert.ok(!fs.existsSync(path.join(e.home, '.claude/skills/archsmith/scripts/__pycache__')));
});

test('refuses to overwrite without --force, replaces with it', () => {
  const e = env();
  assert.strictEqual(run(['install', 'codex'], e), 0);
  assert.strictEqual(run(['install', 'codex'], e), 1);
  assert.strictEqual(run(['install', 'codex', '--force'], e), 0);
});

test('rejects unknown tools, options and prototype keys', () => {
  const e = env();
  assert.strictEqual(run(['install', 'nope'], e), 2);
  assert.strictEqual(run(['install', 'toString'], e), 2);
  assert.strictEqual(run(['install', '--bogus'], e), 2);
  assert.strictEqual(run([], e), 2);
});

test('--project installs under cwd', () => {
  const e = env();
  assert.strictEqual(run(['install', 'cursor', '--project'], e), 0);
  assert.ok(fs.existsSync(path.join(e.cwd, '.cursor/skills/archsmith/SKILL.md')));
});
