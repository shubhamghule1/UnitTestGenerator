import os
import shutil

def delete_file_after_send(file_path: str):
    """Delete the specified file."""
    if os.path.exists(file_path):
        print(f"Deleting {file_path} File")
        os.remove(file_path)

def delete_dir_after_send(dir_path: str):
    """Delete the specified directory."""
    if os.path.exists(dir_path):
        print(f"Deleting {dir_path} Directory")
        shutil.rmtree(dir_path)
