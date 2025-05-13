
import re
import tempfile
import sys
import os
# Append the src/ folder to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from grading_tool_gui import GradingTool



# === Test 1: Lab name extraction from folder path ===
def test_get_lab_name_valid():
    tool = GradingTool()
    assert tool.get_lab_name("C:/Labs/Lab 2") == "Lab 2"
    assert tool.get_lab_name("D:/SomePath/AI Project/Lab 1") == "Lab 1"

def test_get_lab_name_invalid():
    tool = GradingTool()
    assert tool.get_lab_name("C:/Random Folder/NotALab") is None


# === Test 2: Regex filename matching ===
def test_regex_report_and_java_files():
    # Simulating filenames students would submit
    assert re.match(r"[Gg]\d+.*\.docx", "G6_Report.docx")
    assert re.match(r"(?i)[Gg]\d+.*RangeTest\.java", "g9_RangeTest.java")
    assert re.match(r"(?i)[Gg]\d+.*DataUtilitiesTest\.java", "G5_DataUtilitiesTest.java")


# === Test 3: PDF file creation logic ===
def test_pdf_feedback_saves_correctly():
    tool = GradingTool()

    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_output:
        dummy_feedback = "This is a test feedback.\nLine 2 of feedback."
        dummy_file = "G6_Report.docx"
        output_path = os.path.join(temp_output, dummy_file.replace(".docx", "_Feedback.pdf"))

        tool.save_feedback_to_pdf(dummy_feedback, output_path, dummy_file)

        assert os.path.exists(output_path)
        assert output_path.endswith(".pdf")


# === Test 4: Group number extraction from file name ===
def test_extract_group_number():
    file_name = "G12_Report.docx"
    match = re.match(r"[Gg](\d+)", file_name)
    assert match.group(1) == "12"
