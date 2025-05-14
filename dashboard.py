from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QFrame,
    QApplication,
    QRadioButton,
    QButtonGroup,
    QScrollArea,
    QMenu,
    QToolButton,
)

from PyQt6.QtGui import QIcon, QPixmap, QAction
from PyQt6.QtCore import Qt, QSize, pyqtSignal

import constants
import font_utils
import os
import sys


class DashboardWindow(QMainWindow):
    # Define signals for navigation
    home_button_clicked = pyqtSignal()
    test_button_clicked = pyqtSignal()
    exercises_button_clicked = pyqtSignal()
    model_button_clicked = pyqtSignal()
    profile_button_clicked = pyqtSignal()
    quit_button_clicked = pyqtSignal()
    lstm_clicked = pyqtSignal()
    blazepose_clicked = pyqtSignal()
    attention_mechanism_clicked = pyqtSignal()
    session_selected = pyqtSignal(int)  # Signal emitted when a session is clicked, passes session_id
    
    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager # Store session_manager
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.init_ui()
        # Connect signal and call update method
        self.session_manager.session_updated.connect(self.update_dashboard_data)
        self.update_dashboard_data() 

    def init_ui(self):
        self.setWindowTitle("Dashboard")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setStyleSheet(
            f"background-color: {constants.PRIMARY_100}; color: {constants.PRIMARY_600};"
        )

        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar using the same structure as in exercise.py
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        content_container = QWidget()
        self.content_layout = QVBoxLayout(content_container)
        self.content_layout.setContentsMargins(50, 50, 50, 50)
        self.content_layout.setSpacing(30)

        header_layout = QHBoxLayout()

        greeting_layout = QVBoxLayout()
        self.hello_label = QLabel("Hello, Guest")
        hello_font = font_utils.get_font(size=32, weight=constants.WEIGHT_BOLD)
        self.hello_label.setFont(hello_font)

        self.sessions_label = QLabel("You have 0 sessions today")
        sessions_font = font_utils.get_font(size=18)
        self.sessions_label.setFont(sessions_font)

        greeting_layout.addWidget(self.hello_label)
        greeting_layout.addWidget(self.sessions_label)

        header_layout.addLayout(greeting_layout, 1)

        edit_info_button = QPushButton("Edit info")
        edit_info_button.setFont(font_utils.get_font(size=12))
        edit_info_button.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_info_button.setFixedSize(100, 35)
        edit_info_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_400};
                color: {constants.WHITE};
                padding: 8px 16px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {constants.PRIMARY_500};
            }}
            """
        )

        header_layout.addWidget(edit_info_button)

        # General Information
        info_section = QVBoxLayout()

        info_title = QLabel("General Information")
        info_title_font = font_utils.get_font(size=16, weight=constants.WEIGHT_BOLD)
        info_title.setFont(info_title_font)
        info_section.addWidget(info_title)

        info_grid = QGridLayout()
        info_grid.setHorizontalSpacing(80)
        info_grid.setVerticalSpacing(10)

        self.left_grid = QGridLayout()
        self.left_grid.setHorizontalSpacing(15)
        self.left_grid.setVerticalSpacing(10)

        self.right_grid = QGridLayout()
        self.right_grid.setHorizontalSpacing(15)
        self.right_grid.setVerticalSpacing(10)
        
        # Define the labels for user information
        self.left_info_labels = [
            "Full Name",
            "Contact Number",
            "Sex",
            "Address",
        ]

        self.right_info_labels = [
            "Age",
            "Email",
            "Total Sessions",
            "Last Session",
        ]
        
        # Default values (will be updated with real data)
        left_info_values = [
            "Guest User",
            "Not available",
            "Not specified",
            "Not specified",
        ]
        
        right_info_values = [
            "Not available",
            "Not available",
            "0",
            "Never",
        ]

        self.label_font = font_utils.get_font(size=12)
        self.value_font = font_utils.get_font(size=12)
        
        # Create and store references to the value labels so we can update them later
        self.left_info_value_widgets = []
        self.right_info_value_widgets = []

        for i, (label, value) in enumerate(zip(self.left_info_labels, left_info_values)):
            label_widget = QLabel(label)
            label_widget.setFont(self.label_font)

            value_widget = QLabel(value)
            value_widget.setFont(self.value_font)
            value_widget.setStyleSheet("font-weight: bold;")
            
            self.left_info_value_widgets.append(value_widget)

            self.left_grid.addWidget(label_widget, i, 0)
            self.left_grid.addWidget(value_widget, i, 1)

        for i, (label, value) in enumerate(zip(self.right_info_labels, right_info_values)):
            label_widget = QLabel(label)
            label_widget.setFont(self.label_font)

            value_widget = QLabel(value)
            value_widget.setFont(self.value_font)
            value_widget.setStyleSheet("font-weight: bold;")
            
            self.right_info_value_widgets.append(value_widget)

            self.right_grid.addWidget(label_widget, i, 0)
            self.right_grid.addWidget(value_widget, i, 1)

        left_widget = QWidget()
        left_widget.setLayout(self.left_grid)

        right_widget = QWidget()
        right_widget.setLayout(self.right_grid)

        info_grid.addWidget(left_widget, 0, 0)
        info_grid.addWidget(right_widget, 0, 1)

        info_section.addLayout(info_grid)

        # Exercise Repetition
        exercise_section = QVBoxLayout()

        exercise_title = QLabel("Exercise Repetition:")
        exercise_title.setFont(info_title_font)
        exercise_section.addWidget(exercise_title)

        exercise_options_layout = QGridLayout()
        exercise_options_layout.setHorizontalSpacing(30)
        exercise_options_layout.setVerticalSpacing(10)

        exercise_group = QButtonGroup(self)

        radio_font = font_utils.get_font(size=12)

        self.three_radio = QRadioButton("3")
        self.three_radio.setFont(radio_font)
        self.three_radio.setChecked(True)
        exercise_group.addButton(self.three_radio)

        self.five_radio = QRadioButton("5")
        self.five_radio.setFont(radio_font)
        exercise_group.addButton(self.five_radio)

        self.seven_radio = QRadioButton("7")
        self.seven_radio.setFont(radio_font)
        exercise_group.addButton(self.seven_radio)

        radio_style = """
        QRadioButton {
            spacing: 5px;
        }
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
        }
        """

        self.three_radio.setStyleSheet(radio_style)
        self.five_radio.setStyleSheet(radio_style)
        self.seven_radio.setStyleSheet(radio_style)

        exercise_options_layout.addWidget(self.three_radio, 0, 0)
        exercise_options_layout.addWidget(self.five_radio, 0, 1)
        exercise_options_layout.addWidget(self.seven_radio, 0, 2)

        exercise_section.addLayout(exercise_options_layout)

        # Position Preference
        position_section = QVBoxLayout()

        position_title = QLabel("Preferred Position:")
        position_title.setFont(info_title_font)
        position_section.addWidget(position_title)

        position_options_layout = QHBoxLayout()

        position_group = QButtonGroup(self)

        self.sitting_radio = QRadioButton("Sitting")
        self.sitting_radio.setFont(radio_font)
        position_group.addButton(self.sitting_radio)

        self.standing_radio = QRadioButton("Standing")
        self.standing_radio.setFont(radio_font)
        self.standing_radio.setChecked(True) # Default
        position_group.addButton(self.standing_radio)

        self.sitting_radio.setStyleSheet(radio_style)
        self.standing_radio.setStyleSheet(radio_style)

        position_options_layout.addWidget(self.sitting_radio)
        position_options_layout.addWidget(self.standing_radio)
        position_options_layout.addStretch()

        position_section.addLayout(position_options_layout)

        latest_sessions_frame = QFrame()
        latest_sessions_frame.setFixedWidth(320)
        latest_sessions_frame.setStyleSheet(
            f"""
            background-color: {constants.PRIMARY_300};
            border-radius: 10px;
            """
        )

        # Latest Sessions
        latest_sessions_main_layout = QVBoxLayout(latest_sessions_frame)
        latest_sessions_main_layout.setContentsMargins(15, 15, 15, 15)
        latest_sessions_main_layout.setSpacing(10)

        sessions_header = QHBoxLayout()

        latest_sessions_title = QLabel("Latest Sessions")
        latest_sessions_title.setFont(
            font_utils.get_font(size=16, weight=constants.WEIGHT_BOLD)
        )
        latest_sessions_title.setStyleSheet(f"color: {constants.WHITE};")

        sessions_header.addWidget(latest_sessions_title)

        arrow_label = QLabel()
        arrow_pixmap = QPixmap(
            os.path.join(self.script_dir, "imgs", "arrow-diagonal.png")
        )
        arrow_label.setPixmap(
            arrow_pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio)
        )
        arrow_label.setStyleSheet("background: transparent;")

        sessions_header.addWidget(arrow_label)

        latest_sessions_main_layout.addLayout(sessions_header)

        sessions_subtitle = QLabel("Stay updated on your last session.")
        sessions_subtitle.setFont(font_utils.get_font(size=12))
        sessions_subtitle.setStyleSheet(f"color: {constants.WHITE};")
        latest_sessions_main_layout.addWidget(sessions_subtitle)

        session_scroll_area = QScrollArea()
        session_scroll_area.setWidgetResizable(True)
        session_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        session_scroll_area.setStyleSheet("background: transparent;")

        scroll_content = QWidget()
        # Store scroll_layout as an instance variable to access it later
        self.sessions_scroll_layout = QVBoxLayout(scroll_content)
        self.sessions_scroll_layout.setContentsMargins(0, 5, 0, 5)
        self.sessions_scroll_layout.setSpacing(10)

        self.sessions_scroll_layout.addStretch(1) # Keep the stretch
        session_scroll_area.setWidget(scroll_content)
        latest_sessions_main_layout.addWidget(session_scroll_area, 1)

        dashboard_layout = QHBoxLayout()

        left_content = QVBoxLayout()
        left_content.setSpacing(15)
        left_content.addLayout(header_layout) # Header first
        left_content.addSpacing(15) # Spacing
        # Add sections back to the left side
        left_content.addLayout(info_section)
        left_content.addSpacing(10)
        left_content.addLayout(exercise_section)
        left_content.addSpacing(10)
        left_content.addLayout(position_section)
        left_content.addStretch(1)

        # Add left content and right sessions panel to dashboard layout
        dashboard_layout.addLayout(left_content, 3) # Left takes 3/4 space
        dashboard_layout.addWidget(latest_sessions_frame, 1) # Right takes 1/4 space

        # Add the dashboard layout to the main content area
        self.content_layout.addLayout(dashboard_layout)

        main_layout.addWidget(content_container, 1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def go_to_home(self):
        self.home_button_clicked.emit()
        print("Navigate to Home page")

    def go_to_test(self):
        self.test_button_clicked.emit()
        print("Navigate to Test page")

    def go_to_exercises(self):
        self.exercises_button_clicked.emit()
        print("Navigate to Exercises page")

    def go_to_model(self):
        self.model_button_clicked.emit()
        print("Navigate to Model page")

    def logout(self):
        self.session_manager.logout_user()
        self.quit_button_clicked.emit()
        print("Logged out.")
        
    def create_sidebar(self):
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet(f"background-color: {constants.PRIMARY_400};")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo
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
        self.home_button = QPushButton("  Home")
        self.home_button.setFont(font_utils.get_font(size=10))
        self.home_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.HOME_ICON_PATH):
            self.home_button.setIcon(QIcon(constants.HOME_ICON_PATH))
            self.home_button.setIconSize(QSize(18, 18))
        self.home_button.clicked.connect(self.home_button_clicked.emit)
        self.home_button.setStyleSheet(
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
        sidebar_layout.addWidget(self.home_button)
        
        # Exercises button
        self.exercises_button = QPushButton("  Exercises")
        self.exercises_button.setFont(font_utils.get_font(size=10))
        self.exercises_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.EXERCISES_ICON_PATH):
            self.exercises_button.setIcon(QIcon(constants.EXERCISES_ICON_PATH))
            self.exercises_button.setIconSize(QSize(18, 18))
        self.exercises_button.clicked.connect(self.exercises_button_clicked.emit)
        self.exercises_button.setStyleSheet(
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
        sidebar_layout.addWidget(self.exercises_button)
        
        # Model button with dropdown
        self.model_button = QToolButton()
        self.model_button.setText("  Model")
        self.model_button.setFont(font_utils.get_font(size=10))
        self.model_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if os.path.exists(constants.MODEL_ICON_PATH):
            self.model_button.setIcon(QIcon(constants.MODEL_ICON_PATH))
            self.model_button.setIconSize(QSize(18, 18))
        
        self.model_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
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
        attention_mechanism_action.triggered.connect(self.attention_mechanism_clicked.emit)
        
        model_menu.addAction(lstm_action)
        model_menu.addAction(blazepose_action)
        model_menu.addAction(attention_mechanism_action)
        
        self.model_button.setMenu(model_menu)
        sidebar_layout.addWidget(self.model_button)
        
        # Profile Dashboard button (active)
        self.profile_button = QPushButton("  Profile Dashboard")
        self.profile_button.setFont(font_utils.get_font(size=10))
        self.profile_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.PROFILE_ICON_PATH):
            self.profile_button.setIcon(QIcon(constants.PROFILE_ICON_PATH))
            self.profile_button.setIconSize(QSize(18, 18))
        self.profile_button.clicked.connect(self.profile_button_clicked.emit)
        self.profile_button.setStyleSheet(
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
        sidebar_layout.addWidget(self.profile_button)
        
        # Test button
        self.test_button = QPushButton("  Test Exercises")
        self.test_button.setFont(font_utils.get_font(size=10))
        self.test_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.EXERCISES_ICON_PATH):
            self.test_button.setIcon(QIcon(constants.EXERCISES_ICON_PATH))
            self.test_button.setIconSize(QSize(18, 18))
        self.test_button.clicked.connect(self.test_button_clicked.emit)
        self.test_button.setStyleSheet(
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
        sidebar_layout.addWidget(self.test_button)
        
        sidebar_layout.addStretch()
        
        # Quit button
        self.quit_button = QPushButton("  Quit")
        self.quit_button.setFont(font_utils.get_font(size=10))
        self.quit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.QUIT_ICON_PATH):
            self.quit_button.setIcon(QIcon(constants.QUIT_ICON_PATH))
            self.quit_button.setIconSize(QSize(18, 18))
        self.quit_button.clicked.connect(self.quit_button_clicked.emit)
        self.quit_button.setStyleSheet(
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
        sidebar_layout.addWidget(self.quit_button)
        
        return sidebar

    # Re-add update_dashboard_data method
    def update_dashboard_data(self):
        user_name = self.session_manager.get_user_name()
        user_details = self.session_manager.get_user_details()
        session_stats = self.session_manager.get_session_stats()

        if user_name:
            self.hello_label.setText(f"Hello, {user_name}")
        else:
             self.hello_label.setText("Hello, Guest")

        if self.session_manager.is_logged_in():
            total_sessions = session_stats.get('total_completed_sessions', 0)
            last_session_date = session_stats.get('last_session_date', 'N/A')

            self.sessions_label.setText(f"You have completed {total_sessions} sessions.")
            # Update user details panel
            self.update_user_details(user_details, session_stats)

            # Fetch onboarding details and update preference controls
            onboarding_details = self.session_manager.get_onboarding_details()
            if onboarding_details:
                self.update_preference_controls(onboarding_details)
            else:
                 # Optional: Set default state if no onboarding data
                 self.update_preference_controls({}) # Pass empty dict for defaults

            # Update latest sessions display
            self.update_latest_sessions_display()

        else:
            # Handle logged out state
            self.hello_label.setText("Hello, Guest")
            self.sessions_label.setText("Log in to see your session data.")
            # Reset user details panel (optional, could show defaults or clear)
            self.update_user_details(None, {}) # Pass None or default dict
            
            # Clear/reset preference controls on logout
            self.update_preference_controls({}) # Pass empty dict for defaults
            
            # Clear latest sessions display when logged out
            self.update_latest_sessions_display(clear_only=True)

    # Re-add update_user_details method
    def update_user_details(self, user_details, session_stats):
        # Default values for logged out state or if details are missing
        default_left_values = [
            "Guest User", "Not available", "Not specified", "Not specified",
        ]
        default_right_values = [
            "Not available", "Not available", "0", "Never",
        ]
        
        left_values = default_left_values
        right_values = default_right_values

        if user_details:
            # Update left info panel if user_details exist
            full_name = f"{user_details.get('first_name', '')} {user_details.get('last_name', '')}".strip()
            if not full_name: full_name = default_left_values[0]
            contact = user_details.get('contact_number') or default_left_values[1]
            sex = user_details.get('sex') or default_left_values[2]
            address = user_details.get('address') or default_left_values[3]
            left_values = [full_name, contact, sex, address]
            
            # Update right info panel if user_details exist
            age = str(user_details.get('age', default_right_values[0]))
            email = user_details.get('email') or default_right_values[1]
            # Use session_stats passed to this method to update info grid
            total_sessions = str(session_stats.get('total_completed_sessions', default_right_values[2]))
            last_session = session_stats.get('last_session_date', default_right_values[3])
             # Basic formatting for last_session date if needed here, similar to update_dashboard_data
            if isinstance(last_session, str) and last_session != 'Never' and ' ' in last_session:
                 last_session = last_session.split(' ')[0] # Show date part only
            elif last_session is None:
                 last_session = 'Never'
                 
            right_values = [age, email, total_sessions, last_session]
        
        # Apply the determined values to the widgets
        for widget, value in zip(self.left_info_value_widgets, left_values):
            widget.setText(str(value))
        
        for widget, value in zip(self.right_info_value_widgets, right_values):
            widget.setText(str(value))
        
        # Force update (optional, usually not needed unless experiencing display issues)
        # for widget in self.left_info_value_widgets + self.right_info_value_widgets:
        #     widget.repaint()

    # New method to update preference radio buttons
    def update_preference_controls(self, onboarding_data):
        preferred_reps = onboarding_data.get('preferred_reps', 3) # Default to 3 reps
        needs_assistance = onboarding_data.get('needs_assistance', False) # Default to False (Standing)

        # Set Exercise Repetition radio button
        if preferred_reps == 3:
            self.three_radio.setChecked(True)
        elif preferred_reps == 5:
            self.five_radio.setChecked(True)
        elif preferred_reps == 7:
            self.seven_radio.setChecked(True)
        else:
            self.three_radio.setChecked(True) # Fallback default

        # Set Preferred Position radio button
        if needs_assistance:
            self.sitting_radio.setChecked(True)
        else:
            self.standing_radio.setChecked(True)

    # New method to update the latest sessions display
    def update_latest_sessions_display(self, clear_only=False):
        # Clear existing session cards first
        # Remove items in reverse order to avoid index issues
        while self.sessions_scroll_layout.count() > 1: # Keep the stretch item
            item = self.sessions_scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            # If item is a layout, delete it properly (though unlikely here)
            layout_item = item.layout()
            if layout_item:
                # Recursively delete widgets in the layout
                while layout_item.count():
                    sub_item = layout_item.takeAt(0)
                    sub_widget = sub_item.widget()
                    if sub_widget:
                        sub_widget.deleteLater()
                # Delete the layout itself? Usually widgets are parented, deleting them suffices.
                # layout_item.deleteLater() # Be cautious with deleting layouts directly

        if clear_only:
             # Optionally add a message when logged out/no sessions
            no_sessions_label = QLabel("No recent sessions found.")
            no_sessions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_sessions_label.setStyleSheet(f"color: {constants.PRIMARY_600};") # Use an appropriate color
            self.sessions_scroll_layout.insertWidget(0, no_sessions_label) # Insert at the top
            return

        # Fetch latest sessions data
        latest_sessions = self.session_manager.get_latest_sessions(limit=10) # Fetch e.g., 10 latest

        if not latest_sessions:
            no_sessions_label = QLabel("No recent sessions found.")
            no_sessions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_sessions_label.setStyleSheet(f"color: {constants.PRIMARY_600};")
            self.sessions_scroll_layout.insertWidget(0, no_sessions_label)
            return

        # Create and add new session cards
        for entry in latest_sessions:
            session_card = QPushButton()
            session_card.setFixedHeight(60)
            session_card.setCursor(Qt.CursorShape.PointingHandCursor)
            session_card.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {constants.WHITE};
                    border-radius: 8px;
                    text-align: left;
                    padding: 8px 10px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {constants.PRIMARY_100};
                }}
                """
            )

            session_card_layout = QVBoxLayout(session_card)
            session_card_layout.setContentsMargins(10, 8, 10, 8)
            session_card_layout.setSpacing(2)
            session_card_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            exercise_name = entry.get("exercise", "Unknown Exercise")
            exercise_label = QLabel(exercise_name)
            exercise_label.setFont(
                font_utils.get_font(size=12, weight=constants.WEIGHT_BOLD)
            )
            exercise_label.setStyleSheet("background: transparent; border: none;")

            session_date_str = entry.get("date", "Unknown Date")
            # Format the date nicely
            formatted_date = session_date_str
            try:
                from PyQt6.QtCore import QDateTime
                dt = QDateTime.fromString(session_date_str, "yyyy-MM-dd HH:mm:ss")
                if dt.isValid():
                     formatted_date = dt.toString("MMM dd, yyyy")
                else: # Basic fallback if format is just date
                     dt = QDateTime.fromString(session_date_str, "yyyy-MM-dd")
                     if dt.isValid():
                          formatted_date = dt.toString("MMM dd, yyyy")
                     # Keep original string if parsing fails
            except ImportError:
                 pass # Keep original string
            except Exception:
                 pass # Keep original string

            date_label = QLabel(formatted_date)
            date_label.setFont(font_utils.get_font(size=11))
            date_label.setStyleSheet("background: transparent; border: none;")

            session_card_layout.addWidget(exercise_label)
            session_card_layout.addWidget(date_label)

            # Store the session ID in the button's property
            session_id = entry.get("session_id")
            if session_id:
                # Connect click event to emit signal with session_id
                session_card.clicked.connect(lambda checked=False, sid=session_id: self.session_selected.emit(sid))

            # Insert new cards before the stretch item
            self.sessions_scroll_layout.insertWidget(self.sessions_scroll_layout.count() - 1, session_card)

