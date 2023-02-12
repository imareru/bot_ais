from deeppavlov import build_model, train_model
from deeppavlov.core.common.file import read_json
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Dispatcher, types, Bot


# model_config = read_json('squad_ru_bert_infer.json')
# model = build_model(model_config, download=True)
# print("CQA model was built")

model_config_intent = read_json('intent_catcher.json')
# model = train_model(model_config)
# print("Model was trained")
model_intent = build_model(model_config_intent)
print("Intent model was built")

class ChooseStep(StatesGroup):
    waiting_for_question = State()

async def intent_choice(message: types.Message, state:FSMContext):
    intent_result = model_intent([message.text])
    if intent_result[0] == 'question':
        await message.answer(intent_result[0])
        # await state.set_state(ChooseStep.waiting_for_question)
        await message.answer("Введите вопрос к фиксированному тексту:")
    elif intent_result[0] == 'repeat':
        await message.answer(intent_result[0])
        await message.answer_sticker("CAACAgIAAxkBAAEG9kVjpY5tiwid2uvI4HCQd2_F-ionywACVh0AAtwgGUu3V_QUT-LlPywE")
    elif intent_result[0] == 'tell_me_more':
        await message.answer(intent_result[0])
        await message.answer("Information:")
        await message.answer("This bot was created for Artificial Intelligence Systems by Renata Akhmetzyanova, group №09-952")
    else:
        await message.reply("I do not understand you")


async def fixed_question(message: types.Message, state:FSMContext):
    await message.answer("Next step with fixed text")
    context_file = open("textFile.txt", encoding="utf8")
    context = context_file.read()
    question = message.text
    answer = model([context], [question])
    if answer[0] == ['']:
        await message.reply("Answer was not found")
        await state.set_state(ChooseStep.waiting_for_question)
    await message.answer(''.join(answer[0]).capitalize())



def register_handler_intent_steps(dp: Dispatcher):
    dp.register_message_handler(intent_choice, state="*")
    dp.register_message_handler(fixed_question, state=ChooseStep.waiting_for_question)
