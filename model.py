from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
    QScrollArea,
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize, pyqtSignal

import constants
import font_utils
import os
from typing import Dict


class ModelWindow(QMainWindow):
    home_button_clicked = pyqtSignal()
    exercise_button_clicked = pyqtSignal()
    profile_button_clicked = pyqtSignal()
    quit_button_clicked = pyqtSignal()
    test_button_clicked = pyqtSignal()
    
    lstm_clicked = pyqtSignal()
    blazepose_clicked = pyqtSignal()
    attention_mechanism_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.current_page = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("RevAItalize - Model")
        self.setStyleSheet(
            f"background-color: {constants.PRIMARY_100}; color: {constants.PRIMARY_800};"
        )
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # sidebar
        sidebar = self.create_sidebar()
        
        self.content_area = QWidget()
        self.content_area.setStyleSheet(f"background-color: {constants.PRIMARY_100};")
        
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(50, 30, 50, 30)
        
        top_bar = QHBoxLayout()
        logo_image = QLabel()
        if os.path.exists(constants.REVAITALIZE_LOGO_PATH):
            logo_image.setPixmap(QIcon(constants.REVAITALIZE_LOGO_PATH).pixmap(QSize(220, 50)))
        else:
            logo_image.setText("RevAItalize")
            logo_image.setFont(font_utils.get_font(size=32, weight=constants.WEIGHT_BOLD))
            logo_image.setStyleSheet(f"color: {constants.PRIMARY_800};")
        logo_image.setAlignment(Qt.AlignmentFlag.AlignRight)
        top_bar.addStretch()
        top_bar.addWidget(logo_image)
        
        self.content_layout.addLayout(top_bar)
        
        # Scroll Area for the stacked widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
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
        """)

        self.stacked_widget = QStackedWidget()
        
       
        self.lstm_page = self.create_lstm_page()
        self.blazepose_page = self.create_blazepose_page()
        self.attention_mechanism_page = self.create_attention_mechanism_page()
        
      
        self.stacked_widget.addWidget(self.lstm_page)
        self.stacked_widget.addWidget(self.blazepose_page)
        self.stacked_widget.addWidget(self.attention_mechanism_page)
        
        scroll_area.setWidget(self.stacked_widget) # Put stacked_widget inside scroll_area
        self.content_layout.addWidget(scroll_area, 1) # Add scroll_area to content_layout
        
        bottom_section = QHBoxLayout()
        bottom_section.addStretch(1)
        
        test_button = QPushButton("  Test Exercises")
        test_button.setFont(font_utils.get_font(size=12))
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
        
        bottom_section.addWidget(test_button)
        self.content_layout.addLayout(bottom_section)
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area, 1)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        self.resize(1200, 800)
        
        # Default to LSTM page
        self.show_lstm_page()
    
    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(190)
        sidebar.setStyleSheet(f"background-color: {constants.PRIMARY_400};")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo button
        logo_icon_path = os.path.join(self.script_dir, constants.EXERCISE_ICON_PATH)
        logo_icon = QIcon(logo_icon_path)
        logo_button = QPushButton()
        logo_button.setIcon(logo_icon)
        logo_button.setIconSize(QSize(50, 50))
        logo_button.setCursor(Qt.CursorShape.PointingHandCursor)
        logo_button.setStyleSheet(
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
        sidebar_layout.addWidget(logo_button)
        
        top_padding = QWidget()
        top_padding.setFixedHeight(20)
        top_padding.setStyleSheet(f"background-color: {constants.PRIMARY_400};")
        sidebar_layout.addWidget(top_padding)
        
        # Navigation buttons
        home_button = QPushButton("  Home")
        home_button.setFont(font_utils.get_font(size=10))
        home_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.HOME_ICON_PATH):
            home_button.setIcon(QIcon(constants.HOME_ICON_PATH))
            home_button.setIconSize(QSize(18, 18))
        home_button.clicked.connect(self.home_button_clicked.emit)
        home_button.setStyleSheet(
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
        sidebar_layout.addWidget(home_button)
        
        # Exercises button
        exercises_button = QPushButton("  Exercises")
        exercises_button.setFont(font_utils.get_font(size=10))
        exercises_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.EXERCISES_ICON_PATH):
            exercises_button.setIcon(QIcon(constants.EXERCISES_ICON_PATH))
            exercises_button.setIconSize(QSize(18, 18))
        exercises_button.clicked.connect(self.exercise_button_clicked.emit)
        exercises_button.setStyleSheet(
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
        sidebar_layout.addWidget(exercises_button)
        
        # Model button - active/selected
        model_button = QPushButton("  Model")
        model_button.setFont(font_utils.get_font(size=10))
        model_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.MODEL_ICON_PATH):
            model_button.setIcon(QIcon(constants.MODEL_ICON_PATH))
            model_button.setIconSize(QSize(18, 18))
        model_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_200};
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
        sidebar_layout.addWidget(model_button)
        
        # Model submenu
        self.model_buttons: Dict[str, QPushButton] = {}
        
        # LSTM button
        lstm_button = QPushButton("  LSTM")
        lstm_button.setFont(font_utils.get_font(size=10))
        lstm_button.setCursor(Qt.CursorShape.PointingHandCursor)
        lstm_button.clicked.connect(self.show_lstm_page)
        lstm_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_400};
                color: {constants.WHITE};
                padding: 15px;
                padding-left: 30px;
                text-align: left;
                border: none;
                width: 100%;
            }}
            QPushButton:hover {{
                background-color: {constants.PRIMARY_600};
            }}
            """
        )
        sidebar_layout.addWidget(lstm_button)
        self.model_buttons["lstm"] = lstm_button
        
        # Blazepose button
        blazepose_button = QPushButton("  Blazepose")
        blazepose_button.setFont(font_utils.get_font(size=10))
        blazepose_button.setCursor(Qt.CursorShape.PointingHandCursor)
        blazepose_button.clicked.connect(self.show_blazepose_page)
        blazepose_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_400};
                color: {constants.WHITE};
                padding: 15px;
                padding-left: 30px;
                text-align: left;
                border: none;
                width: 100%;
            }}
            QPushButton:hover {{
                background-color: {constants.PRIMARY_600};
            }}
            """
        )
        sidebar_layout.addWidget(blazepose_button)
        self.model_buttons["blazepose"] = blazepose_button
        
        # Attention Mechanism button
        attention_button = QPushButton("  Attention Mechanism")
        attention_button.setFont(font_utils.get_font(size=10))
        attention_button.setCursor(Qt.CursorShape.PointingHandCursor)
        attention_button.clicked.connect(self.show_attention_mechanism_page)
        attention_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_400};
                color: {constants.WHITE};
                padding: 15px;
                padding-left: 30px;
                text-align: left;
                border: none;
                width: 100%;
            }}
            QPushButton:hover {{
                background-color: {constants.PRIMARY_600};
            }}
            """
        )
        sidebar_layout.addWidget(attention_button)
        self.model_buttons["attention"] = attention_button
        
        # Profile button
        profile_button = QPushButton("  Profile Dashboard")
        profile_button.setFont(font_utils.get_font(size=10))
        profile_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.PROFILE_ICON_PATH):
            profile_button.setIcon(QIcon(constants.PROFILE_ICON_PATH))
            profile_button.setIconSize(QSize(18, 18))
        profile_button.clicked.connect(self.profile_button_clicked.emit)
        profile_button.setStyleSheet(
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
        sidebar_layout.addWidget(profile_button)
        
        sidebar_layout.addStretch()
        
        # Quit button
        quit_button = QPushButton("  Quit")
        quit_button.setFont(font_utils.get_font(size=10))
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
        
        return sidebar

    def create_lstm_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Long-Short Term Memory (LSTM)")
        title_label.setFont(font_utils.get_font(size=36, weight=constants.WEIGHT_BOLD))
        title_label.setStyleSheet(f"color: {constants.PRIMARY_800};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title_label)
        
        # Description text
        description = """LSTM is a type of recurrent neural networks (RNN), and the component of an artificial neural network that has additional memory cells for time steps that remember previous information. Typically, LSTM is used to efficiently learn and interpret complex data sequences. In this study, sequence analysis models like Long-Short Term Memory (LSTM) are essential for enabling real-time classification of rehabilitation exercises, allowing for precise tracking of motion patterns over time.

Moreover, based on a different study, LSTM is the kind of model that can accurately represent sequential data like human posture and gesture details using key skeletal landmarks. On the contrary, when compared to conventional RNN, LSTM is the type of model that uses a complex gating mechanism that enables the retention of long-range dependencies which then evades the problem of gradient vanishing or gradient exploding during training when using conventional RNN. As a result, it is recommended to use LSTM as the basis model of the study as it possesses the ability to retain information which in turn can be enhanced when attention mechanism is applied."""
        
        description_label = QLabel(description)
        description_label.setFont(font_utils.get_font(size=12))
        description_label.setWordWrap(True)
        description_label.setStyleSheet(f"color: {constants.PRIMARY_800};")
        description_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        layout.addWidget(description_label)
        
        # References text
        reference_text = "(Rahman et al., 2022), (Raza et al., 2023), (Zaher, 2024)"
        reference_label = QLabel(reference_text)
        reference_label.setFont(font_utils.get_font(size=12))
        reference_label.setWordWrap(True)
        reference_label.setStyleSheet(f"color: {constants.PRIMARY_800};")
        layout.addWidget(reference_label)
        
        image_container = QWidget()
        image_layout = QHBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(40)  
        
        if os.path.exists(constants.LSTM1_IMAGE_PATH):
            left_image_container = QWidget()
            left_image_layout = QVBoxLayout(left_image_container)
            left_image_layout.setContentsMargins(0, 0, 0, 0)
            left_image_layout.setSpacing(5)
            
            left_image = QLabel()
            left_pixmap = QPixmap(constants.LSTM1_IMAGE_PATH)
            left_image.setPixmap(left_pixmap.scaled(400, 240, Qt.AspectRatioMode.KeepAspectRatio))
            left_image_layout.addWidget(left_image)
            
            left_url = QLabel("https://www.onnxinstitute.org/neural-network-zoo/")
            left_url.setFont(font_utils.get_font(size=10))
            left_url.setStyleSheet(f"color: {constants.PRIMARY_800};")
            left_image_layout.addWidget(left_url)
            
            image_layout.addWidget(left_image_container)
        
        if os.path.exists(constants.LSTM2_IMAGE_PATH):
            right_image_container = QWidget()
            right_image_layout = QVBoxLayout(right_image_container)
            right_image_layout.setContentsMargins(0, 0, 0, 0)
            right_image_layout.setSpacing(5)
            
            right_image = QLabel()
            right_pixmap = QPixmap(constants.LSTM2_IMAGE_PATH)
            right_image.setPixmap(right_pixmap.scaled(400, 240, Qt.AspectRatioMode.KeepAspectRatio))
            right_image_layout.addWidget(right_image)
            
            right_url = QLabel("https://images.app.goo.gl/FmSf16muzd4kwg9")
            right_url.setFont(font_utils.get_font(size=10))
            right_url.setStyleSheet(f"color: {constants.PRIMARY_800};")
            right_image_layout.addWidget(right_url)
            
            image_layout.addWidget(right_image_container)
        
        layout.addWidget(image_container)
        layout.addStretch()
        
        return page
    
    def create_blazepose_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Blazepose")
        title_label.setFont(font_utils.get_font(size=36, weight=constants.WEIGHT_BOLD))
        title_label.setStyleSheet(f"color: {constants.PRIMARY_800};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title_label)
        
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(80)
        
        # Description text
        description = """LSTM is a type of recurrent neural networks (RNN), and the component of an artificial neural network that has additional memory cells for time steps that remember previous information. Typically, LSTM is used to efficiently learn and interpret complex data sequences. In this study, sequence analysis models like Long-Short Term Memory (LSTM) are essential for enabling real-time classification of rehabilitation exercises, allowing for precise tracking of motion patterns over time.
        
Moreover, based on a different study, LSTM is the kind of model that can accurately represent sequential data like human posture and gesture details using key skeletal landmarks. On the contrary, when compared to conventional RNN, LSTM is the type of model that uses a complex gating mechanism that enables the retention of long-range dependencies which then evades the problem of gradient vanishing or gradient exploding during training when using conventional RNN. As a result, it is recommended to use LSTM as the basis model of the study as it possesses the ability to retain information which in turn can be enhanced when attention mechanism is applied."""
        
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 20)
        text_layout.setSpacing(10)
        
        description_label = QLabel(description)
        description_label.setFont(font_utils.get_font(size=14))
        description_label.setWordWrap(True)
        description_label.setStyleSheet(f"color: {constants.PRIMARY_800};")
        description_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        text_layout.addWidget(description_label)
        
        # References text
        reference_text = "(Rahman et al., 2022), (Raza et al., 2023), (Zaher, 2024)"
        reference_label = QLabel(reference_text)
        reference_label.setFont(font_utils.get_font(size=12))
        reference_label.setWordWrap(True)
        reference_label.setStyleSheet(f"color: {constants.PRIMARY_800};")
        text_layout.addWidget(reference_label)
        
        content_layout.addWidget(text_container, 1)
        
        if os.path.exists(constants.BLAZEPOSE_IMAGE_PATH):
            image_container = QWidget()
            image_layout = QVBoxLayout(image_container)
            image_layout.setContentsMargins(0, 0, 0, 0)
            image_layout.setSpacing(5)
            
            image = QLabel()
            pixmap = QPixmap(constants.BLAZEPOSE_IMAGE_PATH)
            image.setPixmap(pixmap.scaled(400, 450, Qt.AspectRatioMode.KeepAspectRatio))
            image.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_layout.addWidget(image)
            
            url_label = QLabel("https://arxiv.ices.utexas.edu/html/2006.10204")
            url_label.setFont(font_utils.get_font(size=10))
            url_label.setStyleSheet(f"color: {constants.PRIMARY_800}; margin-bottom: 100px;")
            image_layout.addWidget(url_label)
            
            content_layout.addWidget(image_container)
        
        layout.addWidget(content_widget)
        layout.addStretch()
        
        return page
    
    def create_attention_mechanism_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Attention Mechanism")
        title_label.setFont(font_utils.get_font(size=36, weight=constants.WEIGHT_BOLD))
        title_label.setStyleSheet(f"color: {constants.PRIMARY_800};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title_label)
        
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(80)
        
        # Description text
        description = """LSTM is a type of recurrent neural networks (RNN), and the component of an artificial neural network that has additional memory cells for time steps that remember previous information. Typically, LSTM is used to efficiently learn and interpret complex data sequences. In this study, sequence analysis models like Long-Short Term Memory (LSTM) are essential for enabling real-time classification of rehabilitation exercises, allowing for precise tracking of motion patterns over time.
        
Moreover, based on a different study, LSTM is the kind of model that can accurately represent sequential data like human posture and gesture details using key skeletal landmarks. On the contrary, when compared to conventional RNN, LSTM is the type of model that uses a complex gating mechanism that enables the retention of long-range dependencies which then evades the problem of gradient vanishing or gradient exploding during training when using conventional RNN. As a result, it is recommended to use LSTM as the basis model of the study as it possesses the ability to retain information which in turn can be enhanced when attention mechanism is applied."""
        
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 20)
        text_layout.setSpacing(10)
        
        description_label = QLabel(description)
        description_label.setFont(font_utils.get_font(size=14))
        description_label.setWordWrap(True)
        description_label.setStyleSheet(f"color: {constants.PRIMARY_800};")
        description_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        text_layout.addWidget(description_label)
        
        # References text
        reference_text = "(Rahman et al., 2022), (Raza et al., 2023), (Zaher, 2024)"
        reference_label = QLabel(reference_text)
        reference_label.setFont(font_utils.get_font(size=12))
        reference_label.setWordWrap(True)
        reference_label.setStyleSheet(f"color: {constants.PRIMARY_800};")
        text_layout.addWidget(reference_label)
        
        content_layout.addWidget(text_container, 1)
        
        if os.path.exists(constants.ATTENTION_MECHANISM_IMAGE_PATH):
            image_container = QWidget()
            image_layout = QVBoxLayout(image_container)
            image_layout.setContentsMargins(0, 0, 0, 0)
            image_layout.setSpacing(5)
            
            image = QLabel()
            pixmap = QPixmap(constants.ATTENTION_MECHANISM_IMAGE_PATH)
            image.setPixmap(pixmap.scaled(400, 450, Qt.AspectRatioMode.KeepAspectRatio))
            image.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_layout.addWidget(image)
            
            url_label = QLabel("https://arxiv.org/abs/1706.03762")
            url_label.setFont(font_utils.get_font(size=10))
            url_label.setStyleSheet(f"color: {constants.PRIMARY_800}; margin-bottom: 100px;")
            image_layout.addWidget(url_label)
            
            content_layout.addWidget(image_container)
        
        layout.addWidget(content_widget)
        layout.addStretch()
        
        return page
    
    def show_lstm_page(self):
        self.stacked_widget.setCurrentWidget(self.lstm_page)
        self.current_page = "lstm"
        self.update_submenu_states()
        
    def show_blazepose_page(self):
        self.stacked_widget.setCurrentWidget(self.blazepose_page)
        self.current_page = "blazepose"
        self.update_submenu_states()
        
    def show_attention_mechanism_page(self):
        self.stacked_widget.setCurrentWidget(self.attention_mechanism_page)
        self.current_page = "attention"
        self.update_submenu_states()
    
    def update_submenu_states(self):
        for name, button in self.model_buttons.items():
            if name == self.current_page:
                button.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {constants.PRIMARY_500};
                        color: {constants.WHITE};
                        padding: 15px;
                        padding-left: 30px;
                        text-align: left;
                        border: none;
                        width: 100%;
                    }}
                    QPushButton:hover {{
                        background-color: {constants.PRIMARY_500};
                    }}
                    """
                )
            else:
                button.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {constants.PRIMARY_400};
                        color: {constants.WHITE};
                        padding: 15px;
                        padding-left: 30px;
                        text-align: left;
                        border: none;
                        width: 100%;
                    }}
                    QPushButton:hover {{
                        background-color: {constants.PRIMARY_600};
                    }}
                    """
                )
