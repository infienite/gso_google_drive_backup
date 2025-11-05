"""
Gallery Size Organizer (GSO) for Google Drive Backup

A simple script to organize phone gallery files into subfolders of size ~15GB each
to enable user to backup each folder into separate free-tier Google Drive account.
This allows users to keep memories in a safe place with good accessibility in case
of file corruption or loss. Other than that, user can also store at zero overhead
cost. User can also use Google Photos to store image more systematically.
The only downside of storing like this is user have to switch account to browse
for specific files. It's recommended that user use this method to backup only,
while keeping an easily accessible copy on handheld devices.

To run this script:
1. Download Pydroid or Termux on your phone.
2. Copy and paste this script into Pydroid editor.
3. Run the script (there will be prompt to confirm folder path to your gallery)


Author: infienite (https://github.com/infienite)
License: MIT
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

SUBFOLDER_MAX_SIZE_GB = 15  # Specify the default max size for each subfolders


def get_filesize(file):
    """
    Return size of this file
    """
    return os.path.getsize(file)


def get_mtime(file):
    """
    Return the last modified datetime of this file
    """
    return datetime.fromtimestamp(os.stat(file).st_mtime)


def move_file(file, subfolder):
    """
    Move file into subfolder within the same parent folder. Returns path to the moved file.
    """
    source = Path(file)
    target = Path(source.parent, subfolder)
    target.mkdir(exist_ok=True)
    target = Path(target, source.name)
    shutil.move(str(source), str(target))


def format_date(date: datetime):
    """
    Return string with format `day.month.year`
    """
    return date.strftime("%d.%m.%Y")


def split_gallery(files):
    """
    Split the gallery files into subfolders each containing about 15GB data in order of file modification date ascending. Each folder will be named after the date of the first and the last file which fit the constraint of having <= 15GB per folder.
    """
    # Add metadata to file
    gallery_files = []
    for file in files:
        _file = {
            "file": file,
            "size": get_filesize(file),
            "date": get_mtime(file)
        }
        gallery_files.append(_file)
    
    # Sort based on modified date
    gallery_files.sort(key=lambda f: f["date"])

    # Classify files into subfolders where each subfolder contains <= 15GB total filesize
    subfolders = [0]  # Stores the start and end index of files contained in one subfolder
    total_size, max_size = 0, SUBFOLDER_MAX_SIZE_GB*1024**3  # The size is default measured in bytes (15GB -> 1.5e+10B)
    i = 0
    for file in gallery_files:
        total_size += file["size"]
        if total_size > max_size:
            j = subfolders.pop()
            subfolders.append((j, i-1))
            subfolders.append(i)
            total_size = file["size"]
        i += 1

    # Analyze file operations
    subfolders_created = []
    subfolders_size = []
    files_moved, files_unchanged = 0, 0

    # Perform operations to refactor files
    for subfolder in subfolders:
        if type(subfolder) == type(1):
            break
        i, j = subfolder
        subfolder_name = f"{format_date(gallery_files[i]['date'])}-{format_date(gallery_files[j]['date'])}"
        total_size = 0
        for k in range(i, j+1):
            move_file(gallery_files[k]["file"], subfolder_name)
            total_size += gallery_files[k]["size"]
            files_moved += 1
        subfolders_size.append(total_size)
        subfolders_created.append(subfolder_name)

    files_unchanged = len(gallery_files) - files_moved
    
    # Return statistics as result of this operation
    return {
        "subfolders_created": subfolders_created,
        "subfolders_size": subfolders_size,
        "files_moved": files_moved,
        "files_unchanged": files_unchanged
    }


def get_gallery_folder():
    """
    Return the path to the gallery folder (by default from Camera). This function checks for most common location to least common location known to be used by different phone manufacturer. Return None if none any of this location exist.
    """
    # These are the typical paths to check from most common to least common
    common_camera_paths = [
        '/storage/emulated/0/DCIM/Camera',      # Most Android phones
        '/storage/emulated/0/DCIM',             # Some phones put directly in DCIM
        '/storage/emulated/0/Pictures',         # Alternative location
        '/storage/emulated/0/Pictures/Camera',  # Some manufacturers
        '/storage/emulated/0/Camera',           # Less common but possible
    ]

    # Determine which one is first to be found exist
    for path in common_camera_paths:
        try:
            os.listdir(Path(path))
            return path
        except FileNotFoundError:
            continue


def get_files(folder):
    """
    Get the list of files inside the specified folder. Each file is represented as a string of its absolute path. 
    """
    filenames = os.listdir(folder)
    files = list(map(lambda filename: Path(folder, filename), filenames))
    return files


def ui_confirm_yn(question):
    """
    Return truth value based on user answer to the question.
    """
    while True:
        r = input(f"{question} [Y/n]: ").capitalize()

        if r == "Y" or r == "YE" or r == "YES":
            return True
        elif r == "N" or r == "NO":
            return False
        

def ui_input_path(prompt):
    """
    Return validated path string based on user path input.
    """
    while True:
        r = input(f"{prompt} ").capitalize()

        try:
            os.listdir(Path(r))
            return r
        except FileNotFoundError:
            print("Path is not valid")


def main():
    """
    App controller bridging between user interface and backend execution
    """
    # Get path to the gallery folder
    folder = get_gallery_folder()

    if not folder:
        print("Gallery folder isn't found. Checked:\n1. '/storage/emulated/0/DCIM/Camera'\n2. '/storage/emulated/0/DCIM'\netc...")
        folder = ui_input_path("Please manually enter path to the gallery folder:")

    confirm = ui_confirm_yn(f"Confirm gallery folder is at {folder}?")
    
    while not confirm:
        folder = ui_input_path("Please manually enter path to the gallery folder:")
        confirm = ui_confirm_yn(f"Confirm gallery folder is at {folder}?")

    # Get files in the gallery folder
    files = get_files(folder)

    # Perform split operations
    stats = split_gallery(files)

    print()
    if stats["files_moved"] != 0:
        print(f"Files moved: {stats["files_moved"]}       Files unchanged: {stats["files_unchanged"]}")
        print(f"Subfolders created:")
        print(f"No         Subfolder           Size ")
        print(f"--   ---------------------   --------")
        for i, subfolder in enumerate(zip(stats["subfolders_created"], stats["subfolders_size"])):
            subfolder_name, size = subfolder
            size = size / (1024**3)  # Convert from B to GB unit
            print("%2d   %11s   %2.3fGB" % ((i+1), subfolder_name, size))
    else:
        print(f"No operations performed because the total size of files does not exceed {SUBFOLDER_MAX_SIZE_GB}GB")


if __name__ == "__main__":
    main()
