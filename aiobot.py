import json
import asyncio
import logging
import sys
from enum import Enum
import aiohttp
import aiofiles

import time 
from aiogram import Bot, Dispatcher, Router, types , F 
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart , Command
from aiogram.types import Message , CallbackQuery ,FSInputFile
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup , InlineKeyboardMarkup , InlineKeyboardButton , KeyboardButton , ReplyKeyboardRemove 

from aiogram.fsm.state import StatesGroup , State





#Отправка рассылки всем пользователям которые есть в базе данных.
class sendall(StatesGroup):
    getphoto = State()
    gettext = State()
    getbutton = State() #
    getlink = State() #




#TOKEN = "7352009164:AAHD84f31ubJwRvt9JX8AIuXeaSaY7bOSBw"
TOKEN = "7377143690:AAGob-Uf_jV3-bWEvJycGtbV3gTMDDKU0K0"

bot = Bot(TOKEN)
dp = Dispatcher()
router = Router()




def load_data():
    try:
        with open('usersdb.json', 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {"users": [], "total_users": 0}
    return data

def save_data(data):
    with open('usersdb.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)




# Главная клавиатура
mainkb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить заголовок"),
            KeyboardButton(text="Изменить заголовок")
        ],
        [
            KeyboardButton(text="Добавить номер"),
            KeyboardButton(text="Изменить номер")
        ],
        [
            KeyboardButton(text="Добавить описание"),
            KeyboardButton(text="Изменить описание")
        ],
        [
            KeyboardButton(text="Добавить изображение"),
            KeyboardButton(text="Изменить изображение")
        ],
        [
            KeyboardButton(text="Посмотреть"),
            KeyboardButton(text="Опубликовать"),
            KeyboardButton(text="Очистить")
        ]
    ],
    resize_keyboard=True
)
# Команды 
commands = [
    'Добавить заголовок',
    'Изменить заголовок',
    'Добавить номер',
    'Изменить номер',
    'Добавить описание',
    'Изменить описание',
    'Добавить изображение',
    'Изменить изображение',
    'Посмотреть',
    'Опубликовать',
    'Очистить'
]



class TelegramInfo:
    def __init__(self):
        self.id = -1
        self.fullName = ''
        self.userName = ''

class AdInfo:
    def __init__(self):
        self.title = ''
        self.phone = ''
        self.description = ''
        self.image_id = None

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)

class UserState(Enum):
    NONE = 0
    NUMBER = 1
    IMAGE = 2
    DESCRIPTION = 3
    TITLE = 4

class User:
    def __init__(self):
        self.tgInfo = TelegramInfo()
        self.adInfo = AdInfo()




async def load_data_from_json():
    try:
        async with aiofiles.open('users_data.json', 'r') as infile:
            data = json.loads(await infile.read())
            users = {int(k): User() for k, v in data['users'].items()}
            for user_id, user_data in data['users'].items():
                user = users[int(user_id)]
                user.tgInfo = TelegramInfo()
                user.tgInfo.id = user_data['tgInfo']['id']
                user.tgInfo.fullName = user_data['tgInfo']['fullName']
                user.tgInfo.userName = user_data['tgInfo']['userName']
                user.adInfo = AdInfo()
                user.adInfo.title = user_data['adInfo']['title']
                user.adInfo.phone = user_data['adInfo']['phone']
                user.adInfo.description = user_data['adInfo']['description']
                user.adInfo.image_id = user_data['adInfo']['image_id']
            states = {int(k): UserState[v] for k, v in data['states'].items()}
            return users, states
    except FileNotFoundError:
        return {}, {}

async def save_data_to_json():
    data = {
        'users': {user_id: {
            'tgInfo': {
                'id': user.tgInfo.id,
                'fullName': user.tgInfo.fullName,
                'userName': user.tgInfo.userName
            },
            'adInfo': {
                'title': user.adInfo.title,
                'phone': user.adInfo.phone,
                'description': user.adInfo.description,
                'image_id': user.adInfo.image_id
            }
        } for user_id, user in users.items()},
        'states': {user_id: state.name for user_id, state in states.items()}
    }
    async with aiofiles.open('users_data.json', 'w') as outfile:
        await outfile.write(json.dumps(data, indent=4))






