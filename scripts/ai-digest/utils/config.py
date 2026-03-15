"""Configuration and constants for AI Daily Digest."""

# Model configurations — only the models used by the digest pipeline.
MODELS = {
    "haiku": {
        "id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "input_cost_per_1k": 0.000125,
        "output_cost_per_1k": 0.000625,
        "name": "Claude Haiku 4.5",
    },
    "sonnet": {
        "id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "input_cost_per_1k": 0.003,
        "output_cost_per_1k": 0.015,
        "name": "Claude Sonnet 4",
    },
}

# AWS configuration
AWS_REGION = "us-east-1"
