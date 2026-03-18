import tensorflow as tf
import tf2onnx
import onnx
import os

print("🔄 Converting H5 model to ONNX...")
model = tf.keras.models.load_model('models/tomato_model.h5', compile=False)
print(f'✓ Model loaded. Input shape: {model.input_shape}')

input_sig = [tf.TensorSpec(model.inputs[0].shape, tf.float32, name='input')]
onnx_model, _ = tf2onnx.convert.from_keras(
    model, 
    input_signature=input_sig, 
    opset=13
)

onnx.save(onnx_model, 'models/tomato_model.onnx')
size_mb = os.path.getsize('models/tomato_model.onnx') / (1024 * 1024)
print(f'✅ Converted! Size: {size_mb:.1f} MB')
