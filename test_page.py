import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from numba import jit
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QComboBox,
    QSizePolicy,
    QToolButton,
    QMenu,
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon, QImage, QPixmap, QAction
from PyQt6.QtCore import QSize, Qt, QThread, QMutex, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
import sys
import signal
import time
from collections import deque
import constants
import font_utils
import os

# Numba-optimized functions
@jit(nopython=True, parallel=True, fastmath=True)
def process_keypoints(keypoints_array, thresholds):
    """Optimized function to process keypoints and make predictions"""
    # This is a placeholder for your actual model inference
    # In a real implementation, you'd integrate with TensorFlow differently
    # since Numba doesn't directly work with TensorFlow operations
    return np.any(keypoints_array > thresholds), np.max(keypoints_array)


@jit(nopython=True)
def extract_keypoints_numba(landmarks_x, landmarks_y, landmarks_z, keypoints_indices):
    """Extract keypoints using Numba for performance"""
    kp_np = np.zeros(18)
    for i, kp_idx in enumerate(keypoints_indices):
        kp_np[3 * i] = landmarks_x[kp_idx]
        kp_np[3 * i + 1] = landmarks_y[kp_idx]
        kp_np[3 * i + 2] = landmarks_z[kp_idx]
    return kp_np


def get_evaluation_from_binary(binary_array, return_error_indices=False):
    """
    Returns a concise, grouped human-readable string for the flagged joints.
    If return_error_indices=True, also returns a list of pose indices (11-16) that are erroneous.
    """
    joint_names = [
        "Left Shoulder", "Right Shoulder", "Left Elbow", "Right Elbow", "Left Wrist", "Right Wrist"
    ]
    pose_indices = [11, 12, 13, 14, 15, 16]
    arr = binary_array[0] if hasattr(binary_array, '__len__') and hasattr(binary_array[0], '__len__') else binary_array
    if len(arr) != 6:
        return ("Unknown error", []) if return_error_indices else "Unknown error"
    # Indices for easier reference
    ls, rs, le, re, lw, rw = arr
    # All joints
    if all(arr):
        label = "Upper Extremity"
    elif ls and rs and not (le or re or lw or rw):
        label = "Spine"
    elif le and re and not (ls or rs or lw or rw):
        label = "Both Elbows"
    elif lw and rw and not (ls or rs or le or re):
        label = "Both Wrists"
    elif le and lw and not (ls or rs or re or rw):
        label = "Left Forearm"
    elif re and rw and not (ls or rs or le or lw):
        label = "Right Forearm"
    elif ls and le and lw and not (rs or re or rw):
        label = "Left Arm"
    elif rs and re and rw and not (ls or le or lw):
        label = "Right Arm"
    elif ls and rs and (le or re or lw or rw) and not (not le and not re and not lw and not rw):
        if le and re and lw and rw:
            label = "Upper Extremity"
        else:
            label = "Spine"
    else:
        error_labels = [name for bit, name in zip(arr, joint_names) if bit]
        if not error_labels:
            label = "Correct"
        else:
            label = ", ".join(error_labels)
    error_indices = [pose_indices[i] for i, bit in enumerate(arr) if bit]
    if return_error_indices:
        return label, error_indices
    return label


def draw_custom_landmarks(image, landmarks, error_indices=None):
    """
    Draw only landmarks from 11-24 with color coding:
    - Red for connections/keypoints in error_indices
    - Green otherwise
    error_indices: list of pose indices (e.g., [11, 13, 15])
    
    landmarks: Can be either MediaPipe Pose Solution landmarks (has .landmark attribute) 
              or MediaPipe Tasks landmarks (direct list of landmarks)
    
    Note: Image should already be flipped for correct display
    """
    if not isinstance(error_indices, (list, tuple, set)):
        error_indices = []
    # Define keypoint indices for upper body (11-24)
    upper_body_indices = list(range(11, 25))
    # BGR format colors for OpenCV
    RED = (182, 0, 18)
    GREEN = (101, 184, 101)
    height, width, _ = image.shape
    
    # Make a copy of the image to draw on
    output_image = image.copy()
    
    # Check if landmarks is from old API (has .landmark attribute) or new Tasks API (direct list)
    if hasattr(landmarks, 'landmark'):
        landmark_list = landmarks.landmark
    else:
        landmark_list = landmarks  # It's already a list in the Tasks API

    # Draw keypoints
    for idx in upper_body_indices:
        if idx < len(landmark_list):
            landmark = landmark_list[idx]
            # Convert normalized coordinates to pixel values
            # Flip X coordinate since the image is already flipped
            landmark_px = (int((1-landmark.x) * width), int(landmark.y * height))
            # Use BGR color format (OpenCV default)
            color = RED if idx in error_indices else GREEN
            cv2.circle(output_image, landmark_px, 7, color, -1)  # Make points slightly bigger

    # Define connections for upper body
    upper_body_connections = [
        (11, 12),  # Shoulders
        (11, 13),
        (13, 15),  # Left arm
        (12, 14),
        (14, 16),  # Right arm
        (11, 23),
        (12, 24),  # Hip connections
        (23, 24),  # Hip line
    ]

    # Draw connections
    for connection in upper_body_connections:
        start_idx, end_idx = connection
        if start_idx < len(landmark_list) and end_idx < len(landmark_list):
            start = landmark_list[start_idx]
            end = landmark_list[end_idx]
            # Flip X coordinates since the image is already flipped
            start_point = (int((1-start.x) * width), int(start.y * height))
            end_point = (int((1-end.x) * width), int(end.y * height))
            color = RED if (start_idx in error_indices or end_idx in error_indices) else GREEN
            cv2.line(output_image, start_point, end_point, color, 4)

    return output_image  # No need to flip again, already flipped



