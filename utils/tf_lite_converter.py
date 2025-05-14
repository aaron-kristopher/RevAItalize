import os
import tensorflow as tf
import sys

# Ensure parent directory is in sys.path for import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from architecture.custom_model import PositionalEncoding, ErrorF1Score, error_focused_loss

MODELS_DIR = os.path.join(os.path.dirname(__file__), '../models')

CUSTOM_OBJECTS = {
    'PositionalEncoding': PositionalEncoding,
    'ErrorF1Score': ErrorF1Score,
    'loss': error_focused_loss,
}

def convert_keras_to_tflite(models_dir):
    """
    Converts all .keras models in the specified directory to .tflite format.
    The .tflite files are saved in the same directory as the originals.
    """
    for filename in os.listdir(models_dir):
        if filename.endswith('.keras'):
            keras_path = os.path.join(models_dir, filename)
            tflite_path = os.path.splitext(keras_path)[0] + '.tflite'

            print(f"Converting {keras_path} -> {tflite_path}")
            try:
                model = tf.keras.models.load_model(keras_path, custom_objects=CUSTOM_OBJECTS)
                converter = tf.lite.TFLiteConverter.from_keras_model(model)
                converter.target_spec.supported_ops = [
                    tf.lite.OpsSet.TFLITE_BUILTINS,
                    tf.lite.OpsSet.SELECT_TF_OPS
                ]
                converter._experimental_lower_tensor_list_ops = False
                tflite_model = converter.convert()
                with open(tflite_path, 'wb') as f:
                    f.write(tflite_model)
                print(f"Successfully converted: {filename} -> {os.path.basename(tflite_path)}")
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")


if __name__ == "__main__":
    convert_keras_to_tflite(MODELS_DIR)
    print("Conversion complete.")
