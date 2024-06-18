import os
import zipfile
import requests
import streamlit as st
from moviepy.editor import VideoFileClip
import speech_recognition as sr

# Helper function to download a file from URL
def download_file(url, dest_path):
    with st.spinner(f"Downloading {os.path.basename(dest_path)}..."):
        response = requests.get(url, stream=True)
        with open(dest_path, 'wb') as file:
            total_length = int(response.headers.get('content-length'))
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                progress = file.tell() / total_length
                st.progress(progress)
        st.success(f"{os.path.basename(dest_path)} downloaded successfully!")

# Function to transcribe audio using Google Web API
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        
    try:
        with st.spinner("Transcribing audio..."):
            transcription = recognizer.recognize_google(audio)
        return transcription
    except sr.UnknownValueError:
        return "Transcription failed: Audio not clear."
    except sr.RequestError:
        return "Transcription failed: Could not request results."

# Function to save transcription to a text file
def save_transcription(transcription, output_path):
    with open(output_path, 'w') as f:
        f.write(transcription)
    st.success(f"Transcription saved to: {os.path.basename(output_path)}")

# Function to process video: extract audio and transcribe
def process_video(video_path):
    try:
        with st.spinner(f"Processing {os.path.basename(video_path)}..."):
            # Extract audio
            video = VideoFileClip(video_path)
            audio_path = os.path.join("output", os.path.splitext(os.path.basename(video_path))[0] + '.wav')
            video.audio.write_audiofile(audio_path, codec='pcm_s16le', fps=16000)

            # Transcribe audio
            transcription = transcribe_audio(audio_path)
            transcription_output_path = os.path.join("output", os.path.splitext(os.path.basename(audio_path))[0] + '.txt')
            save_transcription(transcription, transcription_output_path)

        st.success(f"{os.path.basename(video_path)} processing complete!")
        return True

    except Exception as e:
        st.error(f"Error processing {os.path.basename(video_path)}: {str(e)}")
        return False

# Main function to run the Streamlit app
def main():
    st.title("Audio and Video Processing App")

    # Sidebar option to choose upload method
    upload_option = st.sidebar.selectbox("Choose upload option", 
                                         ["Process single file", "Process multiple files", 
                                          "Extract files from zip", "Download files from URL"])

    # Handling upload and processing of a single file
    if upload_option == "Process single file":
        file = st.file_uploader("Upload a single audio/video file", type=["mp4", "mkv", "wav"])
        if file:
            file_path = os.path.join("./uploaded_files", file.name)
            with open(file_path, "wb") as f:
                f.write(file.read())
            success = process_video(file_path)
            if success:
                st.write("Processing successful!")
                # Add download button for transcription output file
                st.download_button(
                    label="Download Transcription",
                    data=open(os.path.join("output", os.path.splitext(file.name)[0] + '.txt'), 'rb').read(),
                    file_name=os.path.splitext(file.name)[0] + '.txt'
                )
            else:
                st.error("Processing failed.")

    # Handling upload and processing of multiple files
    elif upload_option == "Process multiple files":
        st.write("Upload multiple audio/video files")
        uploaded_files = st.file_uploader("Choose multiple files", type=["mp4", "mkv", "wav"], 
                                          accept_multiple_files=True)
        if uploaded_files:
            for file in uploaded_files:
                file_path = os.path.join("./uploaded_files", file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())
                success = process_video(file_path)
                if success:
                    st.write(f"Processing {file.name} successful!")
                else:
                    st.error(f"Processing {file.name} failed.")

            # Create a zip file containing all transcription output files
            zip_path = "./output_files.zip"
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for root, _, files in os.walk("./output"):
                    for file in files:
                        if file.endswith('.txt'):
                            zip_file.write(os.path.join(root, file), arcname=file)

            # Add download button for the zip file
            st.download_button(
                label="Download All Transcriptions as Zip",
                data=open(zip_path, 'rb').read(),
                file_name="output_files.zip"
            )

    # Handling extraction of files from a zip archive
    elif upload_option == "Extract files from zip":
        st.write("Upload a zip file containing audio/video files")
        zip_file = st.file_uploader("Choose a zip file", type="zip")
        if zip_file:
            zip_path = os.path.join("./uploaded_zips", zip_file.name)
            with open(zip_path, "wb") as f:
                f.write(zip_file.read())
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("./input_files")

            for root, dirs, files in os.walk("./input_files"):
                for file in files:
                    if file.endswith('.mp4') or file.endswith('.mkv') or file.endswith('.wav'):
                        file_path = os.path.join(root, file)
                        success = process_video(file_path)
                        if success:
                            st.write(f"Processing {file} successful!")
                        else:
                            st.error(f"Processing {file} failed.")

    # Handling download of files from a URL (zip file containing audio/video files)
    elif upload_option == "Download files from URL":
        st.write("Provide URL of the zip file containing audio/video files")
        zip_url = st.text_input("Enter URL")
        if st.button("Download"):
            zip_path = "./downloaded_files.zip"
            download_file(zip_url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("./input_files")

            for root, dirs, files in os.walk("./input_files"):
                for file in files:
                    if file.endswith('.mp4') or file.endswith('.mkv') or file.endswith('.wav'):
                        file_path = os.path.join(root, file)
                        success = process_video(file_path)
                        if success:
                            st.write(f"Processing {file} successful!")
                        else:
                            st.error(f"Processing {file} failed.")

if __name__ == "__main__":
    main()
