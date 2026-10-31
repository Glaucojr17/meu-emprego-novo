"""Native CrewAI Bedrock integration for the synchronous application pipeline."""

import logging
import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from crewai.llms.providers.bedrock.completion import BedrockCompletion

logger = logging.getLogger(__name__)
TRANSIENT_ERRORS = {
    "ThrottlingException", "ServiceUnavailableException",
    "InternalServerException", "ModelNotReadyException",
}


class FallbackClient:
    """Retry only a failed API request, never replay already executed tools."""

    def __init__(self, client, fallback_model):
        self.client = client
        self.fallback_model = fallback_model

    def converse(self, **request):
        try:
            return self.client.converse(**request)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code not in TRANSIENT_ERRORS or not self.fallback_model:
                raise
            if request["modelId"] == self.fallback_model:
                raise
            logger.warning("Bedrock %s: switching from %s to %s", code,
                           request["modelId"], self.fallback_model)
            return self.client.converse(**{**request, "modelId": self.fallback_model})


class ProjectBedrockLLM(BedrockCompletion):
    fallback_model: str | None = None

    def _build_sync_client(self):
        # Explicit profile prevents unrelated environment credentials from taking
        # precedence over the project's restricted IAM identity.
        profile = os.getenv("AWS_PROFILE")
        if not profile:
            raise ValueError("Configure AWS_PROFILE for local Bedrock access")
        session = boto3.Session(profile_name=profile, region_name=self.region_name)
        client = session.client("bedrock-runtime", config=Config(
            read_timeout=300, connect_timeout=10,
            retries={"max_attempts": 3, "mode": "standard"},
        ))
        return FallbackClient(client, self.fallback_model)

    async def acall(self, *args, **kwargs):
        raise NotImplementedError("Use synchronous call() for the local Bedrock pipeline")
