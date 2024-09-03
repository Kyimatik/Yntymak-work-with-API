from aiogram.types import ReplyKeyboardMarkup , InlineKeyboardMarkup , InlineKeyboardButton , KeyboardButton , ReplyKeyboardRemove



#Обычные кнопки которые видны всегда 
mainkb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Новое объявление 🛠")
            
        ]
    ],
    resize_keyboard=True
)

cancel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена ❌")
            
        ]
    ],
    resize_keyboard=True
)

#Изменения своих данных в профиле!
options = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да",callback_data="yesbitches"),
            InlineKeyboardButton(text="Нет",callback_data="nobitches")
                                
        ]
    ],
    resize_keyboard=True
)