@dp.message(Command("start"))
async def start(message: Message):
    data = load_data()
    
    user_id = message.from_user.id
    
    # Если пользователь еще не был добавлен в базу данных
    if user_id not in data["users"]:
        data["users"].append(user_id)
        data["total_users"] += 1
        save_data(data)  # Сохраняем обновленные данные
    

    start_text = """Требования к публикацию и содержанию объявлений

 При нарушении этих правил пользователь будет заблокирован и больше не сможет опубликовать обьявление

 Разрешается публиковать
• объявление о работе с ежедневной или с ежемесячной оплатой

Запрещается публиковать 
 • Любая реклама (объявление которое не имеет отношение к работе)
• Объявление в котором присутствует оскорбительные слова
• Запрещено публиковать повторные объявления (можно публиковать только через 4-5 часов)

Также все команды : 
<b>Очистить</b> - очистить публикацию
<b>Опубликовать</b> - публикация вашего объявления на сайт
<b>Посмотреть</b> - посмотреть ваше объявление
"""
    await message.answer(start_text , reply_markup=mainkb , parse_mode="HTML")


@dp.message(F.content_type.in_({'text', 'photo'}))
async def message_reply(message):
    try:
        text = str(message.html_text)
        user_id = message.from_user.id
        chat_id = message.chat.id
        if user_id in users:
            pass
        else:
            user = User()
            user.adInfo = AdInfo()
            user.tgInfo = TelegramInfo()
            user.tgInfo.id = user_id
            user.tgInfo.userName = message.from_user.username
            user.tgInfo.fullName = message.from_user.full_name
            users[user_id] = user
            states[user_id] = UserState.NONE
        if text in commands:
            command = message.html_text.lower()
            if command == 'добавить номер' or command == 'изменить номер':
                states[user_id] = UserState.NUMBER
                await bot.send_message(chat_id, 'Введите номер')
            elif command == 'добавить изображение' or command == 'изменить изображение':
                states[user_id] = UserState.IMAGE
                await bot.send_message(chat_id, 'Выберите изображение')
            elif command == 'добавить описание' or command ==  'изменить описание':
                states[user_id] = UserState.DESCRIPTION
                await bot.send_message(chat_id, 'Введите описание')
            elif command == 'добавить заголовок' or command == 'изменить заголовок':
                states[user_id] = UserState.TITLE
                await bot.send_message(chat_id, 'Введите название')
            elif command == 'опубликовать':
                await publish(chat_id, user_id)
            elif command == 'очистить':
                await clear(chat_id, user_id)
            elif command == 'посмотреть':
                await show_ad(chat_id, user_id)
            else:
                states[user_id] = UserState.NONE
                await bot.send_message(chat_id, 'Команда не найдена')
            await save_data_to_json()

        else:
            state = states[user_id]
            user = users[user_id]
            if state == UserState.NUMBER:
                user.adInfo.phone = text
                await bot.send_message(chat_id, 'Номер добавлен')
                await show_ad(chat_id, user_id)
                states[user_id] = UserState.NONE  # Сброс состояния
            elif state == UserState.DESCRIPTION:
                user.adInfo.description = text
                await bot.send_message(chat_id, 'Описание добавлено')
                await show_ad(chat_id, user_id)
                states[user_id] = UserState.NONE  # Сброс состояния
            elif state == UserState.IMAGE:
                await choose_photo(chat_id, user_id, message.photo)
                await show_ad(chat_id, user_id)
                states[user_id] = UserState.NONE  # Сброс состояния
            elif state == UserState.TITLE:
                user.adInfo.title = text
                await bot.send_message(chat_id, 'Название добавлено')
                await show_ad(chat_id, user_id)
                states[user_id] = UserState.NONE  # Сброс состояния
            else:
                states[user_id] = UserState.NONE
                await bot.send_message(chat_id, 'NOT FOUND')
            await save_data_to_json()
    except:
        pass



