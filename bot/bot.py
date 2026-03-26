import sys
import asyncio

from handlers.commands.commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_message,
)


def run_test(command: str) -> None:
    """Run a command in test mode and print result to stdout."""
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

    if cmd.startswith("/"):
        handlers = {
            "/start": lambda: handle_start(),
            "/help": lambda: handle_help(),
            "/health": lambda: handle_health(),
            "/labs": lambda: handle_labs(),
            "/scores": lambda: handle_scores(arg),
        }
        if cmd in handlers:
            print(handlers[cmd]())
        else:
            print(f"Unknown command: {cmd}\nUse /help to see available commands.")
    else:
        # Plain text — route via LLM
        print(handle_message(command))


async def run_bot() -> None:
    from aiogram import Bot, Dispatcher, F
    from aiogram.filters import Command
    from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
    import config

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    def start_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Health", callback_data="cmd_health"),
                InlineKeyboardButton(text="📚 Labs", callback_data="cmd_labs"),
            ],
            [
                InlineKeyboardButton(text="🏆 Top students lab-04", callback_data="query_top"),
                InlineKeyboardButton(text="📉 Lowest pass rate", callback_data="query_lowest"),
            ],
        ])

    @dp.message(Command("start"))
    async def cmd_start(message: Message) -> None:
        await message.answer(handle_start(), reply_markup=start_keyboard())

    @dp.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        await message.answer(handle_help())

    @dp.message(Command("health"))
    async def cmd_health(message: Message) -> None:
        await message.answer(handle_health())

    @dp.message(Command("labs"))
    async def cmd_labs(message: Message) -> None:
        await message.answer(handle_labs())

    @dp.message(Command("scores"))
    async def cmd_scores(message: Message) -> None:
        arg = ""
        if message.text:
            parts = message.text.split(maxsplit=1)
            arg = parts[1] if len(parts) > 1 else ""
        await message.answer(handle_scores(arg))

    @dp.callback_query(F.data == "cmd_health")
    async def cb_health(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(handle_health())

    @dp.callback_query(F.data == "cmd_labs")
    async def cb_labs(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(handle_labs())

    @dp.callback_query(F.data == "query_top")
    async def cb_top(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(handle_message("who are the top 5 students in lab-04?"))

    @dp.callback_query(F.data == "query_lowest")
    async def cb_lowest(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(handle_message("which lab has the lowest pass rate?"))

    @dp.message(F.text)
    async def handle_text(message: Message) -> None:
        if message.text and not message.text.startswith("/"):
            response = handle_message(message.text)
            await message.answer(response)

    await dp.start_polling(bot)


if __name__ == "__main__":
    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        command = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "/help"
        run_test(command)
    else:
        asyncio.run(run_bot())
