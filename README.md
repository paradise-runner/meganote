# 📝 MegaNote

<img src="meganote.jpg" alt="drawing" width="200"/>

MegaNote is a utility that syncs handwritten notes from your Supernote device, extracts text using advanced LLMs (Large Language Models), and enhances the extracted content with metadata, tags, and links.

## ✨ Features

- **🧠 Local First AI**: Use your computer to get your work done, no cloud provider in your way. No data privacy concerns.
- **🔄 Sync from Supernote**: Automatically sync your .note files from a Supernote device over WiFi
- **📊 Text Extraction**: Convert handwritten notes to text using state-of-the-art LLMs
- **🏷️ Metadata Enhancement**: Automatically generate tags and keywords for your notes
- **🔗 Bidirectional Links**: Create a network of interconnected notes with [[wiki-style links]]
- **📝 Obsidian Integration**: Sync your processed notes directly to your Obsidian vault
- **💻 Command-line Interface**: Simple command-line tools for automation and control

## ⚠️ Warning ⚠️
- In order for this tool to work, you need to set your Supernote device to allow [access over WiFi](https://support.supernote.com/en_US/Tools-Features/wi-fi-transfer) when you want to sync notes.

## 🧰 Requirements

- Hardware and Software Requirements
   - Supernote device (A5X, A6X, A6X Pro, or A6X Pro 2)
   - A minimum of M1 Mac with 16GB of ram, or a Windows/Linux computer with a GPU with at least 16GB of VRAM for defaults  
      - Note: You can change gemma3:12b to gemma3:4b in the command line options to use a smaller model that only requires 8GB of VRAM
- `uv` (Ultraviolet) package manager
- Network connectivity between your computer and Supernote


### Cost 💸 
- As configured, this tool costs no money to run. 
   - Ollama models can be run locally on a Mac with M1 with 16GB of RAM

## 🚀 Installation

1. Clone this repository:
   ```
   git clone https://github.com/paradise-runner/meganote.git
   cd meganote
   ```

2. Install UV package installer (recommended over pip):
   ```
   curl -sSf https://install.ultraviolet.rs | sh
   ```

3. Install Ollama (if you want to use local models):
   ```
   # For MacOS
   brew install ollama/tap/ollama
   ```
   ```
   # For Linux
   curl -sSfL https://ollama.com/download.sh | sh
   ```
   ```
   # For Windows
   # Download the installer from https://ollama.com/download
   ```

4. Install dependencies using UV:
   ```
   uv sync
   ```

5. Configure your LLM API access:

   **For Ollama models:**
   ```
   # Ensure Ollama is installed (https://ollama.com/)
   # Pull models you want to use (defaults below)
   ollama pull qwen2.5:3b
   ollama pull gemma3:12b
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
  - `watch`: Continuously monitor for Supernote and sync when available
  - `note-to-png`: Convert .note files to PNG format
- `--fresh-data`: Fetch fresh data directly from your Supernote device (legacy option)
- `--file`: Specify a single file to process (useful for testing)
- `--supernote-ip`: Specify your Supernote's IP address (default: 192.168.1.139)
- `--supernote-port`: Specify your Supernote's port number (default: 8089)
- `--image-llm-model`: Specify the LLM model for text extraction (default: gemma3:12b)
- `--metadata-model`: Specify the LLM model for metadata generation (default: qwen2.5:3b)
- `--ignore-dirs`: Comma-separated list of directories to ignore (default: "Work")
- `--delay-hours`: Hours to wait between sync operations in watch mode (default: 1.0)
- `--check-interval`: Seconds between checking for Supernote availability in watch mode (default: 60)

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

**Watch for Supernote device and automatically sync:**
```
uv run main.py --operation watch --delay-hours 2 --check-interval 120
```

**Convert .note files to PNG format:**
```
uv run main.py --operation note-to-png
```

**Sync notes to an Obsidian vault (converts .txt files to markdown and preserves folder structure):**
```
uv run main.py --operation obsidian --obsidian-path /path/to/obsidian/vault
```

**Sync notes to a custom folder in an Obsidian vault:**
```
uv run main.py --operation obsidian --obsidian-path /path/to/obsidian/vault --obsidian-folder "My Supernote Notes"
```

Output files will be stored in the following directories:
- 📂 Raw files from Supernote: `data/`
- 🖼️ Extracted images: `images/`
- 📄 Processed text notes: `notes/`

## Open Source AI Model Ranking at Text Extraction
### Prompt: `extract text from the image`
| Model Name | Text Extraction Quality
|----------|------------|------
| gemini-2.5-pro-exp-03-25 | 100%
| gemma3:12b | 94.46%
| gemma3:4b | 94.02%
| llama3.2-vision:11b | 4.35%

### Prompt: `extract text from this image into markdown without any extra text or formatting in the response.`
| Model Name | Text Extraction Quality
|----------|------------|------
| gemma3:12b | 94.77%
| gemma3:4b | 95.98%
| llama3.2-vision:11b | 92.44%


### Prompt: `transcripe the text in the image as accurately as possible into markdown format without any extra text or formatting in the response.`
| Model Name | Text Extraction Quality
|----------|------------|------
| gemma3:12b | 96.49%
| gemma3:4b | 96.25%
| llama3.2-vision:11b | 95.40%