if __name__ == "__main__":
    # Define MockSessionManager for standalone testing
    class MockSessionManager:
        session_updated = pyqtSignal(dict)
        def get_user_name(self): return "Test User"
        def is_logged_in(self): return True
        def get_session_stats(self): return {'total_completed_sessions': 5, 'last_session_date': '2023-10-27 10:00:00'}
        def get_user_details(self): 
            return {
                'first_name': 'Mock', 'last_name': 'User', 'email': 'mock@test.com', 
                'contact_number': '1234567890', 'sex': 'Other', 'address': '123 Mock St', 'age': 30
            }
        # Add mock for get_onboarding_details
        def get_onboarding_details(self):
            # Return some mock onboarding data
            return {'needs_assistance': True, 'preferred_reps': 5}
        # Add mock for get_latest_sessions if needed for standalone testing later
        def get_latest_sessions(self, limit=5):
             # Return some mock sessions for standalone testing
            return [
                {"exercise": "Mock Flank Stretch", "date": "2024-01-15 10:00:00"},
                {"exercise": "Mock Torso Rotation", "date": "2024-01-14 15:30:00"},
                {"exercise": "Mock Back Arch", "date": "2024-01-13 09:00:00"},
            ] * (limit // 3 + 1) # Simple way to generate more if limit > 3

    app = QApplication(sys.argv)
    mock_session = MockSessionManager()
    # Pass mock session manager when running directly
    window = DashboardWindow(mock_session)
    window.show()
    sys.exit(app.exec())
