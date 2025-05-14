import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QPushButton,
    QStackedWidget,
    QButtonGroup,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont

import constants

GREY = "#9793A0"

HEADER_FONT = QFont("Poppins", 22, QFont.Weight.ExtraBold)
BUTTON_FONT = QFont("Poppins", 12, QFont.Weight.Bold)
RADIO_FONT = QFont("Poppins", 16, QFont.Weight.Bold)
INPUT_FONT = QFont("Poppins", 16, QFont.Weight.Normal)

BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {constants.PRIMARY_700};
        color: {constants.WHITE};
        border-radius: 5px;
        padding: 12px 20px;
    }}
    QPushButton:hover {{
        background-color: {constants.PRIMARY_500};
    }}
    QPushButton:pressed {{
        background-color: {constants.PRIMARY_300};
    }}
"""
RADIO_STYLE = f""" 
    QRadioButton {{
        color: {constants.PRIMARY_700};
        spacing: 20px;
    }}
    QRadioButton::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 1px solid {constants.PRIMARY_700};
        background-color: {constants.WHITE};
    }}
    QRadioButton::indicator:checked {{
        background-color: {constants.PRIMARY_700};
        border: 1px solid {constants.PRIMARY_700};
        width: 16px;
        height: 16px;
        border-radius: 8px;
    }}
"""


class OnboardingWindow(QMainWindow):
    # Signal emitted when onboarding is complete with user preferences
    onboarding_completed = pyqtSignal(bool, int)  # needs_assistance, preferred_reps
    
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self.needs_assistance = False  # Default value
        self.preferred_reps = 5  # Default value
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Onboarding Page")
        self.setMinimumSize(900, 600)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.left_panel = QWidget()
        self.left_panel.setStyleSheet(f"background-color: {constants.WHITE};")

        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_layout.setSpacing(20)

        self.right_panel = QWidget()
        self.right_panel.setStyleSheet(f"background-color: {constants.WHITE};")

        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        self.left_layout.addWidget(self.stacked_widget)

        self.create_page_one()
        self.create_page_two()

        self.image_label = QLabel()
        self.image_label.setContentsMargins(0, 0, 0, 0)
        image_path = "imgs/onboarding.png"
        self.image_label.setPixmap(QPixmap(image_path))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.right_layout.addWidget(self.image_label)

        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.right_panel)
        self.setCentralWidget(main_widget)

    def create_header(self, text):
        header = QLabel(text)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(HEADER_FONT)
        header.setStyleSheet(f"color: {constants.PRIMARY_700};")
        header.setWordWrap(True)
        header.setContentsMargins(40, 0, 40, 0)
        return header

    def create_button(self, text, width=150):
        button = QPushButton(text)
        button.setFixedWidth(width)
        button.setFont(BUTTON_FONT)
        button.setStyleSheet(BUTTON_STYLE)
        return button

    def create_radio_group(self, options):
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(10)

        button_group = QButtonGroup(self)

        radio_font = QFont("Poppins", 16, QFont.Weight.Bold)

        for option in options:
            radio_container = QWidget()
            radio_container.setFixedWidth(350)

            radio_layout = QHBoxLayout(radio_container)
            radio_layout.setContentsMargins(0, 0, 0, 0)

            radio = QRadioButton("")
            button_group.addButton(radio)

            radio.setFont(radio_font)
            radio.setMinimumHeight(40)
            radio.setStyleSheet(
                f"""
                QRadioButton {{
                    color: {constants.PRIMARY_700};
                    spacing: 30px;
                }}
                QRadioButton::indicator {{
                    width: 18px;
                    height: 18px;
                    border-radius: 9px;
                    border: 1px solid {constants.PRIMARY_700};
                    background-color: {constants.WHITE};
                    align: top;
                }}
                QRadioButton::indicator:checked {{
                    background-color: {constants.PRIMARY_700};
                    border: 1px solid {constants.PRIMARY_700};
                    width: 18px;
                    height: 18px;
                    border-radius: 9px;
                }}
            """
            )

            text_label = QLabel(option)
            text_label.setFont(radio_font)
            text_label.setWordWrap(True)
            text_label.setStyleSheet(f"color: {constants.PRIMARY_700};")
            text_label.setFixedHeight(60)

            radio_layout.addWidget(radio, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            radio_layout.addWidget(text_label, 1)
            radio_layout.addStretch()

            text_label.mousePressEvent = lambda event, r=radio: r.click()
            main_layout.addWidget(
                radio_container, alignment=Qt.AlignmentFlag.AlignHCenter
            )

        return container, button_group

    def create_navigation_buttons(
        self, prev_index=None, next_index=None, is_submit=False
    ):
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(50, 20, 50, 20)

        button_width = 150

        if prev_index is not None:
            prev_button = self.create_button("Previous")
            prev_button.clicked.connect(
                lambda: self.stacked_widget.setCurrentIndex(prev_index)
            )
            nav_layout.addWidget(prev_button)
        else:
            nav_layout.addStretch()

        nav_layout.addStretch()

        if is_submit:
            submit_button = self.create_button("Submit")
            submit_button.clicked.connect(self.submit_form)
            nav_layout.addWidget(submit_button)
        elif next_index is not None:
            next_button = self.create_button("Next", width=button_width)
            next_button.clicked.connect(
                lambda: self.stacked_widget.setCurrentIndex(next_index)
            )
            nav_layout.addWidget(next_button)

        return nav_layout

    def create_page_one(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        header = self.create_header(
            "Do you currently feel significant pain or discomfort after performing similar exercises?"
        )
        layout.addWidget(header)

        options = ["Yes", "No"]
        radio_group, self.assistance_group = self.create_radio_group(options)
        layout.addWidget(radio_group)
        
        # Set default selection to 'No'
        if self.assistance_group.buttons():
            self.assistance_group.buttons()[1].setChecked(True)  # 'No' is the second option

        nav_layout = self.create_navigation_buttons(next_index=1)
        layout.addLayout(nav_layout)

        self.stacked_widget.addWidget(page)

    def create_page_two(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        header = self.create_header(
            "How many repetitions would you like a session to contain?"
        )
        layout.addWidget(header)

        options = ["3", "5", "7"]
        radio_group, self.reps_group = self.create_radio_group(options)
        layout.addWidget(radio_group)
        
        # Set default selection to '5'
        if self.reps_group.buttons():
            self.reps_group.buttons()[1].setChecked(True)  # '5' is the second option

        nav_layout = self.create_navigation_buttons(prev_index=0, is_submit=True)
        layout.addLayout(nav_layout)

        self.stacked_widget.addWidget(page)

    def submit_form(self):
        print("Form submitted!")
        
        # Get user's preference for assistance
        if self.assistance_group.checkedButton():
            assistance_index = self.assistance_group.buttons().index(self.assistance_group.checkedButton())
            self.needs_assistance = assistance_index == 0  # True if 'Yes' is selected (first option)
        
        # Get user's preferred repetitions
        if self.reps_group.checkedButton():
            reps_index = self.reps_group.buttons().index(self.reps_group.checkedButton())
            reps_options = [3, 5, 7]  # Corresponding to the options shown
            self.preferred_reps = reps_options[reps_index]
        
        print(f"Needs assistance: {self.needs_assistance}, Preferred reps: {self.preferred_reps}")
        
        # Emit signal with user preferences
        self.onboarding_completed.emit(self.needs_assistance, self.preferred_reps)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OnboardingWindow()
    window.showMaximized()
    sys.exit(app.exec())
