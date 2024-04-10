from aiogram import Bot
from aiogram import Dispatcher
from aiogram import executor
from aiogram.utils import deep_linking
#from aiogram.utils import executor

from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import CallbackQuery
from aiogram.types import Message
from json import dumps
from json import loads
from json import load
import sys
import os
import db
import config
import json
import pandas as pd
import logging


#questions = os.path.dirname(sys.argv[0])
#with open(os.path.join(questions, 'questions.json'), 'rt') as jsonfile:
    #data = json.load(jsonfile)
    
questions = load(open("questions.json", "r", encoding="utf-8"))
#questions = load(open("C:\Users\ACER\Desktop\Einstein_IQ_Bot-master\bot.py", "r", encoding="utf-8"))
#"C:\Users\ACER\Desktop\Einstein_IQ_Bot-master\bot.py"
#bot = Bot(token=config.TOKEN) #Ваш токен
bot = Bot(token='6806372479:AAHTiIRPU6zFdXlZhpm9mg4bW-e_3kHe3p8')
#dp = Dispatcher(bot=bot)
dp = Dispatcher(bot)

#questions = load(open("questions.json", "r", encoding="utf-8"))


def compose_markup(question: int):
    km = InlineKeyboardMarkup(row_width=3)
    for i in range(len(questions[question]["variants"])):
        cd = {
            "question": question,
            "answer": i
        }
        km.insert(InlineKeyboardButton(questions[question]["variants"][i], callback_data=dumps(cd)))
    return km


def reset(uid: int):
    db.set_in_process(uid, False)
    db.change_questions_passed(uid, 0)
    db.change_questions_message(uid, 0)
    db.change_current_question(uid, 0)


@dp.callback_query_handler(lambda c: True)
async def answer_handler(callback: CallbackQuery):
    data = loads(callback.data)
    q = data["question"]
    is_correct = questions[q]["correct_answer"] - 1 == data["answer"]
    passed = db.get_questions_passed(callback.from_user.id)
    msg = db.get_questions_message(callback.from_user.id)
    if is_correct:
        passed += 1
        db.change_questions_passed(callback.from_user.id, passed)
    if q + 1 > len(questions) - 1:
        reset(callback.from_user.id)
        await bot.delete_message(callback.from_user.id, msg)
        await bot.send_message(
            callback.from_user.id,
            f"🎉 *Ура*, вы прошли этот тест\\!\n\n🔒 В любом случает\\, тест завершен\\.\n✅ Правильных ответов\\: *{passed} з {len(questions)}*\\.\n\n🔄 *Пройти тест снова* \\- /play", parse_mode="MarkdownV2"
        )
        return
    await bot.edit_message_text(
        questions[q + 1]["text"],
        callback.from_user.id,
        msg,
        reply_markup=compose_markup(q + 1),
        parse_mode="MarkdownV2"
    )


@dp.message_handler(commands=["play"])
async def go_handler(message: Message):
    if not db.is_exists(message.from_user.id):
        db.add(message.from_user.id)
    if db.is_in_process(message.from_user.id):
        await bot.send_message(message.from_user.id, "🚫 Вы не можете начать тест, потому что *вы уже его проходите*\\.", parse_mode="MarkdownV2")
        return
    db.set_in_process(message.from_user.id, True)
    msg = await bot.send_message(
        message.from_user.id,
        questions[0]["text"],
        reply_markup=compose_markup(0),
        parse_mode="MarkdownV2"
    )
    db.change_questions_message(message.from_user.id, msg.message_id)
    db.change_current_question(message.from_user.id, 0)
    db.change_questions_passed(message.from_user.id, 0)


@dp.message_handler(commands=["finish"])
async def quit_handler(message: Message):
    if not db.is_in_process(message.from_user.id):
        await bot.send_message(message.from_user.id, "❗️Вы еще *не начали тест*\\.", parse_mode="MarkdownV2")
        return
    reset(message.from_user.id)
    await bot.send_message(message.from_user.id, "✅ Вы успешно *закончили тест*\\.", parse_mode="MarkdownV2")


@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.answer("👋 *Привет\\!* \n🧠 *Предлагаю проверить ваше логическое мышление\\.*\n\n📝 Необходимо будет ответить на *15 вопросов*\\. \n⏱ Если будете думать как следует, что я рекомендую, тест займет *около 10 минут*\\. \n\n⁉️ *Каждый вопрос* — логичное условие, в соответствии с ситуацией\\. \n📄 Для каждого условия я предлагаю *несколько вариантов ответов*, в соответствии с логикой\\. \n\n⁉️ Правильным является *только один* ответ, его вам и требуется выбрать\\. \n🔍 Постарайтесь *абстрагироваться от реального мира* и принимать решения, основываясь только на этих условиях\\.\n\n*Начать тест* \\- /play\n*Закончить тест* \\- /finish\n*Техническая поддержка* \\- /help", parse_mode="MarkdownV2")


@dp.message_handler(commands=['help'])
async def cmd_answer(message: Message):
    await message.answer("⁉️<b> Если у вас есть проблемы.</b> \n✉️ <b>Напишите мне</b> <a href='https://t.me/igo791820'>@igo791820</a><b>.</b>", disable_web_page_preview=True, parse_mode="HTML")
    

def main() -> None:
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
