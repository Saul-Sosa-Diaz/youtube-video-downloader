import argparse
import logging
import subprocess
import sys
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

OUTPUT_DIR = Path("videos")
YTDLP_FORMAT = "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best"


def read_urls(csv_path: Path) -> list[tuple[str, str]]:
    """Parse a CSV file and return a list of (identifier, url) pairs.

    Expects a CSV with two columns: a video identifier and a URL. The first
    row is treated as a header and skipped automatically. Rows with missing
    values in either column are dropped.

    Args:
        csv_path: Path to the CSV file to read.

    Returns:
        A list of (identifier, url) tuples in the order they appear in the file.
    """
    df = pd.read_csv(csv_path, header=0, names=["id", "url"], dtype=str)
    df = df.dropna(subset=["identifier", "url"])
    df = df.apply(lambda col: col.str.strip())
    return list(df.itertuples(index=False, name=None))


def format_identifier(raw: str) -> str:
    """Format a video identifier as a zero-padded two-digit string.

    If the value can be interpreted as an integer it is zero-padded to at
    least two digits (e.g. '3' -> '03', '12' -> '12'). Non-numeric values
    are returned unchanged so that arbitrary identifiers still work.

    Args:
        raw: The raw identifier string read from the CSV.

    Returns:
        A zero-padded string when the input is numeric, otherwise the
        original string.
    """
    try:
        return f"{int(raw):02d}"
    except ValueError:
        return raw


def build_output_path(identifier: str) -> Path:
    """Build the output file path for a given video identifier.

    The file is placed inside OUTPUT_DIR and follows the naming convention
    ``video_<identifier>.mp4``, where <identifier> is zero-padded when possible.

    Args:
        identifier: The raw video identifier string from the CSV.

    Returns:
        A Path pointing to the expected output file.
    """
    return OUTPUT_DIR / f"video_{format_identifier(identifier)}.mp4"


def download_clip(url: str, output: Path, duration: str) -> None:
    """Download the first N minutes of a video using yt-dlp and ffmpeg.

    Delegates the actual time-cutting to ffmpeg via yt-dlp's external
    downloader interface, which avoids downloading the full video before
    trimming.

    Args:
        url: The video URL to download from.
        output: Destination file path for the resulting MP4.
        duration: The duration of the clip to download (e.g. '00:04:00').

    Raises:
        subprocess.CalledProcessError: If yt-dlp exits with a non-zero
            return code (e.g. unavailable video, network error).
    """
    cmd = [
        "yt-dlp",
        "-f",
        YTDLP_FORMAT,
        "--external-downloader",
        "ffmpeg",
        "--external-downloader-args",
        f"ffmpeg_i:-ss 00:00:00 -to {duration}",
        "-o",
        str(output),
        url,
    ]
    subprocess.run(cmd, check=True)


def download_video_clips(csv_file: str = "enlaces.csv", duration: str = "00:04:00") -> None:
    """Iterate over a CSV of video URLs and download a short clip from each.

    For every entry in the CSV, the function checks whether the output file
    already exists and skips it if so, making repeated runs safe. Downloads
    that fail are logged and skipped so the rest of the batch can continue.

    Args:
        csv_file: Path to the CSV file containing the video list. Defaults
            to 'enlaces.csv' in the current working directory. The file must
            have a header row followed by rows with two columns: identifier and url.
        duration: Timespan duration to download (format HH:MM:SS).
    """
    csv_path = Path(csv_file)

    if not csv_path.exists():
        logging.error(f"'{csv_file}' not found. Create it with columns: identifier,url")
        sys.exit(1)

    entries = read_urls(csv_path)
    if not entries:
        logging.error(f"'{csv_file}' is empty or not formatted correctly.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    total = len(entries)

    for i, (identifier, url) in enumerate(entries, start=1):
        output = build_output_path(identifier)
        prefix = f"[{i}/{total}]"

        if output.exists():
            logging.info(f"{prefix} Already downloaded, skipping: {output.name}")
            continue

        logging.info(f"{prefix} Downloading first {duration} of video #{identifier}")
        logging.info(f"  URL: {url}")

        try:
            download_clip(url, output, duration)
            logging.info(f"{prefix} Done: {output.name}")
        except subprocess.CalledProcessError as exc:
            logging.error(f"{prefix} Failed to download {url}: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download short clips from videos defined in a CSV file."
    )
    parser.add_argument(
        "csv_file",
        type=str,
        nargs="?",
        default="enlaces.csv",
        help="Path to the CSV file containing identifier and url columns (default: enlaces.csv)",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=str,
        default="00:04:00",
        help="Duration of the clip to download in HH:MM:SS format (default: 00:04:00)",
    )
    args = parser.parse_args()

    download_video_clips(args.csv_file, args.duration)
