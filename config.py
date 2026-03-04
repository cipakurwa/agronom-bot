import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота от @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "Ваш токен бота")

# Токен Hugging Face (https://huggingface.co/settings/tokens)
HF_TOKEN = os.getenv("HF_TOKEN", "Ваш токен Hugging Face")

# Имя модели на Hugging Face
MODEL_NAME = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"

print("✅ Конфигурация загружена")
print(f"📊 Модель: {MODEL_NAME}")
