import asyncio
import logging
import sys
import httpx
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
BACKEND = os.getenv("BACKEND")

# FSM для регистрации
class RegistrationStates(StatesGroup):
    full_name = State()
    group = State()
    photo = State()
    wishes = State()

dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user_id = str(message.from_user.id)
    user_name = message.from_user.full_name
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND}/user/{user_id}")
            
            if response.status_code == 200:
                user_data = response.json()
                user = user_data['user']
                
                if user.get('reciver_id') and user.get('reciver'):
                    recipient = user['reciver']
                    notification_text = (
                        f"🎅 Тайный Санта уже начался!\n\n"
                        f"🎁 Ваш подопечный:\n"
                        f"👤 Имя: {recipient.get('name', 'Неизвестно')}\n"
                        f"👤 Фамилия: {recipient.get('surname', 'Неизвестно')}\n"
                        f"� Telegram: @{recipient.get('telegram_name', 'нет_юзернейма')}\n"
                        f"� Группа: {recipient.get('group', 'Неизвестно')}\n"
                        f"💭 Пожелания: {recipient.get('wishes', 'Нет пожеланий')}\n\n"
                        f"🤫 Помните: это тайна! Не рассказывайте кому, дарите подарок!\n\n"
                        f"📅 Дедлайн: 1 декабря"
                    )
                 
                    if recipient.get("photo"):
                        await message.answer_photo(
                            recipient["photo"],
                            caption=notification_text
                        )
                    else:
                        await message.answer(notification_text)
                else:
                   
                    await message.answer(
                        f"🎅 Распределение Тайного Санты состоится 1 декабря!\n"
                        f"🎁 Ожидайте сообщений о вашем подопечном!"
                    )
            elif response.status_code == 404:
                await message.answer(
                    f"Привет, мой друг, время нам познакомиться! \n" 
                    "Пожалуйста, введите ваше имя и фамилию через пробел:"
                )
                await state.set_state(RegistrationStates.full_name)
            else:
                await message.answer("Sorry, there was an error checking your account. Please try again later.")
                
        except httpx.RequestError:
            await message.answer(
                f"Hello, {html.bold(user_name)}! \n"
                "Backend service is currently unavailable. Please try again later."
            )


@dp.message(RegistrationStates.full_name)
async def process_full_name(message: Message, state: FSMContext) -> None:
    full_name = message.text.strip()
    
    parts = full_name.split()
    if len(parts) < 2:
        await message.answer(
            "Пожалуйста, введите имя и фамилию через пробел.\n"
            "Например: Иван Иванов"
        )
        return  
    
    name = parts[0]
    surname = " ".join(parts[1:])  
    
    await state.update_data(name=name, surname=surname, full_name=full_name)
    await message.answer(
        "Хорошо! Теперь введите номер вашей группы:\n\n"
        "📚 Пример формата: 15.14Д-ГГ01/25б"
    )
    await state.set_state(RegistrationStates.group)


@dp.message(RegistrationStates.group)
async def process_group(message: Message, state: FSMContext) -> None:
    await state.update_data(group=message.text)
    await message.answer(
        "Отлично! Теперь отправьте свою фотографию:\n\n"
        "📸 Пожалуйста, загрузите фото, чтобы другие участники могли узнать вас лучше!"
    )
    await state.set_state(RegistrationStates.photo)


@dp.message(RegistrationStates.photo, F.photo)
async def process_photo(message: Message, state: FSMContext) -> None:
    photo = message.photo[-1]
    file_id = photo.file_id
    
    await state.update_data(photo=file_id)
    await message.answer("Фото получено! Напишите ваши пожелания (если нет пожеланий, напишите '-' ):")
    await state.set_state(RegistrationStates.wishes)


@dp.message(RegistrationStates.photo)
async def process_photo_invalid(message: Message) -> None:
    await message.answer("Пожалуйста, отправьте фотографию, а не текст или другие файлы.")


