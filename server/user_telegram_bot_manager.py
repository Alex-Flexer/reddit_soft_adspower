import asyncio
import logging
import sys
from random import random
from secrets import token_hex

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    BotCommand
)

from functions.check_transaction import check_transaction
import database.database_functions as db


form_router = Router()

TOKEN = "8078572509:AAHT8WKFdUmViX_LC9_qRRebtsVpPxtkPN4"

BOT_COMMANDS = [
    BotCommand(command="start", description="Start bot"),
    BotCommand(command="help", description="Find out everything you need about us"),
    BotCommand(command="support", description="Contact our support team"),
    BotCommand(command="login", description="Log in your account to get more functionality"),
]

CANCEL_KEYBOARD_MARKUP =\
    ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Cancel")]],
        resize_keyboard=True
    )

MAIN_KEYBOARD_MARKUP =\
    ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Log out"),
                KeyboardButton(text="Account info"),
            ],
            [
                KeyboardButton(text="Renew Subscription"),
                KeyboardButton(text="Get Confirmation Code"),
            ]
        ],
        resize_keyboard=True,
    )

CHECKING_TRANSACTION_KEYBOARD_MARKUP =\
    ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Cancel"),
                KeyboardButton(text="Check Transaction"),
            ]
        ],
        resize_keyboard=True,
    )


class Form(StatesGroup):
    set_password = State()
    renew_subscription = State()
    confirm_code = State()


@form_router.message(CommandStart())
async def command_start(message: Message) -> None:
    res = await message.answer(
        "You are welcomed by reddit-syndicate! Some about as:\n\n"
        "Reddit Syndicate is a powerful automation tool tailored for"
        "users, businesses, and creators who want to promote their Reddit accounts.\n\n"
        "With a single software, handle millions of tasks at once—from content "
        "scheduling and posting to data gathering and community engagement."
    )


@form_router.message(Command("help"))
async def command_help(message: Message) -> None:
    await message.answer(
        "How can I help you?\n\n"
        "If you have an account please use command /login to log in. "
        "Then you will get more functionality inside the chatbot.\n\n"
        f"If you have not created your own account yet, you can do it {html.link('here', 'http://90.156.168.186:8000/sign-up')}.\n\n"
        f"Also if you have some software problem or some other questions you can contact to our support team (reddsyndicate@mail.ru)."
    )


@form_router.message(Command("support"))
async def command_support(message: Message) -> None:
    await message.answer(
        "Contact to our support team (reddsyndicate@mail.ru) "
        "if you have some software problem or some other questions."
    )


@form_router.message(Command("login"))
async def command_login(message: Message, state: FSMContext) -> None:
    username = message.from_user.username
            
    if not db.check_user_exists(username):
        await message.answer(
            f"User with username \"{username}\" does not exist"
        )
    else:
        await state.set_state(Form.set_password)
        await message.answer(
            "Please, enter your password:",
            reply_markup=CANCEL_KEYBOARD_MARKUP
        )


@form_router.message(F.text.casefold() == "get confirmation code")
async def command_get_confirmation_code(message: Message, state: FSMContext) -> None:
    is_logged_in = await state.get_value("logged_in")
    if not is_logged_in:
        await message.answer(
            "Please, firstly log in. Use command /login",
            reply_markup=ReplyKeyboardRemove()
            )
        return

    username: str = message.from_user.username
    auth_code = token_hex(16)
    db.update_email_code(username, auth_code)

    await message.answer(
        f"Your confirm code: {auth_code}"
        if db.check_user_exists(username)
        else f"User with username \"{username}\" does not exist"
    )



