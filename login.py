import os
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal

import constants
import font_utils


class LoginWindow(QWidget):
    # Define a signal that carries email and password strings
    login_attempt = pyqtSignal(str, str)
    create_account_requested = (
        pyqtSignal()
    )  # Define a signal for create account request

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # --- Fonts ---
        subheading_font = font_utils.get_font(size=16, weight=constants.WEIGHT_SEMIBOLD)
        text_font = font_utils.get_font(size=12)
        input_font = font_utils.get_font(size=12)
        button_font = font_utils.get_font(size=12, weight=constants.WEIGHT_SEMIBOLD)

        # --- Styles ---
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: 
                    qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                    stop: 0 {constants.PRIMARY_400}, 
                                    stop: 1 {constants.PRIMARY_300});
                color: {constants.WHITE};
            }}
            QLineEdit {{
                background-color: transparent;
                color: {constants.WHITE};
                border: 1px solid {constants.WHITE};
                border-radius: 12px;
                padding: 10px 15px;
                margin-bottom: 5px;
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border: 2px solid {constants.WHITE};
            }}
            QPushButton#LoginButton {{
                background-color: {constants.WHITE};
                color: {constants.PRIMARY_400};
                border-radius: 15px;
                padding: 12px 25px;
                min-height: 22px;
            }}
            QPushButton#LoginButton:hover {{
                background-color: {constants.PRIMARY_100};
            }}
             QPushButton#CreateAccountButton {{
                background-color: {constants.PRIMARY_800};
                color: {constants.WHITE};
                border-radius: 15px;
                padding: 12px 25px;
                min-height: 22px;
            }}
            QPushButton#CreateAccountButton:hover {{
                background-color: transparent;
                border: 2px solid {constants.PRIMARY_300};
            }}
        """
        )

        # --- Widgets ---

        image_path = os.path.join("imgs", "simplified-splash.png")
        splash_image = QLabel()
        pixmap = QPixmap(image_path)
        # Scale pixmap while preserving aspect ratio if needed
        pixmap = pixmap.scaled(
            400,
            400,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        splash_image.setPixmap(pixmap)
        splash_image.setStyleSheet(
            "background-color: transparent; margin-bottom: 25px;"
        )
        splash_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subheading_label = QLabel("Welcome to Your Post-Rehabilitation Assistant")
        subheading_label.setFont(subheading_font)
        subheading_label.setStyleSheet("background-color: transparent;")
        subheading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setFont(input_font)
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedWidth(300)  # Fixed width for inputs

        self.password_input = QLineEdit()
        self.password_input.setFont(input_font)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(300)

        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("LoginButton")  # For specific styling
        self.login_button.setStyleSheet(f"""
            QPushButton#LoginButton {{
                background-color: {constants.PRIMARY_800};
                color: {constants.WHITE};
            }}
            QPushButton#LoginButton:hover {{
                background-color: {constants.PRIMARY_600};
                border: 2px solid {constants.PRIMARY_600};
            }}
        """)
        self.login_button.setFont(button_font)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setFixedWidth(200)
        self.login_button.clicked.connect(self._handle_login)

        no_account_label = QLabel("No account?")
        no_account_label.setStyleSheet("background-color: transparent")
        no_account_label.setFont(text_font)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedWidth(300)

        self.create_account_button = QPushButton("Create Account")
        self.create_account_button.setObjectName("CreateAccountButton")  # For styling
        self.create_account_button.setFont(input_font)  # Slightly less prominent font
        self.create_account_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.create_account_button.setStyleSheet(
            f"""
            QPushButton#CreateAccountButton {{
                background-color: transparent;
                color: {constants.WHITE};
                border: 2px solid {constants.WHITE};
            }}
            QPushButton#CreateAccountButton:hover {{
                background-color: {constants.WHITE};
                color: {constants.PRIMARY_400};
            }}
        """
        )
        self.create_account_button.setFixedWidth(200)
        self.create_account_button.clicked.connect(self._handle_create_account)

        # --- Layout ---
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)  # Add padding around the form

        # Center the form elements vertically and horizontally
        layout.addStretch(1)
        layout.addWidget(splash_image, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(40)

        layout.addWidget(subheading_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(40)  # Extra space after title

        # Email Input Group
        layout.addWidget(self.email_input, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        # Password Input Group
        layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)  # Extra space before buttons

        # ButtonssetMaximumWidth
        layout.addWidget(self.login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(40)
        layout.addWidget(no_account_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(line, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(
            self.create_account_button, alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addStretch(1)

        self.setLayout(layout)

    def _handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        # Emit the signal with the entered credentials
        self.login_attempt.emit(email, password)

    def _handle_create_account(self):
        print("Create Account button clicked - Emitting request")
        self.create_account_requested.emit()  # Emit signal instead of managing windows directly


if __name__ == "__main__":
    pass
