#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const PACKAGE_ROOT = path.resolve(__dirname, "..");
const DEFAULT_OUT = path.join(".forsy", "trace-skill");
const FILES_TO_COPY = [
  {
    source: path.join(PACKAGE_ROOT, "skill.md"),
    target: "skill.md",
  },
  {
    source: path.join(PACKAGE_ROOT, "schema", "forsy_trace_schema_v0_1.json"),
    target: path.join("schema", "forsy_trace_schema_v0_1.json"),
  },
];

function printHelp() {
  console.log(`Forsy Trace Skill CLI

Usage:
  forsy-trace-skill init [--out <path>] [--force]

Commands:
  init          Copy the open Forsy Trace Skill and schema into this project.

Options:
  --out <path>  Output directory. Defaults to ${DEFAULT_OUT}
  --force       Overwrite existing copied files.
  -h, --help    Show this help text.

This installer is local-only. It does not call external services and does not submit traces anywhere.`);
}

function fail(message) {
  console.error(`Error: ${message}`);
  process.exitCode = 1;
}

function parseArgs(argv) {
  const args = {
    command: null,
    out: DEFAULT_OUT,
    force: false,
    help: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "-h" || arg === "--help") {
      args.help = true;
    } else if (arg === "--force") {
      args.force = true;
    } else if (arg === "--out") {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) {
        throw new Error("--out requires a path.");
      }
      args.out = value;
      index += 1;
    } else if (!args.command) {
      args.command = arg;
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  return args;
}

function assertReadableSourceFiles() {
  for (const file of FILES_TO_COPY) {
    if (!fs.existsSync(file.source)) {
      throw new Error(`Installer source file is missing: ${path.relative(PACKAGE_ROOT, file.source)}`);
    }
  }
}

function copyFile(source, target, force) {
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(source, target);
}

function initProject(options) {
  assertReadableSourceFiles();

  const outputRoot = path.resolve(process.cwd(), options.out);
  const targets = FILES_TO_COPY.map((file) => ({
    ...file,
    targetPath: path.join(outputRoot, file.target),
  }));
  const existingTargets = targets.filter((file) => fs.existsSync(file.targetPath));
  if (existingTargets.length > 0 && !options.force) {
    const paths = existingTargets.map((file) => path.relative(process.cwd(), file.targetPath)).join(", ");
    throw new Error(`${paths} already exist. Re-run with --force to overwrite them.`);
  }

  const copied = [];

  for (const file of targets) {
    copyFile(file.source, file.targetPath, options.force);
    copied.push(path.relative(process.cwd(), file.targetPath));
  }

  console.log("Forsy Trace Skill installed.");
  console.log("");
  console.log(`Output: ${path.relative(process.cwd(), outputRoot) || "."}`);
  console.log("");
  console.log("Copied:");
  for (const file of copied) {
    console.log(`  - ${file}`);
  }
  console.log("");
  console.log("Next steps:");
  console.log("  1. Read the installed skill.md before capturing traces.");
  console.log("  2. Use the schema JSON as the local reference for structured agent work traces.");
  console.log("  3. Keep trace collection local unless you explicitly build your own export workflow.");
}

function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    fail(error.message);
    return;
  }

  if (args.help || !args.command) {
    printHelp();
    return;
  }

  if (args.command !== "init") {
    fail(`Unknown command: ${args.command}`);
    console.error("");
    printHelp();
    return;
  }

  try {
    initProject(args);
  } catch (error) {
    fail(error.message);
  }
}

main();
