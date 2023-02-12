import asyncio
import logging
import multiprocessing
from multiprocessing import Process
from ContextQuestionAnswering import tokenfile
from ContextQuestionAnswering.common import register_handlers_common
from intent_steps import register_handler_intent_steps
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from deeppavlov import build_model, train_model, configs
from deeppavlov.core.common.file import read_json

logger = logging.getLogger(__name__)
bot = Bot(tokenfile.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# while True:
#     msg = input()
#     print(model([msg, msg]))

# def handle_question(message):
#     question = message.text
#     print(question)
#     reply = model(["question"])
#     if len(reply) > 0 and reply[0][0].strip() != "":
#         bot.send_message()

async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    # Регистрация хэндлеров
    register_handlers_common(dp)
    register_handler_intent_steps(dp)

    # Запуск поллинга
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())