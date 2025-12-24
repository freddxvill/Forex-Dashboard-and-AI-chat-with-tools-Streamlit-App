from utils.llm_agent import get_llm_response
import unittest
from unittest.mock import patch, MagicMock

class TestLLMAgent(unittest.TestCase):
    def test_provider_switch(self):
        config = {
            "provider": "Gemini",
            "gemini_key": "dummy_key",
            "av_key": "dummy_av"
        }
        # We don't want to actually call the API, just check if it initializes and tries to call
        with patch('langchain_classic.agents.AgentExecutor.invoke') as mock_invoke:
            mock_invoke.return_value = {"output": "Mocked response"}
            response = get_llm_response("Test prompt", config)
            self.assertEqual(response, "Mocked response")

    def test_missing_av_key(self):
        config = {
            "provider": "Gemini",
            "gemini_key": "dummy_key",
            "av_key": None
        }
        # In our implementation, we set ALPHA_VANTAGE_API_KEY = av_key
        # Tools will fail if key is None
        from utils.llm_agent import call_api_tool
        import utils.llm_agent
        utils.llm_agent.ALPHA_VANTAGE_API_KEY = None
        res = call_api_tool("FX_DAILY", from_symbol="EUR", to_symbol="USD")
        self.assertIn("error", res)

if __name__ == "__main__":
    unittest.main()
