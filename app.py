import os
import zipfile
import requests
import streamlit as st
from spleeter.separator import Separator
from moviepy.editor import VideoFileClip
import speech_recognition as sr
import tensorflow as tf

# Initialize Spleeter separator
separator = Separator('spleeter:2stems')

# TensorFlow session configuration
config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)

# Helper functions for file operations
def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    with open(dest_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def remove_audio_from_video(video_path, output_format='webm'):
    video = VideoFileClip(video_path)
    video_no_audio = video.without_audio()
    output_path = os.path.splitext(video_path)[0] + f"_no_audio.{output_format}"
    video_no_audio.write_videofile(output_path, codec='libvpx' if output_format == 'webm' else 'libx264')
    return output_path

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        
    try:
        transcription = recognizer.recognize_google(audio)
        return transcription
    except sr.UnknownValueError:
        return "Transcription failed: Audio not clear."
    except sr.RequestError:
        return "Transcription failed: Could not request results."

def save_transcription(transcription, output_path):
    with open(output_path, 'w') as f:
        f.write(transcription)
    st.success(f"Transcription saved to: {output_path}")

def process_video(video_path, use_gpu=False):
    try:
        with st.spinner(f"Processing {os.path.basename(video_path)}..."):
            # Extract audio
            video = VideoFileClip(video_path)
            audio_path = os.path.splitext(video_path)[0] + '.wav'
            video.audio.write_audiofile(audio_path, codec='pcm_s16le', fps=16000)

            # Separate music from audio
            output_path = os.path.join("output", os.path.splitext(os.path.basename(video_path))[0])
            os.makedirs(output_path, exist_ok=True)

            if use_gpu:
                separator.set_gpu_memory_limit(8)  # Adjust based on your GPU memory
                separator.set_forward_device("gpu")
            else:
                separator.set_forward_device("cpu")

            separator.separate_to_file(audio_path, output_path)

            # Remove audio from video
            video_no_audio_path = remove_audio_from_video(video_path)
            video_no_audio_output_path = os.path.join(output_path, os.path.basename(video_no_audio_path))
            os.rename(video_no_audio_path, video_no_audio_output_path)

            # Transcribe audio
            transcription = transcribe_audio(audio_path)
            transcription_path = os.path.join(output_path, os.path.splitext(os.path.basename(audio_path))[0] + '.txt')
            save_transcription(transcription, transcription_path)

        st.success(f"{os.path.basename(video_path)} processing complete!")
        return True

    except Exception as e:
        st.error(f"Error processing {os.path.basename(video_path)}: {str(e)}")
        return False

def main():
    st.title("Audio and Video Processing App")

    upload_option = st.sidebar.selectbox("Choose upload option", 
                                         ["Process single file", "Process multiple files", 
                                          "Extract files from zip", "Download files from URL"])

    if upload_option == "Process single file":
        file = st.file_uploader("Upload a single audio/video file", type=["mp4", "mkv", "wav"])
        if file:
            file_path = os.path.join("./uploaded_files", file.name)
            with open(file_path, "wb") as f:
                f.write(file.read())
            use_gpu = st.sidebar.checkbox("Use GPU (if available)")
            success = process_video(file_path, use_gpu)
            if success:
                st.write("Processing successful!")
            else:
                st.error("Processing failed.")

    elif upload_option == "Process multiple files":
        st.write("Upload multiple audio/video files")
        uploaded_files = st.file_uploader("Choose multiple files", type=["mp4", "mkv", "wav"], 
                                          accept_multiple_files=True)
        if uploaded_files:
            use_gpu = st.sidebar.checkbox("Use GPU (if available)")
            for file in uploaded_files:
                file_path = os.path.join("./uploaded_files", file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())
                success = process_video(file_path, use_gpu)
                if success:
                    st.write(f"Processing {file.name} successful!")
                else:
                    st.error(f"Processing {file.name} failed.")

    elif upload_option == "Extract files from zip":
        st.write("Upload a zip file containing audio/video files")
        zip_file = st.file_uploader("Choose a zip file", type="zip")
        if zip_file:
            zip_path = os.path.join("./uploaded_zips", zip_file.name)
            with open(zip_path, "wb") as f:
                f.write(zip_file.read())
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("./input_files")

            use_gpu = st.sidebar.checkbox("Use GPU (if available)")
            for root, dirs, files in os.walk("./input_files"):
                for file in files:
                    if file.endswith('.mp4') or file.endswith('.mkv') or file.endswith('.wav'):
                        file_path = os.path.join(root, file)
                        success = process_video(file_path, use_gpu)
                        if success:
                            st.write(f"Processing {file} successful!")
                        else:
                            st.error(f"Processing {file} failed.")

    elif upload_option == "Download files from URL":
        st.write("Provide URL of the zip file containing audio/video files")
        zip_url = st.text_input("Enter URL")
        if st.button("Download"):
            zip_path = "./downloaded_files.zip"
            download_file(zip_url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("./input_files")

            use_gpu = st.sidebar.checkbox("Use GPU (if available)")
            for root, dirs, files in os.walk("./input_files"):
                for file in files:
                    if file.endswith('.mp4') or file.endswith('.mkv') or file.endswith('.wav'):
                        file_path = os.path.join(root, file)
                        success = process_video(file_path, use_gpu)
                        if success:
                            st.write(f"Processing {file} successful!")
                        else:
                            st.error(f"Processing {file} failed.")

if __name__ == "__main__":
    main()