async def publish(chat_id, user_id):
    user = users[user_id]
    if user.adInfo.title == '' or user.adInfo.description == '' or user.adInfo.phone == '':
        await bot.send_message(chat_id, 'Заполните данные')
        return
    url_for_upload = ''
    if user.adInfo.image_id is not None:
        path = await get_file_path(user.adInfo.image_id)
        await download_photo(path, user.tgInfo.id)
        url_for_upload = await upload_photo(user.tgInfo.id)

    description = user.adInfo.description + "\n" \
                  + "\nОбьявление пользователя телеграмм: " + " id:" + str(
        user.tgInfo.id) + "\n\nОпубликовано с помощью телеграмм бота @yntymakitem_bot"

    payload = {'key': 'XGaj8cnRdvAqmIxYxnb4yBWBtPzB8O',
               'type': 'insert',
               'object': 'item',
               'action': 'add',
               'userId': '56336',
               'catId': '83',
               'id': '56336',
               'contactName': 'TelegramName',
               's_contact_name': 'TelegramName',
               's_phone': user.adInfo.phone,
               'contactEmail': 'telegabotyntymak@yandex.ru',
               'pk_i_id': '56336',
               'active': 'ACTIVE',
               'enable': 'ENABLED',
               'countryId': 'RU',
               'price': '0',
               'currency': 'RU',
               'showEmail': '1',
               'secret': 'XGaj8cnRdvAqmIxYxnb4yBWBtPzB8O',
               "title[" + 'ru_RU' + "]": user.adInfo.title,
               "description[" + 'ru_RU' + "]": description,

               }

    if url_for_upload != '':
        payload["ajax_photos[]"] = url_for_upload

    async with aiohttp.ClientSession() as session:
        async with session.post('https://yntymak.ru/oc-content/plugins/rest/api.php', params=payload) as response:
            response_text = await response.text()

    user.adInfo = AdInfo()
    users.pop(user_id)
    await save_data_to_json()
    await bot.send_message(chat_id, 'Обьявление опубликовано')

async def choose_photo(chat_id, user_id, photos):
    user = users[user_id]
    user.adInfo.image_id = str(photos[2].file_id)
    await bot.send_message(chat_id, 'Изображение выбрано')
    await save_data_to_json()

async def clear(chat_id, user_id):
    user = users[user_id]
    user.adInfo = AdInfo()  
    await bot.send_message(chat_id, 'clear')
    await save_data_to_json()

async def show_ad(chat_id, user_id):
    user = users[user_id]
    title = "Заголовок: " + user.adInfo.title + "\n"
    description = "Описание: " + user.adInfo.description + "\n"
    phone = "Телефон: " + str(user.adInfo.phone) + "\n"
    footer = "Обьявление пользователя телеграмм: @" + str(user.tgInfo.userName) + " id" + str(user.tgInfo.id) + "\n"
    sms = title + description + phone + footer
    await bot.send_message(chat_id, sms)

async def get_file_path(file_id):
    url = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    return data['result']['file_path']


async def download_photo(file_path, user_id):
    try:
        image_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                img_data = await response.read()
                async with aiofiles.open(f'{user_id}.jpg', 'wb') as handler:
                    await handler.write(img_data)
        print(f"Фото сохранено как {user_id}.jpg")
    except Exception as e:
        print(f"Ошибка при сохранении фото: {e}")


async def upload_photo(user_id):
    url = "https://yntymak.ru/index.php?page=ajax&action=ajax_upload"
    async with aiohttp.ClientSession() as session:
        async with aiofiles.open(f'{user_id}.jpg', 'rb') as file:
            form = aiohttp.FormData()
            form.add_field('qqfile', file, filename=f'{user_id}.jpg', content_type='image/jpeg')
            async with session.post(url, data=form) as response:
                response_text = await response.text()
                print(f"Ответ сервера: {response_text}")
                
                # Попробуем сразу декодировать JSON
                try:
                    data = json.loads(response_text)
                    if "uploadName" in data:
                        return data['uploadName']
                    else:
                        print("Ошибка: нет ключа 'uploadName' в ответе сервера.")
                        return None
                except json.JSONDecodeError as e:
                    print(f"Ошибка при декодировании JSON: {e}")
                    return None



