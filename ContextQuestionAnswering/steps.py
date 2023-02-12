from aiogram import Dispatcher, types, Bot
from ContextQuestionAnswering import tokenfile
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from deeppavlov import configs
from deeppavlov import build_model, train_model
from deeppavlov.core.common.file import read_json
import requests
from bs4 import BeautifulSoup

# available_steps = ["Вопрос к фиксированному тексту", "Ввод текста вручную", "Ввод ссылки"]
#
# model_config = read_json('squad_ru_bert_infer.json')
# model = build_model(model_config, download=True)
# print("CQA model was built")
#
# model_config_intent = read_json('intent_catcher.json')
# # model = train_model(model_config)
# # print("Model was trained")
# model_intent = build_model(model_config_intent)
# print("Intent model was built")


class ChooseStep(StatesGroup):
    first_step = State()
    waiting_for_step = State()
    waiting_for_question = State()
    waiting_for_text = State()
    waiting_for_textQ = State()
    waiting_for_link = State()
    waiting_for_linkQ = State()
    waiting_for_action = State()


async def step_choice(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_steps:
        keyboard.add(name)
    await message.answer("Выберите действие:", reply_markup=keyboard)
    await state.set_state(ChooseStep.waiting_for_step)


async def selected_step(message: types.Message, state: FSMContext):
    if message.text not in available_steps:
        await message.answer("Введите действие со встроенного меню")
        return
    if message.text == available_steps[0]:
        await state.set_state(ChooseStep.waiting_for_question)
        await message.answer("Введите вопрос к фиксированному тексту:")
    elif message.text == available_steps[1]:
        await state.set_state(ChooseStep.waiting_for_text)
        await message.answer("Введите текст:")
    elif message.text == available_steps[2]:
        await state.set_state(ChooseStep.waiting_for_link)
        await message.answer("Введите ссылку:")


async def fixed_question(message: types.Message, state: FSMContext):
    print("fixed question")
    context_file = open("textFile.txt", encoding="utf8")
    context = context_file.read()
    question = message.text
    answer = model([context], [question])
    if answer[0] == ['']:
        await message.reply("Ответ не найден")
        await state.set_state(ChooseStep.waiting_for_question)
    await message.answer(''.join(answer[0]).capitalize())


async def process_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await state.set_state(ChooseStep.waiting_for_textQ)
    await message.answer("Контекст установлен")
    await message.answer("Введите вопрос:")


async def input_text(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['question'] = message.text
    context = await state.get_data()
    context = context['text']
    question = await state.get_data()
    question = question['question']
    answer = model([context], [question])
    if answer[0] == ['']:
        await message.reply("Ответ не найден")
        await state.set_state(ChooseStep.waiting_for_textQ)
    await message.answer(''.join(answer[0]).capitalize())


async def parse_html(base_url):
    response = requests.get(base_url)
    if response.status_code == 200:
        print('Success')
    elif response.status_code == 404:
        print('Not Found')
    soup = BeautifulSoup(response.content, "html.parser")
    html_text = soup.text
    return html_text


async def process_link(message: types.Message, state:FSMContext):
    link = await parse_html(message.text)
    async with state.proxy() as data:
        data['link_text'] = link
    await message.answer("Ссылка принята")
    await state.set_state(ChooseStep.waiting_for_linkQ)
    await message.answer("Введите вопрос:")


async def input_link(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['link_question'] = message.text
    context = await state.get_data()
    context = context['link_text']
    question = await state.get_data()
    question = question['link_question']
    answer = model([context], [question])
    if answer[0] == ['']:
        await message.reply("Ответ не найден")
        await state.set_state(ChooseStep.waiting_for_linkQ)
    await message.answer(''.join(answer[0]).capitalize())

async def intent_choice(message: types.Message, state:FSMContext):
    intent_result = model_intent([message.text])
    if intent_result[0] == 'question':
        await message.answer(''.join(intent_result[0]).capitalize())
        await message.answer("Turn to CQA model")

        await message.answer("Введите вопрос к фиксированному тексту:")
        await state.set_state(ChooseStep.waiting_for_question)
        print("cqa")
    elif intent_result[0] == 'repeat':
        await message.answer(''.join(intent_result[0]).capitalize())
        await message.answer("Mona Lisa by Leonardo Da'Vinchi:")
        await message.answer_sticker("CAACAgIAAxkBAAEG9o5jpZQjGVT6tPCBCNXlroJpZkQK9QAC8hIAAvGjoEjaFvOOIdoTMCwE")
    elif intent_result[0] == 'tell_me_more':
        await message.answer(''.join(intent_result[0]).capitalize())
        await message.answer("Information:")
        await message.answer("This bot was created for Artificial Intelligence Systems by Renata Akhmetzyanova, group №09-952")
    else:
        await message.reply("I do not understand you")



def register_handlers_steps(dp: Dispatcher):
    dp.register_message_handler(intent_choice, commands="intent", state=ChooseStep.first_step)
    # dp.register_message_handler(step_choice, state=ChooseStep.first_step)
    dp.register_message_handler(selected_step, state=ChooseStep.waiting_for_step)
    dp.register_message_handler(fixed_question, state=ChooseStep.waiting_for_question)
    dp.register_message_handler(input_text, state=ChooseStep.waiting_for_textQ)
    dp.register_message_handler(process_text, state=ChooseStep.waiting_for_text)
    dp.register_message_handler(input_link, state=ChooseStep.waiting_for_linkQ)
    dp.register_message_handler(process_link, state=ChooseStep.waiting_for_link)
