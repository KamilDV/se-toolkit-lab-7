import sys
import asyncio

from handlers.commands.commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)


def run_test(command: str) -> None:
    """Run a command in test mode and print result to stdout."""
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

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
        print(f"Unknown command: {cmd}")


async def run_bot() -> None:
    from aiogram import Bot, Dispatcher
    from aiogram.filters import Command
    from aiogram.types import Message
    import config

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: Message) -> None:
        await message.answer(handle_start())

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

    await dp.start_polling(bot)


if __name__ == "__main__":
    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        command = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "/help"
        run_test(command)
    else:
        asyncio.run(run_bot())
