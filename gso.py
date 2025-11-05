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


Author: infienite (https://github.com/infienite/gso_google_drive_backup)
License: MIT
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

SUBFOLDER_MAX_SIZE_GB = 15  # Specify the default max size for each subfolders
GSO_FOLDER = "/storage/0/emulated/GSO Backups"  # Storing all subfolders
LOG_FILE = "./last_operation.log"  # Store operation infor


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


def copy_file(file, subfolder):
    """
    Copy file into subfolder
    """
    source = Path(file)
    target = Path(subfolder)
    os.makedirs(target, exist_ok=True)
    target = Path(target, source.name)
    shutil.copy(str(source), str(target))


def format_date(date: datetime):
    """
    Return string with format `day.month.year`
    """
    return date.strftime("%d.%m.%Y")


def files_to_gallery_files(files):
    """
    Retrieve metadata from files to make it gallery files
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
    
    with open(LOG_FILE, "w") as file:
        line = file.readline()
        if line != "":
            last_dt = datetime.fromtimestamp(float(line))
            print(f"Previous backup stores files until {format_date(last_dt)}.")
            confirm = ui_confirm_yn("Do you want to backup files after this timestamp?")
            if confirm:
                gallery_files = list(map(gallery_files, lambda file: file["date"] > last_dt))
            
    return gallery_files


def split_gallery(gallery_files: list[dict]):
    """
    Split the gallery files into subfolders each containing about 15GB data in order of file modification date ascending. Each folder will be named after the date of the first and the last file which fit the constraint of having <= 15GB per folder.
    """
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
    files_copied = 0

    # Perform operations to copy files
    for subfolder in subfolders:
        if type(subfolder) == type(1):
            break
        i, j = subfolder
        subfolder_name = f"{GSO_FOLDER}/{format_date(gallery_files[i]['date'])}-{format_date(gallery_files[j]['date'])}"
        total_size = 0
        for k in range(i, j+1):
            copy_file(gallery_files[k]["file"], subfolder_name)
            total_size += gallery_files[k]["size"]
            files_copied += 1
        subfolders_size.append(total_size)
        subfolders_created.append(subfolder_name)
    
    # Log last file date operated on
    if len(gallery_files) != 0:
        with open(LOG_FILE, "w") as file:
            file.write(gallery_files[-1]["date"].timestamp())
    
    # Return statistics as result of this operation
    return {
        "subfolders_created": subfolders_created,
        "subfolders_size": subfolders_size,
        "files_copied": files_copied,
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


def get_additional_folders():
    """
    Return the path to other common folders containing images and videos. Other common folders include WhatsApp Images, Telegram and Screenshots.
    """
    whatsapp = [
        "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images",
        "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images/Sent",
        "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images/Private"
    ]

    telegram = [
        "/storage/emulated/0/Pictures/Telegram"
    ]

    screenshot = [
        "/storage/emulated/0/DCIM/Screenshots"
    ]

    other_common_folders = whatsapp + telegram + screenshot
    error_index = []

    for i in range(len(other_common_folders)):
        try:
            path = other_common_folders[i]
            os.listdir(Path(path))
        except FileNotFoundError:
            error_index.append(i)   
            continue
    
    for i in error_index:
        other_common_folders.pop(i)

    return other_common_folders


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

    other_folders = get_additional_folders()

    print("Additional folders:")
    for i in range(len(other_folders)):
        print(i, other_folders[i])

    # Get files in the gallery folder
    files = get_files(folder+other_folders)

    gallery_files = files_to_gallery_files(files)

    total_size = 0
    for file in gallery_files:
        total_size += file["size"]
    
    print(f"This operation will take additional {"%.2f" % (total_size / 1024**3)}GB storage space.")
    confirm = ui_confirm_yn(f"Do you wish to continue?")

    # Main operation to split gallery
    stats = split_gallery(gallery_files)

    print()
    print(f"Files copied: {stats["files_copied"]}")
    print(f"Subfolders created:")
    print(f"No         Subfolder           Size ")
    print(f"--   ---------------------   --------")
    for i, subfolder in enumerate(zip(stats["subfolders_created"], stats["subfolders_size"])):
        subfolder_name, size = subfolder
        size = size / (1024**3)  # Convert from B to GB unit
        print("%2d   %11s   %2.3fGB" % ((i+1), subfolder_name, size))
    print(f"All subfolders are stored at {GSO_FOLDER}")


if __name__ == "__main__":
    main()