@dp.message(RegistrationStates.wishes)
async def process_wishes(message: Message, state: FSMContext) -> None:
    user_data = await state.update_data(wishes=message.text)
    user_id = str(message.from_user.id)
    
    async with httpx.AsyncClient() as client:
        try:
            user_payload = {
                "telegram_id": user_id,
                "telegram_name": message.from_user.username if message.from_user.username else "",
                "name": user_data["name"],
                "surname": user_data["surname"],
                "group": user_data["group"],
                "wishes": user_data["wishes"],
                "photo": user_data.get("photo", "")
            }
            
            response = await client.post(f"{BACKEND}/user", json=user_payload)
            
            if response.status_code == 201:
             
                confirmation_text = (
                    f"🎉 Поздравляю, {html.bold(user_data['full_name'])}! Вы успешно зарегистрированы!\n\n"
                    f"📋 Ваши данные:\n"
                    f"👤 Имя: {user_data['name']}\n"
                    f"👤 Фамилия: {user_data['surname']}\n"
                    f"📚 Группа: {user_data['group']}\n"
                    f"💭 Пожелания: {user_data['wishes']}\n\n"
                    f"🎅 Распределение Тайного Санты состоится 1 декабря!"
                )
                
               
                if user_data.get("photo"):
                    await message.answer_photo(
                        user_data["photo"],
                        caption=confirmation_text
                    )
                else:
                    await message.answer(confirmation_text)
            else:
                await message.answer("Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")
                
        except httpx.RequestError:
            await message.answer("Бэкэнд недоступен. Попробуйте зарегистрироваться позже.")
    
    await state.clear()


@dp.message(Command("startGame"))
async def command_start_game_handler(message: Message) -> None:
    user_id = str(message.from_user.id)
    
    async with httpx.AsyncClient() as client:
        try:
            admin_response = await client.get(f"{BACKEND}/user/admin/{user_id}")
            if admin_response.status_code != 200:
                await message.answer("Только администратор может запустить игру!")
                return
        except httpx.RequestError:
            await message.answer("Ошибка проверки прав администратора. Попробуйте позже.")
            return
    
        
        try:
            response = await client.post(f"{BACKEND}/utils/assign-secret-santas")
            if response.status_code != 200:
                await message.answer("Ошибка при распределении игроков. Попробуйте позже.")
                return
                
            
            users_response = await client.get(f"{BACKEND}/user")
            if users_response.status_code == 200:
                users_data = users_response.json()
                
                for user in users_data.get("users", []):
                    if user.get("reciver"):  
                        telegram_id = user.get("telegram_id")
                        recipient = user.get("reciver")
                    
                        notification_text = (
                            f"🎅 Тайный Санта начался!\n\n"
                            f"🎁 Ваш подопечный:\n"
                            f"👤 Имя: {recipient.get('name', 'Неизвестно')}\n"
                            f"👤 Фамилия: {recipient.get('surname', 'Неизвестно')}\n"
                            f"📱 Telegram: @{recipient.get('telegram_name', 'нет_юзернейма')}\n"
                            f"📚 Группа: {recipient.get('group', 'Неизвестно')}\n"
                            f"💭 Пожелания: {recipient.get('wishes', 'Нет пожеланий')}\n\n"
                            f"🤫 Помните: это тайна! Не рассказывайте кому дарите подарок!\n\n"
                            f"📅 Дедлайн: 1 декабря"
                        )
                        
                        try:
                            if recipient.get("photo"):
                                await message.bot.send_photo(
                                    chat_id=telegram_id,
                                    photo=recipient["photo"],
                                    caption=notification_text
                                )
                            else:
                                await message.bot.send_message(
                                    chat_id=telegram_id,
                                    text=notification_text
                                )
                        except Exception as e:
                            print(f"Failed to send message to {telegram_id}: {e}")
                
                await message.answer("🎉 Тайный Санта успешно запущен! Все участники уведомлены о своих подопечных.")
                
            else:
                await message.answer("Ошибка при получении списка игроков.")
                
        except httpx.RequestError:
            await message.answer("Ошибка подключения к бэкенду. Попробуйте позже.")




async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
