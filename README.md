# GolfSwing
A personal project for tracking golf swings and offering swing improvement

Best when the camera is in front of you and hase a great clear view of the users full body, club, and ball. DO NOT USE WITH SLOWMOTION. 

GOLFSWING PROJECT - SETUP GUIDE
-------------------------------

🧱 REQUIREMENTS:
- Python 3.11 or newer
- Git (optional)
- A terminal (Command Prompt, PowerShell, or bash)
- Basic understanding of command line

📁 1. UNZIP & NAVIGATE TO PROJECT
Unzip the project folder and go into it:

    cd GolfSwing

🌱 2. CREATE A VIRTUAL ENVIRONMENT
(Recommended for dependency isolation)

Windows:

    python -m venv .venv
    .venv\Scripts\activate

macOS/Linux:

    python3 -m venv .venv
    source .venv/bin/activate

📦 3. INSTALL DEPENDENCIES

Run the following command in the activated virtual environment:

    pip install flask opencv-python numpy mediapipe

Or if using a `requirements.txt`:

    pip install -r requirements.txt

🛠 If you don’t have one yet, you can generate it later with:

    pip freeze > requirements.txt

▶️ 4. RUN THE APPLICATION

Start the Flask app:

    python app.py

You’ll see something like:

    * Running on http://127.0.0.1:5000

Open that URL in your web browser to use the app.

🧪 5. VERIFY FUNCTIONALITY

Try uploading a video through the web UI.
If the console prints:

    ❌ Error: Could not open video.

Ensure the uploaded file is:
- A supported format (`.mp4`, `.mov`, etc.)
- Not corrupted
- Properly saved in the `uploads/` directory

✅ 6. DONE!

🎉 Your GolfSwing analyzer is now live locally.
You can start testing swing uploads and analyzing your mechanics.

---


