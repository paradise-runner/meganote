import os
import shutil
from pathlib import Path

def convert_txt_to_markdown(txt_file_path, markdown_file_path):
    """
    Converts a .txt file to markdown format.
    
    Args:
        txt_file_path (str): Path to the txt file.
        markdown_file_path (str): Path to save the converted markdown file.
    """
    with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
        content = txt_file.read()
    
    # Write to markdown file
    with open(markdown_file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(content)
    
    return markdown_file_path

def sync_to_obsidian(notes_folder, obsidian_path, obsidian_folder="Supernote", synced_files=None):
    """
    Syncs the notes folder to a specified Obsidian vault, maintaining folder structure.
    
    Args:
        notes_folder (str): Path to the folder containing processed notes.
        obsidian_path (str): Path to the Obsidian vault root directory.
        obsidian_folder (str): Name of the folder in the Obsidian vault to sync to.
        synced_files (list): Optional list of specific files to sync. If None, all files are synced.
    """
    # Ensure the notes folder exists
    if not os.path.exists(notes_folder):
        raise FileNotFoundError(f"Notes folder '{notes_folder}' does not exist")
    
    # Ensure the Obsidian path exists
    if not os.path.exists(obsidian_path):
        raise FileNotFoundError(f"Obsidian vault path '{obsidian_path}' does not exist")
    
    # Create the target folder in Obsidian vault if it doesn't exist
    target_folder = os.path.join(obsidian_path, obsidian_folder)
    os.makedirs(target_folder, exist_ok=True)
    
    # Temporary folder for converted files
    temp_dir = os.path.join(os.path.dirname(notes_folder), "temp_markdown")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Lists to keep track of files
    markdown_files = []
    txt_files = []
    converted_files = []
    
    # If synced_files is provided, only process those specific files
    if synced_files:
        for file in synced_files:
            # Convert the file path to just the filename for matching
            file_path = Path(file)
            filename = file_path.stem
            
            # Check for markdown files
            markdown_file = os.path.join(notes_folder, f"{filename}.md")
            if os.path.exists(markdown_file):
                markdown_files.append(markdown_file)
            
            # Check for txt files
            txt_file = os.path.join(notes_folder, f"{filename}.txt")
            if os.path.exists(txt_file):
                txt_files.append(txt_file)
    else:
        # Recursively walk through the notes folder
        for root, _, files in os.walk(notes_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.md'):
                    markdown_files.append(file_path)
                elif file.endswith('.txt'):
                    txt_files.append(file_path)
    
    # Convert txt files to markdown while maintaining folder structure
    for txt_file in txt_files:
        # Get the relative path from notes_folder to maintain structure
        rel_path = os.path.relpath(txt_file, notes_folder)
        rel_dir = os.path.dirname(rel_path)
        filename = os.path.basename(txt_file)
        stem = Path(txt_file).stem
        
        # Create subdirectories in temp folder if needed
        temp_subdir = os.path.join(temp_dir, rel_dir)
        os.makedirs(temp_subdir, exist_ok=True)
        
        # Path for the new markdown file
        target_md_file = os.path.join(temp_subdir, f"{stem}.md")
        
        try:
            converted_file = convert_txt_to_markdown(txt_file, target_md_file)
            converted_files.append(converted_file)
            print(f"Converted {rel_path} to markdown")
        except Exception as e:
            print(f"Error converting {rel_path}: {str(e)}")
    
    # Combine all files to copy
    all_files = markdown_files + converted_files
    files_copied = 0
    
    # Copy each file to the Obsidian vault, maintaining folder structure
    for file in all_files:
        # For markdown files, get path relative to notes_folder
        if file in markdown_files:
            rel_path = os.path.relpath(file, notes_folder)
        # For converted files, get path relative to temp_dir
        else:
            rel_path = os.path.relpath(file, temp_dir)
        
        # Create target directory structure in Obsidian vault
        target_dir = os.path.join(target_folder, os.path.dirname(rel_path))
        os.makedirs(target_dir, exist_ok=True)
        
        # Full path to target file
        target_file = os.path.join(target_folder, rel_path)
        
        try:
            shutil.copy2(file, target_file)
            files_copied += 1
        except Exception as e:
            print(f"Error copying {rel_path}: {str(e)}")
    
    # Clean up temporary directory
    if os.path.exists(temp_dir):
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                try:
                    os.rmdir(os.path.join(root, dir))
                except:
                    pass  # Ignore if we can't delete a directory
        try:
            os.rmdir(temp_dir)
        except:
            pass  # Ignore if we can't delete the root temp directory
    
    print(f"Synced {files_copied} notes to Obsidian vault at '{target_folder}'")
    print(f"Converted {len(converted_files)} text files to markdown format")
    
    return files_copied
