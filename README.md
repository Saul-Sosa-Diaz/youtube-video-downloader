# Video Downloader CLI

An automated Python script designed to download specific segments of videos from a list provided in a `.csv` file.

This program leverages `yt-dlp` and delegates the time-slicing logic directly to `ffmpeg`. This approach **prevents the program from downloading the entire video**, saving massive amounts of time and bandwidth by fetching only the explicitly requested fragments.

## System Requirements

Before you begin, ensure the following core tools are installed on your base system:

* **Python 3.8+**
* **FFmpeg** (essential tool used for downloading video slices on-the-fly).

**Install FFmpeg on Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Install FFmpeg on macOS:**
```bash
brew install ffmpeg
```

## Setup Python Environment

It relies on a few major libraries. We highly recommend using a virtual environment to avoid conflicts with your system's global libraries:

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate the virtual environment
# (On Windows use: venv\Scripts\activate)
source venv/bin/activate

# 3. Install required Python packages
pip install pandas yt-dlp
```

## CSV File Format

The script requires a `.csv` (comma-separated values) file containing the list of videos you want to download. The file must follow these rules:

1. **Two Columns**: The first column must be an `identifier` (e.g., number, ID, or text name), and the second column must be the video `url`.
2. **Header Row**: The first row will always be parsed as a header and skipped, regardless of its text.
3. **Number padding**: If the identifier happens to be a plain number (e.g., `1`, `2`), the script will automatically pad it with a zero to keep sorting clean (e.g., `video_01.mp4`, `video_02.mp4`).

**Example `links.csv` file:**
```csv
id,url
1,https://www.youtube.com/watch?v=dQw4w9WgXcQ
2,https://www.youtube.com/watch?v=EjemploDeURL
MyVideo,https://www.youtube.com/watch?v=AnotherExample
```

## Usage

Start the batch download by calling the python script.

### Default Execution
Without any arguments, the script will look for an `links.csv` file in the current directory and download the first 4 minutes (`00:04:00`) of every video.

```bash
python3 download_videos.py
```

### Specifying the CSV File
You can provide the name of your CSV explicitly as the first argument:

```bash
python3 download_videos.py my_video_list.csv
```

### Changing the Download Duration (`--duration`)
Use the `--duration` or `-d` flag to adjust the length of the clip to be downloaded. You must write it in the format `HH:MM:SS`.

**Example: Download only the first 30 seconds of each video**
```bash
python3 download_videos.py my_video_list.csv --duration 00:00:30
```

**Example: Download the first 10 minutes**
```bash
python3 download_videos.py links.csv -d 00:10:00
```

### Help Menu
If you forget the arguments, bring up the help screen at any time:
```bash
python3 download_videos.py --help
```

## Output Specifics
1. **Directory:** The downloaded videos will be automatically deposited in a `videos/` directory, which will be created if it doesn't exist.
2. **Resuming/Skipping:** If you cancel the execution (e.g., pressing `Ctrl+C`), the next time you run the script, it will scan the output folder and automatically skip the videos that have already been fully downloaded.
3. **Quality:** By default, it grabs standard up to 1080p MP4 formats combined with the best audio available.
