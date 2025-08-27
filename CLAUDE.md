# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MegaNote is a Python utility that syncs handwritten notes from Supernote devices and extracts text using local LLMs (Large Language Models). It's designed for local-first AI processing with no cloud dependencies.

## Key Commands

### Development
- **Install dependencies**: `uv sync`
- **Run the main CLI**: `uv run main.py [options]`
- **Code formatting**: `ruff` (available as dependency)

### Primary Operations
- **Full sync workflow**: `uv run main.py --operation sync`
- **Pull files only**: `uv run main.py --operation pull`
- **Extract text from existing images**: `uv run main.py --operation extract`
- **Watch mode**: `uv run main.py --operation watch`
- **Convert to PNG**: `uv run main.py --operation note-to-png`
- **Sync to Obsidian**: `uv run main.py --operation obsidian --obsidian-path /path/to/vault`

### Model Configuration
- **Default image extraction model**: `gemma3:12b` (requires ~16GB RAM/VRAM)
- **Alternative smaller model**: `gemma3:4b` (requires ~8GB VRAM)
- **Override model**: `--image-llm-model MODEL_NAME`

## Architecture

### Core Processing Pipeline
1. **Sync**: `src/supernote.py` - Connects to Supernote device via WiFi, downloads .note files
2. **Convert**: `src/supernote.py` - Converts .note files to PNG images using supernotelib
3. **Extract**: `src/text_extraction.py` - Uses LLMs to extract text from PNG images
5. **Export**: `src/obsidian.py` - Syncs processed notes to Obsidian vaults

### Key Modules
- **main.py**: CLI entry point with argument parsing
- **src/sync.py**: Orchestrates the full sync workflow
- **src/llm_utils.py**: Centralized LLM interaction with retry logic and rate limiting
- **src/utilities.py**: Helper functions for file filtering and text processing
- **src/watch.py**: Continuous monitoring for Supernote device availability

### Data Flow
- **Raw notes**: `data/` (original .note files from Supernote)
- **Images**: `images/` (PNG conversions of notes)
- **Processed text**: `notes/` (extracted text files)

### LLM Integration
- Uses `llm` library for model abstraction
- Supports Ollama for local models (primary use case)
- Rate limiting implemented for cloud-based models
- Text extraction prompt: "transcribe the text in the image as accurately as possible into markdown format without any extra text or formatting in the response"

### Supernote Device Integration
- Connects via WiFi on default IP 192.168.1.139:8089
- Uses supernotelib for .note file parsing and PNG conversion
- Implements checksum-based sync to avoid unnecessary transfers
- Supports directory filtering with `--ignore-dirs`

## Development Notes

### Dependencies
- **UV package manager** (preferred over pip)
- **Ollama** for local LLM hosting
- **supernotelib** for Supernote file handling
- **llm library** for model abstraction

### Configuration
- No package.json (Python project)
- Dependencies defined in pyproject.toml
- Default models optimized for local execution on M1 Macs with 16GB RAM

### Testing
- LLM evaluation framework in `src/text_extraction.py`
- Model comparison utilities for testing text extraction quality
- Test images stored in `test_images/`