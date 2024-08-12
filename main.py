import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
import sqlite3
from config import TOKEN
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
import logging
from googletrans import Translator

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup): # эти состояния используются для сохранения данных в базу данных
    name = State()
    age = State()
    university = State()
    facultet = State()

def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL, 
    age INTEGER NOT NULL, 
    university TEXT NOT NULL,
    facultet TEXT NOT NULL)
    ''')
    conn.commit()
    conn.close()

init_db()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(f"Привет, как тебя зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный возраст (целое число).")
        return
    await state.update_data(age=message.text)
    await message.answer(f"Где ты учишься?")
    await state.set_state(Form.university)

@dp.message(Form.university)
async def university(message: Message, state: FSMContext):
    await state.update_data(university=message.text)
    await message.answer(f"На каком факультете?")
    await state.set_state(Form.facultet)

@dp.message(Form.facultet)
async def facultet(message: Message, state: FSMContext):
    await state.update_data(facultet=message.text)
    user_data = await state.get_data()

    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO students (name, age, university, facultet) VALUES (?, ?, ?, ?)", (user_data['name'], user_data['age'], user_data['university'], user_data['facultet']))
    conn.commit()
    conn.close()

    await message.answer(f"Ваши данные сохранены!\n"
                         f"Имя: {user_data['name']}\n"
                         f"Возраст: {user_data['age']}\n"
                         f"ВУЗ: {user_data['university']}\n"
                         f"Факультет: {user_data['facultet']}")




async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())