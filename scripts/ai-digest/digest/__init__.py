"""AI Daily Digest — Bedrock-powered RSS summarizer for Obsidian."""

from pathlib import Path

# Vault root: __file__ is scripts/ai-digest/digest/__init__.py → parents[3] is vault root.
VAULT_ROOT = str(Path(__file__).resolve().parents[3])
