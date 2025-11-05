# Gallery Size Organizer (GSO) for Google Drive Backup
a
A Python script to organize phone gallery for free-tier Google Drive backup.

## Features
- 🎞️ Organize photos and videos into folders
- 📦 Google Drive backup ready
    - Each folder contains max 15GB for free-tier Google Drive storage
- ⚡ Simple and fast

#### Google Drive Backup
The main purpose of the script's inception is to support a frugal digital life. With **zero-cost overhead**, this script allows you to:
1. **Backup** photos and videos into multiple free-tier Google account
    - It works by organizing files into multiple folders, each with max **15GB** size (as Google Drive offers free 15GB storage only) 
2. Backup each folder into **separate Google account**
3. **Systematically sort** the files by making each folder contains file from a start data until an end date in ascending order.

> ***NOTE:*** It's recommended that this method is only used for backups, not for everyday access. Keep a copy on your own device and treat this method for backups.

## Installation
To setup this script on your phone:
1. Download [Pydroid](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3&hl=en) on your phone.
2. Ensure file permission is granted for the application.
3. Copy and paste the [script]() into the application's code editor.
4. Save the file as `gso.py`

## Usage
Open the terminal and run:
```bash
python gso.py
```

## Supported Devices
- Most Android phones
- Works with Pydroid 3 and Termux
- Requires storage permissions

## License
MIT License - see [LICENSE]() file for details
