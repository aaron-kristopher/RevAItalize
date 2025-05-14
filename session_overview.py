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
    QToolButton,
    QMenu,
)

from PyQt6.QtGui import QIcon, QPixmap, QAction, QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRectF, QPointF
from PyQt6.QtSql import QSqlQuery

import constants
import font_utils
import os
import sys
import math
from datetime import datetime


class PieChartWidget(QWidget):
    def __init__(self, correct=5, incorrect=2):
        super().__init__()
        self.correct = correct
        self.incorrect = incorrect
        self.total = self.correct + self.incorrect
        self.setMinimumSize(300, 300)
        
    def update_data(self, correct, incorrect):
        self.correct = correct
        self.incorrect = incorrect
        self.total = self.correct + self.incorrect
        self.update()  
        
    def paintEvent(self, event):
        if self.total == 0:  
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        rect_size = min(width, height) - 20
        
        rect = QRectF((width - rect_size) / 2, (height - rect_size) / 2, rect_size, rect_size)
        
        # Convert to integers as required by drawPie
        correct_degrees = int((self.correct / self.total) * 360 * 16)
        incorrect_degrees = int((self.incorrect / self.total) * 360 * 16)
        
        # Convert QRectF to QRect for compatibility
        rect_int = rect.toRect()
        
        correct_brush = QBrush(QColor(constants.PRIMARY_800))
        painter.setBrush(correct_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPie(rect_int, 0, correct_degrees)
        
        incorrect_brush = QBrush(QColor("#A3E4FF"))  
        painter.setBrush(incorrect_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPie(rect_int, correct_degrees, incorrect_degrees)
        
        painter.end()


class SessionOverviewWindow(QMainWindow):
    # Define signals for navigation
    back_button_clicked = pyqtSignal()
    home_button_clicked = pyqtSignal()
    test_button_clicked = pyqtSignal()
    exercises_button_clicked = pyqtSignal()
    model_button_clicked = pyqtSignal()
    profile_button_clicked = pyqtSignal()
    quit_button_clicked = pyqtSignal()
    lstm_clicked = pyqtSignal()
    blazepose_clicked = pyqtSignal()
    attention_mechanism_clicked = pyqtSignal()
    
    def __init__(self, session_manager=None, session_id=None):
        super().__init__()
        self.session_manager = session_manager
        self.session_id = session_id
        
        # Default session data (will be overridden by database data if available)
        self.session_data = {
            "exercise_name": "Unknown Exercise",
            "date": "Unknown Date",
            "total_repetitions": 0,
            "correct_repetitions": 0,
            "incorrect_repetitions": 0,
            "notes": ""
        }
        
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load session data from database if session_id is provided
        if session_id and session_manager:
            self.load_session_data()
            
        self.init_ui()
        
    def load_session_data(self):
        """Load session data from the database based on session_id"""
        if not self.session_id:
            return
            
        try:
            # Get session details
            query = QSqlQuery()
            sql_query = """
                SELECT s.session_date, s.notes, s.completed
                FROM Sessions s
                WHERE s.id = ?
            """
            if not query.prepare(sql_query):
                print(f"Error preparing session query: {query.lastError().text()}")
                return
                
            query.addBindValue(self.session_id)
            
            if query.exec() and query.next():
                session_date = query.value(0)
                notes = query.value(1) or ""
                completed = bool(query.value(2))
                
                # Format date nicely
                try:
                    date_obj = datetime.strptime(session_date, "%Y-%m-%d %H:%M:%S")
                    formatted_date = date_obj.strftime("%B %d, %Y")
                except:
                    formatted_date = session_date
                
                self.session_data["date"] = formatted_date
                self.session_data["notes"] = notes
                
                # Get exercise details for this session
                query = QSqlQuery()
                sql_query = """
                    SELECT e.name, se.total_reps, se.incorrect_reps, se.error_type
                    FROM SessionExercises se
                    JOIN exercises e ON se.exercise_id = e.id
                    WHERE se.session_id = ?
                """
                if not query.prepare(sql_query):
                    print(f"Error preparing exercise query: {query.lastError().text()}")
                    return
                    
                query.addBindValue(self.session_id)
                
                if query.exec() and query.next():
                    exercise_name = query.value(0)
                    total_reps = query.value(1)
                    incorrect_reps = query.value(2)
                    error_type = query.value(3) or ""
                    
                    self.session_data["exercise_name"] = exercise_name
                    self.session_data["total_repetitions"] = total_reps
                    self.session_data["correct_repetitions"] = total_reps - incorrect_reps
                    self.session_data["incorrect_repetitions"] = incorrect_reps
                    
                    if error_type and not self.session_data["notes"]:
                        self.session_data["notes"] = f"Error type: {error_type}"
        except Exception as e:
            print(f"Error loading session data: {e}")

    def init_ui(self):
        self.setWindowTitle("Session Overview")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setStyleSheet(
            f"background-color: #F0F8FF; color: {constants.PRIMARY_600};"
        )

        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(50, 50, 50, 50)
        content_layout.setSpacing(30)

        header_layout = QHBoxLayout()
        
        button_title_layout = QHBoxLayout()
        
        back_button = QPushButton("Back")
        back_button.setFont(font_utils.get_font(size=14))
        back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        back_button.setFixedSize(100, 40)
        back_button.clicked.connect(self.back_button_clicked.emit)
        back_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_800}; 
                color: {constants.WHITE};
                padding: 8px 16px;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {constants.PRIMARY_900};
            }}
            """
        )
        button_title_layout.addWidget(back_button)
        
        button_title_layout.addSpacing(15)
        
        # Overview
        title_label = QLabel("Overview")
        title_font = font_utils.get_font(size=32, weight=constants.WEIGHT_BOLD)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        button_title_layout.addWidget(title_label)
        
        header_layout.addLayout(button_title_layout)
        
        # RevAltalize
        logo_image = QLabel()
        if os.path.exists(constants.REVAITALIZE_LOGO_PATH):
            logo_image.setPixmap(QIcon(constants.REVAITALIZE_LOGO_PATH).pixmap(QSize(220, 50)))
        else:
            logo_image.setText("RevAItalize")
            logo_image.setFont(font_utils.get_font(size=32, weight=constants.WEIGHT_BOLD))
            logo_image.setStyleSheet(f"color: {constants.PRIMARY_800};")
        logo_image.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(logo_image)
        
        content_layout.addLayout(header_layout)
        
        content_layout.addSpacing(10)
        
        # Exercise details
        details_grid = QGridLayout()
        details_grid.setColumnStretch(2, 2)  # Label column
        details_grid.setColumnStretch(2, 2)  # Value column
        
        # Exercise name row
        exercise_name_label = QLabel("Exercise name")
        exercise_name_label.setStyleSheet("margin-left: 130px;")
        exercise_name_label.setFont(font_utils.get_font(size=18))
        details_grid.addWidget(exercise_name_label, 0, 0)
        
        self.exercise_name_value = QLabel(self.session_data["exercise_name"])
        self.exercise_name_value.setFont(font_utils.get_font(size=18, weight=constants.WEIGHT_BOLD))
        details_grid.addWidget(self.exercise_name_value, 0, 1)
        
        # Date row
        date_label = QLabel("Date")
        date_label.setStyleSheet("margin-left: 130px;")
        date_label.setFont(font_utils.get_font(size=18))
        details_grid.addWidget(date_label, 1, 0)
        
        self.date_value = QLabel(self.session_data["date"])
        self.date_value.setFont(font_utils.get_font(size=18, weight=constants.WEIGHT_BOLD))
        details_grid.addWidget(self.date_value, 1, 1)
        
        content_layout.addLayout(details_grid)
        
        # Main container
        main_frame = QFrame()
        main_frame.setFixedWidth(1000)  
        main_frame.setStyleSheet(
            f"""
            background-color: white;
            border-radius: 10px;
            border: 1px solid {constants.PRIMARY_300};
            """
        )
        main_frame_layout = QVBoxLayout(main_frame)
        main_frame_layout.setContentsMargins(20, 20, 20, 20)
        main_frame_layout.setSpacing(0)
        
        # Total repetition 
        total_rep_layout = QHBoxLayout()
        total_rep_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        total_rep_label = QLabel("Total Repetition  ")
        total_rep_label.setFont(font_utils.get_font(size=18))
        total_rep_label.setStyleSheet("border: none;")
        
        self.total_rep_value = QLabel(str(self.session_data["total_repetitions"]))
        self.total_rep_value.setFont(font_utils.get_font(size=18, weight=constants.WEIGHT_BOLD))
        self.total_rep_value.setStyleSheet(f"color: {constants.PRIMARY_400}; border: none;")
        
        total_rep_layout.addWidget(total_rep_label)
        total_rep_layout.addWidget(self.total_rep_value)
        
        main_frame_layout.addLayout(total_rep_layout)
        
        chart_legend_layout = QHBoxLayout()
        chart_legend_layout.setContentsMargins(0, 30, 0, 30)  
        chart_legend_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter) 
        
        pie_chart_container = QHBoxLayout()
        pie_chart_container.addSpacing(100)
        
        # Pie chart
        self.pie_chart = PieChartWidget(
            correct=self.session_data["correct_repetitions"],
            incorrect=self.session_data["incorrect_repetitions"]
        )
        pie_chart_container.addWidget(self.pie_chart)
        pie_chart_container.addStretch(1)
        
        chart_legend_layout.addLayout(pie_chart_container, 2) 
        
        legend_layout = QVBoxLayout()
        legend_layout.setContentsMargins(0, 0, 200, 0)  
        legend_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter) 
        
        # Correct 
        correct_legend_layout = QHBoxLayout()
        correct_color_box = QFrame()
        correct_color_box.setFixedSize(20, 20)
        correct_color_box.setStyleSheet(f"""
            background-color: {constants.PRIMARY_800};
            border: none;
        """)
        
        correct_label = QLabel("Correct")
        correct_label.setFont(font_utils.get_font(size=18))
        correct_label.setStyleSheet("border: none;")
        
        self.correct_value = QLabel(str(self.session_data["correct_repetitions"]))
        self.correct_value.setFont(font_utils.get_font(size=18, weight=constants.WEIGHT_BOLD))
        self.correct_value.setStyleSheet(f"color: {constants.PRIMARY_400}; border: none;")
        
        correct_legend_layout.addWidget(correct_color_box)
        correct_legend_layout.addSpacing(10)
        correct_legend_layout.addWidget(correct_label)
        correct_legend_layout.addSpacing(15)
        correct_legend_layout.addWidget(self.correct_value)
        
        # Incorrect legend
        incorrect_legend_layout = QHBoxLayout()
        incorrect_color_box = QFrame()
        incorrect_color_box.setFixedSize(20, 20)
        incorrect_color_box.setStyleSheet(f"""
            background-color: #A3E4FF;
            border: none;
        """)
        
        incorrect_label = QLabel("Incorrect")
        incorrect_label.setFont(font_utils.get_font(size=18))
        incorrect_label.setStyleSheet("border: none;")
        
        self.incorrect_value = QLabel(str(self.session_data["incorrect_repetitions"]))
        self.incorrect_value.setFont(font_utils.get_font(size=18, weight=constants.WEIGHT_BOLD))
        self.incorrect_value.setStyleSheet(f"color: {constants.PRIMARY_400}; border: none;")
        
        incorrect_legend_layout.addWidget(incorrect_color_box)
        incorrect_legend_layout.addSpacing(10)
        incorrect_legend_layout.addWidget(incorrect_label)
        incorrect_legend_layout.addSpacing(15)  # Reduced spacing
        incorrect_legend_layout.addWidget(self.incorrect_value)
        
        legend_layout.addLayout(correct_legend_layout)
        legend_layout.addSpacing(20)
        legend_layout.addLayout(incorrect_legend_layout)
        
        chart_legend_layout.addLayout(legend_layout)
        
        main_frame_layout.addLayout(chart_legend_layout)
        
        # Exercise notes 
        notes_frame = QFrame()
        notes_frame.setMinimumHeight(150) 
        notes_frame.setMinimumWidth(400)  
        notes_frame.setStyleSheet(
            f"""
            background-color: white;
            border: 1px solid {constants.PRIMARY_300};
            border-radius: 8px;
            """
        )
        
        notes_layout = QVBoxLayout(notes_frame)
        notes_layout.setContentsMargins(20, 20, 20, 20)
        notes_layout.setSpacing(15)
        
        notes_title = QLabel("Exercise notes:")
        notes_title.setFont(font_utils.get_font(size=16, weight=constants.WEIGHT_BOLD))
        notes_title.setStyleSheet("border: none; padding: 0;")
        notes_title.setAlignment(Qt.AlignmentFlag.AlignLeft) 
        notes_layout.addWidget(notes_title, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.notes_content = QLabel(self.session_data["notes"])
        self.notes_content.setFont(font_utils.get_font(size=14))
        self.notes_content.setWordWrap(True)
        self.notes_content.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        self.notes_content.setStyleSheet("border: none;")
        notes_layout.addWidget(self.notes_content, 1, Qt.AlignmentFlag.AlignCenter)
        
        notes_container = QHBoxLayout()
        notes_container.addStretch(1)
        notes_container.addWidget(notes_frame)
        
        main_frame_layout.addLayout(notes_container)
        
        content_layout.addWidget(main_frame, 0, Qt.AlignmentFlag.AlignHCenter)
        content_layout.addStretch(1)
        
        main_layout.addWidget(content_container, 1)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_sidebar(self):
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
        
        # Model button
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
        
        # Profile Dashboard button
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
        
    def set_session_data(self, session_data):
        """Update the UI with new session data"""
        self.session_data = session_data
        
        # Update basic info
        self.exercise_name_value.setText(session_data.get("exercise_name", "Unknown Exercise"))
        self.date_value.setText(session_data.get("date", "Unknown Date"))
        
        # Update repetition data
        total_reps = session_data.get("total_repetitions", 0)
        correct_reps = session_data.get("correct_repetitions", 0)
        incorrect_reps = session_data.get("incorrect_repetitions", 0)
        
        self.total_rep_value.setText(str(total_reps))
        self.correct_value.setText(str(correct_reps))
        self.incorrect_value.setText(str(incorrect_reps))
        
        # Update pie chart
        self.pie_chart.update_data(correct_reps, incorrect_reps)
        
        # Update notes
        self.notes_content.setText(session_data.get("notes", "No notes available"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Test data
    test_session_data = {
        "exercise_name": "Flank Stretch",
        "date": "December 20, 2024",
        "total_repetitions": 7,
        "correct_repetitions": 5,
        "incorrect_repetitions": 2,
        "notes": "Major errors in left elbow"
    }
    
    window = SessionOverviewWindow(session_data=test_session_data)
    window.show()
    sys.exit(app.exec())