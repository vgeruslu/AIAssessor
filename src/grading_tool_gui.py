import sys
import os
import re
import json
import openai
import dropbox
from fpdf import FPDF
from style import GradingToolStyles  # Import the stylesheet class
from PyQt6.QtCore import QThreadPool, QRunnable, pyqtSignal, QObject
import subprocess
import platform


# Load the API key from config.json
##with open("config.json", "r") as config_file:
   ## config = json.load(config_file)
    ##openai.api_key = config["openai_api_key"]
   ## dropbox_token = config["dropbox_access_token"]


from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget, QFileDialog, QTextEdit, QMessageBox
)

class WorkerSignals(QObject):
    """Defines signals for the worker thread to communicate with the main UI thread."""
    log_signal = pyqtSignal(str)  # Signal for updating logs
    finished_signal = pyqtSignal()  # Signal when processing is done

class GradingWorker(QRunnable):
    """Worker thread for processing files asynchronously."""
    def __init__(self, files, folder_path, lab_number, log_callback, main_window):
        super().__init__()
        self.files = files
        self.folder_path = folder_path
        self.lab_number = lab_number
        self.signals = WorkerSignals()
        self.log_callback = log_callback  # Function to update logs in UI
        self.main_window = main_window  # Reference to main window for calling its methods

    def run(self):
        """Runs the grading process in a background thread."""
        self.log_callback(f"\n========================")
        self.log_callback(f"📂 Processing Lab {self.lab_number} Reports")
        self.log_callback(f"========================\n")

        range_test_links = {}
        data_utilities_test_links = {}

        # 🟢 If it's Lab 2 or Lab 3, handle Java files first
        if self.lab_number in [2, 3]:
            self.log_callback(f"\n========================")
            self.log_callback(f"🔄 Uploading Java Test Files for Lab {self.lab_number}")
            self.log_callback(f"========================\n")

            for file in self.files:
                file_path = os.path.join(self.folder_path, file)

                if file.endswith(".java"):
                    if re.match(r"(?i)[Gg]\d+.*RangeTest\.java", file):
                        self.log_callback(f"📤 Uploading: {file}")
                        range_test_links[file] = self.main_window.upload_to_dropbox(file_path, self.lab_number)

                    elif re.match(r"(?i)[Gg]\d+.*DataUtilitiesTest\.java", file):
                        self.log_callback(f"📤 Uploading: {file}")
                        data_utilities_test_links[file] = self.main_window.upload_to_dropbox(file_path, self.lab_number)

        # 🟢 Process `.docx` reports
        for file in self.files:
            file_path = os.path.join(self.folder_path, file)

            if file.endswith(".docx") and re.match(r"[Gg]\d+.*\.docx", file):
                self.log_callback(f"\n📄 Found Report: {file}")

                try:
                    # Upload report to Dropbox
                    report_link = self.main_window.upload_to_dropbox(file_path, self.lab_number)

                    if not report_link:
                        self.log_callback(f"🚫 Skipping {file} (Already Exists in Dropbox)\n")
                        continue

                    self.log_callback(f"📤 Uploaded to Dropbox: {report_link}\n")

                    # Load Lab-specific grading prompt
                    prompt_path = os.path.join(self.folder_path, f"Lab{self.lab_number}_prompt.txt")
                    if not os.path.exists(prompt_path):
                        raise FileNotFoundError(f"❌ Prompt file not found: {prompt_path}")

                    with open(prompt_path, "r") as prompt_file:
                        lab_prompt = prompt_file.read()

                    # Extract Java file links for Lab 2 and Lab 3
                    range_test_link = None
                    data_utilities_test_link = None

                    if self.lab_number in [2, 3]:
                        group_number = re.match(r"[Gg](\d+)", file).group(1)
                        range_test_link = range_test_links.get(f"G{group_number}_RangeTest.java") or range_test_links.get(f"g{group_number}_RangeTest.java")
                        data_utilities_test_link = data_utilities_test_links.get(f"G{group_number}_DataUtilitiesTest.java") or data_utilities_test_links.get(f"g{group_number}_DataUtilitiesTest.java")

                    # 🟢 Send all relevant file links to ChatGPT
                    self.log_callback(f"💬 Sending Report to ChatGPT for Grading...")
                    feedback = self.main_window.get_chatgpt_feedback(report_link, lab_prompt, range_test_link, data_utilities_test_link)

                    # 🟢 Save feedback to PDF in the output folder
                    output_folder = self.main_window.output_text.text()
                    output_path = os.path.join(output_folder, f"{file.replace('.docx', '_Feedback.pdf')}")
                    self.main_window.save_feedback_to_pdf(feedback, output_path, file)

                    # 🟢 Log success
                    self.log_callback(f"✅ Feedback Saved: {output_path}\n")

                except Exception as e:
                    self.log_callback(f"\n⚠️ ERROR: ChatGPT API Failed for {file}")
                    self.log_callback(f"❗ {e}\n")

        self.signals.finished_signal.emit()  # Notify UI when done

