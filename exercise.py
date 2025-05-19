from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QMenu,
    QToolButton,
    QStackedWidget,
    QFrame,
    QScrollArea
)
from PyQt6.QtGui import QIcon, QPixmap, QAction, QImage
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
import cv2 

import constants
import font_utils
import os

class ExercisesWindow(QMainWindow):
    home_button_clicked = pyqtSignal()
    profile_button_clicked = pyqtSignal()
    quit_button_clicked = pyqtSignal()
    lstm_clicked = pyqtSignal()
    blazepose_clicked = pyqtSignal()
    attention_mechanism_clicked = pyqtSignal()
    test_button_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.stacked_widget = QStackedWidget()
        
        self.main_view = QWidget()
        self.init_main_view()
        
        self.torso_view = self.create_exercise_detail_view("Torso Rotation", constants.TORSO_PREVIEW_VID)
        self.flank_view = self.create_exercise_detail_view("Flank Stretch", constants.FLANK_PREVIEW_VID)
        self.hiding_view = self.create_exercise_detail_view("Hiding Face", constants.HIDING_FACE_PREVIEW_VID)
        
        self.stacked_widget.addWidget(self.main_view)
        self.stacked_widget.addWidget(self.torso_view)
        self.stacked_widget.addWidget(self.flank_view)
        self.stacked_widget.addWidget(self.hiding_view)
        
        self.setCentralWidget(self.stacked_widget)
        
        self.setWindowTitle("RevAItalize - Exercises")
        self.resize(1200, 800)

    def init_main_view(self):
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        content_area = QWidget()
        content_area.setStyleSheet(f"background-color: {constants.PRIMARY_100};")
        
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(50, 30, 50, 30)
        
        # --- Start of scrollable content for main_view ---
        scroll_area_main = QScrollArea()
        scroll_area_main.setWidgetResizable(True)
        scroll_area_main.setStyleSheet(f"""
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
                background: {constants.GRAY};
                border: 1px solid {constants.PRIMARY_700};
                border-radius: 6px;
                width: 12px;
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
        
        scroll_content_widget_main = QWidget()
        scroll_content_layout_main = QVBoxLayout(scroll_content_widget_main)
        scroll_content_layout_main.setContentsMargins(0,0,0,0) # Adjust as needed
        scroll_content_layout_main.setSpacing(20) # Original spacing for content_layout parts

        # Description text 
        description_text = QLabel("These three exercises have been chosen in relation to the available datasets for low-back treatment.")
        description_text.setFont(font_utils.get_font(size=16))
        description_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_text.setWordWrap(True)
        description_text.setStyleSheet(f"color: {constants.PRIMARY_800}; margin-top: 50px;")
        
        scroll_content_layout_main.addWidget(description_text)
        
        exercise_layout = QHBoxLayout()
        exercise_layout.setSpacing(0)  
        exercise_layout.setContentsMargins(0, 0, 0, 0)
        
        torso_img_path = os.path.join(self.script_dir, "imgs", "torso-rotation-ex.png")
        flank_img_path = os.path.join(self.script_dir, "imgs", "flank-stretch-ex.png")
        hiding_img_path = os.path.join(self.script_dir, "imgs", "hiding-face-ex.png")
        
        torso_container, torso_img = self.create_clickable_image("Torso Rotation", torso_img_path)
        flank_container, flank_img = self.create_clickable_image("Flank Stretch", flank_img_path)
        hiding_container, hiding_img = self.create_clickable_image("Hiding Face", hiding_img_path)
        
        # Connect image clicks to show detail views
        torso_img.mousePressEvent = lambda event: self.stacked_widget.setCurrentWidget(self.torso_view)
        flank_img.mousePressEvent = lambda event: self.stacked_widget.setCurrentWidget(self.flank_view)
        hiding_img.mousePressEvent = lambda event: self.stacked_widget.setCurrentWidget(self.hiding_view)
        
        exercise_layout.addWidget(torso_container, 1)  
        exercise_layout.addWidget(flank_container, 1)  
        exercise_layout.addWidget(hiding_container, 1)  
        
        scroll_content_layout_main.addLayout(exercise_layout)
        
        # Data utilization section
        data_title = QLabel("Data Utilization")
        data_title.setFont(font_utils.get_font(size=18, weight=constants.WEIGHT_BOLD))
        data_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        data_title.setStyleSheet(f"color: {constants.PRIMARY_800}; margin-top: 30px;")
        
        data_desc = QLabel(
            "The Kinesiotherapy and Rehabilitation for Assisted Ambient Living (KERAAL) post-rehabilitation exercise data "
            "was chosen to train and validate the LSTM model amounting to 2,622 data points. The researchers organized "
            "the dataset into five groups (1A, 1B, 2A, 2B, and 3), with videos in Group 3 formatted as AVI (960x544 resolution) "
            "and the others in MP4 (480x360 resolution). Each group contained videos of three exercises (hiding face, torso "
            "rotation, flank stretch), and Groups 1A, 2A, and 3 featured annotations by two medical experts in XML Anvil "
            "format. These annotations detailed exercise correctness, error type, involved body part, and error timestamps."
        )
        data_desc.setFont(font_utils.get_font(size=12))
        data_desc.setWordWrap(True)
        data_desc.setAlignment(Qt.AlignmentFlag.AlignJustify)
        data_desc.setStyleSheet(f"color: {constants.PRIMARY_800};")
        
        scroll_content_layout_main.addWidget(data_title)
        scroll_content_layout_main.addSpacing(10)
        scroll_content_layout_main.addWidget(data_desc)
        
        scroll_content_layout_main.addStretch()
        scroll_content_widget_main.setLayout(scroll_content_layout_main)
        scroll_area_main.setWidget(scroll_content_widget_main)
        
        content_layout.addWidget(scroll_area_main, 1) # Add the scroll area to the main content layout, stretch factor 1
        
        # Test exercises button (remains at the bottom of content_area, after scroll area)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        test_button = QPushButton(" Test Exercises")
        test_button.setFont(font_utils.get_font(size=12))
        test_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.EXERCISES_ICON_PATH):
            test_button.setIcon(QIcon(constants.EXERCISES_ICON_PATH))
            test_button.setIconSize(QSize(20, 20))
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
        
        button_layout.addWidget(test_button)
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_area, 1)
        
        self.main_view.setLayout(main_layout)
    def create_clickable_image(self, title, image_path):
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {constants.PRIMARY_500};
                border: none;
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout(container)
        
        # Image
        img_label = QLabel()
        img_label.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            img_label.setPixmap(pixmap.scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            img_label.setText("Image not found")
        
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(font_utils.get_font(size=14, weight=constants.WEIGHT_BOLD))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"color: {constants.WHITE};")
        
        layout.addWidget(img_label)
        layout.addWidget(title_label)
        
        return container, img_label

    def create_exercise_detail_view(self, exercise_name, video_path):
        detail_view = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        content_area = QWidget()
        content_area.setStyleSheet(f"background-color: {constants.PRIMARY_100};")
        
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(50, 30, 50, 30)
        
        top_bar = QHBoxLayout()
        
        # Back button
        back_button = QPushButton("Back")
        back_button.setFont(font_utils.get_font(size=12))
        back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_view))
        back_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_800};
                color: {constants.WHITE};
                padding: 8px 10px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {constants.PRIMARY_600};
            }}
            """
        )
        back_button.setFixedWidth(100)
        top_bar.addWidget(back_button)
        
        top_bar.addStretch()
        
        # RevAItalize logo 
        logo_image = QLabel()
        if os.path.exists(constants.REVAITALIZE_LOGO_PATH):
            logo_image.setPixmap(QIcon(constants.REVAITALIZE_LOGO_PATH).pixmap(QSize(220, 50)))
        else:
            logo_image.setText("RevAItalize")
            logo_image.setFont(font_utils.get_font(size=32, weight=constants.WEIGHT_BOLD))
            logo_image.setStyleSheet(f"color: {constants.PRIMARY_800};")
        logo_image.setAlignment(Qt.AlignmentFlag.AlignRight)
        top_bar.addWidget(logo_image)
        
        content_layout.addLayout(top_bar)
        content_layout.addSpacing(20)
        
        # --- Start of scrollable content for detail_view ---
        scroll_area_detail = QScrollArea()
        scroll_area_detail.setWidgetResizable(True)
        scroll_area_detail.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
                margin-top: 15px; /* Added top margin */
            }}
            QScrollBar:vertical {{
                border: 1px solid {constants.PRIMARY_700};
                background: {constants.GRAY};
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
        """)
        
        scroll_content_widget_detail = QWidget()
        scroll_content_layout_detail = QVBoxLayout(scroll_content_widget_detail)
        scroll_content_layout_detail.setContentsMargins(0,0,0,0)
        scroll_content_layout_detail.setSpacing(0)
        
        scroll_content_layout_detail.addStretch(1)
        
        exercise_content = QHBoxLayout()
        exercise_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        video_container = QFrame()
        video_container.setStyleSheet(
            f"""
            QFrame {{
                background-color: {constants.PRIMARY_500};
                border: none;
                border-radius: 10px;
            }}
            """
        )
        video_container.setMaximumHeight(350)
        
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)  
        
        # Video display label
        video_label = QLabel()
        video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        video_label.setMinimumSize(420, 280) 
        video_label.setMaximumSize(420, 280) 
        video_label.setScaledContents(False)
        video_label.setStyleSheet(f"background-color: {constants.PRIMARY_400}; border-radius: 8px;")
        
        video_layout.addWidget(video_label)
        
        exercise_content.addWidget(video_container)
        exercise_content.addSpacing(20)  
        
        instructions_container = QVBoxLayout()
        
        # Exercise title
        title_label = QLabel("How to Perform this Exercise?")
        title_label.setFont(font_utils.get_font(size=24, weight=constants.WEIGHT_BOLD))
        title_label.setStyleSheet(f"color: {constants.PRIMARY_800}; margin-top: 45px;")
        
        # Specific exercise name subtitle
        subtitle_label = QLabel(exercise_name)
        subtitle_label.setFont(font_utils.get_font(size=18, weight=constants.WEIGHT_SEMIBOLD))
        subtitle_label.setStyleSheet(f"color: {constants.PRIMARY_700}; margin-top: 25px;")

        # Instructions text based on exercise type
        instruction_text = QLabel()
        if exercise_name == "Torso Rotation":
            instruction_text.setText(
                "  <b>Target Areas:</b> Spine, core, and obliques<br>"
                "  <b>Purpose:</b> Improves spinal mobility, flexibility, and reduces pain.<br><br>"
                "  <b>Instructions:</b><br><br>"
                "  <b>1. Starting Position:</b><br>"
                "     • Sit upright on a chair with your feet flat on the floor, shoulder-width apart.<br>"
                "     • Keep your back straight and shoulders relaxed.<br><br>"
                "  <b>2. Execution:</b><br>"
                "     • Slowly rotate your upper body to the right while keeping your hips and lower body stable.<br>"
                "     • Hold the end position briefly (2–3 seconds), feeling a gentle stretch along your side and spine.<br>"
                "     • Return to the center with control.<br>"
                "     • Repeat the same movement to the left.<br><br>"
                "  <b>3. Tips:</b><br>"
                "     • Do not allow your knees or hips to twist.<br>"
                "     • Avoid jerky or rapid movements; keep it slow and fluid."
            )
        elif exercise_name == "Flank Stretch":
            instruction_text.setText(
                "  <b>Target Areas:</b> Side torso, obliques, and lower back<br>"
                "  <b>Purpose:</b> Enhances flexibility and relieves tension in the lower back.<br><br>"
                "  <b>Instructions:</b><br><br>"
                "  <b>1. Starting Position:</b><br>"
                "     • Sit upright on a stable chair.<br>"
                "     • Keep your back straight and feet flat on the floor.<br><br>"
                "  <b>2. Execution:</b><br>"
                "     • Lift your right arm straight overhead, keeping your arm close to your ear.<br>"
                "     • Inhale deeply, and as you exhale, slowly bend your torso to the left—away from the lifted arm.<br>"
                "     • Feel the stretch along your right side.<br>"
                "     • Hold for 5–10 seconds, breathing steadily.<br>"
                "     • Return to the center and switch sides.<br><br>"
                "  <b>3. Tips:</b><br>"
                "     • Avoid leaning forward or twisting.<br>"
                "     • Do not over extend.<br>"
                "     • Keep your arm extended and your neck relaxed."
            )
        else:  # Hiding Face
            instruction_text.setText(
                "  <b>Target Areas:</b> Shoulders, upper back, neck, and core<br>"
                "  <b>Purpose:</b> Promotes upper body mobility, core engagement, and spinal stability.<br><br>"
                "  <b>Instructions:</b><br><br>"
                "  <b>1. Starting Position:</b><br>"
                "     • Sit or stand upright with your feet shoulder-width apart.<br>"
                "     • Raise both arms to shoulder height with elbows bent at 90 degrees in front of your face, as if \"hiding your face\" behind your forearms.<br>"
                "     • Your forearms should point straight up (like the letter \"L\").<br><br>"
                "  <b>2. Execution:</b><br>"
                "     • Slowly rotate both elbows outwards away from each other (like a goalpost).<br>"
                "     • Engage your core and upper back muscles during the movement.<br>"
                "     • Pause briefly, then return to the starting position with control.<br><br>"
                "  <b>3. Tips:</b><br>"
                "     • Keep your shoulders level and avoid shrugging.<br>"
                "     • Maintain a straight spine and stable hips.<br>"
                "     • Avoid jerky arm movements—smooth control is key."
            )
        
        instruction_text.setFont(font_utils.get_font(size=14))
        instruction_text.setWordWrap(True)
        instruction_text.setAlignment(Qt.AlignmentFlag.AlignJustify)
        instruction_text.setStyleSheet(f"color: {constants.PRIMARY_800};")
        instruction_text.setTextFormat(Qt.TextFormat.RichText)
        
        instructions_container.addWidget(title_label)
        instructions_container.addWidget(subtitle_label)
        instructions_container.addSpacing(20)
        instructions_container.addWidget(instruction_text)
        instructions_container.addStretch()
        
        exercise_content.addLayout(instructions_container, 1)
        
        scroll_content_layout_detail.addLayout(exercise_content)
        scroll_content_layout_detail.addStretch(1)
        scroll_content_widget_detail.setLayout(scroll_content_layout_detail)
        scroll_area_detail.setWidget(scroll_content_widget_detail)
        
        content_layout.addWidget(scroll_area_detail, 1)
        
        button_container = QHBoxLayout()
        button_container.addStretch()
        
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
        
        button_container.addWidget(test_button)
        content_layout.addLayout(button_container)
        
        main_layout.addWidget(content_area, 1)
        detail_view.setLayout(main_layout)
        
        # Set up video playback
        self.video_full_path = os.path.join(self.script_dir, video_path)
        
        # Define a function to update the video frame (will be connected to a timer)
        def update_frame():
            ret, frame = cap.read()
            if not ret:
                # If reached the end of the video, reset to beginning
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    return
            
            # Convert the frame to RGB format (from BGR)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Scale the frame to fit the label while maintaining aspect ratio
            h, w, ch = frame_rgb.shape
            label_w, label_h = video_label.width(), video_label.height()
            
            # Calculate scaling factor to fit within the label
            scale = min(label_w / w, label_h / h)
            new_w, new_h = int(w * scale), int(h * scale)
            
            # Resize the frame
            frame_resized = cv2.resize(frame_rgb, (new_w, new_h))
            
            # Convert to QImage and then to QPixmap
            bytes_per_line = ch * new_w
            q_img = QImage(frame_resized.data, new_w, new_h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # Set the pixmap to the label
            video_label.setPixmap(pixmap)
        
        # Open the video file
        cap = cv2.VideoCapture(self.video_full_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {self.video_full_path}")
            video_label.setText("Video not available")
            video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            # Create a timer to update the video frame
            timer = QTimer(detail_view)
            timer.timeout.connect(update_frame)
            timer.start(33)  # Update at approximately 30 fps
            
            # Call update_frame once to show the first frame
            update_frame()
        
        return detail_view

    def update_frame(self):
        # This method will be implemented for the main view's video playback
        pass
    def create_sidebar(self):
        # Create the sidebar for navigation
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
        exercises_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_600};
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
        
        # Model Selection dropdown
        self.model_button = QToolButton()
        self.model_button.setText("  Model Selection")
        self.model_button.setFont(font_utils.get_font(size=10))
        self.model_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.MODEL_ICON_PATH):
            self.model_button.setIcon(QIcon(constants.MODEL_ICON_PATH))
            self.model_button.setIconSize(QSize(18, 18))
        self.model_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.model_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
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
        
        # Profile Dashboard button
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
