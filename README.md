# 📝 MegaNote

<img src="meganote.jpg" alt="drawing" width="200"/>

MegaNote is a utility that syncs handwritten notes from your Supernote device, extracts text using advanced LLMs (Large Language Models), and enhances the extracted content with metadata, tags, and links.

## ✨ Features

- **🔄 Sync from Supernote**: Automatically sync your .note files from a Supernote device over WiFi
- **📊 Text Extraction**: Convert handwritten notes to text using state-of-the-art LLMs
- **🏷️ Metadata Enhancement**: Automatically generate tags and keywords for your notes
- **🔗 Bidirectional Links**: Create a network of interconnected notes with [[wiki-style links]]
- **💻 Command-line Interface**: Simple command-line tools for automation and control

## ⚠️ Warning ⚠️
- In order for this tool to work, you need to set your Supernote device to allow [access over WiFi](https://support.supernote.com/en_US/Tools-Features/wi-fi-transfer) when you want to sync notes.

## 🧰 Requirements

- Hardware and Software Requirements
   - Supernote device (A5X, A6X, A6X Pro, or A6X Pro 2)
   - A minimum of M1 Mac, or a Windows/Linux computer with a GPU with at least 8GB of VRAM
- `uv` (Ultraviolet) package manager`
- LLM API access (Google Gemini API key and/or Ollama)
- Network connectivity between your computer and Supernote


### Cost 💸 
- As configured, this tool costs no money to run. 
   - The Gemini API is free for personal use and configured to guard against rate limits
   - Ollama models can be run locally on a Mac with M1 or greater CPU

## 🚀 Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/meganote.git
   cd meganote
   ```

2. Install UV package installer (recommended over pip):
   ```
   curl -sSf https://install.ultraviolet.rs | sh
   ```

3. Install dependencies using UV:
   ```
   uv sync
   ```

4. Install LLM command-line tool:
   ```
   uv pip install llm
   ```

5. Install required LLM plugins:
   ```
   # Install Gemini plugin for Google's models
   uv llm install gemini
   
   # Install Ollama plugin for local model access
   uv llm install llm-ollama
   ```

6. Configure your LLM API access:

   **For Gemini API:**
   ```
   # Set your Gemini API key
   llm keys set gemini
   # When prompted, enter your API key from https://aistudio.google.com/
   ```
      - As configured, this tool costs no money to run.
      
   **For Ollama models:**
   ```
   # Ensure Ollama is installed (https://ollama.com/)
   # Pull models you want to use (defaults below)
   ollama pull qwen2.5:3b
   ollama pull gemma3:latest
   ```

## 🔍 Usage

### Basic Usage

To sync new notes from your Supernote, extract text, and generate metadata:

```
uv run main.py --operation sync --supernote-ip 192.168.1.139 --supernote-port 8089
```

### 🛠️ Command-Line Options

The tool offers several command-line options for different operations:

- `--operation`: Specify the operation to perform:
  - `sync`: Sync files from Supernote, extract text, and generate metadata
  - `pull`: Only sync files from the Supernote (no processing)
  - `extract`: Extract text from images
  - `metadata`: Generate metadata for synced files
  - `test-img`: Test LLM image evaluation
- `--fresh-data`: Fetch fresh data directly from your Supernote device (legacy option)
- `--file`: Specify a single file to process (useful for testing)
- `--supernote-ip`: Specify your Supernote's IP address (default: 192.168.1.139)
- `--supernote-port`: Specify your Supernote's port number (default: 8089)
- `--image-llm-model`: Specify the LLM model for text extraction (default: gemini-2.5-pro-exp-03-25)
- `--metadata-model`: Specify the LLM model for metadata generation (default: qwen2.5:3b)

### 📋 Common Usage Examples

**Sync new notes, extract text, and generate metadata:**
```
uv run main.py --operation sync
```

**Sync notes from a specific Supernote IP address:**
```
uv run main.py --operation sync --supernote-ip 192.168.0.123
```

**Only pull files from the Supernote (without processing):**
```
uv run main.py --operation pull
```

**Generate metadata for existing notes:**
```
uv run main.py --operation metadata
```

**Extract text from existing local data (no fresh sync):**
```
uv run main.py --operation extract
```

**Test LLM image evaluation with a specific file:**
```
uv run main.py --operation test-img --file my_note.png
```

Output files will be stored in the following directories:
- 📂 Raw files from Supernote: `data/`
- 🖼️ Extracted images: `images/`
- 📄 Processed text notes: `notes/`

