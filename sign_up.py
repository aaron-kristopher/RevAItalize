from PyQt6.QtSql import QSqlQuery
from PyQt6.QtWidgets import (
    QMessageBox,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QApplication,
    QCheckBox,
    QGridLayout,
    QSizePolicy,
)
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt, pyqtSignal
import os

import sys

import font_utils
import constants


class SignUpWindow(QWidget):
    back_to_login_requested = pyqtSignal()
    sign_up_attempted = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("RevAItalize - Sign Up")
        self.setStyleSheet(f"background-color: {constants.WHITE};")  # Main background

        # --- Fonts ---
        title_font = font_utils.get_font(size=24, weight=constants.WEIGHT_BOLD)
        subheading_font = font_utils.get_font(size=10)
        label_font = font_utils.get_font(size=8, weight=constants.WEIGHT_SEMIBOLD)
        button_font = font_utils.get_font(size=12, weight=constants.WEIGHT_SEMIBOLD)
        link_button_font = font_utils.get_font(
            size=10, weight=constants.WEIGHT_SEMIBOLD
        )

        # --- Main Layout (Horizontal) ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(64, 64, 64, 64)

        # --- Left Column (Image Panel) ---
        left_panel = QWidget()
        left_panel.setStyleSheet(
            f"""
            background-color: {constants.PRIMARY_400};
            border-radius: 15px;
            """
        )
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image_path = os.path.join("imgs", "splash_img.png")
        splash_image = QLabel()
        pixmap = QPixmap(image_path)
        # Scale pixmap while preserving aspect ratio if needed
        pixmap = pixmap.scaled(
            350,
            350,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        splash_image.setPixmap(pixmap)
        splash_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(splash_image)

        left_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # --- Right Column (Form Panel) ---
        right_panel = QWidget()
        right_panel.setStyleSheet(
            f"background-color: {constants.WHITE}; color: {constants.PRIMARY_400};"
        )
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(40, 20, 40, 20)
        right_layout.setSpacing(15)
        right_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )  # Align form elements to the top

        # --- Form Widgets ---
        # Header
        title_label = QLabel("Create an account")
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {constants.PRIMARY_900};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subheading & Login Link
        login_link_layout = QVBoxLayout()
        login_link_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_wrapper = QHBoxLayout()
        subheading_label = QLabel("Already have an account?")
        subheading_label.setFont(subheading_font)
        subheading_label.setStyleSheet(f"color: {constants.PRIMARY_400};")

        login_button_link = QPushButton("Log in")
        login_button_link.setFont(link_button_font)
        login_button_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        login_button_link.setStyleSheet(
            f"""
            QPushButton {{
                color: {constants.PRIMARY_900};
                border: none;
                text-align: center;
                background-color: transparent;
                padding: 0;
                text-decoration: underline; 
            }}
            QPushButton:hover {{
                color: {constants.PRIMARY_700}; 
            }}
        """
        )
        login_button_link.clicked.connect(self._handle_go_to_login)
        login_wrapper.addWidget(subheading_label)
        login_wrapper.addWidget(login_button_link)
        login_link_layout.addLayout(login_wrapper)
        login_link_layout.addStretch(1)  # Push to left

        # Form Grid
        form_grid_layout = QGridLayout()
        form_grid_layout.setSpacing(10)

        # Input Fields Function Helper
        def create_input(placeholder):
            line_edit = QLineEdit()
            line_edit.setStyleSheet(
                f"""
                QLineEdit {{
                    background-color: transparent;
                    color: {constants.PRIMARY_900};
                    border: 1px solid {constants.PRIMARY_200};
                    border-radius: 10px;
                    padding: 8px 12px;
                    margin-bottom: 15px;
                    min-height: 20px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {constants.PRIMARY_900};
                }}
            """
            )
            input_label = QLabel(f"{placeholder}:*")
            input_label.setFont(label_font)
            return line_edit, input_label

        # Row 1: First Name, Last Name
        self.first_name_input, first_name_label = create_input("First Name")
        self.last_name_input, last_name_label = create_input("Last Name")
        form_grid_layout.addWidget(first_name_label, 0, 0)
        form_grid_layout.addWidget(self.first_name_input, 1, 0)
        form_grid_layout.addWidget(last_name_label, 0, 1)
        form_grid_layout.addWidget(self.last_name_input, 1, 1)

        # Row 2: Email, Contact Number
        self.email_input, email_label = create_input("Email")
        self.contact_input, contact_label = create_input("Contact Number")
        form_grid_layout.addWidget(email_label, 2, 0)
        form_grid_layout.addWidget(self.email_input, 3, 0)
        form_grid_layout.addWidget(contact_label, 2, 1)
        form_grid_layout.addWidget(self.contact_input, 3, 1)

        # Row 3: Age, Sex
        self.age_input, age_label = create_input("Age")
        self.sex_input, sex_label = create_input("Sex")  # Consider QComboBox later
        form_grid_layout.addWidget(age_label, 4, 0)
        form_grid_layout.addWidget(self.age_input, 5, 0)
        form_grid_layout.addWidget(sex_label, 4, 1)
        form_grid_layout.addWidget(self.sex_input, 5, 1)

        # Row 4: Address
        self.address_input, address_label = create_input("Address")
        form_grid_layout.addWidget(address_label, 6, 0, 1, 2)  # Span 2 columns
        form_grid_layout.addWidget(self.address_input, 7, 0, 1, 2)  # Span 2 columns

        # Row 5: Password
        self.password_input, password_label = create_input("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_grid_layout.addWidget(password_label, 8, 0, 1, 2)  # Span 2 columns
        form_grid_layout.addWidget(self.password_input, 9, 0, 1, 2)  # Span 2 columns

        # Terms and Service Checkbox
        self.terms_checkbox = QCheckBox("I accept the Terms and Service")
        self.terms_checkbox.setFont(subheading_font)
        self.terms_checkbox.setStyleSheet(
            f"color: {constants.PRIMARY_700}; spacing: 5px;"
        )

        # Create Account Button
        self.create_account_button = QPushButton("Create Account")
        self.create_account_button.setFont(button_font)
        self.create_account_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.create_account_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_400};
                color: {constants.WHITE};
                border-radius: 5px;
                padding: 10px 20px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {constants.PRIMARY_700};
            }}
            QPushButton:disabled {{
                 background-color: {constants.PRIMARY_200};
                 color: {constants.PRIMARY_400};
            }}
        """
        )
        self.create_account_button.clicked.connect(self._handle_sign_up)
        # Initially disable button until terms are accepted
        self.create_account_button.setEnabled(False)
        self.terms_checkbox.stateChanged.connect(
            lambda state: self.create_account_button.setEnabled(
                state == Qt.CheckState.Checked.value
            )
        )

        # Add widgets to right layout
        right_layout.addWidget(title_label)
        right_layout.addLayout(login_link_layout)
        right_layout.addSpacing(20)  # Space before form
        right_layout.addLayout(form_grid_layout)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.terms_checkbox)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.create_account_button)
        right_layout.addStretch(1)  # Push elements upwards

        right_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        main_layout.setStretch(0, 4)
        main_layout.setStretch(1, 6)

        self.setLayout(main_layout)

    def _handle_sign_up(self):
        print("Sign Up button clicked")
        user_data = {
            "First Name": self.first_name_input.text(),
            "Last Name": self.last_name_input.text(),
            "Email": self.email_input.text(),
            "Contact": self.contact_input.text(),
            "Age": self.age_input.text(),
            "Sex": self.sex_input.text(),
            "Address": self.address_input.text(),
            "Password": self.password_input.text(),
        }

        # Basic empty field check
        for key, value in user_data.items():
            if not value:
                QMessageBox.warning(
                    self,
                    "Sign Up Details",
                    f"""
    Data for {key} is empty!
    {key} must not be empty.
                    """,
                )
                return

        # Emit signal to let the ApplicationController handle the database operations
        # This avoids duplicate user creation
        self.sign_up_attempted.emit(user_data)

    def _handle_go_to_login(self):
        print("Log in link clicked - Emitting request")
        self.back_to_login_requested.emit()  # <<< EMIT SIGNAL INSTEAD


# --- Main Execution --- #
if __name__ == "__main__":
    # Ensure QApplication instance exists
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    sign_up_win = SignUpWindow()
    sign_up_win.show()
    sys.exit(app.exec())
