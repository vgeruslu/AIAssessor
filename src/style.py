class GradingToolStyles:
    """Class to provide styles for the AI-Assisted Grading Tool."""
    
    @staticmethod
    def get_light_stylesheet():
        """Returns the Light Mode stylesheet"""
        return """
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Open Sans', sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 5px;
            }
            QLineEdit {
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 6px;
                background-color: #fff;
                font-size: 13px;
                color: #000;
            }
            QPushButton {
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton#browseButton {
                background-color: #0078D7; /* Blue */
                color: white;
            }
            QPushButton#browseButton:hover {
                background-color: #005fa3;
            }
            QPushButton#switchModeButton {
                background-color: #FFA500; /* Orange */
                color: white;
            }
            QPushButton#switchModeButton:hover {
                background-color: #CC8400;
            }
            QPushButton#processButton {
                background-color: #4CAF50; /* Green */
                color: white;
            }
            QPushButton#processButton:hover {
                background-color: #388E3C;
            }
            QTextEdit {
                background-color: #eaeaea;  /* Light Gray */
                color: #000;
                font-family: Consolas;
                font-size: 12px;
                border: 1px solid #aaa;
                padding: 5px;
            }
        """

    @staticmethod
    def get_dark_stylesheet():
        """Returns the Dark Mode stylesheet"""
        return """
            QWidget {
                background-color: #121212;
                font-family: 'Open Sans', sans-serif;
                font-size: 14px;
                color: #ddd;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #fff;
                padding: 5px;
            }
            QLineEdit {
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                background-color: #222;
                font-size: 13px;
                color: #fff;
            }
            QPushButton {
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton#browseButton {
                background-color: #0078D7; /* Blue */
                color: white;
            }
            QPushButton#browseButton:hover {
                background-color: #005fa3;
            }
            QPushButton#switchModeButton {
                background-color: #FFA500; /* Orange */
                color: white;
            }
            QPushButton#switchModeButton:hover {
                background-color: #CC8400;
            }
            QPushButton#processButton {
                background-color: #4CAF50; /* Green */
                color: white;
            }
            QPushButton#processButton:hover {
                background-color: #388E3C;
            }
            QTextEdit {
                background-color: #1E1E1E;  /* Keep dark */
                color: #ddd;
                font-family: Consolas;
                font-size: 12px;
                border: 1px solid #555;
                padding: 5px;
            }
        """
