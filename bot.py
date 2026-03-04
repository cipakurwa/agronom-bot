import logging
import io
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ParseMode

from config import BOT_TOKEN, HF_TOKEN, MODEL_NAME
from model_loader import predict
from disease_translator import translate
from disease_advice import get_advice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    text = (
        "🌱 *Добро пожаловать в AI-бота Агроном!*\n\n"
        "Отправьте фото листа растения, и я определю болезнь или дам рекомендации по уходу.\n\n"
        "📸 *Как это работает:*\n"
        "1. Сделайте четкое фото листа.\n"
        "2. Отправьте его боту.\n"
        "3. Получите диагноз и советы на русском языке.\n\n"
        "Просто отправьте фото, чтобы начать!"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(content_types=["photo"])
async def photo_handler(message: types.Message):
    status_msg = await message.answer("🔍 Анализирую изображение...")

    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        downloaded = await bot.download_file(file.file_path)
        image_bytes = io.BytesIO(downloaded.read())

        predictions = predict(image_bytes, MODEL_NAME, HF_TOKEN)

        answer = "*🔬 Результаты анализа:*\n\n"
        # Список для вариантов с вероятностью >= 30%
        high_conf_predictions = []

        for i, pred in enumerate(predictions, 1):
            label = pred["class"]
            conf = pred["confidence"] * 100
            russian = translate(label)
            answer += f"{i}. *{russian}* – {conf:.1f}%\n"
            if conf >= 30.0:
                high_conf_predictions.append((russian, label, conf))

        if high_conf_predictions:
            answer += f"\n💊 *Рекомендации:*\n"
            for russian_name, label, conf in high_conf_predictions:
                advice = get_advice(label)
                answer += f"\n🔹 *{russian_name}* (вероятность {conf:.1f}%):\n{advice}\n"
        else:
            # Если нет вариантов с высокой вероятностью, даем рекомендации для первого
            best_label = predictions[0]["class"]
            advice = get_advice(best_label)
            answer += f"\n💊 *Рекомендации для наиболее вероятного варианта:*\n{advice}"

        await status_msg.edit_text(answer, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.exception("Ошибка при обработке фото")
        await status_msg.edit_text("😔 Произошла ошибка. Попробуйте другое фото.")

if __name__ == "__main__":
    logger.info("🚀 Бот запускается...")
    executor.start_polling(dp, skip_updates=True)
