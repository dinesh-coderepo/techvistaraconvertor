# Tech Vistara Audio to Video Converter

This project is a web-based tool for creating videos from uploaded audio files and images using Flask and Vanilla JS.

## Local Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-name>
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

4. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   ```

5. Run the Flask application:
   ```
   flask run
   ```

6. Open a web browser and navigate to `http://localhost:5000` to use the application.

## Features

- Upload audio files (MP3, WAV, OGG, FLAC, AAC, M4A, WMA, AIFF)
- Upload image files (JPG, JPEG, PNG, GIF)
- Select video resolution and quality
- Create videos from audio and image files
- Download created videos

For detailed information about the implementation and techniques used, please refer to the [IMPLEMENTATION.md](IMPLEMENTATION.md) file.
