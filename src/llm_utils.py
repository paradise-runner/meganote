import time
import json
from typing import Optional, List
from enum import Enum

import llm
from llm.models import Attachment, Model


class LLMModelType(Enum):
    """Enum for different LLM model types and their purposes."""

    TEXT_EXTRACTION = "text_extraction"
    METADATA_GENERATION = "metadata_generation"


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


def extract_text_from_image(
    model_id: str,
    image_path: str,
    prompt: str = "extract the handwriting and correct spelling",
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


def generate_tags_with_llm(
    model_id: str,
    text: str,
    max_tags: int = 3,
) -> List[str]:
    """
    Centralized function for tag generation using LLM.

    Args:
        model_id: The LLM model ID to use
        text: The text to generate tags for
        max_tags: Maximum number of tags to generate

    Returns:
        List[str]: List of generated tags
    """
    model = get_llm_model(model_id)
    prompt = f"Given this notebook text, provide a list of tags that serve as a theme category or primary subject with a maximum of {max_tags} tags possible. text: {text}"
    schema = llm.schema_dsl("tag,description", multi=True)

    response = call_llm_with_retry(model=model, prompt=prompt, schema=schema)

    resp_json = json.loads(response)
    return [tag["tag"] for tag in resp_json["items"]]


def generate_keywords_with_llm(
    model_id: str,
    text: str,
    max_keywords: int = 7,
) -> List[str]:
    """
    Centralized function for keyword generation using LLM.

    Args:
        model_id: The LLM model ID to use
        text: The text to generate keywords for
        max_keywords: Maximum number of keywords to generate

    Returns:
        List[str]: List of generated keywords
    """
    model = get_llm_model(model_id)
    prompt = f"Given this notebook text, provide a list of keywords that work as wiki-style links and are central to the content of the text to link relevant notes together with a maximum of {max_keywords} tags possible. text: {text}"
    schema = llm.schema_dsl("keyword,description", multi=True)

    response = call_llm_with_retry(model=model, prompt=prompt, schema=schema)

    resp_json = json.loads(response)
    return [kw["keyword"] for kw in resp_json["items"]]
