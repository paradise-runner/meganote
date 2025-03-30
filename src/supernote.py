import os
import re
import json
import requests
import hashlib
import shutil
import concurrent.futures

from supernotelib.cmds.supernote_tool import convert_to_png
from supernotelib.parser import load_notebook

from src.utilities import (
    ConversionArgs,
    filter_out_unsynced_files,
)

# Default values - will be overridden by parameters
DEFAULT_SUPERNOTE_IP = "192.168.1.139"
DEFAULT_SUPERNOTE_PORT = 8089


def get_supernote_url(ip=DEFAULT_SUPERNOTE_IP, port=DEFAULT_SUPERNOTE_PORT):
    supernote_ip_address = f"http://{ip}:{port}"
    supernote_root = "/Note"
    return supernote_ip_address, f"{supernote_ip_address}{supernote_root}"


def get_supernote_json(response_text) -> dict:
    # extract the json string from the notes text that follows `const json = '{...}'`
    pattern = r"const json = '({.*?})'"
    match = re.search(pattern, response_text)
    if match:
        json_string = match.group(1)
        return json.loads(json_string)
    else:
        raise ValueError("No JSON string found in the response text.")


def get_supernote_data(url: str) -> dict:
    # get the json data from the Supernote
    request = {
        "method": "get",
        "url": url,
        "headers": {"Content-Type": "application/json"},
    }
    response = requests.request(**request)

    # check if the request was successful
    if response.status_code == 200:
        return get_supernote_json(response.text)
    else:
        print(
            f"Failed to get notes and folders: {response.status_code} - {response.text}"
        )
        return {}


def walk_folder(folder, notes, ip_address, ignore_dirs=None):
    folder_data = get_supernote_data(f"{ip_address}/{folder['uri']}")
    for obj in folder_data["fileList"]:
        if obj["isDirectory"]:
            # Skip this directory if it's in the ignore list
            if ignore_dirs and obj["name"] in ignore_dirs:
                print(f"Ignoring directory: {obj['name']}")
                continue
            walk_folder(obj, notes, ip_address, ignore_dirs)
        else:
            notes.append(obj)


def walk_supernote(
    ip=DEFAULT_SUPERNOTE_IP, port=DEFAULT_SUPERNOTE_PORT, ignore_dirs=None
) -> list:
    ip_address, url = get_supernote_url(ip, port)
    root_data = get_supernote_data(url)

    notes = [obj for obj in root_data["fileList"] if not obj["isDirectory"]]

    folders = [
        obj
        for obj in root_data["fileList"]
        if obj["isDirectory"] and (not ignore_dirs or obj["name"] not in ignore_dirs)
    ]

    # Walk through and each folder recursively and get all the notes
    for folder in folders:
        print(f"Folder: {folder['name']}")
        walk_folder(folder, notes, ip_address, ignore_dirs)

    return notes


def download_file(url, file_path):
    print(f"Downloading {url} to {file_path}")
    # download the file from the url and save it to the file path
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded {file_path}")
    else:
        print(f"Failed to download {url}: {response.status_code} - {response.text}")


def calculate_sha256(file_path):
    """Calculate the SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash in chunks to efficiently handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def sync_notes_files(
    notes, data_folder="data", ip=DEFAULT_SUPERNOTE_IP, port=DEFAULT_SUPERNOTE_PORT
) -> list:
    # Create the data folder if it doesn't exist
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    # Create a temporary folder for downloading
    tmp_folder = f"tmp_{data_folder}"
    if os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder)
    os.makedirs(tmp_folder)

    # Get the Supernote URL with the provided IP and port
    _, url = get_supernote_url(ip, port)

    # Keep track of files that were downloaded
    downloaded_files = []

    # persist the notes from the supernote to the temp folder
    for note in notes:
        # remove the '/Note' from the uri
        note_uri = note["uri"].replace("/Note", "")
        tmp_note_path = f"{tmp_folder}{note_uri}"
        final_note_path = f"{data_folder}{note_uri}"

        # create each folder in the path
        os.makedirs(os.path.dirname(tmp_note_path), exist_ok=True)

        # download the note to temp folder
        download_file(f"{url}{note_uri}", tmp_note_path)
        downloaded_files.append((tmp_note_path, final_note_path))

    synced_files = []

    # Compare checksums and replace files if different
    for tmp_path, final_path in downloaded_files:
        if not os.path.exists(final_path):
            # File doesn't exist in the final location, just move it
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            shutil.move(tmp_path, final_path)
            print(f"New file added: {final_path}")
            synced_files.append(final_path)
        else:
            # Compare checksums
            tmp_checksum = calculate_sha256(tmp_path)
            existing_checksum = calculate_sha256(final_path)

            if tmp_checksum != existing_checksum:
                # Files are different, replace the existing file
                os.replace(tmp_path, final_path)
                print(f"Updated file: {final_path}")
                synced_files.append(final_path)
            else:
                # Files are identical, remove the temporary file
                os.remove(tmp_path)
                print(f"File unchanged: {final_path}")

    # Clean up the temporary directory
    if os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder)

    return synced_files


def convert_single_note_to_png(note_file, output_folder):
    """Convert a single note file to PNG."""
    try:
        base_name = os.path.splitext(os.path.basename(note_file))[0]
        output_file = os.path.join(output_folder, f"{base_name}.png")

        args = ConversionArgs(
            input=note_file,
            output=output_file,
            number=0,  # Convert first page by default
            all=True,  # Set to True if you want to convert all pages
            exclude_background=False,  # Set to True if you want transparent background
        )

        notebook = load_notebook(args.input, policy=args.policy)
        convert_to_png(args, notebook, palette=None)
        return f"Successfully converted {note_file} to PNG"
    except Exception as e:
        return f"Error converting {note_file}: {str(e)}"


def convert_notes_to_png(input_folder="data", output_folder="images", synced_files=[]):
    notes_files = filter_out_unsynced_files(
        folder=input_folder,
        synced_files=synced_files,
    )

    # Create an images folder if it doesn't exist
    if not os.path.exists(output_folder):
        print(f"Creating output folder: {output_folder}")
        os.makedirs(output_folder)

    # Use ThreadPoolExecutor to process conversions in parallel
    # Set max_workers to a reasonable number based on CPU cores
    max_workers = min(len(notes_files), os.cpu_count())

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create a dictionary of futures to file names for status tracking
        future_to_note = {
            executor.submit(
                convert_single_note_to_png, note_file, output_folder
            ): note_file
            for note_file in notes_files
        }

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_note):
            note_file = future_to_note[future]
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"Failed to convert {note_file}: {str(e)}")


def refresh_local_from_supernote(
    data_folder="data",
    images_folder="images",
    ip=DEFAULT_SUPERNOTE_IP,
    port=DEFAULT_SUPERNOTE_PORT,
    ignore_dirs=None,
) -> list:
    # find out what exists on the supernote
    notes_data = walk_supernote(ip=ip, port=port, ignore_dirs=ignore_dirs)

    # sync the notes to the data folder
    synced_files = sync_notes_files(
        notes_data, data_folder=data_folder, ip=ip, port=port
    )

    # convert the notes to pngs for ingesting
    convert_notes_to_png(
        input_folder=data_folder, output_folder=images_folder, synced_files=synced_files
    )

    return synced_files
