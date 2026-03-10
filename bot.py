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

# Список поддерживаемых культур (сгенерирован из классов модели)
SUPPORTED_CROPS = [
    "Яблоня", "Голубика", "Вишня", "Кукуруза", "Виноград", "Апельсин",
    "Персик", "Перец", "Картофель", "Малина", "Соя", "Тыквенные",
    "Клубника", "Томат"
]

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    text = (
        "🌱 *Добро пожаловать в AI-бота Агроном!*\n\n"
        "Я помогаю диагностировать болезни растений по фотографии листа.\n\n"
        "📸 *Как это работает:*\n"
        "1. Сделайте чёткое фото листа.\n"
        "2. Отправьте его мне.\n"
        "3. Я определю болезнь и дам рекомендации.\n\n"
        "🔍 *Какие растения я знаю?* Введите /plants, чтобы увидеть список.\n"
        "ℹ️ *Помощь* — /help"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(commands=["help"])
async def help_handler(message: types.Message):
    text = (
        "🆘 *Помощь по использованию*\n\n"
        "Я определяю болезни по фото листа. Отправьте мне чёткое изображение, и я выдам вероятный диагноз.\n\n"
        "Если результат вас смущает, можете отправить ещё одно фото под другим углом или описать симптомы текстом – я учту это.\n\n"
        "Список культур, которые я знаю: /plants\n"
        "О проекте: /about"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(commands=["plants"])
async def plants_handler(message: types.Message):
    crops_list = "\n• " + "\n• ".join(SUPPORTED_CROPS)
    text = f"🌿 *Поддерживаемые культуры:*\n{crops_list}\n\nВсего 38 классов болезней (включая здоровые растения)."
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(commands=["about"])
async def about_handler(message: types.Message):
    text = (
        "🤖 *О боте*\n\n"
        "Бот создан в рамках курсового проекта «Быстрое создание MVP в Data Science».\n"
        "Использует модель MobileNetV2, дообученную на датасете PlantVillage (38 классов).\n"
        "Точность модели: 95.4%.\n\n"
        "Авторы: команда 96"
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
            best_label = predictions[0]["class"]
            advice = get_advice(best_label)
            answer += f"\n💊 *Рекомендации для наиболее вероятного варианта:*\n{advice}"

        # Добавляем предложение уточнить диагноз
        answer += "\n\n_Если вы не уверены, отправьте ещё одно фото под другим ракурсом или опишите симптомы текстом._"

        await status_msg.edit_text(answer, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.exception("Ошибка при обработке фото")
        await status_msg.edit_text("😔 Произошла ошибка. Попробуйте другое фото.")

@dp.message_handler(content_types=["text"])
async def text_handler(message: types.Message):
    # Отвечаем на любые текстовые сообщения (кроме команд) предложением отправить фото
    await message.reply(
        "Я понимаю только фотографии. Пожалуйста, отправьте фото листа растения.\n"
        "Если нужна помощь, введите /help"
    )

if __name__ == "__main__":
    logger.info("🚀 Бот запускается...")
    executor.start_polling(dp, skip_updates=True)
