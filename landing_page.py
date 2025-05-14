import os
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QPixmap

import font_utils
import constants


class LandingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("RevAItalize")
        self.setStyleSheet(
            f"background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {constants.PRIMARY_400}, stop: 1 {constants.PRIMARY_300}); color: {constants.WHITE};"
        )
        poppins_semi_12 = font_utils.get_font(size=12, weight=constants.WEIGHT_SEMIBOLD)

        # Set app splash image
        image_label = QLabel()
        image_label.setStyleSheet("background: transparent;")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        splash_img = QPixmap(os.path.join("imgs", "splash_img.png"))
        image_label.setPixmap(splash_img)

        # Set Layout

        # Top layout with splash page image
        group_layout = QHBoxLayout()
        group_layout.addWidget(image_label)

        # Bottom layout with buttons
        button_layout = QHBoxLayout()

        self.sign_up_button = QPushButton("Sign Up")
        self.sign_up_button.setFont(poppins_semi_12)
        self.sign_up_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sign_up_button.setStyleSheet(
            f"""
                QPushButton {{
                    background-color: transparent;
                    color: {constants.WHITE};
                    padding: 12px 32px;
                    border: 2px solid {constants.WHITE};
                    border-radius: 12px;
                    margin: 0px 24px;
                }}

                QPushButton:hover {{
                    background-color: {constants.WHITE};
                    color: {constants.PRIMARY_400};
                }}
            """
        )

        self.login_button = QPushButton("Login")
        self.login_button.setFont(poppins_semi_12)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet(
            f"""
                QPushButton {{
                    background-color: {constants.PRIMARY_800};
                    color: {constants.WHITE};
                    padding: 12px 32px;
                    border: 2px solid {constants.PRIMARY_800};
                    border-radius: 12px;
                    margin: 0px 24px;
                }}

                QPushButton:hover {{
                    background-color: {constants.WHITE};
                    color: {constants.PRIMARY_400};
                    border: 2px solid {constants.WHITE};
                }}
            """
        )

        button_layout.addWidget(self.sign_up_button)
        button_layout.addWidget(self.login_button)

        # Main Layout
        main_layout = QHBoxLayout()

        center_layout = QVBoxLayout()
        center_layout.addStretch(1)
        center_layout.addLayout(group_layout)
        center_layout.addLayout(button_layout)
        center_layout.addStretch(1)

        main_layout.addStretch(1)
        main_layout.addLayout(center_layout)
        main_layout.addStretch(1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    # Ensure QApplication instance exists
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    landing_window = LandingWindow()
    landing_window.showFullScreen()
    sys.exit(app.exec())
