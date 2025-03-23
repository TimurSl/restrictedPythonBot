import asyncio
import io
import os
import sys
import traceback
import html
from types import MappingProxyType

import dotenv
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import safe_builtins
from limits import limited_builtins
from RestrictedPython.PrintCollector import PrintCollector
from RestrictedPython.Eval import default_guarded_getiter
from RestrictedPython.Guards import guarded_iter_unpack_sequence

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

dotenv.load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

dp = Dispatcher()

output_buffer = io.StringIO()
original_stdout = sys.stdout

def exec_restricted(user_code: str) -> str:
    try:
        user_code += "\nresult = printed"
        sys.stdout = output_buffer
        byte_code = compile_restricted(user_code, "<string>", "exec")

        builtins = dict(safe_builtins)
        builtins.__delitem__("range")
        builtins.update(limited_builtins)
        builtins = MappingProxyType(builtins)

        globals_dict = {
            '__builtins__': builtins,
            '_print_': PrintCollector,
            '_getattr_': getattr,
            '_write_': lambda x: x,
            '_getiter_': default_guarded_getiter,
            '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
            '__name__': '__main__',
        }

        locals_dict = {}
        exec(byte_code, globals_dict, locals_dict)

        result = locals_dict.get("result", None)


        return result or "Код выполнен без вывода."

    except Exception:
        return traceback.format_exc()





@dp.message(Command("exec"))
async def exec_handler(message: types.Message):
    parts = message.text.split('\n', 1)
    if len(parts) < 2 or not parts[1].strip():
        await message.reply("Пожалуйста, напиши код на следующей строке после /exec")
        return

    code = parts[1].strip()
    result = exec_restricted(code)
    escaped_result = html.escape(result)  # Экранируем HTML-символы
    await message.reply(f"<b>Результат:</b>\n<pre>{escaped_result}</pre>", parse_mode="HTML")

async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
