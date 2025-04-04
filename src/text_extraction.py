import re
import os
import time

import llm
from llm.models import Attachment, Model

from src.supernote import (
    refresh_local_from_supernote,
)
from src.utilities import (
    diff_percent,
    show_diff,
    clean_text,
)
from src.utilities import (
    filter_out_unsynced_files,
)


def round_robbin_image_eval_llms(
    image_eval_llms, images_folder="test_images", output_folder="llm_roundtable"
):
    """
    This functions is used to test models and run a single image through each model and see which one gives the best results.

    The models are run in a round-robbin fashion, so that each model gets a chance to process the image.
    The results are saved to a file in the output_folder.

    """
    # get a list of all the .png files in the images folder
    print(f"Searching for .png files in the {images_folder} folder...")
    files = os.listdir(images_folder)
    test_image = files[0]

    llm_models = [
        model for model in llm.get_models() if model.model_id in image_eval_llms
    ]

    for model in llm_models:
        print(f"Extracting text from {test_image} using {model.model_id}")
        # extract the text from the image using the llm
        text = call_llm_for_extraction(
            model,
            images_folder=images_folder,
            notebook_page_img=test_image,
        )

        text = clean_text(
            text
        )  # clean up the text, make everything lowercase, and remove any extra spaces, new lines, or tabs
        output_file = f"{output_folder}/{model.model_id}.txt"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as file:
            file.write(text)


def validate_llm_image_eval(
    image_eval_llms,
    test_text_file="test_text_file.txt",
    eval_folder="llm_roundtable",
    debug=False,
):
    """
    This function is used to validate the results of the llm image evaluation.
    It will compare the results of each model and see which one is the best.
    The results are saved to a file in the eval_folder.
    The test_text_file.txt file is used to compare the results of each model.
    The test_text_file.txt file is the expected output of the the text extraction.

    image_eval_llms: list of llm model ids to test
    test_text_file: path to the file containing expected output
    eval_folder: folder where evaluation results are stored
    debug: if True, print the expected and actual output of the test
    """
    # open the test_text_file.txt file and read the text
    with open(test_text_file, "r") as file:
        test_text = file.read()

    # open the eval_folder and read the text from each file
    llm_models = [
        model for model in llm.get_models() if model.model_id in image_eval_llms
    ]

    failed_models = []
    passed_models = []

    for model in llm_models:
        with open(f"{eval_folder}/{model.model_id}.txt", "r") as file:
            model_text = file.read()

        test_text = clean_text(test_text)

        # compare the text from the model to the test text
        if model_text == test_text:
            print(f"✅✅✅ {model.model_id} passed the test! ✅✅✅")
            passed_models.append(model.model_id)
        else:
            print(f"❌❌❌ {model.model_id} failed the test! ❌❌❌")
            failed_models.append(
                {
                    "model": model.model_id,
                    "expected": test_text,
                    "actual": model_text,
                    "% diff": diff_percent(test_text, model_text),
                }
            )
            if debug:
                show_diff(test_text, model_text)

    print("\n")
    for model in passed_models:
        print(f"✅ Model: {model} had a 100% similarity to the expected text.")

    for model in failed_models:
        diff_percentage = model["% diff"]
        if diff_percentage < 80:
            emoji = "❌"  # Red X for very poor similarity (< 80%)
        elif diff_percentage < 90:
            emoji = "⚠️"  # Warning for poor similarity (80-90%)
        elif diff_percentage < 95:
            emoji = "⚡"  # Lightning for ok similarity (90-95%)
        elif diff_percentage < 98:
            emoji = "⭐"  # Star for good similarity (95-98%)
        else:
            emoji = "🔍"  # Magnifying glass for very close similarity (98-100%)

        print(
            f"{emoji} Model: {model['model']} had a {diff_percentage:.2f}% similarity to the expected text."
        )


