from PyQt6.QtGui import QFont, QFontDatabase
import constants

# Store the loaded font family name globally within this module
_font_family = None


def load_fonts():
    """Loads all required application fonts into the QFontDatabase."""
    global _font_family

    font_paths = [
        constants.POPPINS_REGULAR_PATH,
        constants.POPPINS_BOLD_PATH,
        constants.POPPINS_ITALIC_PATH,
        constants.POPPINS_SEMIBOLD_PATH,
    ]

    loaded_ids = []
    for path in font_paths:
        font_id = QFontDatabase.addApplicationFont(path)
        if font_id == -1:
            print(f"Error loading font: {path}")
        else:
            loaded_ids.append(font_id)

    if not loaded_ids:
        print("No fonts loaded successfully. Using system default.")
        _font_family = QFont().family()
    else:
        # Assume all Poppins fonts register under the same family name.
        # Get the family name from the first successfully loaded font.
        families = QFontDatabase.applicationFontFamilies(loaded_ids[0])
        if families:
            _font_family = families[0]
            print(f"Loaded font family: {_font_family}")
        else:
            print(
                "Could not determine font family name after loading. Using system default."
            )
            _font_family = QFont().family()


def get_font(
    size: int, weight: int = constants.WEIGHT_REGULAR, italic: bool = False
) -> QFont:
    """Creates a QFont instance with the loaded application font family."""
    global _font_family

    if _font_family is None:
        # Should not happen if load_fonts() is called first, but as a fallback
        print("Warning: Font family not loaded. Using default font.")
        load_fonts()  # Attempt to load if not already
        if _font_family is None:  # Still not loaded?
            _font_family = QFont().family()

    font = QFont(_font_family, size)
    font.setWeight(weight)
    font.setItalic(italic)
    return font
