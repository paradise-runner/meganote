from src.supernote import (
    refresh_local_from_supernote,
    DEFAULT_SUPERNOTE_IP,
    DEFAULT_SUPERNOTE_PORT,
)
from src.text_extraction import (
    extract_text_from_images,
)
from src.meta import (
    generate_metadata,
)


def process_synced_files_from_supernote(
    data_folder="data",
    images_folder="images",
    image_llm_model="gemma3:12b",
    metadata_model="qwen2.5:3b",
    supernote_ip=DEFAULT_SUPERNOTE_IP,
    supernote_port=DEFAULT_SUPERNOTE_PORT,
) -> list:
    synced_files = refresh_local_from_supernote(
        data_folder=data_folder, 
        images_folder=images_folder,
        ip=supernote_ip,
        port=supernote_port
    )

    extract_text_from_images(
        images_folder=images_folder,
        data_folder=data_folder,
        output_folder="notes",
        image_eval_llm=image_llm_model,
        synced_files=synced_files,
    )

    generate_metadata(
        extracted_data="notes",
        metadata_model_id=metadata_model,
        synced_files=synced_files,
    )

    return synced_files  # Return synced files list to caller

