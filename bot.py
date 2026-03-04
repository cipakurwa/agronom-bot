import logging
import io
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ParseMode

from config import BOT_TOKEN
from model_loader_local import predict, load_model
from disease_translator import translate_disease_name
from disease_advice import get_advice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    welcome_text = (
        "🌱 *Добро пожаловать в AI-бота Агроном!* 🌱\n\n"
        "🔬 *Я специализируюсь на диагностике болезней растений*\n\n"
        "📸 *Как это работает:*\n"
        "1. Отправьте фото больного листа\n"
        "2. Я определю заболевание по нейросети\n"
        "3. Вы получите рекомендации по лечению на русском языке\n\n"
        "🌽 *Поддерживаемые культуры:*\n"
        "• Томаты, картофель, перец\n"
        "• Яблоня, вишня, персик\n"
        "• Виноград, клубника\n"
        "• Кукуруза, соя, тыквенные\n\n"
        "📊 *Всего 38 классов болезней*\n\n"
        "Просто отправьте фото, чтобы начать!"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=["status"])
async def status_handler(message: types.Message):
    await message.answer("✅ Бот работает\n🌱 Модель загружена\n📊 Готов к диагностике")


@dp.message_handler(content_types=["photo"])
async def photo_handler(message: types.Message):
    status_msg = await message.answer("🔍 Анализирую растение... (это займет несколько секунд)")

    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        downloaded_file = await bot.download_file(file.file_path)
        image_bytes = io.BytesIO(downloaded_file.read())

        predictions = predict(image_bytes)

        result_text = "*🔬 Результаты анализа:*\n\n"
        for i, pred in enumerate(predictions, 1):
            disease_class = pred['class']
            confidence = pred['confidence'] * 100
            russian_name = translate_disease_name(disease_class)

            if confidence > 80:
                emoji = "✅"
            elif confidence > 50:
                emoji = "⚠️"
            else:
                emoji = "❓"

            result_text += f"{emoji} *Вариант {i}:* {russian_name}\n"
            result_text += f"   Уверенность: {confidence:.1f}%\n\n"

        best_prediction = predictions[0]['class']
        advice = get_advice(best_prediction)

        result_text += f"💊 *Рекомендации:*\n{advice}\n\n"
        result_text += "---\n🤖 Модель: InceptionResNetV2 (PlantVillage)"

        await status_msg.edit_text(result_text, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Ошибка обработки фото: {e}", exc_info=True)
        await status_msg.edit_text("😔 Произошла ошибка при анализе. Попробуйте другое фото.")


async def on_startup(dp):
    logger.info("🚀 Запуск бота...")
    try:
        load_model()
        logger.info("✅ Бот готов к работе!")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        logger.error("Бот не сможет работать без модели!")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)