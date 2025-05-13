📘 AI-Assisted Grading Tool
This Python desktop application automates the grading of software testing assignments using OpenAI’s GPT-3.5 API. It allows instructors to process student .docx reports and .java test files in batch, generate rubric-aligned feedback, and save results as structured PDF files.

Developed as part of a Final Year Project at Queen’s University Belfast (CSC4006).

🚀 Features
Batch processing of student lab submissions

Uploads files to Dropbox and retrieves public file links

Dynamically constructs grading prompts using GPT-3.5

Saves AI-generated feedback as PDF

GUI with light/dark mode toggle

Real-time logging of each grading step

Unit-tested utility logic

📂 Folder Structure
AIGradingTool/
├── src/                   # Main application code
│   ├── grading_tool_gui.py
│   ├── style.py
│   └── main.py
├── tests/                 # Unit tests
│   └── test_core_logic.py
├── docs/                  # Documentation - example prompts
├── requirements.txt       # Python dependencies
├── config_template.json   # Example config file (see below)
└── README.md              

🔧 Installation
1. Clone the Repository
git clone https://gitlab.eeecs.qub.ac.uk/40298772/ai-assisted-grading-tool
cd ai-assisted-grading-tool

2. Set Up a Virtual Environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

3. Install Dependencies
pip install -r requirements.txt


🔑 Configuration
To enable file uploads and sharing via Dropbox, you must create a developer app and generate an access token:

Step 1: Create a Dropbox Developer App
🔗 [Dropbox App Console](https://www.dropbox.com/developers/apps)
-Click "Create app"
-Choose:
    Scoped access
    App folder (recommended — access is limited to its own folder)
-Name your app (e.g., AI Grading Tool Dataset)
-Click "Create app"

Step 2: Generate an Access Token
-In your app dashboard, scroll to OAuth 2
-Click "Generate access token"
-Copy and securely store the token
-Create config.json and paste token into your config.json like this:

{
  "openai_api_key": "your-openai-api-key",
  "dropbox_access_token": "your-dropbox-access-token"
}

Step 3: Set Required Permissions
-Go to Permissions in the sidebar
-Enable:
    ✅ files.content.write
    ✅ files.content.read
    ✅ sharing.write
-Scroll down and click Submit to save changes

🧪 Running Unit Tests
To run tests:
pytest tests/

These test:
- Folder name parsing
- Regex matching
- PDF feedback generation

🖼️ Usage Instructions
1. Launch the application:
python src/main.py

2. Select the Input Folder: 
Should contain format of:
GX_Report.docx
GX_RangeTest.java
GX_DataUtilitiesTest.java
LabX_prompt.txt

3. Select the Output Folder

4. Click "Process" to begin grading

5. Click "View Feedback" to open the folder containing the generated PDFs

📄 License
This project is for academic research and educational use only.

👨‍💻 Author
Name: Niall Hurson

Student ID: 40298772

Course: MEng Computer Science, Queen’s University Belfast

Supervisor: Dr. Vahid Garousi

(Please Note Github does not contain reports/ code files as these are confidential - access must be requested from supervisor)