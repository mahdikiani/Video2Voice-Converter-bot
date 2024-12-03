import asyncio
import subprocess
from pathlib import Path


async def run_command_async(command):
    process = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise subprocess.CalledProcessError(
            process.returncode, command, output=stdout, stderr=stderr
        )

    return stdout, stderr


async def convert_to_mp3(input_video: Path):
    output_audio = input_video.parent / f"ffmpeg_{input_video.stem}.mp3"
    command = [
        "ffmpeg",
        "-i",
        str(input_video),
        "-q:a",
        "0",
        "-map",
        "a",
        "-b:a",
        "32k",
        str(output_audio),
    ]

    try:
        stdout, stderr = await run_command_async(command)
        print(f"Conversion to MP3 completed: {output_audio}")
        return output_audio
    except subprocess.CalledProcessError as e:
        # Print full error details
        print("An error occurred during the conversion process.")
        print("Standard output:", e.output.decode())
        print("Standard error:", e.stderr.decode())
        raise e


async def encode_mp3_with_lame(input_file: Path, bitrate=32):
    input_file_name = input_file.stem.lstrip("ffmpeg_")
    output_file = input_file.parent / f"{input_file_name}.mp3"
    command = ["lame", "-b", str(bitrate), str(input_file), str(output_file)]

    try:
        await run_command_async(command)
        print(
            f"Successfully encoded {input_file} to {output_file} with bitrate {bitrate} kbps."
        )
        return output_file
    except subprocess.CalledProcessError as e:
        print("An error occurred during the encoding process:", e.stderr.decode())
        raise e


async def get_mp3_metadata(mp3_file: Path):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(mp3_file),
    ]

    try:
        stdout, stderr = await run_command_async(command)
        # Parse the output
        duration = float(stdout.decode().strip())  # Duration in seconds
        print(f"Duration: {duration} seconds")
        return duration
    except subprocess.CalledProcessError as e:
        print("An error occurred while retrieving metadata:", e.stderr.decode())
        raise e


# # Function to convert video to mp3
# def convert_to_mp3(input_video: Path):
#     output_audio = input_video.parent / f"ffmpeg_{input_video.stem}.mp3"
#     # (
#     #     ffmpeg.input(input_video)
#     #     .output(output_audio, qscale_a=0, acodec="libmp3lame", audio_bitrate="32k")
#     #     .run()
#     # )
#     command = [
#         "ffmpeg",
#         "-i",
#         str(input_video),
#         "-q:a",
#         "0",
#         "-map",
#         "a",
#         "-b:a",
#         "32k",
#         output_audio,
#     ]
#     try:
#         subprocess.run(command, check=True)

#         return output_audio
#     except subprocess.CalledProcessError as e:
#         print("An error occurred during the conversion process:", e)
#         raise e


# def encode_mp3_with_lame(input_file: Path, bitrate=32):
#     # Construct the LAME command
#     input_file_name = input_file.stem.lstrip("ffmpeg_")
#     output_file = input_file.parent / f"{input_file_name}.mp3"
#     command = ["lame", "-b", str(bitrate), str(input_file), str(output_file)]

#     # Execute the command using subprocess
#     try:
#         subprocess.run(command, check=True)
#         print(
#             f"Successfully encoded {input_file} to {output_file} with bitrate {bitrate} kbps."
#         )
#         return output_file
#     except subprocess.CalledProcessError as e:
#         print("An error occurred during the encoding process:", e)
#         raise e
