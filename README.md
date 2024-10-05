# Tech Vistara Audio to Video Converter

This project is a web-based tool for creating videos from uploaded audio files and images using Flask and Vanilla JS.

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

## Configuration

1. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   ```
   Replace `your_secret_key_here` with a secure random string.

2. Ensure the `uploads` directory exists in the project root:
   ```
   mkdir -p uploads/audio uploads/images uploads/videos
   ```

## Running the Application

1. Activate the virtual environment if not already active:
   ```
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

2. Start the Flask application:
   ```
   flask run
   ```

3. Open a web browser and navigate to `http://localhost:5000` to use the application.

## Troubleshooting

### Common Issues and Solutions

1. **FFmpeg not found**: Ensure FFmpeg is installed and added to your system's PATH.
2. **File upload errors**: Check if the `uploads` directory and its subdirectories exist and have the correct permissions.
3. **Video creation fails**: Verify that the uploaded audio and image files are not corrupted and are in supported formats.

### Checking Logs

- Application logs are printed to the console where you run the Flask server.
- For more detailed logging, you can modify the logging level in `app.py`:
  ```python
  app.logger.setLevel(logging.DEBUG)
  ```

## Development

### Running Tests

Currently, there are no automated tests for this project. This is an area for potential improvement.

### Contributing to the Project

1. Fork the repository on GitHub.
2. Clone your forked repository locally.
3. Create a new branch for your feature or bug fix.
4. Make your changes and commit them with clear, concise commit messages.
5. Push your changes to your fork on GitHub.
6. Create a pull request from your fork to the main repository.

## Features

- Upload audio files (MP3, WAV, OGG, FLAC, AAC, M4A, WMA, AIFF)
- Upload image files (JPG, JPEG, PNG, GIF)
- Select video resolution and quality
- Create videos from audio and image files
- Download created videos

For detailed information about the implementation and techniques used, please refer to the [IMPLEMENTATION.md](IMPLEMENTATION.md) file.
