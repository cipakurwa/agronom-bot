import os
from dotenv import load_dotenv

load_dotenv()

# ========== ТОКЕНЫ ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "8578494775:AAFYUwE7lC_8OiqmtUpkR_ftc2VkdL-0PcY")
# ============================

# Путь к локальному файлу модели
MODEL_PATH = "Pretrained_model.h5"

print("✅ Конфигурация загружена")
print(f"📊 Модель: {MODEL_PATH}")
print(f"🌱 Тип: InceptionResNetV2 (38 классов)")