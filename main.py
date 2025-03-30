import argparse
from src.supernote import (
    refresh_local_from_supernote,
    convert_notes_to_png,
    DEFAULT_SUPERNOTE_IP,
    DEFAULT_SUPERNOTE_PORT,
)

from src.text_extraction import (
    test_llm_image_eval,
    extract_text_from_images,
)
from src.meta import (
    generate_metadata,
)
from src.sync import (
    process_synced_files_from_supernote,
)
from src.watch import (
    watch_for_supernote,
)


def cli():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Process Supernote data and perform operations."
    )
    parser.add_argument(
        "--fresh-data", action="store_true", help="Fetch fresh data from Supernote"
    )
    parser.add_argument(
        "--operation",
        choices=[
            "extract",
            "test-img",
            "metadata",
            "sync",
            "pull",
            "note-to-png",
            "watch",
        ],
        default="",
        help="""Operation to perform on either one, synced files (new/updated notes) or all files. 
        \"extract\" will extract text from images,
        \"test-img\" will test the LLM image evaluation,
        \"metadata\" will generate metadata for the synced files, 
        \"sync\" will sync the files from the supernote and generate metadata for all files,
        \"pull\" will pull the files from the supernote,
        \"note-to-png\" will convert notes to PNG format,
        \"watch\" will continuously monitor for Supernote and sync when available.""",
    )

    parser.add_argument(
        "--file",
        type=str,
        default="",
        help="File to process (for testing purposes)",
    )
    parser.add_argument(
        "--ignore-dirs",
        type=str,
        default="Work",
        help="Comma-separated list of directories to ignore during operations (e.g. 'Work')",
    )
    parser.add_argument(
        "--image-llm-model",
        type=str,
        default="gemma3:12b",
        help="LLM model for text extraction from images",
    )
    parser.add_argument(
        "--metadata-model",
        type=str,
        default="qwen2.5:3b",
        help="LLM model for metadata generation",
    )
    parser.add_argument(
        "--supernote-ip",
        type=str,
        default=DEFAULT_SUPERNOTE_IP,
        help=f"IP address of the Supernote device (default: {DEFAULT_SUPERNOTE_IP})",
    )
    parser.add_argument(
        "--supernote-port",
        type=int,
        default=DEFAULT_SUPERNOTE_PORT,
        help=f"Port number for the Supernote device (default: {DEFAULT_SUPERNOTE_PORT})",
    )
    parser.add_argument(
        "--delay-hours",
        type=float,
        default=1.0,
        help="Hours to wait between sync operations in watch mode (default: 1.0)",
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=60,
        help="Seconds between checking for Supernote availability in watch mode (default: 60)",
    )
    args = parser.parse_args()

    if args.fresh_data:
        if args.operation in ["sync", "pull"]:
            print(
                "Syncing happens automatically on either sync or pull, no need to use --fresh-data."
            )
        else:
            # walk the supernote device and get all the notes
            ignore_dirs = args.ignore_dirs.split(",") if args.ignore_dirs else None
            synced_files = refresh_local_from_supernote(
                ip=args.supernote_ip, port=args.supernote_port, ignore_dirs=ignore_dirs
            )
    else:
        # use the local data folder
        synced_files = []

    if args.file:
        synced_files = [args.file]

    if not args.operation:
        print("Please specify an operation using --operation.")
        return

    if args.operation == "test-img":
        # test the llm image evaluation across a set of llms
        test_llm_image_eval(
            test_text_file="test_text_file.txt",
            eval_folder="llm_roundtable",
            fresh_sn_data_fetch=args.fresh_data,
            fresh_llm_data_fetch=True,
            debug=True,
        )
    elif args.operation == "metadata":
        # generate metadata for the synced files
        generate_metadata(
            extracted_data="notes",
            metadata_model_id=args.metadata_model,
            synced_files=synced_files,
        )
    elif args.operation == "extract":
        # extract text from the pngs using the llm
        extract_text_from_images(
            images_folder="images",
            data_folder="data",
            output_folder="notes",
            image_eval_llm=args.image_llm_model,
            synced_files=synced_files,
        )
    elif args.operation == "sync":
        ignore_dirs = args.ignore_dirs.split(",") if args.ignore_dirs else None
        process_synced_files_from_supernote(
            data_folder="data",
            images_folder="images",
            image_llm_model=args.image_llm_model,
            metadata_model=args.metadata_model,
            supernote_ip=args.supernote_ip,
            supernote_port=args.supernote_port,
            ignore_dirs=ignore_dirs,
        )
    elif args.operation == "pull":
        # pull the files from the supernote
        ignore_dirs = args.ignore_dirs.split(",") if args.ignore_dirs else None
        synced_files = refresh_local_from_supernote(
            data_folder="data",
            images_folder="images",
            ip=args.supernote_ip,
            port=args.supernote_port,
            ignore_dirs=ignore_dirs,
        )
        print(f"Pulled {len(synced_files)} files from the Supernote.")
    elif args.operation == "watch":
        ignore_dirs = args.ignore_dirs.split(",") if args.ignore_dirs else None
        print(
            f"Starting watch service for Supernote at {args.supernote_ip}:{args.supernote_port}"
        )
        print(
            f"Sync delay set to {args.delay_hours} hours, check interval {args.check_interval} seconds"
        )
        watch_for_supernote(
            data_folder="data",
            images_folder="images",
            image_llm_model=args.image_llm_model,
            metadata_model=args.metadata_model,
            supernote_ip=args.supernote_ip,
            supernote_port=args.supernote_port,
            delay_hours=args.delay_hours,
            check_interval=args.check_interval,
            ignore_dirs=ignore_dirs,
        )
    elif args.operation == "note-to-png":
        ignore_dirs = args.ignore_dirs.split(",") if args.ignore_dirs else None
        convert_notes_to_png(
            input_folder="data",
            output_folder="images",
            synced_files=synced_files,
            # Note: This function doesn't currently use ignore_dirs in the implementation
            # but we should be consistent in passing the parameter for future use
        )
    else:
        print(f"Unknown operation: {args.operation}")
        raise ValueError(f"Unknown operation: {args.operation}")


if __name__ == "__main__":
    cli()
