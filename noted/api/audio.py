import subprocess
from pathlib import Path


def extract_audio(
    input_file: str, output_folder: str, output_file: str = None
):
    input_file = Path(input_file)
    basename = input_file.stem
    if output_file is None:
        output_file = Path(output_folder, f"{basename}_out.mp3")
    else:
        output_file = Path(output_folder, output_file)
    command = [
        "ffmpeg",
        "-i",
        input_file,
        "-vn",
        "-c:a",
        "libmp3lame",
        output_file,
    ]
    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    return output_file.name


def main():
    # Example usage
    input_video = "tmp/example.mp4"
    # output_audio = "tmp/example.mp3"
    extract_audio(input_video, "tmp")


if __name__ == "__main__":
    main()