class VideoThread(QThread):
    frame_update = pyqtSignal(np.ndarray, str)
    fps_update = pyqtSignal(float)
    prediction_signal = pyqtSignal(str)
    enough_frames_signal = pyqtSignal()

    def __init__(self, model_path):
        super().__init__()
        # Load TensorFlow Lite model
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # MediaPipe Tasks setup for BlazePose
        self.blazepose_model_path = "./models/pose_landmarker_full.task"
        self.camera_index = 0
        self.latest_pose_result = None
        
        # Initialize MediaPipe Tasks API
        self.BaseOptions = mp.tasks.BaseOptions
        self.PoseLandmarker = mp.tasks.vision.PoseLandmarker
        self.PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        self.VisionRunningMode = mp.tasks.vision.RunningMode
        
        # Skip the streaming mode and use the image mode instead to avoid async issues
        self.pose_landmarker = self.PoseLandmarker.create_from_options(
            self.PoseLandmarkerOptions(
                base_options=self.BaseOptions(model_asset_path=self.blazepose_model_path),
                running_mode=self.VisionRunningMode.IMAGE,  # Use IMAGE mode instead of LIVE_STREAM
                min_pose_detection_confidence=0.90,
                min_pose_presence_confidence=0.75,
                min_tracking_confidence=0.90,
                output_segmentation_masks=False,
                num_poses=1  # We only need one pose for our application
            )
        )

        self.SLIDING_AMOUNT = 10
        self.WINDOW_FRAME_AMOUNT = 10
        self.exercise_thresholds = {
            "Hiding Face": np.array([0.4, 0.45, 0.6, 0.6, 0.65, 0.55]),
            "Torso Rotation": np.array([0.75, 0.65, 0.75, 0.7, 0.75, 0.7]),
            "Flank Stretch": np.array([0.75, 0.7, 0.7, 0.8, 0.7, 0.8]),
        }
        self.current_exercise = "Hiding Face"  # Set default here
        # Add one-hot encoding mapping for exercises
        self.exercise_encoding = {
            "Flank Stretch": np.array([1.0, 0.0, 0.0], dtype=np.float32),
            "Hiding Face": np.array([0.0, 1.0, 0.0], dtype=np.float32),
            "Torso Rotation": np.array([0.0, 0.0, 1.0], dtype=np.float32),
        }
        self.exercise_encoding_data = self.exercise_encoding[self.current_exercise]
        self.BEST_THRESHOLDS = self.exercise_thresholds[self.current_exercise]
        self.running = False
        self.keypoint_data = []
        self.predicted_class = "Waiting"
        self.keypoints_of_interest = np.array([11, 12, 13, 14, 15, 16])
        self.target_fps = 15  # Target frames per second
        self.min_frame_time = 1.0 / self.target_fps  # Minimum time between frames
        self.last_frame_timestamp = 0

        # Use deque for efficient sliding window implementation
        self.keypoint_deque = deque(
            maxlen=self.WINDOW_FRAME_AMOUNT
        )  # additional 3 data points for encoded exercise information

        # Performance monitoring
        self.frame_times = deque(maxlen=30)  # Use deque with fixed size
        self.last_frame_time = 0
        self.current_fps = 0

        # Threading protection
        self.mutex = QMutex()

        self.current_frame_count = 0

        # Inference control
        self.frames_since_inference = 0
        self._enough_frames_emitted = False

        # Pre-allocate memory for inference
        # Update shape to accommodate exercise encoding (3) + keypoints (18) = 21
        self.model_input = np.zeros(
            (1, self.WINDOW_FRAME_AMOUNT, 21),
            dtype=np.float32,
        )

    # Set the current exercise and update relevant settings
    def set_current_exercise(self, exercise_name):
        # Acquire the mutex lock for thread safety
        self.mutex.lock()
        try:
            # Check if we're in the middle of a repetition
            if hasattr(self, 'parent') and self.parent and hasattr(self.parent, 'current_rep'):
                if self.parent.current_rep > 0 and self.parent.current_rep < self.parent.total_reps:
                    print("Cannot change exercise in the middle of a repetition")
                    self.mutex.unlock()
                    return False
            
            # Safe to change exercise
            if exercise_name in self.exercise_encoding and exercise_name in self.exercise_thresholds:
                self.current_exercise = exercise_name
                self.exercise_encoding_data = self.exercise_encoding[exercise_name]
                self.BEST_THRESHOLDS = self.exercise_thresholds[exercise_name]
                print(f"Exercise changed to: {exercise_name}")
                
                # Clear the keypoint deque to start fresh with the new exercise
                self.keypoint_deque.clear()
                self.frames_since_inference = 0
                self.predicted_class = "Waiting"
                self.mutex.unlock()
                return True
            else:
                print(f"Warning: Unknown exercise '{exercise_name}'")
                self.mutex.unlock()
                return False
        except Exception as e:
            print(f"Error changing exercise: {e}")
            # Make sure to unlock the mutex even if an exception occurs
            self.mutex.unlock()
            return False

    # Set how many frames to discard/add when sliding the window
    def set_sliding_amount(self, amount):
        """Set how many frames to discard/add when sliding the window"""
        if 0 < amount < self.WINDOW_FRAME_AMOUNT:
            self.SLIDING_AMOUNT = amount
        else:
            print(
                f"Invalid sliding amount. Must be between 1 and {self.WINDOW_FRAME_AMOUNT-1}"
            )

    # Set the target FPS cap
    def set_target_fps(self, fps):
        """Set the target FPS cap"""
        if fps > 0:
            self.target_fps = fps
            self.min_frame_time = 1.0 / fps
        else:
            print("Invalid FPS value. Must be greater than 0.")

    # We're not using the callback approach anymore since we're using IMAGE mode

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open camera")
            self.running = False
            # Emit a blank frame or error message if needed
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                error_frame,
                "Camera 0 Failed",
                (50, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
            self.frame_update.emit(error_frame, "Error")
            return
        
        self.last_frame_timestamp = time.time()
        self.last_frame_time = time.time()
        self.frames_since_inference = 0

        while self.running:
            if not self._enough_frames_emitted and self.frames_since_inference >= 10:
                self._enough_frames_emitted = True
                self.enough_frames_signal.emit()
                
            current_time = time.time()
            elapsed = current_time - self.last_frame_timestamp

            # FPS limiting
            if elapsed < self.min_frame_time:
                sleep_time = self.min_frame_time - elapsed
                time.sleep(max(0, sleep_time - 0.001))  # Adjust for sleep inaccuracy
                current_time = time.time()
                elapsed = current_time - self.last_frame_timestamp

            self.last_frame_timestamp = current_time

            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                # Optionally attempt to reopen the camera or break
                time.sleep(0.5)
                # Try reopening
                cap.release()
                cap = cv2.VideoCapture(self.camera_index)
                if not cap.isOpened():
                    print(f"Error: Could not reopen camera {self.camera_index}.")
                    break  # Exit loop if reopen fails
                continue  # Skip the rest of the loop iteration

            self.current_frame_count += 1

            # Process frame - keep original BGR frame for drawing
            # MediaPipe expects RGB input
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Use MediaPipe Tasks API for pose detection
            frame_timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
            # Create MediaPipe Image from RGB frame
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            
            # Use synchronous detection instead of async with proper error handling
            try:
                result = self.pose_landmarker.detect(mp_image)
            except ValueError as e:
                # Handle "Task runner is currently not running" error
                print(f"Pose detection error: {e}")
                if "Task runner is currently not running" in str(e):
                    # The thread is likely being stopped, so exit gracefully
                    break
                # For other errors, set result to None and continue
                result = None
            
            # Prepare data for display and potential inference
            self.mutex.lock()
            current_pred = self.predicted_class
            current_exercise = self.current_exercise
            self.mutex.unlock()

            # Compute error_indices for coloring
            error_indices = []
            if 'yhat_binary' in locals():
                _, error_indices = get_evaluation_from_binary(yhat_binary, return_error_indices=True)

            # Always flip the frame for consistent display
            frame = cv2.flip(frame_rgb, 1)  # Mirror horizontally for natural viewing
            
            if result and result.pose_landmarks and len(result.pose_landmarks) > 0:
                # Draw landmarks on the flipped RGB frame
                frame = draw_custom_landmarks(
                    frame, result.pose_landmarks[0], error_indices=error_indices
                )

                # Extract landmarks from the first detected pose
                landmarks = result.pose_landmarks[0]
                # Extract keypoints using the modified extract_keypoints_numba function
                kp_np = extract_keypoints_numba(
                    np.array([landmark.x for landmark in landmarks], dtype=np.float32),
                    np.array([landmark.y for landmark in landmarks], dtype=np.float32),
                    np.array([landmark.z for landmark in landmarks], dtype=np.float32),
                    self.keypoints_of_interest,
                )
                
                # Get the one-hot encoding for the current exercise
                exercise_vec = self.exercise_encoding[current_exercise]

                # Concatenate exercise encoding and keypoints
                frame_features = np.concatenate((exercise_vec, kp_np))

                # Append the combined features to the deque
                self.keypoint_deque.append(frame_features)

                # Only run inference if deque is full
                if (
                    len(self.keypoint_deque) == self.WINDOW_FRAME_AMOUNT
                    and self.frames_since_inference == 10
                ):
                    self.frames_since_inference = 0
                    self.model_input[0] = np.array(self.keypoint_deque)

                    # Perform inference
                    input_data = self.model_input.astype(self.input_details[0]['dtype'])
                    self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
                    self.interpreter.invoke()
                    yhat_prob = self.interpreter.get_tensor(self.output_details[0]['index'])
                    yhat_binary = (yhat_prob > self.BEST_THRESHOLDS).astype(int)
                    new_pred = get_evaluation_from_binary(yhat_binary)

                    # Update shared state safely
                    self.mutex.lock()
                    self.predicted_class = new_pred
                    self.mutex.unlock()
                else:
                    self.frames_since_inference += 1

            else:
                # Handle case with no landmarks detected
                self.mutex.lock()
                self.predicted_class = "No Person"
                self.mutex.unlock()

            # Update FPS
            frame_time = current_time - self.last_frame_time
            self.frame_times.append(frame_time)
            self.last_frame_time = current_time
            if len(self.frame_times) > 1:
                self.current_fps = len(self.frame_times) / sum(self.frame_times)
                self.fps_update.emit(self.current_fps)

            # Emit updated frame and latest prediction
            self.mutex.lock()
            class_to_emit = self.predicted_class
            self.mutex.unlock()
            self.frame_update.emit(frame, class_to_emit)

        # Release camera resources
        if cap.isOpened():
            cap.release()
            
        # Clean up pose landmarker resources
        if self.pose_landmarker:
            try:
                self.pose_landmarker.close()
            except ValueError:
                # Safely ignore "Task runner is currently not running" error
                pass
            except Exception as e:
                print(f"Error closing pose landmarker in run method: {e}")
                
        print("Video thread stopped.")

    # Change the camera source
    def set_camera(self, camera_index):
        """Change the camera source"""
        if self.running:
            self.stop()
            self.camera_index = camera_index
            self.start()
        else:
            self.camera_index = camera_index

    # Set how many frames to skip for performance
    def set_frame_skip(self, skip_value):
        """Set how many frames to skip for performance"""
        self.frame_skip = skip_value

    # Safely stop the thread
    def stop(self):
        """Safely stop the thread"""
        # Set running flag to false first to signal the thread to stop
        self.running = False
        
        # Wait a short time to allow the thread to exit any processing loops
        time.sleep(0.1)
        
        # Close the pose landmarker to release resources
        if hasattr(self, 'pose_landmarker') and self.pose_landmarker:
            try:
                self.pose_landmarker.close()
            except ValueError:
                # Safely ignore "Task runner is currently not running" error
                pass
            except Exception as e:
                print(f"Error closing pose landmarker: {e}")
                
        # Wait for the thread to finish
        self.wait()
        
        # Release camera resources if they exist
        if hasattr(self, "capture") and self.capture.isOpened():
            self.capture.release()



class MainWindow(QMainWindow):
    home_button_clicked = pyqtSignal()
    session_completed = pyqtSignal(str, int, int)  # Exercise name, total reps, incorrect reps
    exercise_button_clicked = pyqtSignal()
    model_button_clicked = pyqtSignal()
    profile_button_clicked = pyqtSignal()
    quit_button_clicked = pyqtSignal()
    lstm_clicked = pyqtSignal()
    blazepose_clicked = pyqtSignal()
    attention_mechanism_clicked = pyqtSignal()
    
    def __init__(self, model_path, session_manager=None):
        super().__init__()
        self.model_path = model_path
        self.session_manager = session_manager
        self.thread = None
        self.exercise_selector = QComboBox()
        self.exercise_selector.addItems(
            ["Hiding Face", "Torso Rotation", "Flank Stretch"]
        )
        self.exercise_selector.currentTextChanged.connect(self.change_exercise)
        self.guide_video_path = os.path.join("videos", "hiding_face.mp4")
       
        # Repetition tracking
        if self.session_manager and self.session_manager.is_logged_in():
            self.total_reps = self.session_manager.get_preferred_reps()
        else:
            self.total_reps = 5  # Default when no user is logged in
            
        self.current_rep = 0  # 0 means not started, 1-based indexing for actual reps
        self.rep_buttons = []  # Will store the repetition buttons
        self.current_prediction = ""  # Store current prediction separately from label
        
        # Exercise tracking
        self.current_exercise = "Hiding Face"  # Default exercise
        self.incorrect_reps = 0  # Track incorrect repetitions
        self.error_types = {}  # Track error types and their frequencies
        self.current_rep_has_error = False  # Flag to track if current rep has an error
        self.rep_errors = []  # List to track which reps had errors
        self.current_session_id = None  # Will store the active session ID
        
        # Flag to control prediction label updates
        self.showing_rep_message = False  # True when showing a repetition message
        
        self.init_ui()

    def change_exercise(self, selected):
        if not selected:
            return
        
        # Update the thread's exercise - only proceed if successful
        if self.thread:
            # Pass a reference to self (parent) to the thread for checking rep status
            if not hasattr(self.thread, 'parent'):
                self.thread.parent = self
                
            # Try to change the exercise
            if not self.thread.set_current_exercise(selected):
                print("Could not change exercise at this time")
                # Revert the combo box selection to the current exercise
                self.exercise_selector.blockSignals(True)
                self.exercise_selector.setCurrentText(self.current_exercise)
                self.exercise_selector.blockSignals(False)
                return
        
        # Update the guide video path based on the selected exercise
        exercise_video_map = {
            "Hiding Face": "hiding_face.mp4",
            "Torso Rotation": "torso_rotation.mp4",
            "Flank Stretch": "flank_stretch.mp4",
        }
        
        if selected in exercise_video_map:
            self.guide_video_path = os.path.join("videos", exercise_video_map[selected])
            print(f"Guide video updated to: {self.guide_video_path}")
            
            # If we have a video player, update its source
            if hasattr(self, "media_player") and self.media_player:
                self.media_player.setSource(QUrl.fromLocalFile(self.guide_video_path))
                
            # Reset repetition tracking
            self.current_rep = 0
            self.incorrect_reps = 0
            self.error_types = {}  # Reset error types tracking
            self.current_rep_has_error = False  # Reset error flag
            self.rep_errors = []  # Reset list of reps with errors
            self.showing_rep_message = False  # Reset message flag
            
            # Reset buttons to their default state
            if hasattr(self, 'rep_buttons') and self.rep_buttons:
                for i, button in enumerate(self.rep_buttons, 1):
                    button.setText(str(i))  # Set text to button number (1-based)
                    button.setFixedSize(40, 40)
                    button.setStyleSheet(
                        f"""
                        QPushButton {{
                            background-color: transparent;
                            color: {constants.PRIMARY_800};
                            border: 2px solid {constants.PRIMARY_800};
                            border-radius: 20px;
                        }}
                        """
                    )
            
            # Update buttons to reflect current state
            self.update_rep_buttons()
            
            # Reset prediction label
            self.reset_prediction_label()
            
            # Update the current exercise
            self.current_exercise = selected
        
        # No need for additional reset code - already handled above

    def _create_sidebar(self):
        # Create sidebar widget
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet(f"background-color: {constants.PRIMARY_400};")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Add logo
        logo_icon_path = os.path.join("imgs", "exercise.png")
        logo_icon = QIcon(logo_icon_path)
        icon_size = QSize(50, 50)
        logo_button = QPushButton()
        logo_button.setIcon(logo_icon)
        logo_button.setIconSize(icon_size)
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
        top_padding.setStyleSheet("background-color: transparent;")
        sidebar_layout.addWidget(top_padding)
        
        # Home button
        home_button = QPushButton("  Home")
        home_button.setFont(self.menu_button_font)
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
        self.exercises_button = QPushButton("  Exercises")
        self.exercises_button.setFont(self.menu_button_font)
        self.exercises_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if os.path.exists(constants.EXERCISES_ICON_PATH):
            self.exercises_button.setIcon(QIcon(constants.EXERCISES_ICON_PATH))
            self.exercises_button.setIconSize(QSize(18, 18))
        self.exercises_button.clicked.connect(self.exercise_button_clicked.emit)
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
        self.model_button.setFont(self.menu_button_font)
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
        
        # Create dropdown menu for model button
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
        
        # Profile button
        self.profile_button = QPushButton("  Profile Dashboard")
        self.profile_button.setFont(self.menu_button_font)
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
        self.quit_button = QPushButton("  Quit")
        self.quit_button.setFont(self.menu_button_font)
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
    
    def _toggle_sidebar(self):
        # Toggle sidebar visibility
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.menu_button.setText("☰")
        else:
            self.sidebar.show()
            self.menu_button.setText("X")
    
    def init_ui(self):
        self.prediction_font = font_utils.get_font(size=20, weight=constants.WEIGHT_BOLD)
        self.progress_font = font_utils.get_font(size=16, weight=constants.WEIGHT_SEMIBOLD)
        self.button_font = font_utils.get_font(size=12, weight=constants.WEIGHT_SEMIBOLD)
        self.menu_button_font = font_utils.get_font(size=10)

        self.setWindowTitle("Real-Time Pose Classification")
        self.setStyleSheet(f"background-color: {constants.WHITE};")
        
        # Create sidebar
        self.sidebar = self._create_sidebar()
        # Initially hide the sidebar
        self.sidebar.hide()
        
        # Create overall layout
        overall_layout = QHBoxLayout()
        overall_layout.setContentsMargins(0, 0, 0, 0)
        overall_layout.setSpacing(0)
        
        # Add sidebar to overall layout
        overall_layout.addWidget(self.sidebar)
        
        # Create content widget
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {constants.WHITE};")
        content_layout = QVBoxLayout(content_widget)
        
        # Create hamburger menu button
        self.menu_button = QPushButton("☰")
        self.menu_button.setFont(self.menu_button_font)
        self.menu_button.clicked.connect(self._toggle_sidebar)
        self.menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.PRIMARY_800};
                color: {constants.WHITE};
                padding: 5px 10px;
                border-radius: 8px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {constants.PRIMARY_600};
                color: {constants.WHITE};
            }}
            """
        )
        
        # Add menu button and logo to top of content layout
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.menu_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Add prediction label in the center
        self.prediction_label = QLabel("Waiting for prediction")
        self.prediction_label.setFont(self.prediction_font)
        self.prediction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prediction_label.setStyleSheet(f"color: {constants.PRIMARY_800};")
        top_bar.addWidget(self.prediction_label, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add RevAItalize logo on the right
        logo_image = QLabel()
        if os.path.exists(constants.REVAITALIZE_LOGO_PATH):
            logo_image.setPixmap(QIcon(constants.REVAITALIZE_LOGO_PATH).pixmap(QSize(180, 40)))
        else:
            logo_image.setText("RevAItalize")
            logo_image.setFont(self.prediction_font)
            logo_image.setStyleSheet(f"color: {constants.PRIMARY_800};")
        logo_image.setAlignment(Qt.AlignmentFlag.AlignRight)
        top_bar.addWidget(logo_image, alignment=Qt.AlignmentFlag.AlignRight)
        
        content_layout.addLayout(top_bar)

        # Video display
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet(
            "background-color: black;"
        )
        self.video_label.setScaledContents(True)
        self.video_label.setMaximumSize(960, 810)

        # Video Guide display using QVideoWidget
        self.video_guide_widget = QVideoWidget()
        # Set aspect ratio mode to maintain aspect ratio while filling the frame (crops overflow)
        self.video_guide_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatioByExpanding)

        # PyQt Multimedia Player for guide video
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_guide_widget)

        # Connect media status changes to handle end of video
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)

        # Exercise Selector with improved styling
        self.exercise_selector = QComboBox()
        self.exercise_selector.addItems(
            ["Hiding Face", "Torso Rotation", "Flank Stretch"]
        )
        self.exercise_selector.currentTextChanged.connect(self.change_exercise)
        self.exercise_selector.setFont(self.button_font)
        self.exercise_selector.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {constants.PRIMARY_800};
                color: {constants.WHITE};
                padding: 10px 20px;
                border-radius: 8px;
            }}
            QComboBox:hover {{
                background-color: {constants.PRIMARY_600};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 25px;
                border-left: 1px solid {constants.WHITE};
            }}
            QComboBox QAbstractItemView {{
                background-color: {constants.PRIMARY_400};
                color: {constants.WHITE};
                selection-background-color: {constants.PRIMARY_800};
                selection-color: {constants.WHITE};
                border: none;
                padding: 5px;
            }}
            """
        )

        # Selected Exercise Label
        self.current_exercise_label = QLabel("Hiding Face")

        # Buttons
        self.start_button = QPushButton("Start")
        self.start_button.setFont(self.button_font)
        self.start_button.clicked.connect(self.start_exercise)
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {constants.SUCCESS};
                color: {constants.WHITE};
                padding: 10px 40px 10px 40px; 
                border: 2px solid {constants.SUCCESS};
                border-radius: 12px; 
                text-align: left; 
            }}

            QPushButton:hover {{
                background-color: {constants.MINT};
                border: 2px solid {constants.MINT};
                color: {constants.WHITE};
            }}

        """)

        # Performance controls - center the start button with exercise selector
        bottom_button_group = QHBoxLayout()
        bottom_button_group.addStretch(1)
        bottom_button_group.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        bottom_button_group.addSpacing(20)  # Add some spacing between the buttons
        bottom_button_group.addWidget(self.exercise_selector, alignment=Qt.AlignmentFlag.AlignCenter)
        bottom_button_group.addStretch(1)


        # Sidebar progress content - Repetition tracking
        bottom_progress_layout = QHBoxLayout()
        bottom_progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add logo button instead of text label
        logo_icon_path = os.path.join("imgs", "exercise.png")
        logo_icon = QIcon(logo_icon_path)
        icon_size = QSize(48, 48)
        self.logo_button = QPushButton()
        self.logo_button.setIcon(logo_icon)
        self.logo_button.setIconSize(icon_size)
        self.logo_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logo_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0px;
            }
        """
        )
        self.logo_button.setFlat(True)

        progress_label = QLabel("Progress:")
        progress_label.setFont(self.progress_font)
        progress_label.setStyleSheet(f"color: {constants.PRIMARY_800};")
        bottom_progress_layout.addWidget(progress_label)
        bottom_progress_layout.setContentsMargins(60, 0, 60, 0)
        
        # Clear previous buttons if any
        self.rep_buttons = []
        
        # Create a widget to hold buttons with even vertical distribution
        buttons_container = QWidget()
        buttons_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        buttons_grid = QHBoxLayout(buttons_container)
        buttons_grid.setSpacing(0)  # We'll control spacing with stretch factors
        buttons_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center alignment
        buttons_grid.setContentsMargins(10, 0, 10, 0)  # Add some horizontal padding
        
        # Create circular buttons for repetitions
        for i in range(1, self.total_reps + 1):
            button = QPushButton(f"{i}")
            # Make buttons perfectly circular
            button.setFixedSize(40, 40)  # Fixed size for circle
            button.setFont(self.button_font)
            
            # Set initial style - upcoming reps
            if i == 1:  # First rep is current when starting
                button.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {constants.PRIMARY_800};
                        color: {constants.WHITE};
                        border-radius: 20px;
                        font-weight: bold;
                    }}
                    """
                )
            else:
                button.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {constants.WHITE};
                        border-radius: 20px;
                        border: 2px solid {constants.WHITE};
                    }}
                    """
                )
            
            self.rep_buttons.append(button)
            # Add the button with a stretch before and after for even spacing
            buttons_grid.addStretch(1)
            buttons_grid.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
            if i < self.total_reps:
                buttons_grid.addStretch(1)
        
        # Add the buttons container to the sidebar to fill available space
        bottom_progress_layout.addWidget(buttons_container, 1)  # Give it a stretch factor to fill space


        # Layouts
        top_layout = QVBoxLayout()
        top_layout.addWidget(self.prediction_label)

        # Create a grid-like video layout with 50:50 sizing
        video_layout = QHBoxLayout()
        video_layout.addWidget(self.video_label, 50)  # 50% of space
        video_layout.addWidget(self.video_guide_widget, 50)  # 50% of space
        
        # Bottom Layout
        bottom_layout = QVBoxLayout()
        bottom_layout.addLayout(bottom_progress_layout)
        bottom_layout.addLayout(bottom_button_group)

        # Add all layouts to content layout
        content_layout.addLayout(top_layout, stretch=1)
        content_layout.addLayout(video_layout, stretch=5)
        content_layout.addLayout(bottom_layout, stretch=2)
        
        # Add content widget to overall layout
        overall_layout.addWidget(content_widget, 1)  # Give content area a stretch factor of 1

        # Create overall container
        overall_container = QWidget()
        overall_container.setLayout(overall_layout)
        self.setCentralWidget(overall_container)
        self.resize(1024, 768)  # Set a reasonable default size

    def start_exercise(self):
        """Start the exercise with a countdown"""
        if self.current_rep == 0 or self.current_rep > self.total_reps:
            self.current_rep = 1
            self.incorrect_reps = 0  # Reset incorrect repetitions counter
            self.error_types = {}  # Track error types and their frequencies
            self.current_rep_has_error = False  # Reset error flag for new rep
            self.rep_errors = []  # Reset list of reps with errors
            print(f"DEBUG - Starting new exercise session. Reset incorrect_reps to {self.incorrect_reps}")
            self.update_rep_buttons()
            
            # Create a new session if user is logged in and starting fresh
            if self.session_manager and self.session_manager.is_logged_in() and not self.current_session_id:
                self.current_session_id = self.session_manager.create_session()
                print(f"Created new session with ID: {self.current_session_id}")
        
        # Clear the repetition message flag when start is clicked
        self.showing_rep_message = False
        
        self.countdown_seconds = 3  # Set your adjustable delay here (seconds)
        self._countdown_value = self.countdown_seconds
        self.start_button.setEnabled(False)
        self.prediction_label.setText(f"Starting in {self._countdown_value}...")
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._update_countdown)
        self._countdown_timer.start(1000)

    def _update_countdown(self):
        self._countdown_value -= 1
        if self._countdown_value > 0:
            self.prediction_label.setText(f"Starting in {self._countdown_value}...")
        else:
            self._countdown_timer.stop()
            self.prediction_label.setText("Waiting for prediction")
            self.start_button.setEnabled(True)
            self.start_video()

    def start_video(self):
        if self.thread is not None and self.thread.isRunning():
            print("Thread already running!")
            return
        self.thread = VideoThread(self.model_path)
        self.thread.frame_update.connect(self.update_frame)
        self.thread.prediction_signal.connect(self.update_prediction)
        self.thread.enough_frames_signal.connect(self.start_guide_video)
        self.thread.start()
        print("Video started (feedback collecting frames)")
        # Do NOT start the guide video yet; wait for enough_frames_signal

    def stop_video(self):
        # Stop pose estimation thread
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            print("Stopping pose estimation thread...")
        # Stop guide video playback
        if self.media_player:
            self.media_player.stop()
            print("Guide video stopped.")

    def start_guide_video(self):
        # Play guide video if path is set
        if self.guide_video_path and os.path.exists(self.guide_video_path):
            self.media_player.stop()
            self.media_player.setSource(QUrl.fromLocalFile(self.guide_video_path))
            self.media_player.setPosition(0)
            self.media_player.play()
            print("Guide video started after collecting 10 frames.")
        elif not self.guide_video_path:
            print("Guide video path is not set.")
        else:
            print(f"Guide video file not found: {self.guide_video_path}")

    def handle_media_status(self, status):
        """Handles changes in the media player's status, like end of media."""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            print("Guide video finished.")
            # Stop both the video guide and the feedback (pose estimation thread)
            self.stop_video()
            
            # Check if the completed repetition had an error
            completed_rep = self.current_rep
            if self.current_rep_has_error:
                # Only count a repetition as incorrect once, even if it had multiple errors
                if completed_rep not in self.rep_errors:
                    self.rep_errors.append(completed_rep)
                    self.incorrect_reps += 1
                    print(f"Rep {completed_rep} had errors. Incorrect reps: {self.incorrect_reps}/{len(self.rep_errors)}")
            
            # Reset error flag for next repetition
            self.current_rep_has_error = False
            
            # Update repetition tracking - one rep completed
            self.current_rep += 1
            print(f"Completed repetition {completed_rep} of {self.total_reps}")
            print(f"DEBUG - After completing rep, incorrect_reps count: {self.incorrect_reps}")
            
            # Update the rep buttons to reflect progress
            self.update_rep_buttons()
            
            # If all reps are completed, show a message and record the session
            if self.current_rep > self.total_reps:
                message = f"All {self.total_reps} repetitions completed!"
                print(f"DEBUG - All reps completed. Final incorrect_reps count: {self.incorrect_reps}/{self.total_reps}")
                
                # Record the completed exercise in the database if user is logged in
                if self.session_manager and self.session_manager.is_logged_in() and self.current_session_id:
                    self.record_completed_exercise()
            else:
                message = f"Repetition {completed_rep} completed. Click Start for next repetition."
            
            # Set flag to prevent prediction updates
            self.showing_rep_message = True
            
            # Update the label and ensure it's visible
            self.prediction_label.setText(message)
            self.prediction_label.repaint()
            
            # Force immediate UI update
            QApplication.processEvents()

    def update_frame(self, frame, class_name):
        """Update the video label with a new frame."""
        try:
            # Check if frame is valid
            if frame is None or frame.size == 0:
                print("Warning: Received empty frame")
                return
                
            # Convert the frame to QImage
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimage = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            # Scale pixmap to fit label size and preserve aspect ratio
            pixmap = pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.video_label.setPixmap(pixmap)
            
            # Don't track errors here - we'll do it in update_prediction to avoid double counting
            # Just pass the prediction to update_prediction
            self.update_prediction(class_name)
            
        except Exception as e:
            print(f"Error updating frame: {e}")
    
    def reset_prediction_label(self):
        """Reset the prediction label to show the current prediction"""
        # This is now only called manually when needed
        print("Resetting prediction label to show current prediction")
        self.showing_rep_message = False  # Clear the flag
        
        if self.current_prediction:
            # Use the same color-coding as in update_prediction_if_allowed
            if self.current_prediction == "Correct":
                # Use green for correct predictions
                self.prediction_label.setText(f"Prediction: <font color='{constants.SUCCESS}'>{self.current_prediction}</font>")
            elif self.current_prediction == "Waiting" or self.current_prediction == "Waiting for prediction":
                # Use default color for waiting
                self.prediction_label.setText(f"Prediction: <font color='{constants.PRIMARY_800}'>{self.current_prediction}</font>")
            else:
                # Use red for incorrect predictions
                self.prediction_label.setText(f"Prediction: <font color='{constants.DANGER}'>{self.current_prediction}</font>")
            # Force update
            self.prediction_label.repaint()
            QApplication.processEvents()
        
    def update_rep_buttons(self):
        """Update the visual state of repetition buttons based on current_rep"""
        if not self.rep_buttons:
            return  # No buttons to update
            
        for i, button in enumerate(self.rep_buttons, 1):  # 1-based indexing
            if i < self.current_rep:  # Completed reps
                button.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {constants.PRIMARY_800};
                        color: {constants.WHITE};
                        border-radius: 20px;
                    }}
                    """
                )
                button.setFixedSize(40, 40)
                button.setText("🗸")
            elif i == self.current_rep:  # Current rep
                button.setFixedSize(60, 60)
                button.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {constants.PRIMARY_800};
                        color: {constants.WHITE};
                        border-radius: 30px;
                        font-weight: bold;
                    }}
                    """
                )
            else:  # Upcoming reps
                button.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {constants.PRIMARY_800};
                        border: 2px solid {constants.PRIMARY_800};
                        border-radius: 20px;
                    }}
                    """
                )
                button.setFixedSize(40, 40)

    # VLC does not have a direct signal for end-of-media in python-vlc, but we can poll in a timer if needed.
    # For now, you can extend this if you want auto-stop behavior when the video ends.

    def set_total_reps(self, reps):
        """Set the total number of repetitions for the exercise"""
        if reps and isinstance(reps, int) and reps > 0:
            self.total_reps = reps
            
            # If we already have buttons, we need to recreate them
            if hasattr(self, 'rep_buttons') and self.rep_buttons:
                # Clear existing buttons
                for button in self.rep_buttons:
                    if button.parent():
                        button.parent().layout().removeWidget(button)
                        button.deleteLater()
                
                # Reset the list
                self.rep_buttons = []
                
                # Recreate the buttons in the UI
                self.init_ui()
            
            # Reset rep counter if needed
            if self.current_rep > self.total_reps:
                self.current_rep = 0
                
            # Update buttons to reflect current state
            self.update_rep_buttons()
    
    def record_completed_exercise(self):
        """Record the completed exercise in the database"""
        if not self.session_manager or not self.current_session_id:
            print("Cannot record exercise: No active session")
            return
            
        # Get exercise ID from database or create if doesn't exist
        from PyQt6.QtSql import QSqlQuery
        
        # First check if exercise exists
        query = QSqlQuery()
        query.prepare("SELECT id FROM exercises WHERE name = ?")
        query.addBindValue(self.current_exercise)
        
        exercise_id = None
        if query.exec() and query.next():
            exercise_id = query.value(0)
        else:
            # Exercise doesn't exist, create it
            query.prepare("INSERT INTO exercises (name, default_repetitions) VALUES (?, ?)")
            query.addBindValue(self.current_exercise)
            query.addBindValue(self.total_reps)
            
            if query.exec():
                # Get the ID of the newly created exercise
                query.prepare("SELECT last_insert_rowid()")
                if query.exec() and query.next():
                    exercise_id = query.value(0)
        
        if exercise_id:
            # Find the most frequent error type
            error_note = "None"
            if self.incorrect_reps > 0 and self.error_types:
                # Get the most common error type (excluding "No Person")
                filtered_errors = {k: v for k, v in self.error_types.items() if k != "No Person"}
                if filtered_errors:
                    most_common_error = max(filtered_errors.items(), key=lambda x: x[1])
                    error_type, _ = most_common_error
                    # Simplified format without occurrence count
                    error_note = f"Major Errors in {error_type}"
            
            # Record the exercise session with the error count
            success = self.session_manager.record_exercise(
                exercise_id, 
                self.total_reps, 
                self.incorrect_reps,  # This is now the count of repetitions with errors
                error_note  # Most common error type
            )
            
            if success:
                print(f"Successfully recorded exercise session: {self.current_exercise}, {self.total_reps} reps, {self.incorrect_reps} incorrect")
                
                # Complete the session with notes about errors
                notes = None
                if self.incorrect_reps > 0 and error_note:
                    notes = error_note  # Just use the error note directly
                self.session_manager.complete_session(notes)
                
                self.current_session_id = None  # Reset for next session
            else:
                print("Failed to record exercise session")
        else:
            print("Failed to get or create exercise record")
    
    def update_prediction_if_allowed(self, prediction):
        # Only update if we're not showing a repetition message
        if not self.showing_rep_message and not self.prediction_label.text().startswith("Starting in"):
            # Set color based on prediction result
            if prediction == "Correct":
                # Use green for correct predictions
                self.prediction_label.setText(f"Prediction: <font color='{constants.SUCCESS}'>{prediction}</font>")
            elif prediction == "Waiting" or prediction == "Waiting for prediction":
                # Use default color for waiting
                self.prediction_label.setText(f"Prediction: <font color='{constants.PRIMARY_800}'>{prediction}</font>")
            else:
                # Use red for incorrect predictions
                self.prediction_label.setText(f"Prediction: <font color='{constants.DANGER}'>{prediction}</font>")
            
            # Force immediate UI update
            self.prediction_label.repaint()
            QApplication.processEvents()
    
    def update_prediction(self, prediction):
        # Store the current prediction
        self.current_prediction = prediction
        
        # Debug info to track prediction state (less verbose)
        if prediction not in ["Correct", "Waiting", "Waiting for prediction", "No Person"]:
            print(f"DEBUG - Prediction: {prediction}, Current rep: {self.current_rep}")
        
        # Only flag the repetition as having an error if we're actively doing an exercise
        # and not showing a message between repetitions
        # Ignore "No Person" as it's not a valid error - just means the person wasn't detected
        if (prediction not in ["Correct", "Waiting", "Waiting for prediction", "No Person"] and 
            not self.showing_rep_message and
            self.current_rep > 0 and 
            self.current_rep <= self.total_reps):
            
            # Mark this repetition as having an error (we'll count it at the end of the rep)
            self.current_rep_has_error = True
            
            # Track error types for statistics
            if prediction in self.error_types:
                self.error_types[prediction] += 1
            else:
                self.error_types[prediction] = 1
                
            print(f"Error detected in rep {self.current_rep}: {prediction}")
            
        self.update_prediction_if_allowed(prediction)
    
    def closeEvent(self, event):
        self.stop_video()
        event.accept()


def handle_sigint(signal_num, frame):
    print("Ctrl+C received. Cleaning up...")
    if QApplication.instance():
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, MainWindow):
                widget.stop_video()
        QApplication.quit()


signal.signal(signal.SIGINT, handle_sigint)


def main():
    app = QApplication(sys.argv)

    model_path = os.path.join("models", "run_3.tflite")
    window = MainWindow(model_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
