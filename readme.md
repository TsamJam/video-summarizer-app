# Video Summarizer AI

This web application uses the Google Gemini API to generate summaries of videos from URLs (e.g., Instagram). It works by downloading the video, extracting keyframes, analyzing each frame, and then creating a final summary of the content.

## Prerequisites

- Python 3.8+
- `pip` (Python package installer)

## Setup Instructions

1.  **Create Project Directory:**
    Create a folder named `video-summarizer-app` and place the files (`app.py`, `requirements.txt`, etc.) inside it according to the project structure.

2.  **Create a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage dependencies.

    ```bash
    # Navigate into your project directory
    cd video-summarizer-app

    # Create a virtual environment
    python -m venv venv

    # Activate the virtual environment
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Install all the required Python libraries from the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

## How to Get Your `cookies.txt` File

To download content from sites like Instagram, `yt-dlp` needs you to be logged in. You can provide your browser's login session via a cookies file.

1.  Install a browser extension that can export cookies. A recommended one is **"Get cookies.txt LOCALLY"** (available for Chrome and Firefox).
2.  Navigate to the website (e.g., `instagram.com`) and log in.
3.  Click the extension's icon and export the cookies. Save the file as `cookies.txt`.
4.  You will upload this file using the web interface.

**Note:** Your cookies contain sensitive login information. Handle this file securely and do not share it.

## Running the Application

1.  Make sure your virtual environment is activated.
2.  Run the Flask application from your terminal:

    ```bash
    flask run
    ```

3.  Open your web browser and go to `http://127.0.0.1:5000`.

## How to Use

1.  Enter your **Google AI API Key** in the first input field.
2.  Enter the full **URL of the video** you want to summarize.
3.  Click "Choose File" and upload the `cookies.txt` file you exported.
4.  Click the **"Summarize Video"** button and wait for the process to complete.