import time
from typing import Optional, List

import llm
from llm.models import Attachment, Model


def get_llm_model(model_id: str) -> Model:
    """
    Centralized function to get an LLM model by ID.

    Args:
        model_id: The model identifier string

    Returns:
        Model: The LLM model instance

    Raises:
        ValueError: If the model_id is not found or invalid
    """
    try:
        return llm.get_model(model_id)
    except Exception as e:
        raise ValueError(f"Failed to load model '{model_id}': {e}")


def call_llm_with_retry(
    model: Model,
    prompt: str,
    attachments: Optional[List[Attachment]] = None,
    schema: Optional[dict] = None,
    max_retries: int = 2,
    retry_delay: int = 45,
) -> str:
    """
    Centralized function to call LLM with retry logic and rate limiting.

    Args:
        model: The LLM model to use
        prompt: The prompt text
        attachments: Optional list of attachments (for image processing)
        schema: Optional schema for structured output
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries

    Returns:
        str: The model's response text

    Raises:
        Exception: If all retry attempts fail
    """
    # Check if rate limiting is needed (non-ollama models)
    requires_rate_limit = "ollama" not in str(model).lower()

    for attempt in range(max_retries + 1):
        try:
            # Add rate limiting delay for non-ollama models
            if requires_rate_limit and attempt > 0:
                time.sleep(30)
            # Make the LLM call
            if schema:
                response = model.prompt(prompt, schema=schema)
            elif attachments:
                response = model.prompt(prompt, attachments=attachments)
            else:
                response = model.prompt(prompt)

            return response.text()

        except Exception as e:
            if attempt < max_retries:
                print(
                    f"LLM call failed (attempt {attempt + 1}), retrying in {retry_delay}s: {e}"
                )
                time.sleep(retry_delay)
                continue
            else:
                raise e

    raise Exception("LLM call failed after all retry attempts.")


def extract_text_from_image(
    model_id: str,
    image_path: str,
    prompt: str = "extract text from the handwriting and only return the text",
) -> str:
    """
    Centralized function for text extraction from images.

    Args:
        model_id: The LLM model ID to use for extraction
        image_path: Path to the image file
        prompt: The prompt for extraction (optional)

    Returns:
        str: Extracted text from the image
    """
    model = get_llm_model(model_id)
    attachments = [Attachment(path=image_path)]

    return call_llm_with_retry(model=model, prompt=prompt, attachments=attachments)
