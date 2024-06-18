# TranscriptGen 📜🎬

Welcome to TranscriptGen, a powerful and user-friendly tool designed to process and transcribe audio and video files with ease. Whether you're working with single files, multiple files, zip archives, or URLs, TranscriptGen has you covered!

## Features 🌟

- **Single File Processing**: Upload and process individual audio or video files.
- **Multiple File Processing**: Handle multiple files at once with batch processing capabilities.
- **Zip File Extraction**: Upload zip files containing multiple audio or video files for extraction and processing.
- **URL Support**: Download and process files directly from a URL.
- **Audio Transcription**: Automatically transcribe audio from video files using Google Speech Recognition.
- **CPU/GPU Support**: Optimize processing with GPU support if available, ensuring efficient resource usage.
- **User-Friendly Interface**: Intuitive and responsive UI powered by Streamlit.

## Getting Started 🚀

Follow these steps to set up and run TranscriptGen on your local machine.

### Prerequisites

- Python 3.8 or higher
- Required Python packages: `streamlit`, `spleeter`, `tensorflow`, `moviepy`, `speech_recognition`, `requests`

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/TranscriptGen.git
    cd TranscriptGen
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Running the App

Start the Streamlit app with the following command:
```bash
streamlit run app.py
```

This will launch the TranscriptGen app in your default web browser.

## Usage Guide 📖

### Upload Options

- **Process Single File**: Upload an individual audio or video file (`.mp4`, `.mkv`, `.wav`).
- **Process Multiple Files**: Upload multiple audio or video files at once.
- **Extract Files from Zip**: Upload a zip file containing multiple audio or video files.
- **Download Files from URL**: Provide a URL to download and process a zip file.

### Processing Steps

1. **Upload**: Select the appropriate upload option and provide the necessary file(s) or URL.
2. **Processing**: Wait while TranscriptGen processes your files, extracts audio, removes background music, and generates transcriptions.
3. **Transcription**: View and save the transcriptions generated from the audio.

### Options

- **Use GPU**: Enable GPU support (if available) for faster processing.

## Example Output

```plaintext
Processing example_video.mp4...
Extracting audio...
Separating background music...
Transcribing audio...
Transcription saved to: output/example_video_transcription.txt
Processing complete!
```

## Troubleshooting & FAQs 🤔

### Common Issues

- **File Not Found**: Ensure the file path is correct and the file exists.
- **Transcription Failed**: This might occur due to unclear audio or network issues when requesting results from the Google Speech Recognition API.

### FAQs

- **How do I enable GPU support?**  
  Make sure you have the necessary GPU drivers and `tensorflow-gpu` installed. Use the "Use GPU" option in the app.

- **What file formats are supported?**  
  TranscriptGen supports `.mp4`, `.mkv`, and `.wav` files.

## Contributing 🤝

Contributions are welcome! Please open an issue or submit a pull request.

## License 📄

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Thank you for using TranscriptGen! We hope it makes your transcription tasks easier and more efficient. If you have any feedback or suggestions, please feel free to reach out. Happy transcribing! 🎉
