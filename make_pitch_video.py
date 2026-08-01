#!/usr/bin/env python3
import os
import subprocess
import shutil

# Directory containing screenshots
SCREENSHOT_DIR = "screenshots"
OUTPUT_DIR = "video_temp"
FINAL_OUTPUT = "pitch_video.mp4"

# Ensure output temp directory exists
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 13 Screenshots mapped in chronological order to narration text
STORYBOARD = [
    {
        "image": "Screenshot 2026-08-01 at 5.08.59 PM.png",
        "text": "Welcome to ER Handover Triage powered by Gemma, built for the Kaggle Build with Gemma competition."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.09.14 PM.png",
        "text": "Traditional emergency room handovers are chaotic. Verbal notes get miscommunicated, and critical medical history is often lost in transit."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.09.24 PM.png",
        "text": "Our solution creates one continuous patient record, progressively enriched across three persona-tailored views: Paramedic, Nurse, and Doctor."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.09.46 PM.png",
        "text": "In the Paramedic Intake view, EMS personnel dictate handover notes hands-free and capture injury photos during transport."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.09.59 PM.png",
        "text": "Gemma's multimodal audio and vision models instantly synthesize raw dictation into a structured clinical MIST grid."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.10.07 PM.png",
        "text": "Upon arrival, the Triage Nurse accesses the exact same live FHIR-lite patient record with zero data re-entry."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.10.15 PM.png",
        "text": "Gemma automatically extracts key medical entities, including symptoms, vitals, and current medications."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.10.22 PM.png",
        "text": "It audits the patient's last 2 to 3 prior hospital visits, automatically flagging high-risk alerts like severe drug allergies."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.10.32 PM.png",
        "text": "Gemma then executes a visible 3-step Chain-of-Verification, extracting red flags and self-critiquing to output a transparent ESI acuity score."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.11.04 PM.png",
        "text": "The ER Doctor views a live patient queue automatically prioritized by ESI acuity, ensuring critical cases are seen first."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.11.21 PM.png",
        "text": "The doctor assigns clinical staff and dictates bedside progress notes using hands-free speech recognition."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.11.37 PM.png",
        "text": "Gemma structures the doctor's assessment and automatically suggests accurate ICD-10 clinical coding."
    },
    {
        "image": "Screenshot 2026-08-01 at 5.11.58 PM.png",
        "text": "By combining multimodal Gemma reasoning with edge privacy and role-based access, Gemma Lightning Hub delivers triage in light speed."
    }
]

def get_audio_duration(audio_path):
    """Get exact duration of an audio file using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

def main():
    print("🎬 Generating pitch video clips...")
    segment_files = []

    for i, item in enumerate(STORYBOARD):
        img_path = os.path.join(SCREENSHOT_DIR, item["image"])
        audio_aiff = os.path.join(OUTPUT_DIR, f"audio_{i:02d}.aiff")
        audio_wav = os.path.join(OUTPUT_DIR, f"audio_{i:02d}.wav")
        segment_mp4 = os.path.join(OUTPUT_DIR, f"segment_{i:02d}.mp4")

        print(f"\n[Step {i+1}/13] Processing: {item['image']}")
        print(f"  Narration: '{item['text']}'")

        # 1. Generate text-to-speech audio using macOS native 'say' with Samantha voice
        subprocess.run(["say", "-v", "Samantha", "-o", audio_aiff, item["text"]], check=True)

        # 2. Convert AIFF to WAV for ffmpeg compatibility
        subprocess.run(["ffmpeg", "-y", "-i", audio_aiff, "-ac", "2", "-ar", "44100", audio_wav],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # 3. Get precise duration of generated voiceover audio
        duration = get_audio_duration(audio_wav) + 0.5  # Add 0.5s padding for natural transition
        print(f"  Audio Duration: {duration:.2f} seconds")

        # 4. Scale image to 1920x1080 (padded with black bars if needed to ensure uniform resolution)
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", img_path,
            "-i", audio_wav,
            "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black",
            "-c:a", "aac", "-b:a", "192k", "-shortest",
            segment_mp4
        ]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        segment_files.append(segment_mp4)

    # 5. Create concatenation list file for ffmpeg
    concat_list_path = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(concat_list_path, "w") as f:
        for seg in segment_files:
            f.write(f"file '{os.path.abspath(seg)}'\n")

    # 6. Concatenate all segment MP4s into final pitch video
    print("\n🎞️ Stitched all segments into final video...")
    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        FINAL_OUTPUT
    ]
    subprocess.run(concat_cmd, check=True)

    # Clean up temporary directory
    shutil.rmtree(OUTPUT_DIR)
    print(f"\n✅ Pitch video successfully created: {os.path.abspath(FINAL_OUTPUT)}")

if __name__ == "__main__":
    main()
