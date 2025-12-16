import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models, optimizers

DATA_DIR = os.getenv('LEAF_DETECTOR_DATA', 'leaf_detector_data')
SAVE_PATH = os.getenv('LEAF_DETECTOR_OUT', '../models/leaf_detector.h5')

def build_model(input_shape=(128,128,3)):
    base = MobileNetV2(weights='imagenet', include_top=False, input_shape=input_shape)
    base.trainable = False
    x = layers.GlobalAveragePooling2D()(base.output)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    out = layers.Dense(1, activation='sigmoid')(x)
    model = models.Model(inputs=base.input, outputs=out)
    model.compile(optimizer=optimizers.Adam(1e-4), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train():
    # Expect DATA_DIR to have two subfolders: 'leaf' and 'nonleaf'
    train_dir = os.path.join(DATA_DIR, 'train')
    val_dir = os.path.join(DATA_DIR, 'val')

    if not os.path.exists(train_dir):
        raise SystemExit(f"Training data not found at {train_dir}. Create '{DATA_DIR}/train/leaf' and '{DATA_DIR}/train/nonleaf'.")

    img_gen = ImageDataGenerator(rescale=1./255, horizontal_flip=True, rotation_range=20, zoom_range=0.2)
    train_gen = img_gen.flow_from_directory(train_dir, target_size=(128,128), batch_size=32, class_mode='binary')
    val_gen = ImageDataGenerator(rescale=1./255).flow_from_directory(val_dir, target_size=(128,128), batch_size=32, class_mode='binary')

    model = build_model((128,128,3))
    model.fit(train_gen, validation_data=val_gen, epochs=10)
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    model.save(SAVE_PATH)
    print(f"Saved leaf detector to {SAVE_PATH}")

if __name__ == '__main__':
    train()
