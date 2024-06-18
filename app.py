# Import necessary libraries
import os
import zipfile
import requests
import streamlit as st
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

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
        return transcription_output_path  # Return path to transcription file

    except Exception as e:
        st.error(f"Error processing {os.path.basename(video_path)}: {str(e)}")
        return None

# Function to authenticate Google Drive using credentials file
def authenticate_drive(credentials_file):
    gauth = GoogleAuth()
    gauth.credentials = credentials_file.read()  # Read and set credentials
    gauth.SaveCredentialsFile("mycreds.txt")  # Save credentials locally
    drive = GoogleDrive(gauth)
    return drive

# Function to upload file to Google Drive
def upload_to_drive(drive, file_path):
    try:
        file_name = os.path.basename(file_path)
        file_drive = drive.CreateFile({'title': file_name})
        file_drive.SetContentFile(file_path)
        file_drive.Upload()
        return file_drive['id']  # Return file ID on success

    except Exception as e:
        st.error(f"Failed to upload {file_name} to Google Drive: {str(e)}")
        return None

# Main function to run the Streamlit app
def main():
    st.title("Audio and Video Processing App")

    # Google Drive API Credentials
    st.subheader("Google Drive API Credentials")
    client_id = st.text_input("Enter Client ID:")
    client_secret = st.text_input("Enter Client Secret:")
    creds_file = None
    if st.button("Authenticate"):
        try:
            gauth = GoogleAuth()
            gauth.credentials = {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": "your-refresh-token",  # Replace with your refresh token
                "access_token": "your-access-token",    # Replace with your access token
                "token_expiry": None,
                "user_agent": None,
                "revoke_uri": None,
            }
            drive = GoogleDrive(gauth)
            st.success("Authenticated successfully!")
            creds_file = "mycreds.txt"  # Use this file for future authentication
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")

    # Sidebar option to choose upload method
    upload_option = st.sidebar.selectbox("Choose upload option", 
                                         ["Process single file", "Process multiple files", 
                                          "Extract files from zip", "Download files from URL"])

    # Handling upload and processing of a single file
    if upload_option == "Process single file":
        if creds_file:
            file = st.file_uploader("Upload a single audio/video file", type=["mp4", "mkv", "wav"])
            if file:
                file_path = os.path.join("./uploaded_files", file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())
                transcript_file = process_video(file_path)
                if transcript_file:
                    st.write("Processing successful!")
                    # Upload transcript file to Google Drive
                    file_id = upload_to_drive(drive, transcript_file)
                    if file_id:
                        # Provide download link to the user
                        st.markdown(f"Download [transcription file](https://drive.google.com/uc?id={file_id})")
                    else:
                        st.error("Failed to upload transcription file to Google Drive.")
                else:
                    st.error("Processing failed.")

    # Handling upload and processing of multiple files
    elif upload_option == "Process multiple files":
        if creds_file:
            st.write("Upload multiple audio/video files")
            uploaded_files = st.file_uploader("Choose multiple files", type=["mp4", "mkv", "wav"], 
                                              accept_multiple_files=True)
            if uploaded_files:
                for file in uploaded_files:
                    file_path = os.path.join("./uploaded_files", file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.read())
                    transcript_file = process_video(file_path)
                    if transcript_file:
                        st.write(f"Processing {file.name} successful!")
                        # Upload transcript file to Google Drive
                        file_id = upload_to_drive(drive, transcript_file)
                        if file_id:
                            # Provide download link to the user
                            st.markdown(f"Download [transcription file](https://drive.google.com/uc?id={file_id})")
                        else:
                            st.error(f"Failed to upload transcription file for {file.name} to Google Drive.")
                    else:
                        st.error(f"Processing {file.name} failed.")

    # Handling extraction of files from a zip archive
    elif upload_option == "Extract files from zip":
        if creds_file:
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
                            transcript_file = process_video(file_path)
                            if transcript_file:
                                st.write(f"Processing {file} successful!")
                                # Upload transcript file to Google Drive
                                file_id = upload_to_drive(drive, transcript_file)
                                if file_id:
                                    # Provide download link to the user
                                    st.markdown(f"Download [transcription file](https://drive.google.com/uc?id={file_id})")
                                else:
                                    st.error(f"Failed to upload transcription file for {file} to Google Drive.")
                            else:
                                st.error(f"Processing {file} failed.")

    # Handling download of files from a URL (zip file containing audio/video files)
    elif upload_option == "Download files from URL":
        if creds_file:
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
                            transcript_file = process_video(file_path)
                            if transcript_file:
                                st.write(f"Processing {file} successful!")
                                # Upload transcript file to Google Drive
                                file_id = upload_to_drive(drive, transcript_file)
                                if file_id:
                                    # Provide download link to the user
                                    st.markdown(f"Download [transcription file](https://drive.google.com/uc?id={file_id})")
                                else:
                                    st.error(f"Failed to upload transcription file for {file} to Google Drive.")
                            else:
                                st.error(f"Processing {file} failed.")

