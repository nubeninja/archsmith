#!/usr/bin/env node
// Installs the archsmith skill into an AI coding tool's skills folder.
// Usage: npx archsmith install [claude|codex|cursor|agents] [--project] [--force]
// No dependencies, no network access. It never overwrites unless --force is given.
'use strict';
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const TOOLS = { claude: '.claude', codex: '.codex', cursor: '.cursor', agents: '.agents' };
const pkg = require('../package.json');

function usage() {
  return `archsmith ${pkg.version}

Usage: archsmith install [${Object.keys(TOOLS).join('|')}] [--project] [--force]

  install   copy the skill to <home>/.<tool>/skills/archsmith (default tool: claude)
  --project use the current directory instead of your home directory
  --force   replace an existing install

For Claude Code you can also use the plugin marketplace:
  /plugin marketplace add nubeninja/archsmith
  /plugin install archsmith@nubeninja`;
}

function run(argv, env = {}) {
  const home = env.home || os.homedir();
  const cwd = env.cwd || process.cwd();
  const out = env.out || ((m) => console.log(m));
  const err = env.err || ((m) => console.error(m));
  const flags = argv.filter((a) => a.startsWith('-'));
  const pos = argv.filter((a) => !a.startsWith('-'));

  if (flags.includes('--version') || flags.includes('-v')) { out(pkg.version); return 0; }
  if (!pos.length || flags.includes('--help') || flags.includes('-h')) { out(usage()); return pos.length ? 0 : 2; }
  const unknown = flags.filter((f) => !['--project', '--force'].includes(f));
  if (unknown.length) { err(`unknown option: ${unknown[0]}`); return 2; }
  if (pos[0] !== 'install' || pos.length > 2) { err(usage()); return 2; }

  const tool = pos[1] || 'claude';
  if (!Object.hasOwn(TOOLS, tool)) { err(`unknown tool: ${tool}`); return 2; }
  const base = flags.includes('--project') ? cwd : home;
  const dest = path.join(base, TOOLS[tool], 'skills', 'archsmith');
  const src = path.join(__dirname, '..', 'skills', 'archsmith');

  if (fs.existsSync(dest)) {
    if (!flags.includes('--force')) { err(`${dest} already exists; use --force to replace it.`); return 1; }
    fs.rmSync(dest, { recursive: true });
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.cpSync(src, dest, {
    recursive: true,
    filter: (p) => !p.split(path.sep).includes('__pycache__'),
  });
  out(`installed to ${dest}`);
  return 0;
}

if (require.main === module) process.exitCode = run(process.argv.slice(2));
module.exports = { run };
