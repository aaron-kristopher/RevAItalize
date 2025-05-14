from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QMenu,
    QToolButton,
    QScrollArea,
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QSize, pyqtSignal

import constants
import font_utils
import os


class HomeWindow(QMainWindow):
    test_button_clicked = pyqtSignal()
    model_button_clicked = pyqtSignal()
    exercise_button_clicked = pyqtSignal()
    profile_button_clicked = pyqtSignal()
    quit_button_clicked = pyqtSignal()
    lstm_clicked = pyqtSignal()
    blazepose_clicked = pyqtSignal()
    attention_mechanism_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("RevAItalize")
        self.setStyleSheet(
            f"background-color: {constants.PRIMARY_100}; color: {constants.PRIMARY_800};"
        )

        # Fonts
        poppins_bold_32 = font_utils.get_font(size=32, weight=constants.WEIGHT_BOLD)
        poppins_regular_10 = font_utils.get_font(size=10)
        poppins_regular_12 = font_utils.get_font(size=12)
        poppins_regular_14 = font_utils.get_font(size=14)
        poppins_semibold_16 = font_utils.get_font(
            size=16, weight=constants.WEIGHT_SEMIBOLD
        )

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet(f"background-color: {constants.PRIMARY_400};")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        logo_icon_path = os.path.join(self.script_dir, constants.EXERCISE_ICON_PATH)
        logo_icon = QIcon(logo_icon_path)
        self.logo_button = QPushButton()
        self.logo_button.setIcon(logo_icon)
        self.logo_button.setIconSize(QSize(50, 50))
        self.logo_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logo_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0px;
                margin: 10px 0;
                margin-top: 35px; 
            }
            """
        )
        sidebar_layout.addWidget(self.logo_button)

        top_padding = QWidget()
        top_padding.setFixedHeight(20)
        top_padding.setStyleSheet(f"background-color: {constants.PRIMARY_400};")
        sidebar_layout.addWidget(top_padding)

        # Home button
        home_button = QPushButton("  Home")
        home_button.setFont(poppins_regular_10)
        home_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.HOME_ICON_PATH):
            home_button.setIcon(QIcon(constants.HOME_ICON_PATH))
            home_button.setIconSize(QSize(18, 18))
        home_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_700};
                color: {constants.WHITE};
                padding: 15px;
                text-align: left;
                border: none;
                width: 100%;
            }}
            QPushButton:hover {{
                background-color: {constants.PRIMARY_600};
            }}
            """
        )
        sidebar_layout.addWidget(home_button)

        # Exercises button
        self.exercises_button = QToolButton()
        self.exercises_button.setText("  Exercises")
        self.exercises_button.setFont(poppins_regular_10)
        self.exercises_button.setCursor(Qt.CursorShape.PointingHandCursor)

        if os.path.exists(constants.EXERCISES_ICON_PATH):
            self.exercises_button.setIcon(QIcon(constants.EXERCISES_ICON_PATH))
            self.exercises_button.setIconSize(QSize(18, 18))

        self.exercises_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.exercises_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.exercises_button.setArrowType(Qt.ArrowType.NoArrow)

        self.exercises_button.setStyleSheet(
            f"""
            QToolButton {{
                background-color: {constants.PRIMARY_400};
                color: {constants.WHITE};
                padding: 15px;
                text-align: left;
                border: none;
                width: 100%;
            }}
            QToolButton:hover {{
                background-color: {constants.PRIMARY_600};
            }}
            QToolButton::menu-indicator {{
                image: url({constants.RIGHT_ARROW_ICON_PATH});
                subcontrol-position: right center;
                subcontrol-origin: padding;
                padding-right: 10px;
            }}
            """
        )
        self.exercises_button.setFixedWidth(180)

        self.exercises_button.clicked.connect(self.exercise_button_clicked.emit)

        sidebar_layout.addWidget(self.exercises_button)

        self.model_button = QToolButton()
        self.model_button.setText("  Model")
        self.model_button.setFont(poppins_regular_10)
        self.model_button.setCursor(Qt.CursorShape.PointingHandCursor)

        if os.path.exists(constants.MODEL_ICON_PATH):
            self.model_button.setIcon(QIcon(constants.MODEL_ICON_PATH))
            self.model_button.setIconSize(QSize(18, 18))

        self.model_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.model_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.model_button.setArrowType(Qt.ArrowType.NoArrow)

        self.model_button.setStyleSheet(
            f"""
            QToolButton {{
                background-color: {constants.PRIMARY_400};
                color: {constants.WHITE};
                padding: 15px;
                text-align: left;
                border: none;
                width: 100%;
            }}
            QToolButton:hover {{
                background-color: {constants.PRIMARY_600};
            }}
            QToolButton::menu-indicator {{
                image: url({constants.RIGHT_ARROW_ICON_PATH});
                subcontrol-position: right center;
                subcontrol-origin: padding;
                padding-right: 10px;
            }}
            """
        )
        self.model_button.setFixedWidth(180)

        model_menu = QMenu(self.model_button)
        model_menu.setStyleSheet(
            f"""
            QMenu {{
                background-color: {constants.PRIMARY_500};
                color: {constants.WHITE};
                border: none;
                padding: 5px;
                width: 180px;
            }}
            QMenu::item {{
                padding: 8px 20px;
            }}
            QMenu::item:selected {{
                background-color: {constants.PRIMARY_600};
            }}
            """
        )

        lstm_action = QAction("LSTM", self)
        lstm_action.triggered.connect(self.lstm_clicked.emit)

        blazepose_action = QAction("Blazepose", self)
        blazepose_action.triggered.connect(self.blazepose_clicked.emit)

        attention_mechanism_action = QAction("Attention Mechanism", self)
        attention_mechanism_action.triggered.connect(
            self.attention_mechanism_clicked.emit
        )

        model_menu.addAction(lstm_action)
        model_menu.addAction(blazepose_action)
        model_menu.addAction(attention_mechanism_action)

        self.model_button.setMenu(model_menu)
        sidebar_layout.addWidget(self.model_button)

        self.profile_button = QPushButton("  Profile Dashboard")
        self.profile_button.setFont(poppins_regular_10)
        self.profile_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.PROFILE_ICON_PATH):
            self.profile_button.setIcon(QIcon(constants.PROFILE_ICON_PATH))
            self.profile_button.setIconSize(QSize(18, 18))
        self.profile_button.clicked.connect(self.profile_button_clicked.emit)
        self.profile_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_400};
                color: {constants.WHITE};
                padding: 15px;
                text-align: left;
                border: none;
                width: 100%;
            }}
            QPushButton:hover {{
                background-color: {constants.PRIMARY_600};
            }}
            """
        )
        sidebar_layout.addWidget(self.profile_button)

        sidebar_layout.addStretch()

        # Quit button
        quit_button = QPushButton("  Quit")
        quit_button.setFont(poppins_regular_10)
        quit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.QUIT_ICON_PATH):
            quit_button.setIcon(QIcon(constants.QUIT_ICON_PATH))
            quit_button.setIconSize(QSize(18, 18))
        quit_button.clicked.connect(self.quit_button_clicked.emit)
        quit_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_400};
                color: {constants.WHITE};
                padding: 15px;
                text-align: left;
                border: none;
                width: 100%;
            }}
            QPushButton:hover {{
                background-color: {constants.DANGER};
            }}
            """
        )
        sidebar_layout.addWidget(quit_button)

        # Content area
        content_area = QWidget()
        content_area.setStyleSheet(f"background-color: {constants.PRIMARY_100};")

        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(50, 30, 50, 30)

        top_bar = QHBoxLayout()

        # RevAItalize logo
        logo_image = QLabel()
        if os.path.exists(constants.REVAITALIZE_LOGO_PATH):
            logo_image.setPixmap(
                QIcon(constants.REVAITALIZE_LOGO_PATH).pixmap(QSize(220, 50))
            )
        else:
            logo_image.setText("RevAItalize")
            logo_image.setFont(poppins_bold_32)
            logo_image.setStyleSheet(f"color: {constants.PRIMARY_800};")
        logo_image.setAlignment(Qt.AlignmentFlag.AlignRight)
        top_bar.addStretch()
        top_bar.addWidget(logo_image)

        content_layout.addLayout(top_bar)

        # Overall scroll area for main content and bottom section
        overall_scroll_area = QScrollArea()
        overall_scroll_area.setWidgetResizable(True)
        overall_scroll_area.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
                margin-top: 15px; /* Added top margin */
            }}
            QScrollBar:vertical {{
                background: {constants.GRAY};
                border: 1px solid {constants.PRIMARY_700};
                border-radius: 6px;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {constants.PRIMARY_700};
                min-height: 25px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px; /* Hide default arrows by making them zero height */
            }}
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                border: 1px solid {constants.PRIMARY_400};
                background: {constants.PRIMARY_200};
                height: 12px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {constants.PRIMARY_700};
                min-width: 25px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
                width: 0px; /* Hide default arrows */
            }}
            QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {{
                background: none;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """
        )

        overall_scroll_widget = (
            QWidget()
        )  # Widget to hold the main content and bottom section
        overall_scroll_layout = QVBoxLayout(overall_scroll_widget)
        overall_scroll_layout.setContentsMargins(
            0, 0, 0, 0
        )  # Match original content_layout margins if needed, or set to 0
        overall_scroll_layout.setSpacing(
            0
        )  # Match original content_layout spacing if needed

        # Main content
        main_content = QVBoxLayout()

        # Title and subtitle
        title_text = QLabel("Post-Rehabilitation Exercises")
        title_text.setFont(poppins_bold_32)
        title_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_text.setStyleSheet(f"color: {constants.PRIMARY_800};")

        subheading_text = QLabel("for Low-Back Pain")
        subheading_text.setFont(poppins_semibold_16)
        subheading_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subheading_text.setStyleSheet(f"color: {constants.PRIMARY_800};")

        # Description text
        paragraph_text = QLabel(
            """
            In recent years, the utilization of AI, specifically human pose estimation (HPE),have shown great potential in enhancing accuracy in rehabilitation assessments. Introducing our model RevAItalize, using Long-Short Term Memory (LSTM).This study aims to compare the metrics in classifying the following exercises: torso rotation, flank stretch, and hiding face. Along with, analyzing thedistribution of weights to assess the correlation of labels and attention mechanismweights on each skeletal keypoints. The researchers utilized another model, Blazepose, to serve as a basis of plottingkeypoints and the foundation of our human pose estimation with an accuracy of 90%. The study presents that there is a significant difference in the different metrics of the LSTM model in classifying across different exercises, as well as, a positivecorrelation between the distribution of weights on each skeletal keypoints and the labels for evaluating each exercises.
            """
        )
        paragraph_text.setFont(poppins_regular_14)
        paragraph_text.setWordWrap(True)
        paragraph_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        paragraph_text.setStyleSheet(f"color: {constants.PRIMARY_800};")

        main_content.addWidget(title_text)
        main_content.addWidget(subheading_text)
        main_content.addSpacing(20)
        main_content.addWidget(paragraph_text)
        main_content.setContentsMargins(50, 20, 50, 20)

        overall_scroll_layout.addLayout(main_content)
        overall_scroll_layout.addStretch()  # This stretch was originally in content_layout

        bottom_section = QHBoxLayout()

        bottom_section.addStretch(1)

        test_group = QVBoxLayout()
        test_group.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Exercise icon
        exercise_icon = QLabel()
        if os.path.exists(constants.EXERCISE_ICON_PATH):
            exercise_icon.setPixmap(
                QIcon(constants.EXERCISE_ICON_PATH).pixmap(QSize(50, 50))
            )
        exercise_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ready_text = QLabel("Ready to test the exercises?")
        ready_text.setFont(poppins_regular_12)
        ready_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ready_text.setStyleSheet(f"color: {constants.PRIMARY_800};")

        test_group.addWidget(exercise_icon, 0, Qt.AlignmentFlag.AlignCenter)
        test_group.addWidget(ready_text, 0, Qt.AlignmentFlag.AlignCenter)
        test_group.addSpacing(15)

        # Test button
        test_button = QPushButton("  Test Exercises")
        test_button.setFont(poppins_regular_12)
        if os.path.exists(constants.EXERCISES_ICON_PATH):
            test_button.setIcon(QIcon(constants.EXERCISES_ICON_PATH))
            test_button.setIconSize(QSize(18, 18))
        test_button.setCursor(Qt.CursorShape.PointingHandCursor)
        test_button.clicked.connect(self.test_button_clicked.emit)
        test_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_800};
                color: {constants.WHITE};
                padding: 8px 10px;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background-color: {constants.PRIMARY_600};
            }}
            """
        )
        test_button.setFixedWidth(180)

        test_group.addWidget(test_button, 0, Qt.AlignmentFlag.AlignCenter)

        bottom_section.addLayout(test_group)

        overall_scroll_layout.addLayout(bottom_section)
        overall_scroll_widget.setLayout(overall_scroll_layout)
        overall_scroll_area.setWidget(overall_scroll_widget)

        content_layout.addWidget(
            overall_scroll_area
        )  # Add overall_scroll_area instead of main_content and bottom_section directly

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.resize(1200, 800)
