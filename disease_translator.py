# Словарь перевода названий болезней с английского на русский
DISEASE_TRANSLATIONS = {
    # Яблоня
    "Apple___Apple_scab": "🍎 Парша яблони",
    "Apple___Black_rot": "🍎 Черная гниль яблони",
    "Apple___Cedar_apple_rust": "🍎 Ржавчина яблони (кедровая)",
    "Apple___healthy": "🍎 Яблоня здорова",

    # Голубика
    "Blueberry___healthy": "🫐 Голубика здорова",

    # Вишня
    "Cherry_(including_sour)___Powdery_mildew": "🍒 Мучнистая роса вишни",
    "Cherry_(including_sour)___healthy": "🍒 Вишня здорова",

    # Кукуруза
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "🌽 Церкоспороз кукурузы",
    "Corn_(maize)___Common_rust_": "🌽 Обыкновенная ржавчина кукурузы",
    "Corn_(maize)___Northern_Leaf_Blight": "🌽 Северный гельминтоспориоз кукурузы",
    "Corn_(maize)___healthy": "🌽 Кукуруза здорова",

    # Виноград
    "Grape___Black_rot": "🍇 Черная гниль винограда",
    "Grape___Esca_(Black_Measles)": "🍇 Эска (черная пятнистость) винограда",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "🍇 Пятнистость листьев винограда",
    "Grape___healthy": "🍇 Виноград здоров",

    # Апельсин
    "Orange___Haunglongbing_(Citrus_greening)": "🍊 Хуанлунбин (позеленение цитрусовых)",

    # Персик
    "Peach___Bacterial_spot": "🍑 Бактериальная пятнистость персика",
    "Peach___healthy": "🍑 Персик здоров",

    # Перец
    "Pepper,_bell___Bacterial_spot": "🫑 Бактериальная пятнистость перца",
    "Pepper,_bell___healthy": "🫑 Перец здоров",

    # Картофель
    "Potato___Early_blight": "🥔 Альтернариоз картофеля (ранняя пятнистость)",
    "Potato___Late_blight": "🥔 Фитофтороз картофеля",
    "Potato___healthy": "🥔 Картофель здоров",

    # Малина
    "Raspberry___healthy": "🍇 Малина здорова",

    # Соя
    "Soybean___healthy": "🌱 Соя здорова",

    # Тыквенные
    "Squash___Powdery_mildew": "🎃 Мучнистая роса тыквенных",

    # Клубника
    "Strawberry___Leaf_scorch": "🍓 Красная пятнистость клубники",
    "Strawberry___healthy": "🍓 Клубника здорова",

    # Томат
    "Tomato___Bacterial_spot": "🍅 Бактериальная пятнистость томата",
    "Tomato___Early_blight": "🍅 Альтернариоз томата",
    "Tomato___Late_blight": "🍅 Фитофтороз томата",
    "Tomato___Leaf_Mold": "🍅 Кладоспориоз томата",
    "Tomato___Septoria_leaf_spot": "🍅 Септориоз томата",
    "Tomato___Spider_mites Two-spotted_spider_mite": "🍅 Паутинный клещ на томате",
    "Tomato___Target_Spot": "🍅 Целевая пятнистость томата",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "🍅 Вирус желтой курчавости томата",
    "Tomato___Tomato_mosaic_virus": "🍅 Вирус табачной мозаики томата",
    "Tomato___healthy": "🍅 Томат здоров",
}


def translate_disease_name(english_name: str) -> str:
    """Переводит название болезни с английского на русский"""
    if english_name in DISEASE_TRANSLATIONS:
        return DISEASE_TRANSLATIONS[english_name]

    # Если точного перевода нет, возвращаем читаемый английский
    return english_name.replace('_', ' ').replace('___', ' - ')


def get_crop_name(disease_name: str) -> str:
    """Извлекает название культуры из полного имени болезни"""
    if '___' in disease_name:
        crop = disease_name.split('___')[0]
        return crop.replace('_', ' ')
    return "Растение"