#########################################################################################################################################################
# Кнопка Да или нет
buttonyesorno = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да",callback_data="yesbutton")
        ],
        [
            InlineKeyboardButton(text="Нет",callback_data="nobutton")
                                
        ]
    ],
    resize_keyboard=True
)
# Подтверждение
confirmationyesorno = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да",callback_data="yesconfirm")
        ],
        [
            InlineKeyboardButton(text="Нет",callback_data="noconfirm")
                                
        ]
    ],
    resize_keyboard=True
)

# Фото да или нет
photoyesorno = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да",callback_data="yesphoto")
        ],
        [
            InlineKeyboardButton(text="Нет",callback_data="nophoto")
                                
        ]
    ],
    resize_keyboard=True
)


admin_id = "6355200375"

# Функция запуска рассылки
async def start_sendall(message: types.Message, state: FSMContext):
    if str(message.from_user.id) == admin_id:
        await message.answer(
            f'Здравсвтуйте <b>{message.from_user.first_name}</b>. Хотите ли вы разослать сообщение с фоткой?',
            parse_mode="HTML",
            reply_markup=photoyesorno
        )
    else:
        await message.answer("Error!")

async def process_photo_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "yesphoto":
        await callback.message.answer("Отправьте фотку")
        await state.set_state(sendall.getphoto)
    else:
        await callback.message.answer("Теперь отправьте основной текст!")
        await state.set_state(sendall.gettext)

async def get_photo2(message: types.Message, state: FSMContext):
    await state.update_data(getphoto=message.photo[-1].file_id)
    await message.answer("Теперь отправьте основной текст!")
    await state.set_state(sendall.gettext)

async def gettext123(message: types.Message, state: FSMContext):
    await state.update_data(gettext=message.text)
    await message.answer("Продолжить с кнопкой или нет?", reply_markup=buttonyesorno)

async def process_button_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "yesbutton":
        await callback.message.answer("Отправьте текст кнопки!")
        await state.set_state(sendall.getbutton)
    else:
        await send_preview(callback.message, state)

async def send_preview(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if 'getphoto' in data and data['getphoto']:
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=data['getphoto'],
            caption=data['gettext'],
            reply_markup=create_keyboard(data)
        )
    else:
        await message.answer(
            text=data['gettext'],
            reply_markup=create_keyboard(data)
        )
    await message.answer("Начинаем отправлять?", reply_markup=confirmationyesorno)

async def getbutton123(message: types.Message, state: FSMContext):
    await state.update_data(getbutton=message.text)
    await message.answer("Теперь отправьте ссылку, которую кнопка будет содержать:")
    await state.set_state(sendall.getlink)

async def getlink342(message: types.Message, state: FSMContext):
    await state.update_data(getlink=message.text)
    await send_preview(message, state)

def create_keyboard(data):
    if 'getbutton' in data and data['getbutton'] and 'getlink' in data and data['getlink']:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=data['getbutton'], url=data['getlink'])]
            ],
            resize_keyboard=True
        )
    return None

async def confirm_send(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    added_keyboards = create_keyboard(data)

    data1 = load_data()

    if 'users' not in data1:
        await callback.message.answer("Ошибка: данные не содержат информации о пользователях.")
        await state.clear()
        return
    
    # Получение списка user_ids из JSON данных
    user_ids = data1['users']

    j = 0
    for i in user_ids:
        try:
            if 'getphoto' in data and data['getphoto']:
                await bot.send_photo(
                    chat_id=i,
                    photo=data['getphoto'],
                    caption=data['gettext'],
                    reply_markup=added_keyboards
                )
            else:
                await bot.send_message(
                    chat_id=i,
                    text=data['gettext'],
                    reply_markup=added_keyboards
                )
            j += 1
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {i}: {e}")
        await asyncio.sleep(0.33)  # Используйте asyncio.sleep вместо time.sleep для асинхронного кода

    await callback.message.answer(f"Количество отправленных рассылок: {j}")
    await state.clear()




async def main() -> None:
    global users, states
    # Загрузка данных из JSON перед запуском бота
    users, states = await load_data_from_json()

    
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    
    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())