def test_llm_image_eval(
    test_text_file="test_text_file.txt",
    eval_folder="llm_roundtable",
    fresh_sn_data_fetch=False,
    fresh_llm_data_fetch=True,
    debug=False,
):
    """
    This function is used to test the llm image evaluation."
    """
    if fresh_sn_data_fetch:
        # fetch the data from the supernote and sync it to the data folder
        refresh_local_from_supernote()

    image_eval_llms = [
        # "llama3.2-vision:latest",
        # "gemma3:12b",
        "gemma3:latest",
    ]

    if fresh_llm_data_fetch:
        # have an llm process the notes from pngs to markdown
        round_robbin_image_eval_llms(
            image_eval_llms, images_folder="test_images", output_folder=eval_folder
        )
    # validate the results of the llm image evaluation
    validate_llm_image_eval(
        image_eval_llms,
        test_text_file=test_text_file,
        eval_folder=eval_folder,
        debug=debug,
    )


def call_llm_for_extraction(
    model: Model,
    images_folder="test_images",
    notebook_page_img="test_image.png",
) -> str:
    """
    This function is used to call the llm for image evaluation.
    It will extract the text from the image and return the response.
    The model is the llm model to use for image evaluation.
    The images_folder is the folder where the images are stored.
    The notebook_page_img is the image to extract text from.

    """
    response = model.prompt(
        "extract text from the image",
        attachments=[Attachment(path=f"{images_folder}/{notebook_page_img}")],
    )
    return response.text()


def extract_text_from_images(
    images_folder="images",
    data_folder="data",
    output_folder="notes",
    image_eval_llm="gemma3:12b",
    synced_files=[],
):
    """
    This function is used to extract text from images using the llm.
    The images are stored in the images folder and the output is stored in the notes folder.
    The image_eval_llm is used to extract the text from the images.
    """
    # get a list of all the .png files in the images folder
    print(f"Searching for .png files in the {images_folder} folder...")
    files = filter_out_unsynced_files(
        folder=images_folder,
        synced_files=synced_files,
    )

    # Create an notes folder if it doesn't exist
    if not os.path.exists(output_folder):
        print(f"Creating output folder: {output_folder}")
        os.makedirs(output_folder)

    # get the directory structure of the data folder
    data_structure = {}
    for root, _, _ in os.walk(data_folder):
        # get the relative path of the folder
        relative_path = os.path.relpath(root, data_folder)
        # create a dictionary for the folder
        data_structure[relative_path] = []
        # get the files in the folder
        for file in os.listdir(root):
            # add the file to the folder
            data_structure[relative_path].append(file)

    model = llm.get_model(image_eval_llm)

    requires_rate_limit = False
    if "ollama" not in str(model).lower():
        requires_rate_limit = True

    # loop through the files and extract the text from each image
    for file in files:
        print(f"Extracting text from {file} using {image_eval_llm}")

        # add a 30 second delay between each image to avoid rate limiting
        if requires_rate_limit:
            time.sleep(30)
        # replace the .png with .note and remove the number after the last _
        expected_file_note_name = re.sub(r"_[0-9]+\.png$", ".note", file)
        # remove the images folder from the path
        expected_file_note_name = os.path.basename(expected_file_note_name)
        data_file_path = None
        for ds_path, ds_files in data_structure.items():
            if expected_file_note_name in ds_files:
                data_file_path = os.path.join(
                    data_folder, ds_path, expected_file_note_name
                )
                break
        if data_file_path is None:
            raise ValueError(f"File {file} not found in {images_folder} folder.")

        file_name = os.path.basename(file)
        # remove the .png extension from the file name
        output_file = os.path.join(output_folder, ds_path, f"{file_name[:-4]}.txt")
        # create the output folder if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        try:
            response = call_llm_for_extraction(
                model,
                images_folder=images_folder,
                notebook_page_img=file_name,
            )
        except Exception as e:
            print(f"Error extracting text from {file_name}: {e}")
            time.sleep(45)
            response = call_llm_for_extraction(
                model,
                images_folder=images_folder,
                notebook_page_img=file_name,
            )

        # save the response to a file
        with open(output_file, "w") as _file:
            # update the text to clean it up and remove any first line garbage
            text = response

            # clean up the text, make everything lowercase, and remove any extra spaces, new lines, or tabs
            text = clean_text(text, newline_replacement=False)

            _file.write(text)
