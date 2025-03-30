from src.supernote import (
    DEFAULT_SUPERNOTE_IP,
    DEFAULT_SUPERNOTE_PORT,
)
from src.sync import (
    process_synced_files_from_supernote,
)

import socket
import time
import logging

# Create a dedicated logger for this module
logger = logging.getLogger("meganote.watch")


def is_supernote_available(
    ip=DEFAULT_SUPERNOTE_IP, port=DEFAULT_SUPERNOTE_PORT, timeout=1
):
    """Check if Supernote is available on the network."""
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.close()
        return True
    except (socket.timeout, socket.error):
        return False


def watch_for_supernote(
    data_folder="data",
    images_folder="images",
    image_llm_model="gemma3:12b",
    metadata_model="qwen2.5:3b",
    supernote_ip=DEFAULT_SUPERNOTE_IP,
    supernote_port=DEFAULT_SUPERNOTE_PORT,
    delay_hours=1,
    check_interval=60,  # Check every minute
    ignore_dirs=None,
):
    """
    Watch for Supernote device on the network and sync when available.

    Args:
        data_folder: Directory to store fetched note data
        images_folder: Directory to store converted images
        image_llm_model: LLM model for image text extraction
        metadata_model: LLM model for metadata generation
        supernote_ip: IP address of the Supernote device
        supernote_port: Port number for the Supernote device
        delay_hours: Hours to wait between sync operations (to prevent battery drain)
        check_interval: Seconds to wait between availability checks
        ignore_dirs: List of directories to ignore during sync operations
    """
    # Configure the module's logger
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.setLevel(logging.INFO)
    # Check if logger already has handlers to avoid duplicates
    if not logger.handlers:
        logger.addHandler(handler)

    last_sync_time = 0
    delay_seconds = delay_hours * 3600  # Convert hours to seconds

    logger.info("Starting Supernote watcher service")
    logger.info(
        f"IP: {supernote_ip}, Port: {supernote_port}, Sync delay: {delay_hours} hours"
    )
    if ignore_dirs:
        logger.info(f"Ignoring directories: {', '.join(ignore_dirs)}")

    while True:
        current_time = time.time()

        # Check if Supernote is available
        if is_supernote_available(supernote_ip, supernote_port):
            # Check if enough time has passed since last sync
            if current_time - last_sync_time > delay_seconds:
                logger.info("Supernote detected on network. Starting sync process...")
                try:
                    synced_files = process_synced_files_from_supernote(
                        data_folder=data_folder,
                        images_folder=images_folder,
                        image_llm_model=image_llm_model,
                        metadata_model=metadata_model,
                        supernote_ip=supernote_ip,
                        supernote_port=supernote_port,
                        ignore_dirs=ignore_dirs,
                    )
                    if synced_files:
                        logger.info(f"Successfully synced {len(synced_files)} files.")
                    else:
                        logger.info("Sync completed. No new or updated files found.")
                    last_sync_time = time.time()  # Update last sync time
                except Exception as e:
                    logger.error(f"Error during sync process: {e}")
            else:
                logger.debug(
                    "Supernote available but waiting for delay period to complete."
                )
        else:
            logger.debug("Supernote not detected on network.")

        time.sleep(check_interval)
