import tensorflow as tf
from tensorflow.keras.utils import register_keras_serializable


@register_keras_serializable()
class PositionalEncoding(tf.keras.layers.Layer):
    def __init__(self, max_steps, d_model, use_learned_bias=True, **kwargs):
        super(PositionalEncoding, self).__init__()
        self.max_steps = max_steps
        self.d_model = d_model
        self.use_learned_bias = use_learned_bias
        if use_learned_bias:
            self.bias = self.bias = self.add_weight(
                name="pos_bias",
                shape=[1, 1, d_model],
                initializer="zeros",
                trainable=True,
            )

    def get_angles(self, pos, i):
        angle_rates = 1 / tf.pow(
            10000.0, (2 * (i // 2)) / tf.cast(self.d_model, tf.float32)
        )
        return pos * angle_rates

    def call(self, inputs):
        batch_size, seq_len, _ = (
            tf.shape(inputs)[0],
            tf.shape(inputs)[1],
            tf.shape(inputs)[2],
        )
        position = tf.range(seq_len, dtype=tf.float32)[:, tf.newaxis]
        div_term = tf.range(self.d_model, dtype=tf.float32)[tf.newaxis, :]

        pos_encoding = self.get_angles(position, div_term)
        pos_encoding = tf.concat(
            [tf.sin(pos_encoding[:, 0::2]), tf.cos(pos_encoding[:, 1::2])], axis=-1
        )
        pos_encoding = tf.expand_dims(pos_encoding, 0)

        output = inputs + tf.cast(pos_encoding, dtype=tf.float32)
        if self.use_learned_bias:
            output += self.bias  # soft global tuning
        return output


def error_focused_loss(error_weight=10.0, gamma=2.0):
    def loss(y_true, y_pred):
        # Apply focal loss with class weighting
        # Higher weight for positive class (errors)
        alpha = tf.where(tf.equal(y_true, 1), error_weight, 1.0)

        # Focal loss calculation
        p_t = tf.where(tf.equal(y_true, 1), y_pred, 1 - y_pred)
        focal_weight = tf.pow(1 - p_t, gamma)

        # Apply both weights
        weighted_focal = (
            -alpha * focal_weight * tf.math.log(tf.clip_by_value(p_t, 1e-8, 1.0))
        )

        return tf.reduce_mean(weighted_focal)

    return loss


@register_keras_serializable()
class ErrorF1Score(tf.keras.metrics.Metric):
    def __init__(self, name="error_f1", **kwargs):
        super().__init__(name=name, **kwargs)
        self.precision = tf.keras.metrics.Precision(thresholds=0.5)
        self.recall = tf.keras.metrics.Recall(thresholds=0.5)

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.precision.update_state(y_true, y_pred, sample_weight)
        self.recall.update_state(y_true, y_pred, sample_weight)

    def result(self):
        p = self.precision.result()
        r = self.recall.result()
        return 2 * ((p * r) / (p + r + tf.keras.backend.epsilon()))

    def reset_state(self):
        self.precision.reset_state()
        self.recall.reset_state()

