# Tech Vistara Audio to Video Converter

This project is a web-based tool for creating videos from uploaded audio files and images using Flask and Vanilla JS.

## Features

1. **Audio Upload**: Users can upload audio files in various formats (MP3, WAV, OGG, FLAC, AAC, M4A, WMA, AIFF) with a maximum size of 5MB.
2. **Image Upload**: Users can upload image files (JPG, JPEG, PNG, GIF) with a maximum size of 10MB.
3. **File Management**: The application provides a list of uploaded audio, image, and video files for easy selection.
4. **Video Creation**: Users can create videos by combining uploaded audio and image files.
5. **Customization Options**: Users can select video resolution (480p, 720p, 1080p) and quality (low, medium, high).
6. **Progress Tracking**: Real-time progress updates during video creation.
7. **Video Download**: Users can download the created videos.
8. **Automatic Cleanup**: Old files are automatically removed after 1 hour to manage storage.

## Prerequisites

- Python 3.8 or higher
- FFmpeg 4.2 or higher
- Git (for cloning the repository)

### System-specific requirements

- **Windows**: Install FFmpeg using Chocolatey or download from the official website.
- **macOS**: Install FFmpeg using Homebrew: `brew install ffmpeg`
- **Linux**: Install FFmpeg using your distribution's package manager, e.g., `sudo apt-get install ffmpeg` for Ubuntu/Debian.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/tech-vistara-audio-to-video.git
   cd tech-vistara-audio-to-video
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install FFmpeg:
   - Windows: `choco install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg`

5. Set up the project structure:
   ```
   mkdir -p uploads/audio uploads/images uploads/videos
   ```

## Configuration

1. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   ```
   Replace `your_secret_key_here` with a secure random string.

2. Configure file size limits (optional):
   In `app.py`, you can adjust the `MAX_AUDIO_SIZE` and `MAX_IMAGE_SIZE` variables to change the maximum allowed file sizes.

## Usage

1. Start the Flask application:
   ```
   flask run
   ```

2. Open a web browser and navigate to `http://localhost:5000`.

3. Upload an audio file:
   - Click on the "Choose File" button in the "Upload Audio" section.
   - Select an audio file (MP3, WAV, OGG, FLAC, AAC, M4A, WMA, AIFF).
   - Click the "Upload Audio" button.

4. Upload an image file:
   - Click on the "Choose File" button in the "Upload Image" section.
   - Select an image file (JPG, JPEG, PNG, GIF).
   - Click the "Upload Image" button.

5. Create a video:
   - Select the uploaded audio and image files from the dropdown menus.
   - Choose the desired video resolution and quality.
   - Click the "Create Video" button.
   - Wait for the video creation process to complete (progress will be shown).

6. Download the created video:
   - Once the video is created, a download link will appear.
   - Click the "Download Video" button to save the video to your device.

## File Conversion Process

This application uses FFmpeg for video creation. The process involves the following steps:

1. An image file is looped to create a static video background.
2. The audio file is added to the video as a soundtrack.
3. The video is encoded using the H.264 codec for wide compatibility.
4. The audio is encoded using the AAC codec for high-quality sound.
5. The video is scaled to the selected resolution and bit rate is adjusted based on the chosen quality.

## Troubleshooting

1. **FFmpeg not found**: Ensure FFmpeg is installed and added to your system's PATH.
   - Solution: Reinstall FFmpeg and restart your computer.

2. **File upload errors**: Check if the `uploads` directory and its subdirectories exist and have the correct permissions.
   - Solution: Manually create the directories or run `mkdir -p uploads/audio uploads/images uploads/videos`.

3. **Video creation fails**: Verify that the uploaded audio and image files are not corrupted and are in supported formats.
   - Solution: Try uploading different audio or image files.

4. **'No video parameters found' error**: This can occur if the session data is lost.
   - Solution: Clear your browser cache and try again.

5. **Performance issues**: If the server is slow, it might be due to processing large files.
   - Solution: Try using smaller audio files or lower resolution images.

## Contributing

We welcome contributions to improve the Tech Vistara Audio to Video Converter! Here's how you can contribute:

1. Fork the repository on GitHub.
2. Clone your forked repository locally.
3. Create a new branch for your feature or bug fix.
4. Make your changes and commit them with clear, concise commit messages.
5. Push your changes to your fork on GitHub.
6. Create a pull request from your fork to the main repository.
7. Describe your changes in the pull request description.
8. Wait for a maintainer to review your pull request and address any feedback.

Please ensure that your code adheres to the existing style of the project to make the review process faster.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

