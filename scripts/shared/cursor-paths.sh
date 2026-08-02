#!/usr/bin/env bash
# Cursor CLI PATH helpers — keep search dirs in sync with cursor_paths.py

cursor_cli_search_dirs() {
  printf '%s\n' \
    "${HOME}/.local/bin" \
    "${HOME}/.cursor/bin" \
    "${HOME}/bin" \
    "${HOME}/.npm-global/bin" \
    "/usr/local/bin" \
    "/opt/homebrew/bin"
}

cursor_augment_path() {
  local extra="" dir
  while IFS= read -r dir; do
    extra="${extra:+$extra:}${dir}"
  done < <(cursor_cli_search_dirs)
  printf '%s:%s\n' "$extra" "${PATH:-}"
}

cursor_cli_available() {
  local saved_path
  saved_path="$(cursor_augment_path)"
  PATH="$saved_path" command -v agent >/dev/null 2>&1 \
    || PATH="$saved_path" command -v cursor-agent >/dev/null 2>&1
}
