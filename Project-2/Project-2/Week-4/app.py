from flask import Flask, request
import os
from contract_parser import parse_contract

app = Flask(__name__)

# ✅ Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ✅ Home Page
@app.route("/")
def home():
    return "✅ Week-4 Contract Parser API Running!"


# ✅ Upload Form Page
@app.route("/form")
def form():
    return '''
    <h2>📄 Upload Contract PDF</h2>

    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <br><br>
        <input type="submit" value="Upload & Extract">
    </form>
    '''


# ✅ Upload + Extract Route
@app.route("/upload", methods=["POST"])
def upload_pdf():

    file = request.files["file"]

    # Save file
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    # Extract entities
    output = parse_contract(pdf_path)

    # Show output nicely in browser
    return f"""
    <h2>✅ File Uploaded Successfully!</h2>

    <h3>Filename: {file.filename}</h3>

    <h3>Extracted Entities (Final JSON Output):</h3>

    <pre style="font-size:16px; background:#f4f4f4; padding:15px;">
{output}
    </pre>

    <br>
    <a href="/form">⬅ Upload Another Contract</a>
    """


# ✅ Start Flask Server
if __name__ == "__main__":
    app.run(debug=True)
