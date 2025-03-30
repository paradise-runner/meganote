import os
import re
import json
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import llm
from llm.models import Model
from tqdm import tqdm

from src.utilities import (
    filter_out_unsynced_files,
)

# TODO: LLM Named Entity Recognition + Management
# TODO: LLM Action Item Finding + Management
# TODO: LLM Note/Folder Level Summaries


def get_file_tags(file: str) -> list:
    """
    Get all tags from the text.
    """

    with open(file, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Extract the YAML front matter section
    front_matter_match = re.search(r"---\s*(.*?)\s*---", text, re.DOTALL)
    if not front_matter_match:
        return []
    
    front_matter = front_matter_match.group(1)
    
    # Find all tag entries with proper YAML list format
    tag_lines = re.findall(r"^\s*-\s*(.*)\s*$", front_matter, re.MULTILINE)
    
    # Process each tag, removing potential whitespace
    tags = []
    for line in tag_lines:
        line_tags = [tag.strip() for tag in line.split(",") if tag.strip()]
        tags.extend(line_tags)
    
    return tags


def get_folder_tags_multi_threaded(
    folder: str,
): 
    """
    Get all tags from the text.
    """

    # list all the files in the folder
    files = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename.endswith(".txt"):
                files.append(os.path.join(root, filename))

    with ThreadPoolExecutor() as executor:
        # Use partial to pass the folder argument to get_file_tags
        func = partial(get_file_tags)
        tags_list = list(tqdm(executor.map(func, files), total=len(files)))
    # flatten the list of tags
    tags = [tag for sublist in tags_list for tag in sublist]
    # remove duplicates

    tags = list(set(tags))

    return tags


def generate_metadata(
    extracted_data: str,
    metadata_model_id: Model,
    synced_files: list = [],
):
    model = llm.get_model(metadata_model_id)

    if not os.path.exists(extracted_data):
        raise FileNotFoundError(f"Directory {extracted_data} does not exist.")

    # list all the files in the extracted_data folder
    files = filter_out_unsynced_files(
        folder=extracted_data,
        synced_files=synced_files,
    )

    print(f"Found {len(files)} files to process.")

    all_tags = get_folder_tags_multi_threaded(extracted_data)
    print(f"Found {len(all_tags)} unique tags in the folder.")
    # print the tags
    print("Tags found:")
    for tag in all_tags:
        print(f"- {tag}")

    for file in files:
        print(f"Generating metadata for {file}...")
        # read the file in as a string
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            original_text = text[:]
        if not text:
            print(f"Skipping empty file: {file}")
            continue
        # Get tag recommendations
        tag_recommendations = generate_tags(text, model)

        # Get keyword recommendations using the original text
        keyword_recommendations = generate_keywords(text, model)

        if keyword_recommendations is None:
            pass
            # print("Keywords already exist in the file.")
        else:
            # TODO: If tags have already been generated, but not keywords, this will mark tags as keywords
            # Apply keyword recommendations to the text with tags
            for kw in keyword_recommendations:
                text = re.sub(rf"\b{kw}\b", f"[[{kw}]]", text)

        if tag_recommendations is None:
            final_text = text
        else:
            # Apply tag recommendations
            tags_text = "\n".join([f"- {tag}" for tag in tag_recommendations])

            # Combine the tags and keywords into a single string
            final_text = f"---\ntags:\n{tags_text}\n---\n{text}"

        if final_text != original_text:
            # Write the updated text back to the file
            with open(file, "w", encoding="utf-8") as f:
                f.write(final_text)


# def call_llm_for_tags_update(text, metadata_model) -> list:
#     response = metadata_model.prompt(
#         f"Given this notebook text, provide a list of tags that serve as a theme, category or subject. If there are already tags, assume a high bar for adding new ones and bias towards keeping the list the same. text: {text}",
#         schema=llm.schema_dsl("tag,description", multi=True),
#     )
#     resp_json = json.loads(response.text())
#     return [tag["tag"] for tag in resp_json["items"]]


def call_llm_for_tags_generation(text, metadata_model) -> list:
    response = metadata_model.prompt(
        f"Given this notebook text, provide a list of tags that serve as a theme category or primary subject with a maximum of 3 tags possible. All tags should be one to three hyphenated words. text: {text}",
        schema=llm.schema_dsl("tag,description", multi=True),
    )
    resp_json = json.loads(response.text())
    return [tag["tag"] for tag in resp_json["items"]]


# def call_llm_for_keywords_update(text, metadata_model) -> list:
#     response = metadata_model.prompt(
#         f"Given this notebook text, provide a list of keywords that work as backlinks to link relevant notes together. If there are already keywords, assume a high bar for adding new ones and bias towards keeping the list the same. text: {text}",
#         schema=llm.schema_dsl("keyword,description", multi=True),
#     )
#     resp_json = json.loads(response.text())
#     return [kw["keyword"] for kw in resp_json["items"]]


def call_llm_for_keywords_generation(text, metadata_model) -> list:
    response = metadata_model.prompt(
        f"Given this notebook text, provide a list of keywords that work as wiki-stle links and are central to the content of the text to link relevant notes together with a maximum of 7 tags possible. text: {text}",
        schema=llm.schema_dsl("keyword,description", multi=True),
    )
    resp_json = json.loads(response.text())
    return [kw["keyword"] for kw in resp_json["items"]]


def generate_tags(
    text: str,
    metadata_model: Model,
):
    # find the tags in the file
    tags = re.findall(r"tags:\s*-\s*(.*)", text, re.MULTILINE)

    # either generate new tags or update the existing tags
    if tags:
        recommendation = None
    if not tags:
        # generate new tags
        recommendation = call_llm_for_tags_generation(text, metadata_model)

    return recommendation


def generate_keywords(
    text: str,
    metadata_model: Model,
) -> Optional[list[str]]:
    # find the keywords in the file
    keywords = re.findall(r"\[\[(.*?)\]\]", text)
    if keywords:
        # update the existing keywords
        recommendation = None
    else:
        # generate new keywords
        recommendation = call_llm_for_keywords_generation(text, metadata_model)

    return recommendation