@form_router.message(F.text.casefold() == "cancel")
async def command_cancel(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.set_state(None)
    await message.answer(
        "Cancelled.",
        reply_markup=\
            MAIN_KEYBOARD_MARKUP if current_state == Form.renew_subscription
            else ReplyKeyboardRemove()
    )


@form_router.message(Form.set_password)
async def process_password(message: Message, state: FSMContext) -> None:
    attempts: int | None = await state.get_value("attempts")
    if attempts == 0:
        await message.answer(
            "You have entered the wrong password too many times, "
            "please contact our support.",
            reply_markup=ReplyKeyboardRemove()
            )
        return

    password: str = message.text
    username = message.from_user.username

    if attempts is None:
        attempts = 5

    if not db.check_user_password(username, password):
        attempts = attempts - 1
        if attempts > 0:
            await message.answer(
                "I'm sory, but that's an incorrect password."
                f"You have {attempts} attempts left.",
                reply_markup=CANCEL_KEYBOARD_MARKUP
                )
        else:
            await state.clear()
            await message.answer(
                "I'm sory, but that's an incorrect password."
                "You have spent all your attempts, please contact our support.",
                reply_markup=ReplyKeyboardRemove()
            )

    else:
        db.update_telegram_id(username, message.from_user.id)
        await state.update_data(logged_in=True)
        await state.set_state(None)
        await message.answer(
            "Congratulations! You have successfully logged in.",
            reply_markup=MAIN_KEYBOARD_MARKUP
        )

    await state.update_data(attempts=attempts)


@form_router.message(F.text.casefold() == "log out")
async def process_log_out(message: Message, state: FSMContext) -> None:
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.clear()
        await message.answer(
            "You are successfully logged out.",
            reply_markup=ReplyKeyboardRemove()
        )
    

@form_router.message(F.text.casefold() == "account info")
async def process_account_info(message: Message, state: FSMContext) -> None:
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        username = message.from_user.username
        if db.check_user_exists(username):
            await show_account_info(message, username)
        else:
            await message.answer(
                "You have not logged in yet.",
                reply_markup=ReplyKeyboardRemove()
            )


async def show_account_info(message: Message, email):
    user = db.get_user_by_email(email)

    await message.answer(
        f"Your username: {email},\n"
        f"Your subscription will expire on: {user.subscription_end_date}"
        if db.check_user_subscription(email)
        else "Your subscription has expired or was not activated."
    )


@form_router.message(F.text.casefold() == "renew subscription")
async def process_renew_subscription(message: Message, state: FSMContext):
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.set_state(Form.renew_subscription)
        username = message.from_user.username

        main_price =\
        299 if db.get_user_by_email(username).subscription_end_date is None\
        else 349

        current_price = main_price + round(random(), 3)
        db.update_subscription_price(username, current_price)

        crypto_token = "TMPYVBkVZj5pboTAW3VqsW29QMNq6F9Bwq"

        await message.answer(
            f"Your current subscription price: {current_price}.\n"
            f"Сrypto token for payment: {html.code(crypto_token)}.",
            reply_markup=CHECKING_TRANSACTION_KEYBOARD_MARKUP
        )


@form_router.message(F.text.casefold() == "check transaction", Form.renew_subscription)
async def process_renew_subscription(message: Message, state: FSMContext):
    await state.set_state(None)

    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    username: str = message.from_user.username
    active_price = db.get_user_active_subscription_price(username)

    wainting_message = await message.answer(
        "Transaction is being verified...\n"
        "Please wait, it won't take more than a minute.",
        reply_markup=ReplyKeyboardRemove()
    )

    try:
        transaction_verdict = await check_transaction(active_price)
        await wainting_message.delete()
    except Exception as e:
        print(e)
        await message.reply(
            "Something went wrong, contact our support.",
            reply_markup=MAIN_KEYBOARD_MARKUP
        )
    else:
        answer_text = "Transaction was not found."
        if transaction_verdict:
            answer_text = "The subscription has been successfully renewed."
            db.renew_subscription(username)

        await message.reply(
            answer_text,
            reply_markup=MAIN_KEYBOARD_MARKUP
        )


@form_router.message(default_state)
async def process_unknow_command(message: Message):
    await message.answer("Unknow command.")


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands(commands=BOT_COMMANDS)

    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout)
    asyncio.run(main())
