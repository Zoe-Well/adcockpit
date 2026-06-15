"""DeepSeek LLM initialization via langchain-openai."""
from langchain_openai import ChatOpenAI
from backend.app.core.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL


def get_llm(model: str = "deepseek-chat", temperature: float = 0.1) -> ChatOpenAI:
    """Create a DeepSeek ChatOpenAI instance compatible with Function Calling."""
    return ChatOpenAI(
        model=model,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=temperature,
    )
