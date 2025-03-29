# 📝 MegaNote

MegaNote is a utility that syncs handwritten notes from your Supernote device, extracts text using advanced LLMs (Large Language Models), and enhances the extracted content with metadata, tags, and links.

## ✨ Features

- **🔄 Sync from Supernote**: Automatically sync your .note files from a Supernote device over WiFi
- **📊 Text Extraction**: Convert handwritten notes to text using state-of-the-art LLMs
- **🏷️ Metadata Enhancement**: Automatically generate tags and keywords for your notes
- **🔗 Bidirectional Links**: Create a network of interconnected notes with [[wiki-style links]]
- **💻 Command-line Interface**: Simple command-line tools for automation and control

## 🧰 Requirements

- Python 3.9 or higher
- Supernote device accessible on your local network
- LLM API access (Google Gemini API key and/or Ollama)
- Network connectivity between your computer and Supernote

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
   # When prompted, enter your API key from https://ai.google.dev/
   ```

   **For Ollama models:**
   ```
   # Ensure Ollama is installed (https://ollama.com/)
   # Pull models you want to use
   ollama pull qwen2.5:3b
   ollama pull gemma3:latest
   ```

7. Configure your Supernote device's IP address:
   - Open `src/supernote.py`
   - Update the `SUPERNOTE_IP` variable with your Supernote's IP address
   - Make sure your Supernote's HTTP server is enabled and running on port 8089

## 🔍 Usage

### Basic Usage

To sync new notes from your Supernote, extract text, and generate metadata:

```
uv run main.py --fresh-data
```

### 🛠️ Command-Line Options

The tool offers several command-line options for different operations:

- `--fresh-data`: Fetch fresh data directly from your Supernote device
- `--operation`: Specify the operation to perform:
  - `extract`: Extract text from images (default)
  - `test-img`: Test LLM image evaluation
  - `metadata`: Generate metadata for synced files
- `--file`: Specify a single file to process (useful for testing)

### 📋 Common Usage Examples

**Sync new notes and extract text:**
```
uv run main.py --fresh-data
```

**Generate metadata for existing notes:**
```
uv run main.py --operation metadata
```

**Test LLM image evaluation with a specific file:**
```
uv run main.py --operation test --file my_note.png
```

**Extract text from existing local data (no fresh sync):**
```
uv run main.py
```

Output files will be stored in the following directories:
- 📂 Raw files from Supernote: `data/`
- 🖼️ Extracted images: `images/`
- 📄 Processed text notes: `notes/`

