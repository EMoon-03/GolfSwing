from flask import Flask, render_template, request
import os
import time
from swing_analyzer import analyze_swing

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def clean_old_videos(folder, keep_filename):
    for file in os.listdir(folder):
        if file.endswith('.mp4') and file != keep_filename:
            try:
                os.remove(os.path.join(folder, file))
            except Exception as e:
                print(f"Could not delete {file}: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        club = request.form['club']

        if uploaded_file and uploaded_file.filename.endswith('.mp4'):
            # Create a unique timestamp for file naming
            timestamp = str(int(time.time()))
            input_filename = f"user_video_{timestamp}.mp4"
            video_path = os.path.join(UPLOAD_FOLDER, input_filename)
            uploaded_file.save(video_path)

            # Clean up old uploaded videos
            clean_old_videos(UPLOAD_FOLDER, input_filename)

            # Run analyzer and save to default name
            analysis_text, _ = analyze_swing(video_path, OUTPUT_FOLDER, club)

            # Rename output to a timestamped version to avoid browser cache
            default_output = os.path.join(OUTPUT_FOLDER, 'annotated_swing.mp4')
            output_filename = f"annotated_swing_{timestamp}.mp4"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            if os.path.exists(default_output):
                os.rename(default_output, output_path)

            # Clean up all other annotated videos except this one
            clean_old_videos(OUTPUT_FOLDER, output_filename)

            return render_template('index.html',
                                   analysis=analysis_text,
                                   video_file=output_filename)
        else:
            return "❌ Please upload a .mp4 file."
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)