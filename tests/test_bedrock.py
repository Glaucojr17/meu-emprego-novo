import os
import unittest
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError
from src.bedrock_llm import FallbackClient, ProjectBedrockLLM
from src.llm_factory import get_llm


def error(code):
    return ClientError({"Error": {"Code": code, "Message": "test"}}, "Converse")


class BedrockTests(unittest.TestCase):
    def test_fallback_preserves_tool_history(self):
        client = Mock()
        client.converse.side_effect = [error("ThrottlingException"), {"output": "ok"}]
        request = {"modelId": "opus", "messages": [{"role": "user", "content": [
            {"toolResult": {"toolUseId": "saved", "content": [{"text": "saved"}]}}
        ]}], "toolConfig": {"tools": []}}
        self.assertEqual(FallbackClient(client, "sonnet").converse(**request), {"output": "ok"})
        self.assertEqual(client.converse.call_args.kwargs, {**request, "modelId": "sonnet"})
        self.assertEqual(request["modelId"], "opus")

    def test_permanent_errors_do_not_fallback(self):
        for code in ("AccessDeniedException", "ValidationException", "ResourceNotFoundException"):
            with self.subTest(code=code):
                client = Mock()
                client.converse.side_effect = error(code)
                with self.assertRaises(ClientError):
                    FallbackClient(client, "sonnet").converse(modelId="opus")
                self.assertEqual(client.converse.call_count, 1)

    def test_fallback_failure_propagates_once(self):
        client = Mock()
        client.converse.side_effect = error("ServiceUnavailableException")
        with self.assertRaises(ClientError):
            FallbackClient(client, "sonnet").converse(modelId="opus")
        self.assertEqual(client.converse.call_count, 2)

    def test_no_fallback_for_extraction(self):
        client = Mock()
        client.converse.side_effect = error("ThrottlingException")
        with self.assertRaises(ClientError):
            FallbackClient(client, None).converse(modelId="deepseek.v3.2")
        self.assertEqual(client.converse.call_count, 1)

    @patch.object(ProjectBedrockLLM, "_build_sync_client", return_value=Mock())
    def test_factory_routes_and_preserves_tool_support(self, build):
        with patch.dict(os.environ, {"AWS_PROFILE": "test"}, clear=True):
            main = get_llm("bedrock")
            extraction = get_llm("bedrock", purpose="extraction")
            self.assertEqual(main.model_id, "us.anthropic.claude-opus-4-6-v1")
            self.assertEqual(main.fallback_model, "us.anthropic.claude-sonnet-4-6")
            self.assertTrue(main.supports_function_calling())
            self.assertFalse(main.stream)
            self.assertEqual(extraction.model_id, "deepseek.v3.2")
            self.assertIsNone(extraction.fallback_model)

    def test_missing_profile_fails(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "AWS_PROFILE"):
                get_llm("bedrock")

    @patch("src.bedrock_llm.boto3.Session")
    def test_explicit_profile_is_used(self, session):
        with patch.dict(os.environ, {"AWS_PROFILE": "restricted"}):
            get_llm("bedrock")
        session.assert_called_once_with(profile_name="restricted", region_name="us-east-1")


if __name__ == "__main__":
    unittest.main()
