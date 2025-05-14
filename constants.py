from PyQt6.QtGui import QFont

# Centralized constants for the RevAItalize application

# Colors
PRIMARY_50 = "#EDFBFF"
PRIMARY_100 = "#FCFAFF"  # 0077B6 #002356 #60ADF1 #9FE7FF #6E94BC #EDFBFF
PRIMARY_200 = "#002356"
PRIMARY_300 = "#60ADF1"
PRIMARY_400 = "#0077B6"
PRIMARY_500 = "#6E94BC"
PRIMARY_600 = "#00527E"
PRIMARY_700 = "#002E46"
PRIMARY_800 = "#002356"
PRIMARY_900 = "#00090E"
PRIMARY_950 = "#9FE7FF"

WHITE = "#FCFAFF"
GRAY = "#B9C2CA"
DANGER = "#B60012"
SUCCESS = "#519872"
MINT = "#65B891"

# Font Paths
FONT_DIR = "fonts/Poppins/"
POPPINS_REGULAR_PATH = FONT_DIR + "Poppins-Regular.ttf"
POPPINS_BOLD_PATH = FONT_DIR + "Poppins-Bold.ttf"
POPPINS_ITALIC_PATH = FONT_DIR + "Poppins-Italic.ttf"
POPPINS_SEMIBOLD_PATH = FONT_DIR + "Poppins-SemiBold.ttf"

# Font WeightStyles (using standard PyQt values)
WEIGHT_REGULAR = QFont.Weight.Normal
WEIGHT_SEMIBOLD = QFont.Weight.DemiBold
WEIGHT_BOLD = QFont.Weight.Bold
STYLE_ITALIC = True  # QFont.setItalic takes a boolean

# Paths
EXERCISE_ICON_PATH = "imgs/exercise.png"
PROFILE_ICON_PATH = "imgs/profile.png"
HOME_ICON_PATH = "imgs/home-icon.png"
EXERCISES_ICON_PATH = "imgs/exercises-icon.png"
MODEL_ICON_PATH = "imgs/model-icon.png"
QUIT_ICON_PATH = "imgs/quit-icon.png"
REVAITALIZE_LOGO_PATH = "imgs/revaitalize-logo.png"
RIGHT_ARROW_ICON_PATH = "imgs/right-arrow-icon.png"
LSTM1_IMAGE_PATH = "imgs/lstm1-image.png"
LSTM2_IMAGE_PATH = "imgs/lstm2-image.png"
BLAZEPOSE_IMAGE_PATH = "imgs/blazepose.png"
ATTENTION_MECHANISM_IMAGE_PATH = "imgs/attention-mechanism.png"

# Exercise video paths
TORSO_PREVIEW_VID = "videos/torso-preview.mp4"
FLANK_PREVIEW_VID = "videos/flank-preview.mp4"
HIDING_FACE_PREVIEW_VID = "videos/hiding-preview.mp4"
