import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from keyboards.set_menu import set_main_menu
from middlewares.user_middleware import UserMiddleware, BotMiddleware
from handlers import start_handler
from handlers import admin_handler
from handlers import quiz_handler
from handlers import menu_handler
from services.database import init_models
from aiogram.fsm.storage.redis import RedisStorage, Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

logging.basicConfig(level=logging.DEBUG)

bot: Bot

async def main() -> None:
    config: Config = load_config()
    engine = create_async_engine(url=config.db, echo=True)
    await init_models(engine)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    redis_db = Redis(host=config.redis_host)
    redis_storage = RedisStorage(redis=redis_db)
    bot = Bot(token=config.tg_bot.token,
                   parse_mode='HTML')
    dp: Dispatcher = Dispatcher(storage=redis_storage)
    quiz_handler.router.message.middleware(UserMiddleware(session_maker))
    quiz_handler.router.callback_query.middleware(UserMiddleware(session_maker))
    quiz_handler.router.callback_query.middleware(BotMiddleware(bot))
    start_handler.router.message.middleware(UserMiddleware(session_maker))
    start_handler.router.callback_query.middleware(UserMiddleware(session_maker))
    start_handler.router.callback_query.middleware(BotMiddleware(bot))
    admin_handler.router.message.middleware(UserMiddleware(session_maker))
    admin_handler.router.callback_query.middleware(UserMiddleware(session_maker))
    admin_handler.router.callback_query.middleware(BotMiddleware(bot))
    menu_handler.router.message.middleware(UserMiddleware(session_maker))
    menu_handler.router.callback_query.middleware(UserMiddleware(session_maker))
    menu_handler.router.callback_query.middleware(BotMiddleware(bot))
    dp.include_router(start_handler.router)
    dp.include_router(quiz_handler.router)
    dp.include_router(menu_handler.router)
    dp.include_router(admin_handler.router)
    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
