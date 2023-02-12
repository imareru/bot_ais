import asyncio
import logging
# import multiprocessing
# from multiprocessing import Process
from ContextQuestionAnswering import tokenfile
from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from deeppavlov import configs
from deeppavlov import build_model, train_model
from deeppavlov.core.common.file import read_json

logger = logging.getLogger(__name__)
bot = Bot(tokenfile.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

available_steps = ["Вопрос к фиксированному тексту", "Ввод текста вручную", "Ввод ссылки"]

model_config = read_json('squad_ru_bert_infer.json')
model = build_model(model_config, download=True)
print("CQA model was built")
#
model_config_intent = read_json('intent_catcher.json')
model_intent = build_model(model_config_intent)
print("Intent model was built")


# model_intent = train_model(model_config_intent)
# print("Model was trained")

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/step", description="Выберите действие"),
        BotCommand(command="/start", description="start")
    ]
    await bot.set_my_commands(commands)

class ChooseStep(StatesGroup):
    first_step = State()
    waiting_for_step = State()
    waiting_for_question = State()
    waiting_for_text = State()
    waiting_for_textQ = State()
    waiting_for_link = State()
    waiting_for_linkQ = State()
    waiting_for_action = State()

@dp.message_handler(commands="step")
async def step_choice(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_steps:
        keyboard.add(name)
    await message.answer("Выберите действие:", reply_markup=keyboard)
    await state.set_state(ChooseStep.waiting_for_step)


@dp.message_handler(state=ChooseStep.waiting_for_step)
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

@dp.message_handler(state=ChooseStep.waiting_for_question)
async def fixed_question(message: types.Message, state: FSMContext):
    print("fixed question")
    context_file = open("textFile.txt", encoding="utf8")
    context = context_file.read()
    question = message.text
    answer = model([context], [question])
    if answer[0] == ['']:
        await message.reply("Answer was not found")
        await state.set_state(ChooseStep.waiting_for_question)
    await message.answer(''.join(answer[0]).capitalize())
    await state.set_state(ChooseStep.first_step)

@dp.message_handler(state=ChooseStep.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    print("jsbcjl")
    async with state.proxy() as data:
        data['text'] = message.text
    await state.set_state(ChooseStep.waiting_for_textQ)
    await message.answer("Context is set")
    await message.answer("Ask a question:")

@dp.message_handler(state=ChooseStep.waiting_for_textQ)
async def input_text(message: types.Message, state:FSMContext):
    print("def input_text")
    async with state.proxy() as data:
        data['question'] = message.text
    context = await state.get_data()
    context = context['text']
    question = await state.get_data()
    question = question['question']
    answer = model([context], [question])
    if answer[0] == ['']:
        await message.reply("Answer was not found")
        await state.set_state(ChooseStep.waiting_for_textQ)
    await message.answer(''.join(answer[0]).capitalize())
    await state.set_state(ChooseStep.first_step)

async def parse_html(base_url):
    print("parse_html def")
    # response = requests.get(base_url)
    # if response.status_code == 200:
    #     print('Success')
    # elif response.status_code == 404:
    #     print('Not Found')
    # soup = BeautifulSoup(response.content, "html.parser")
    # html_text = soup.text
    # return html_text

@dp.message_handler(state=ChooseStep.waiting_for_link)
async def process_link(message: types.Message, state:FSMContext):
    print("process_link def")
    # link = await parse_html(message.text)
    # async with state.proxy() as data:
    #     data['link_text'] = link
    # await message.answer("Ссылка принята")
    # await state.set_state(ChooseStep.waiting_for_linkQ)
    # await message.answer("Введите вопрос:")

@dp.message_handler(state=ChooseStep.waiting_for_linkQ)
async def input_link(message:types.Message, state:FSMContext):
    print("input_link def")
    # async with state.proxy() as data:
    #     data['link_question'] = message.text
    # context = await state.get_data()
    # context = context['link_text']
    # question = await state.get_data()
    # question = question['link_question']
    # answer = model([context], [question])
    # if answer[0] == ['']:
    #     await message.reply("Ответ не найден")
    #     await state.set_state(ChooseStep.waiting_for_linkQ)
    # await message.answer(''.join(answer[0]).capitalize())

@dp.message_handler(state=ChooseStep.first_step)
async def intent_choice(message: types.Message, state:FSMContext):
    print("intent_choice def", message.text)
    intent_result = model_intent([message.text])
    # queue.put(message.text)
    # intent_result = queue.get()
    print("Message:", message.text)
    print("Intent:", intent_result[0])
    if intent_result[0] == 'question':
        # await message.answer(''.join(intent_result[0]).capitalize())
        await message.answer("Turn to CQA model")
        await state.set_state(ChooseStep.waiting_for_question)
        await message.answer("Input a question for fixed text:")
    elif intent_result[0] == 'sticker':
        # await message.answer(''.join(intent_result[0]).capitalize())
        await message.answer("Mona Lisa by Leonardo Da'Vinchi:")
        await message.answer_sticker("CAACAgIAAxkBAAEG9o5jpZQjGVT6tPCBCNXlroJpZkQK9QAC8hIAAvGjoEjaFvOOIdoTMCwE")
        await state.set_state(ChooseStep.first_step)
    elif intent_result[0] == 'tell_me_more':
        # await message.answer(''.join(intent_result[0]).capitalize())
        await message.answer("Information:"
                             "This bot was created for Artificial Intelligence Systems by Renata Akhmetzyanova, group №09-952")
        await state.set_state(ChooseStep.first_step)
    elif intent_result[0] == 'input_text':
        await message.answer("Turn to CQA model")
        await message.answer("Send me text")
        await state.set_state(ChooseStep.waiting_for_text)
    else:
        await message.reply("I do not understand you")

@dp.message_handler(state="*", commands=['start', 'reset'])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer("Бот приветствует вас. /step", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ChooseStep.first_step)


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    await dp.start_polling()


if __name__ == '__main__':
    # queue = multiprocessing.Queue()
    # child_process = Process(target=work_with_intent, args=(queue,))
    # child_process.start()
    # queue.get()
    asyncio.run(main())
