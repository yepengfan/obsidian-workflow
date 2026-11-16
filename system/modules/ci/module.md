---
module: ci
label: "Continuous integration"
type: utility
status: active
enabled: true
created: 2026-11-17
updated: 2026-11-17
depends_on: []
requires:
  cli: [node, python3]
  python: ">=3.13"
commands: []
templates: []
scripts: []
hooks: []
folders: [.github/]
config_files: [.github/workflows/tests.yml, pytest.ini, requirements-ci.in, requirements-ci.txt]
tags: [system/module]
---

# Continuous integration

## Overview

GitHub Actions runs the JavaScript and Python function tests for pull requests and pushes to main. Tests use fixtures and temporary files, independently of private vault content and external service credentials.

## Architecture

- `.github/workflows/tests.yml`: test jobs, runtime versions, and timezone coverage.
- `pytest.ini`: Python test discovery and imports for the existing script layout.
- `requirements-ci.in` and generated `requirements-ci.txt`: pinned Python test dependencies.
- `README.md`: local commands and CI coverage.

## Quick start

Open a pull request and review the `Function tests` checks. A failing test fails its job. Merge remains a human action.

## Configuration

The workflow has read-only repository access, version-pinned actions, timeouts, and cancellation of obsolete runs. The module registry describes CI; disabling this manifest alone does not turn off GitHub Actions. Edit the workflow or GitHub Actions settings to change execution.
