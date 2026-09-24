import os
import json
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 5
DATASET_DIR = "dataset"
MODEL_SAVE_PATH = "models/plant_disease_mobilenetv2.keras"
CLASS_NAMES_PATH = "class_names.json"

def main():
    train_dir = os.path.join(DATASET_DIR, "train")
    val_dir = os.path.join(DATASET_DIR, "val")
    if not os.path.exists(val_dir):
        val_dir = os.path.join(DATASET_DIR, "validation")

    print("Loading datasets...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir, image_size=IMAGE_SIZE, batch_size=BATCH_SIZE, shuffle=True
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir, image_size=IMAGE_SIZE, batch_size=BATCH_SIZE, shuffle=False
    )

    class_names = train_ds.class_names
    print(f"Detected {len(class_names)} classes.")

    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    with open(CLASS_NAMES_PATH, "w") as f:
        json.dump(class_names, f)

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    # Standard Rescaling layer [0, 255] -> [-1, 1] for MobileNetV2
    rescaling = layers.Rescaling(1./127.5, offset=-1)

    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
    ])

    base_model = MobileNetV2(
        input_shape=IMAGE_SIZE + (3,), include_top=False, weights="imagenet"
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=IMAGE_SIZE + (3,))
    x = data_augmentation(inputs)
    x = rescaling(x)  # Standard Keras built-in layer (No TrueDivide bug)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(len(class_names), activation="softmax")(x)

    model = models.Model(inputs, outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    print("Starting clean model training...")
    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)
    
    # Save in standard native Keras format
    model.save(MODEL_SAVE_PATH)
    print(f"Model saved cleanly to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    main()