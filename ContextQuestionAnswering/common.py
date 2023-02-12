from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Бот приветствует вас. /step", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ChooseStep.first_step)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