class GradingTool(QMainWindow):
    def __init__(self):
        super().__init__()

        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                openai.api_key = config["openai_api_key"]
                self.dropbox_token = config["dropbox_access_token"]
        except FileNotFoundError:
            print("⚠️ config.json not found. Dropbox and OpenAI will not work in this session.")
            self.dropbox_token = None

        #self.dropbox_token = dropbox_token

        # Create a thread pool
        self.thread_pool = QThreadPool()

        # Set up the main window
        self.setWindowTitle("AI-Assisted Grading Tool")
        self.setGeometry(100, 100, 850, 650)

        # Default to Light Mode
        self.is_dark_mode = False
        self.apply_styles()

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Mode Toggle Button
        self.mode_toggle_button = QPushButton("🌙 Switch to Dark Mode")
        self.mode_toggle_button.setObjectName("switchModeButton")  # Assign ID
        self.mode_toggle_button.clicked.connect(self.toggle_mode)
        self.layout.addWidget(self.mode_toggle_button)

        # Input folder selection
        self.input_label = QLabel("📂 Input folder (Submissions):")
        self.layout.addWidget(self.input_label)

        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Select the folder containing lab submissions...")
        self.layout.addWidget(self.input_text)

        self.input_button = QPushButton("Browse")
        self.input_button.setObjectName("browseButton")  # Assign ID
        self.input_button.clicked.connect(self.browse_input_folder)
        self.layout.addWidget(self.input_button)

        # Output folder selection
        self.output_label = QLabel("📁 Output folder (Grades & Feedback):")
        self.layout.addWidget(self.output_label)

        self.output_text = QLineEdit()
        self.output_text.setPlaceholderText("Select where feedback files will be stored...")
        self.layout.addWidget(self.output_text)

        self.output_button = QPushButton("Browse")
        self.output_button.setObjectName("browseButton")  # Assign ID
        self.output_button.clicked.connect(self.browse_output_folder)
        self.layout.addWidget(self.output_button)

        # Process button
        self.process_button = QPushButton("🚀 Process")
        self.process_button.setObjectName("processButton")  # Assign ID
        self.process_button.clicked.connect(self.process_files)
        self.layout.addWidget(self.process_button)

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.layout.addWidget(self.log_area)

        # View Feedback button
        self.view_pdf_button = QPushButton("📄 View AI Feedback Output Folder")
        self.view_pdf_button.setObjectName("viewPDFButton")
        self.view_pdf_button.clicked.connect(self.open_pdf_viewer)
        self.layout.addWidget(self.view_pdf_button)

    def open_pdf_viewer(self):
        """Opens the output folder in the system's file explorer."""
        output_folder = self.output_text.text()

        if not os.path.exists(output_folder):
            QMessageBox.warning(self, "Error", "Output folder does not exist!")
            return

        try:
            if platform.system() == "Windows":
                os.startfile(output_folder)  # ✅ Corrected for Windows
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", output_folder])
            else:  # Linux
                subprocess.run(["xdg-open", output_folder])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder: {e}")

    def apply_styles(self):
        """Applies the current theme based on is_dark_mode"""
        if self.is_dark_mode:
            self.setStyleSheet(GradingToolStyles.get_dark_stylesheet())
        else:
            self.setStyleSheet(GradingToolStyles.get_light_stylesheet())

    def toggle_mode(self):
        """Switch between Light Mode and Dark Mode"""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_styles()

        # Change button text/icon accordingly
        if self.is_dark_mode:
            self.mode_toggle_button.setText("🌞 Switch to Light Mode")
        else:
            self.mode_toggle_button.setText("🌙 Switch to Dark Mode")
    

    def browse_input_folder(self):
        """Open a file dialog to select the input folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_text.setText(folder)

    def browse_output_folder(self):
        """Open a file dialog to select the output folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_text.setText(folder)

    def process_files(self):
        """Process files using multi-threading to prevent UI freezing."""
        input_folder = self.input_text.text()
        output_folder = self.output_text.text()

        # Validate folders
        if not os.path.exists(input_folder):
            self.log_area.append("Error: Input folder does not exist.")
            return
        if not os.path.exists(output_folder):
            self.log_area.append("Error: Output folder does not exist.")
            return

        # Determine which lab is being processed
        lab_name = self.get_lab_name(input_folder)
        if not lab_name:
            self.log_area.append("Error: Could not determine the lab name from the input folder.")
            return

        self.log_area.append(f"\nProcessing {lab_name}...")

        match = re.search(r"Lab\s*(\d+)", lab_name, re.IGNORECASE)
        if match:
            lab_number = int(match.group(1))
            files = os.listdir(input_folder)

            # Use a worker thread to process files
            worker = GradingWorker(files, input_folder, lab_number, self.update_log, self)
            worker.signals.finished_signal.connect(self.on_processing_complete)

            self.thread_pool.start(worker)
        else:
            self.log_area.append("Error: Unknown lab name.")

    def update_log(self, message):
        """Updates the log area from the worker thread."""
        self.log_area.append(message)
        self.log_area.ensureCursorVisible()  # Auto-scroll to the latest log

    def on_processing_complete(self):
        """Called when the worker thread finishes processing."""
        self.log_area.append("\n✅ Processing Completed!")

    def get_lab_name(self, folder_path):
        """Parse the lab name from the folder path."""
        match = re.search(r"Lab\s*(\d+)", folder_path, re.IGNORECASE)
        return f"Lab {match.group(1)}" if match else None

   
    def save_feedback_to_pdf(self, feedback, output_path, file_name):
        """Save feedback content to a PDF file."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Feedback for {file_name}", ln=True, align="C")
        pdf.ln(10)  # Add spacing

        # Add feedback content
        for line in feedback.split("\n"):
            pdf.multi_cell(0, 10, txt=line)
        pdf.output(output_path)

   
    def get_chatgpt_feedback(self, report_link, lab_prompt, range_test_link=None, data_utilities_test_link=None):
        """Send a prompt to OpenAI's ChatGPT API and retrieve feedback."""
        try:
            client = openai.OpenAI(api_key=openai.api_key)  # Create an API client

            # Construct prompt
            file_links_text = f"The lab report is available at {report_link}."
            if range_test_link:
                file_links_text += f"\nThe RangeTest.java file is available at {range_test_link}."
            if data_utilities_test_link:
                file_links_text += f"\nThe DataUtilitiesTest.java file is available at {data_utilities_test_link}."

            prompt = f"{file_links_text}\n\n{lab_prompt}"

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI grading assistant. Provide detailed feedback on lab reports and Java test files."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Error with ChatGPT API: {e}")

            
    def upload_to_dropbox(self, file_path, lab_number):
        """Uploads a file to Dropbox under a specific Lab folder and retrieves an existing link if available."""
        try:
            dbx = dropbox.Dropbox(self.dropbox_token)
            folder_path = f"/AI Grading Tool Dataset/Lab {lab_number}"
            file_name = f"{folder_path}/{os.path.basename(file_path)}"

            # Check if file already exists in Dropbox
            try:
                metadata = dbx.files_get_metadata(file_name)
                self.log_area.append(f"File already exists: {file_name}")
                
                # Retrieve existing shared link instead of creating a new one
                shared_links = dbx.sharing_list_shared_links(file_name).links
                if shared_links:
                    return shared_links[0].url.replace("?dl=0", "?raw=1")  # Return existing link

            except dropbox.exceptions.ApiError as e:
                if e.error.is_path() and e.error.get_path().is_not_found():
                    pass  # File does not exist, proceed with upload

            # Upload the file (only if it doesn’t exist)
            with open(file_path, "rb") as f:
                dbx.files_upload(f.read(), file_name, mode=dropbox.files.WriteMode("overwrite"))

            # Create a new shared link
            link = dbx.sharing_create_shared_link_with_settings(file_name).url
            return link.replace("?dl=0", "?raw=1")  # Direct download link

        except Exception as e:
            raise RuntimeError(f"Failed to upload {file_path} to Dropbox: {e}")

# Entry point for the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = GradingTool()
    main_window.show()
    sys.exit(app.exec())
