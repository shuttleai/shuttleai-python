from pydantic import BaseModel


class CompletionTokensDetails(BaseModel):
    """
    Details about the tokens used in a completion request.
    """

    reasoning_tokens: int


class UsageInfo(BaseModel):
    """
    Common because will implement future text_completions (legacy) endpoint support in future
    """

    prompt_tokens: int
    # total_tokens: int
    completion_tokens: int
    total_tokens: int
    completion_tokens_details: CompletionTokensDetails | None = None
