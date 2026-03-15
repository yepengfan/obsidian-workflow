"""Bedrock client using the Converse API."""

import boto3

from utils.config import MODELS, AWS_REGION

_bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def get_model_id(model_name: str) -> str:
    """Resolve short name ('sonnet', 'haiku') to full Bedrock model ID."""
    return MODELS[model_name]["id"]


def converse(
    model_name: str,
    messages: list[dict],
    system_prompt: str,
    max_tokens: int = 1024,
) -> dict:
    """Non-streaming Bedrock Converse call.

    Returns {"text": str, "input_tokens": int, "output_tokens": int}
    """
    response = _bedrock_client.converse(
        modelId=get_model_id(model_name),
        messages=messages,
        system=[{"text": system_prompt}],
        inferenceConfig={"maxTokens": max_tokens},
    )
    text = response["output"]["message"]["content"][0]["text"]
    usage = response["usage"]
    return {
        "text": text,
        "input_tokens": usage["inputTokens"],
        "output_tokens": usage["outputTokens"],
    }
