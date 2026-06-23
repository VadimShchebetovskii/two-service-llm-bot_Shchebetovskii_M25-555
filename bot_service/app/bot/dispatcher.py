from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.core.config import settings
from app.bot.handlers import router


_bot: Bot | None = None
_dispatcher: Dispatcher | None = None


def get_bot() -> Bot:
    """Возвращает экземпляр бота (синглтон)."""

    global _bot
    if _bot is None:
        _bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    return _bot


def get_dispatcher() -> Dispatcher:
    """Возвращает экземпляр диспетчера с зарегистрированными обработчиками (синглтон)."""

    global _dispatcher
    if _dispatcher is None:
        _dispatcher = Dispatcher()
        _dispatcher.include_router(router)
    
    return _dispatcher


async def start_polling() -> None:
    """Запускает поллинг бота."""

    bot = get_bot()
    dispatcher = get_dispatcher()
    await dispatcher.start_polling(bot)


async def stop_polling() -> None:
    """Останавливает поллинг бота и закрывает сессию."""

    bot = get_bot()
    await bot.session.close()
