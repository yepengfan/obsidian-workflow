"""CloudWatch custom metrics for Bedrock cost tracking."""

from datetime import datetime, timezone

import boto3

from utils.config import AWS_REGION

NAMESPACE = "BedrockCost"

_cw_client = boto3.client("cloudwatch", region_name=AWS_REGION)


def publish_metrics(
    model_id: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    caller: str = "ai-daily",
) -> None:
    """Send one Bedrock invocation's metrics to CloudWatch."""
    ts = datetime.now(timezone.utc)
    dims = [
        {"Name": "ModelId", "Value": model_id},
        {"Name": "Caller", "Value": caller},
    ]

    _cw_client.put_metric_data(
        Namespace=NAMESPACE,
        MetricData=[
            {
                "MetricName": "InputTokens",
                "Dimensions": dims,
                "Timestamp": ts,
                "Value": input_tokens,
                "Unit": "Count",
            },
            {
                "MetricName": "OutputTokens",
                "Dimensions": dims,
                "Timestamp": ts,
                "Value": output_tokens,
                "Unit": "Count",
            },
            {
                "MetricName": "InferredCost",
                "Dimensions": dims,
                "Timestamp": ts,
                "Value": cost_usd,
                "Unit": "None",
            },
        ],
    )
