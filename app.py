import sys
import os
from PyQt6.QtSql import QSqlQuery
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

# Set High DPI scaling environment variable *before* importing PyQt
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

# Import necessary classes
from login import LoginWindow
from sign_up import SignUpWindow
from landing_page import LandingWindow
from home import HomeWindow
from test_page import MainWindow as TestPageWindow
from exercise import ExercisesWindow
from model import ModelWindow
from onboarding_page import OnboardingWindow
from dashboard import DashboardWindow
from session_overview import SessionOverviewWindow
from db import open_connection
import font_utils


class SessionManager(QObject):
    """Centralized session management for tracking the currently logged in user"""
    session_updated = pyqtSignal(dict)  # Signal emitted when session data changes
    
    def __init__(self):
        super().__init__()
        self.current_user = None  # Will store user data dictionary
        self.current_session_id = None  # Will store active session ID if applicable
    
    def login_user(self, email, password):
        """Attempt to login a user and return success status"""
        query = QSqlQuery()
        sql_query = "SELECT user_id, first_name, last_name, email, contact_number, age, sex, address FROM Users WHERE email = ? AND password = ?"
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return False
            
        query.addBindValue(email)
        query.addBindValue(password)
        
        if query.exec() and query.next():
            # User authenticated, store their info
            user_id = query.value(0)
            self.current_user = {
                'user_id': user_id,
                'first_name': query.value(1),
                'last_name': query.value(2),
                'email': query.value(3),
                'contact_number': query.value(4),
                'age': query.value(5),
                'sex': query.value(6),
                'address': query.value(7)
            }
            
            # Load additional user preferences from UserOnboarding
            self._load_user_preferences(user_id)
            
            # Emit signal that session was updated
            self.session_updated.emit(self.current_user)
            return True
        return False
    
    def _load_user_preferences(self, user_id):
        """Load user preferences from the UserOnboarding table"""
        if not self.current_user:
            return
            
        query = QSqlQuery()
        sql_query = "SELECT needs_assistance, preferred_reps FROM UserOnboarding WHERE user_id = ?"
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return
            
        query.addBindValue(user_id)
        
        if query.exec() and query.next():
            self.current_user['needs_assistance'] = bool(query.value(0))
            self.current_user['preferred_reps'] = query.value(1)
        else:
            # Set defaults if not found
            self.current_user['needs_assistance'] = False
            self.current_user['preferred_reps'] = 5  # Default repetitions
    
    def logout_user(self):
        """Log out the current user"""
        self.current_user = None
        self.current_session_id = None
        self.session_updated.emit({})  # Empty dict indicates no active user
    
    def get_current_user(self):
        """Return the current user information"""
        return self.current_user
    
    def is_logged_in(self):
        """Check if a user is currently logged in"""
        return self.current_user is not None
    
    def get_user_name(self):
        """Get the full name of the current user"""
        if not self.current_user:
            return "Guest"
        return f"{self.current_user['first_name']} {self.current_user['last_name']}"
        
    def get_user_details(self):
        """Get detailed information about the current user"""
        if not self.current_user:
            return None
        return self.current_user
        
    def get_session_count(self):
        """Get the number of sessions for the current user today"""
        if not self.current_user:
            return 0
            
        query = QSqlQuery()
        sql_query = """
            SELECT COUNT(*) FROM Sessions 
            WHERE user_id = ? AND date(session_date) = date('now')
        """
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return 0
            
        query.addBindValue(self.current_user['user_id'])
        
        if query.exec() and query.next():
            return query.value(0)
        return 0
        
    def get_session_stats(self):
        """Get statistics about the user's sessions"""
        if not self.current_user:
            return {}
            
        stats = {}
        
        # Total completed sessions
        query = QSqlQuery()
        sql_query = """
            SELECT COUNT(*) FROM Sessions 
            WHERE user_id = ? AND completed = 1
        """
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return {}
            
        query.addBindValue(self.current_user['user_id'])
        
        if query.exec() and query.next():
            stats['total_completed_sessions'] = query.value(0)
        
        # Most recent session date
        query = QSqlQuery()
        sql_query = """
            SELECT session_date FROM Sessions 
            WHERE user_id = ? 
            ORDER BY session_date DESC LIMIT 1
        """
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return {}
            
        query.addBindValue(self.current_user['user_id'])
        
        if query.exec() and query.next():
            stats['last_session_date'] = query.value(0)
            
        # Total exercises performed
        query = QSqlQuery()
        sql_query = """
            SELECT COUNT(*) FROM SessionExercises se
            JOIN Sessions s ON se.session_id = s.id
            WHERE s.user_id = ?
        """
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return {}
            
        query.addBindValue(self.current_user['user_id'])
        
        if query.exec() and query.next():
            stats['total_exercises'] = query.value(0)
            
        return stats
    
    def get_preferred_reps(self):
        """Get the preferred number of repetitions for the current user"""
        if not self.current_user or 'preferred_reps' not in self.current_user:
            return 5  # Default value
        return self.current_user['preferred_reps']
    
    def create_session(self):
        """Create a new exercise session for the current user"""
        if not self.current_user:
            return None
            
        query = QSqlQuery()
        sql_query = """
            INSERT INTO Sessions (user_id, session_date, completed) 
            VALUES (?, CURRENT_TIMESTAMP, 0)
        """
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return None
            
        query.addBindValue(self.current_user['user_id'])
        
        if query.exec():
            # Get the ID of the newly created session
            query = QSqlQuery()
            sql_query = "SELECT last_insert_rowid()"
            if not query.prepare(sql_query):
                print(f"Error preparing query: {query.lastError().text()}")
                return None
                
            if query.exec() and query.next():
                self.current_session_id = query.value(0)
                return self.current_session_id
        return None
    
    def complete_session(self, notes=None):
        """Mark the current session as completed"""
        if not self.current_session_id:
            return False
            
        query = QSqlQuery()
        if notes:
            sql_query = "UPDATE Sessions SET completed = 1, notes = ? WHERE id = ?"
        else:
            sql_query = "UPDATE Sessions SET completed = 1 WHERE id = ?"
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return False
            
        if notes:
            query.addBindValue(notes)
        query.addBindValue(self.current_session_id)
        success = query.exec()
        
        if success:
            self.current_session_id = None  # Reset current session
        return success
    
    def record_exercise(self, exercise_id, total_reps, incorrect_reps=0, error_type=None):
        """Record an exercise performed in the current session"""
        if not self.current_session_id:
            return False
            
        query = QSqlQuery()
        sql_query = """
            INSERT INTO SessionExercises 
            (session_id, exercise_id, total_reps, incorrect_reps, error_type) 
            VALUES (?, ?, ?, ?, ?)
        """
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return False
            
        query.addBindValue(self.current_session_id)
        query.addBindValue(exercise_id)
        query.addBindValue(total_reps)
        query.addBindValue(incorrect_reps)
        query.addBindValue(error_type)
        
        return query.exec()
        
    def save_onboarding_preferences(self, user_id, needs_assistance, preferred_reps):
        """Save user onboarding preferences to the database"""
        if not user_id:
            return False
            
        # Check if user already has onboarding data
        query = QSqlQuery()
        sql_query = "SELECT id FROM UserOnboarding WHERE user_id = ?"
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return False
            
        query.addBindValue(user_id)
        
        if query.exec() and query.next():
            # Update existing record
            onboarding_id = query.value(0)
            sql_query = """
                UPDATE UserOnboarding 
                SET needs_assistance = ?, preferred_reps = ? 
                WHERE id = ?
            """
            if not query.prepare(sql_query):
                print(f"Error preparing query: {query.lastError().text()}")
                return False
                
            query.addBindValue(1 if needs_assistance else 0)  # Convert boolean to 0/1
            query.addBindValue(preferred_reps)
            query.addBindValue(onboarding_id)
        else:
            # Insert new record
            sql_query = """
                INSERT INTO UserOnboarding 
                (user_id, needs_assistance, preferred_reps) 
                VALUES (?, ?, ?)
            """
            if not query.prepare(sql_query):
                print(f"Error preparing query: {query.lastError().text()}")
                return False
                
            query.addBindValue(user_id)
            query.addBindValue(1 if needs_assistance else 0)  # Convert boolean to 0/1
            query.addBindValue(preferred_reps)
        
        success = query.exec()
        
        if success and self.current_user and int(self.current_user['user_id']) == int(user_id):
            # Update current user's preferences in memory
            self.current_user['needs_assistance'] = needs_assistance
            self.current_user['preferred_reps'] = preferred_reps
            self.session_updated.emit(self.current_user)
            
        return success
        
    def register_user(self, user_data):
        """Register a new user and return their user_id if successful"""
        # Extract user data
        first_name = user_data.get("First Name")
        last_name = user_data.get("Last Name")
        email = user_data.get("Email")
        contact = user_data.get("Contact")
        age = user_data.get("Age")
        sex = user_data.get("Sex")
        address = user_data.get("Address")
        password = user_data.get("Password")
        
        # Basic validation
        if not all([first_name, last_name, email, password]):
            return None
            
        # Check if email already exists
        query = QSqlQuery()
        sql_query = "SELECT COUNT(*) FROM Users WHERE email = ?"
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return None
            
        query.addBindValue(email)
        if query.exec() and query.next() and query.value(0) > 0:
            return None  # Email already exists
            
        # Insert new user
        sql_query = """
            INSERT INTO Users 
            (first_name, last_name, email, contact_number, age, sex, address, password) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return None
            
        query.addBindValue(first_name)
        query.addBindValue(last_name)
        query.addBindValue(email)
        query.addBindValue(contact)
        query.addBindValue(age)
        query.addBindValue(sex)
        query.addBindValue(address)
        query.addBindValue(password)
        
        if not query.exec():
            return None
            
        # Get the new user's ID
        query = QSqlQuery()
        sql_query = "SELECT last_insert_rowid()"
        if not query.prepare(sql_query):
            print(f"Error preparing query: {query.lastError().text()}")
            return None
            
        if query.exec() and query.next():
            user_id = query.value(0)
            
            # Store user data in session
            self.current_user = {
                'user_id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'contact_number': contact,
                'age': age,
                'sex': sex,
                'address': address
            }
            
            # Emit signal that session was updated
            self.session_updated.emit(self.current_user)
            
            return user_id
            
        return None

    def get_latest_sessions(self, limit=5):
        """Fetch the latest session records for the current user."""
        if not self.current_user:
            return []

        user_id = self.current_user['user_id']
        if not user_id:
            return []

        try:
            query = QSqlQuery()
            sql_query = """
                SELECT s.id, s.session_date, e.name
                FROM Sessions s
                JOIN SessionExercises se ON s.id = se.session_id
                JOIN exercises e ON se.exercise_id = e.id
                WHERE s.user_id = :user_id
                ORDER BY s.session_date DESC
                LIMIT :limit;
            """
            if not query.prepare(sql_query):
                print(f"Error preparing query: {query.lastError().text()}")
                return []
                
            query.bindValue(":user_id", user_id)
            query.bindValue(":limit", limit)
            
            if not query.exec():
                print(f"Error executing query: {query.lastError().text()}")
                return []

            # Correctly iterate through QSqlQuery results
            latest_sessions_data = []
            while query.next():
                session_id = query.value(0)
                session_date = query.value(1)
                exercise_name = query.value(2)
                latest_sessions_data.append({
                    "session_id": session_id,
                    "date": session_date,
                    "exercise": exercise_name
                })
                
            return latest_sessions_data
        except Exception as e:
            print(f"An error occurred fetching latest sessions: {e}")
            return []

    def get_onboarding_details(self):
        """Fetch onboarding details (needs_assistance, preferred_reps) for the current user."""
        if not self.current_user:
            return None

        user_id = self.current_user.get('user_id')
        if not user_id:
            return None

        try:
            query = QSqlQuery()
            sql_query = "SELECT needs_assistance, preferred_reps FROM UserOnboarding WHERE user_id = :user_id"
            if not query.prepare(sql_query):
                print(f"Error preparing onboarding details query: {query.lastError().text()}")
                return None
            
            query.bindValue(":user_id", user_id)

            if query.exec() and query.next():
                needs_assistance = bool(query.value(0)) # Convert DB value (0/1) to boolean
                preferred_reps = query.value(1)
                return {'needs_assistance': needs_assistance, 'preferred_reps': preferred_reps}
            else:
                 # Handle case where user might not have onboarding data yet
                 print(f"No onboarding data found for user {user_id}")
                 return None # Indicate no data found

        except Exception as e:
            print(f"An error occurred fetching onboarding details: {e}")
            return None

    def get_user_details(self):
        """Fetch detailed information for the current user."""
        if not self.current_user:
            return None
        return self.current_user


class ApplicationController(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
            
        # --- Initialize Session Manager ---
        self.session_manager = SessionManager()

        # --- Instantiate Windows ---
        self.login_window = LoginWindow()
        self.sign_up_window = SignUpWindow()
        self.landing_window = LandingWindow()
        self.home_window = HomeWindow()
        self.exercise_window = ExercisesWindow()
        self.model_window = ModelWindow()
        self.onboard_window = OnboardingWindow()
        # Pass session_manager to DashboardWindow
        self.dashboard_window = DashboardWindow(self.session_manager)
        # Initialize session overview window with session manager (session_id will be set later)
        self.session_overview_window = SessionOverviewWindow(session_manager=self.session_manager)
        self.test_page_window = TestPageWindow(
            model_path=os.path.join("models", "run_3.tflite"),
            session_manager=self.session_manager
        )  # Adjust path as needed

        font_utils.load_fonts()

        # --- Connect Signals ---
        # Login logic
        self.login_window.login_attempt.connect(self.handle_login_attempt)

        # Navigation signals
        self.login_window.create_account_requested.connect(self.show_sign_up_page)
        self.sign_up_window.back_to_login_requested.connect(self.show_login_page)

        # Sign up logic
        self.sign_up_window.sign_up_attempted.connect(self.handle_sign_up_logic)
        
        # Onboarding logic
        self.onboard_window.onboarding_completed.connect(self.handle_onboarding_completed)


        # Centralized navigation for test/home pages
        self.test_page_window.home_button_clicked.connect(self.show_home_page)
        self.test_page_window.exercise_button_clicked.connect(self.show_exercise_page)
        self.test_page_window.model_button_clicked.connect(self.show_model_page)
        self.test_page_window.profile_button_clicked.connect(self.show_dashboard_page)
        self.test_page_window.quit_button_clicked.connect(self.handle_close_app)
        
        # Connect model submenu signals
        self.test_page_window.lstm_clicked.connect(lambda: self.show_model_page('lstm'))
        self.test_page_window.blazepose_clicked.connect(lambda: self.show_model_page('blazepose'))
        self.test_page_window.attention_mechanism_clicked.connect(lambda: self.show_model_page('attention'))

        # Landing page navigation
        self.landing_window.login_button.clicked.connect(self.show_login_page)
        self.landing_window.sign_up_button.clicked.connect(self.show_sign_up_page)

        # Home page navigation - updated for new UI
        # Connect the model button menu items with specific model types
        self.home_window.test_button_clicked.connect(self.show_test_page)
        self.home_window.lstm_clicked.connect(lambda: self.show_model_page('lstm'))
        self.home_window.blazepose_clicked.connect(lambda: self.show_model_page('blazepose'))
        self.home_window.attention_mechanism_clicked.connect(lambda: self.show_model_page('attention'))
        
        # Connect the main exercises button
        self.home_window.exercise_button_clicked.connect(self.show_exercise_page)
        
        # Connect the exercises button (using the generic exercise button)
        # Note: specific exercise signals were removed as they don't exist in HomeWindow
        
        # Connect profile dashboard button
        self.home_window.profile_button_clicked.connect(self.show_dashboard_page)
        
        # Connect quit button
        self.home_window.quit_button_clicked.connect(self.handle_close_app)

        # Dashboard page navigation
        self.dashboard_window.model_button.clicked.connect(self.show_model_page)
        self.dashboard_window.exercises_button.clicked.connect(self.show_exercise_page)
        self.dashboard_window.test_button.clicked.connect(self.show_test_page)
        self.dashboard_window.home_button.clicked.connect(self.show_home_page)
        # Use quit_button instead of close_app_button
        # self.dashboard_window.quit_button.clicked.connect(self.handle_close_app)

        # Exercise page navigation - connect to signals
        self.exercise_window.home_button_clicked.connect(self.show_home_page)
        self.exercise_window.lstm_clicked.connect(lambda: self.show_model_page('lstm'))
        self.exercise_window.blazepose_clicked.connect(lambda: self.show_model_page('blazepose'))
        self.exercise_window.attention_mechanism_clicked.connect(lambda: self.show_model_page('attention'))
        self.exercise_window.test_button_clicked.connect(self.show_test_page)

        # Model window signals
        self.model_window.home_button_clicked.connect(self.show_home_page)
        self.model_window.test_button_clicked.connect(self.show_test_page)
        self.model_window.lstm_clicked.connect(lambda: self.show_model_page('lstm'))
        self.model_window.blazepose_clicked.connect(lambda: self.show_model_page('blazepose'))
        self.model_window.attention_mechanism_clicked.connect(lambda: self.show_model_page('attention'))
        self.model_window.exercise_button_clicked.connect(self.show_exercise_page)
        self.model_window.profile_button_clicked.connect(self.show_dashboard_page)
        self.model_window.quit_button_clicked.connect(self.handle_close_app)
        
        # Exercise window signals
        self.exercise_window.profile_button_clicked.connect(self.show_dashboard_page)
        self.exercise_window.quit_button_clicked.connect(self.handle_close_app)
        
        # Dashboard window signals
        self.dashboard_window.home_button_clicked.connect(self.show_home_page)
        self.dashboard_window.exercises_button_clicked.connect(self.show_exercise_page)
        self.dashboard_window.test_button_clicked.connect(self.show_test_page)
        self.dashboard_window.lstm_clicked.connect(lambda: self.show_model_page('lstm'))
        self.dashboard_window.blazepose_clicked.connect(lambda: self.show_model_page('blazepose'))
        self.dashboard_window.attention_mechanism_clicked.connect(lambda: self.show_model_page('attention'))
        self.dashboard_window.model_button_clicked.connect(lambda: self.show_model_page('lstm'))
        self.dashboard_window.quit_button_clicked.connect(self.handle_close_app)
        # Connect session selection to show session overview
        self.dashboard_window.session_selected.connect(self.show_session_overview)

        # --- Initial State ---
        self.sign_up_window.hide()
        self.home_window.hide()
        self.model_window.hide()
        self.exercise_window.hide()
        self.onboard_window.hide()
        self.login_window.hide()
        self.landing_window.showFullScreen()

    def handle_login_attempt(self, email, password):
        """Slot to handle login validation and switching."""
        
        if self.session_manager.login_user(email, password):
            print("Login successful, showing home page.")
            # Login successful, SessionManager emits session_updated
            # DashboardWindow connected to this signal will update automatically
            user_name = self.session_manager.get_user_name()
            # Remove direct dashboard updates, rely on signal
            # self.dashboard_window.update_user_info(user_name, self.session_manager.get_session_count())
            # user_details = self.session_manager.get_user_details()
            # session_stats = self.session_manager.get_session_stats()
            # self.dashboard_window.update_user_details(user_details, session_stats)

            # Update test page with user's preferred repetitions
            preferred_reps = self.session_manager.get_preferred_reps()
            self.test_page_window.set_total_reps(preferred_reps)
            
            # Show landing page
            self.login_window.hide()
            self.home_window.showFullScreen()
        else:
            print("Login Failed - Invalid Credentials!")
            QMessageBox.warning(
                self.login_window,
                "Login Failed",
                "Invalid email or password.",
            )

    # --- Navigation Slots ---
    def show_sign_up_page(self):
        """Hides login and shows sign up page."""
        print("MainApp: Switching Login -> Sign Up")
        self.landing_window.hide()
        self.login_window.hide()
        self.sign_up_window.showFullScreen()  # Or .show() if not full screen

    def show_login_page(self):
        """Hides sign up and shows login page."""
        print("MainApp: Switching Sign Up -> Login")
        self.landing_window.hide()
        self.sign_up_window.hide()
        self.login_window.showFullScreen()  # Or .show()

    def show_dashboard_page(self):
        """Hides all other windows and shows the dashboard page."""
        self.test_page_window.hide()
        self.login_window.hide()
        self.landing_window.hide()
        self.model_window.hide()
        self.exercise_window.hide()
        self.test_page_window.hide()
        self.home_window.hide()
        self.dashboard_window.update_dashboard_data()
        self.dashboard_window.showFullScreen()

    def show_home_page(self):
        """Hides all other windows and shows the home page."""
        print("MainApp: Switching to Home Page")
        self.test_page_window.hide()
        self.login_window.hide()
        self.landing_window.hide()
        self.model_window.hide()
        self.exercise_window.hide()
        self.test_page_window.hide()
        self.dashboard_window.hide()
        self.home_window.showFullScreen()

    def show_test_page(self):
        """Hides all other windows and shows the test page."""
        print("MainApp: Switching to Test Page")
        self.home_window.hide()
        self.landing_window.hide()
        self.model_window.hide()
        self.exercise_window.hide()
        self.dashboard_window.hide()
        self.test_page_window.showFullScreen()

    def show_model_page(self, model_type=None):
        """Hides all other windows and shows the model page."""
        print("MainApp: Switching to Model Page")
        self.home_window.hide()
        self.landing_window.hide()
        self.test_page_window.hide()
        self.exercise_window.hide()
        self.dashboard_window.hide()
        self.model_window.showFullScreen()
        
        # Set the specific model view if requested
        if model_type:
            if model_type == 'lstm':
                self.model_window.show_lstm_page()  # Use the proper method
            elif model_type == 'blazepose':
                self.model_window.show_blazepose_page()  # Use the proper method
            elif model_type == 'attention':
                self.model_window.show_attention_mechanism_page()  # Use the proper method

    def show_exercise_page(self):
        """Hides the current page and shows the exercise page."""
        print("MainApp: Switching to Exercise Page")
        self.home_window.hide()
        self.landing_window.hide()
        self.test_page_window.hide()
        self.model_window.hide()
        self.dashboard_window.hide()
        self.exercise_window.showFullScreen()

    # --- Logic Slot ---
    def handle_sign_up_logic(self, user_data):
        """Slot to handle the actual sign up process."""
        print("MainApp: Received sign up data:", user_data)
        
        # Register the user using the SessionManager
        user_id = self.session_manager.register_user(user_data)
        
        if user_id:
            print("Sign Up Successful!")
            
            # Configure onboarding window with the new user's ID
            self.onboard_window.user_id = user_id
            
            # Hide sign up window and show onboarding
            self.sign_up_window.hide()
            self.onboard_window.showFullScreen()
        else:
            print("Sign Up Failed!")
            QMessageBox.warning(
                self.sign_up_window,
                "Sign Up Failed",
                "Could not create account. Please check details and try again.",
            )

    def handle_onboarding_completed(self, needs_assistance, preferred_reps):
        """Handle the completion of the onboarding process"""
        print(f"Onboarding completed: needs_assistance={needs_assistance}, preferred_reps={preferred_reps}")
        
        # Save onboarding preferences to database
        user_id = self.onboard_window.user_id
        if user_id:
            success = self.session_manager.save_onboarding_preferences(
                user_id, needs_assistance, preferred_reps
            )
            
            if success:
                print("Onboarding preferences saved successfully")
                
                # Update test page with user's preferred repetitions
                self.test_page_window.set_total_reps(preferred_reps)
                
                # Update dashboard with user information
                self.dashboard_window.update_dashboard_data()
                
                # Show success message
                QMessageBox.information(
                    self.onboard_window,
                    "Setup Complete",
                    "Your account has been set up successfully!",
                )
                
                # Hide onboarding and show landing page
                self.onboard_window.hide()
                self.landing_window.showFullScreen()
            else:
                print("Failed to save onboarding preferences")
                QMessageBox.warning(
                    self.onboard_window,
                    "Setup Error",
                    "There was an error saving your preferences. Please try again.",
                )
        else:
            print("No user ID available for onboarding")
            QMessageBox.warning(
                self.onboard_window,
                "Setup Error",
                "User information is missing. Please try signing up again."
            )
            
            # Hide onboarding and show landing page
            self.onboard_window.hide()
            self.landing_window.showFullScreen()
            
    def show_session_overview(self, session_id):
        """Shows the session overview window for the specified session."""
        print(f"MainApp: Showing session overview for session {session_id}")
        
        # Hide all other windows
        self.home_window.hide()
        self.landing_window.hide()
        self.test_page_window.hide()
        self.model_window.hide()
        self.exercise_window.hide()
        self.dashboard_window.hide()
        
        # Create a new session overview window with the selected session ID
        # This ensures we always load fresh data
        self.session_overview_window = SessionOverviewWindow(
            session_manager=self.session_manager,
            session_id=session_id
        )
        
        # Connect navigation signals
        self.session_overview_window.back_button_clicked.connect(self.show_dashboard_page)
        self.session_overview_window.home_button_clicked.connect(self.show_home_page)
        self.session_overview_window.test_button_clicked.connect(self.show_test_page)
        self.session_overview_window.exercises_button_clicked.connect(self.show_exercise_page)
        self.session_overview_window.model_button_clicked.connect(self.show_model_page)
        self.session_overview_window.profile_button_clicked.connect(self.show_dashboard_page)
        self.session_overview_window.quit_button_clicked.connect(self.handle_close_app)
        self.session_overview_window.lstm_clicked.connect(lambda: self.show_model_page('lstm'))
        self.session_overview_window.blazepose_clicked.connect(lambda: self.show_model_page('blazepose'))
        self.session_overview_window.attention_mechanism_clicked.connect(lambda: self.show_model_page('attention'))
        
        # Show the session overview window
        self.session_overview_window.showFullScreen()
        
    def handle_close_app(self):
        print("MainApp: Closing application")
        self.app.quit()
        
    def run(self):
        """Starts the application event loop."""
        # Open database connection
        if not open_connection():
            QMessageBox.critical(
                None, "Database Error", "Could not connect to the database."
            )
            return
            
        # Show the initial window
        self.landing_window.showFullScreen()
        sys.exit(self.app.exec())


# Main execution block
if __name__ == "__main__":
    try:
        controller = ApplicationController()
        exit_code = controller.run()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
