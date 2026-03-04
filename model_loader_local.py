import os
import logging
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import InceptionResNetV2
from config import MODEL_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Классы болезней (38 классов из PlantVillage)
CLASSES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy", "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", "Potato___Early_blight",
    "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy", "Soybean___healthy",
    "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot", "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]

IMG_SIZE = 299

_model = None


def check_model_file():
    if not os.path.exists(MODEL_PATH):
        logger.error(f"❌ Файл модели не найден: {MODEL_PATH}")
        return False
    file_size = os.path.getsize(MODEL_PATH)
    logger.info(f"📊 Найден файл модели: {MODEL_PATH} ({file_size / 1024 / 1024:.2f} MB)")
    return True


def create_model():
    """Создаёт точную архитектуру модели на основе весов."""
    logger.info("🏗️ Создание модели InceptionResNetV2 с кастомными слоями...")

    # Базовая модель InceptionResNetV2 без верхушки, с global average pooling
    base_model = InceptionResNetV2(
        weights=None,
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        pooling='avg'  # выход (None, 1536)
    )

    x = base_model.output

    # Первый блок: BatchNorm -> Dense -> BatchNorm -> Dense -> BatchNorm -> Dense -> Dense
    # В соответствии с весами:
    # - batch_normalization_409 (размер 1536)
    # - dense_4 (1536 -> 256)
    # - batch_normalization_410 (размер 256)
    # - dense_5 (256 -> 128)
    # - batch_normalization_411 (размер 128)
    # - dense_6 (128 -> 64)
    # - dense_7 (64 -> 38)

    x = layers.BatchNormalization(name='batch_normalization_409')(x)  # размер 1536

    x = layers.Dense(256, name='dense_4')(x)
    x = layers.BatchNormalization(name='batch_normalization_410')(x)  # размер 256
    # Можно добавить Dropout, если нужно, но весов для него нет
    # x = layers.Dropout(0.5, name='dropout_3')(x)

    x = layers.Dense(128, name='dense_5')(x)
    x = layers.BatchNormalization(name='batch_normalization_411')(x)  # размер 128
    # x = layers.Dropout(0.5, name='dropout_4')(x)

    x = layers.Dense(64, name='dense_6')(x)
    # x = layers.Dropout(0.5, name='dropout_5')(x)

    predictions = layers.Dense(38, activation='softmax', name='dense_7')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    logger.info("✅ Модель создана.")
    return model


def load_weights_by_name(model):
    """Загружает веса по именам слоёв."""
    try:
        logger.info("⏳ Загрузка весов по именам слоёв...")
        model.load_weights(MODEL_PATH, by_name=True, skip_mismatch=True)
        logger.info("✅ Веса успешно загружены.")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки весов: {e}")
        raise


def load_model():
    global _model
    if _model is not None:
        return _model

    if not check_model_file():
        raise FileNotFoundError(f"Файл модели не найден: {MODEL_PATH}")

    _model = create_model()
    load_weights_by_name(_model)

    # Компилируем (необязательно)
    _model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Тестовый прогон
    test_input = np.random.rand(1, IMG_SIZE, IMG_SIZE, 3).astype(np.float32)
    test_output = _model.predict(test_input, verbose=0)
    logger.info(f"🧪 Тестовый прогон: мин={test_output.min():.4f}, макс={test_output.max():.4f}, "
                f"среднее={test_output.mean():.4f}, std={test_output.std():.4f}")

    return _model


def preprocess_image(image_bytes):
    """Предобработка для InceptionResNetV2."""
    img = Image.open(image_bytes).convert("RGB")
    img = img.resize((IMG_SIZE, IMG_SIZE), Image.Resampling.LANCZOS)
    img_array = np.array(img, dtype=np.float32)
    img_array = tf.keras.applications.inception_resnet_v2.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def predict(image_bytes):
    model = load_model()
    img_array = preprocess_image(image_bytes)
    predictions = model.predict(img_array, verbose=0)[0]

    top5_idx = np.argsort(predictions)[-5:][::-1]
    logger.info("📊 Топ-5 предсказаний:")
    for i, idx in enumerate(top5_idx):
        logger.info(f"   {i+1}. {CLASSES[idx]}: {predictions[idx]:.4f}")

    top3_idx = top5_idx[:3]
    results = [{'class': CLASSES[idx], 'confidence': float(predictions[idx])} for idx in top3_idx]
    return results