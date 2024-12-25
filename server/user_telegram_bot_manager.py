import asyncio
import logging
import sys
from datetime import date
from random import random, choice
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
                KeyboardButton(text="Subscriptions Manager"),
            ],
            [
                KeyboardButton(text="Account Info"),
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

ADDING_ACCOUNT_KEYBOARD_MARKUP =\
    ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Cancel"),
            ]
        ],
        resize_keyboard=True,
    )

ADDING_ACCOUNT_KEYBOARD_MARKUP =\
    ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Cancel"),
            ]
        ],
        resize_keyboard=True,
    )

SUBSCRIPTIONS_MANAGER_KEYBOARD_MARKUP =\
    ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Add account"),
                KeyboardButton(text="Delete account"),
            ],
            [
                KeyboardButton(text="Check my accounts"),
                KeyboardButton(text="Check my subscriptions"),

            ],
            [
                KeyboardButton(text="Buy a subscription"),
            ],
            [
                KeyboardButton(text="Home"),
            ]
        ],
        resize_keyboard=True,
    )


class Form(StatesGroup):
    confirm_password = State()
    set_amount_accounts = State()
    check_transaction = State()
    add_account = State()
    delete_account = State()


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
        await state.set_state(Form.confirm_password)
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
        f"Your confirm code: {html.code(auth_code)}"
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
            SUBSCRIPTIONS_MANAGER_KEYBOARD_MARKUP
            if (current_state in {Form.set_amount_accounts, Form.check_transaction, Form.add_account, Form.delete_account})
            else ReplyKeyboardRemove()
    )


@form_router.message(Form.confirm_password)
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
        await state.update_data(logged_in=True)
        await state.set_state(None)
        await message.answer(
            "Congratulations! You have successfully logged in.",
            reply_markup=MAIN_KEYBOARD_MARKUP
        )

    await state.update_data(attempts=attempts)
    

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
    summary_amount_accounts = 0
    subscriptions = db.get_subscriptions(email)
    for sub in subscriptions:
        summary_amount_accounts += sub.amount_accounts_limit

    amount_active_accounts = db.get_amount_active_reddit_acounts(email)
    amount_free_accounts = summary_amount_accounts - amount_active_accounts

    answer_text =\
        f"Your username: {email};\n" +\
        f"You have {amount_active_accounts} active accounts;\n" +\
        (
            "You have reached the limit for adding accounts."
            if amount_free_accounts <= 0
            else f"You can add {amount_free_accounts} more accounts."
        )

    await message.answer(answer_text)


@form_router.message(F.text.casefold() == "subscriptions manager")
async def process_subscriptions_manager(message: Message, state: FSMContext):
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "What would you like to do?",
            reply_markup=SUBSCRIPTIONS_MANAGER_KEYBOARD_MARKUP
        )

@form_router.message(F.text.casefold() == "home")
async def process_home(message: Message, state: FSMContext):
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            choice(["Good there where we are not.",
             "There's no place like home.",
             "East or west, home is best",
             "Home sweet home."]),
            reply_markup=MAIN_KEYBOARD_MARKUP
        )


@form_router.message(F.text.casefold() == "buy a subscription")
async def process_buy_accounts(message: Message, state: FSMContext):
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text="Enter the number of accounts you want to buy:",
            reply_markup=ADDING_ACCOUNT_KEYBOARD_MARKUP
        )
        await state.set_state(Form.set_amount_accounts)


@form_router.message(Form.set_amount_accounts)
async def process_set_amount_accounts(message: Message, state: FSMContext):
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        if not message.text.isalnum():
            await message.answer("The number of accounts must be a natural number!")
        else:
            accounts_amount = int(message.text)
            crypto_token = "TMPYVBkVZj5pboTAW3VqsW29QMNq6F9Bwq"
            current_price = accounts_amount * 20 + round(random(), 3)

            await message.answer(
                f"Your current subscription price: {html.code(current_price)}.\n"
                f"Сrypto token for payment: {html.code(crypto_token)}.",
                reply_markup=CHECKING_TRANSACTION_KEYBOARD_MARKUP
            )
            await state.update_data(accounts_amount=accounts_amount)
            await state.set_state(Form.check_transaction)


@form_router.message(F.text.casefold() == "check transaction", Form.check_transaction)
async def process_check_transaction(message: Message, state: FSMContext):
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
            reply_markup=SUBSCRIPTIONS_MANAGER_KEYBOARD_MARKUP
        )
    else:
        answer_text = "Transaction was not found."
        if transaction_verdict:
            answer_text = "The subscription has been successfully completed!"
            accounts_amount = await state.get_value("accounts_amount")
            db.add_subscription(username, accounts_amount)

        await message.reply(
            answer_text,
            reply_markup=SUBSCRIPTIONS_MANAGER_KEYBOARD_MARKUP
        )


@form_router.message(F.text.casefold() == "check my accounts")
async def process_check_accounts(message: Message, state: FSMContext):
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        username = message.from_user.username
        accounts = db.get_reddit_accounts(username)
        answer_text = "Information about all your active accounts:\n"
        for i, acc in enumerate(accounts, start=1):
            main_string = f"{i}) {html.code(acc.ads_id)} expires "

            time_delt = (acc.subscription.end_date - date.today()).days
            main_string += "today" if time_delt == 0 else f"in {time_delt} days"

            main_string += (";" if i < len(accounts) else ".") + "\n"
            answer_text += main_string

        if len(accounts) == 0:
            answer_text = "You do not have any active accounts."
        await message.answer(answer_text)


@form_router.message(F.text.casefold() == "check my subscriptions")
async def process_check_accounts(message: Message, state: FSMContext):
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        username = message.from_user.username
        subscriptions = db.get_subscriptions(username)
        answer_text = "Information about all your active subscriptions:\n"
        for i, sub in enumerate(subscriptions, start=1):
            main_string = f"{i}) subscriptions to {sub.amount_accounts_limit} expires "

            time_delt = (sub.end_date - date.today()).days
            main_string += "today" if time_delt == 0 else f"in {time_delt} days"

            main_string += (";" if i < len(subscriptions) else ".") + "\n"
            answer_text += main_string

        if len(subscriptions) == 0:
            answer_text = "You do not have any active subscriptions."
        await message.answer(answer_text)


@form_router.message(F.text.casefold() == "add account")
async def process_check_accounts(message: Message, state: FSMContext):
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text="Enter your account adspower-ID",
            reply_markup=ADDING_ACCOUNT_KEYBOARD_MARKUP
        )
        await state.set_state(Form.add_account)


@form_router.message(Form.add_account)
async def process_check_accounts(message: Message, state: FSMContext):
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        username = message.from_user.username
        ads_id = message.text
        res = db.add_reddit_account(username, ads_id)
        await message.answer(
            "Account was successfully added."
            if res else "Account was not added.",
            reply_markup=SUBSCRIPTIONS_MANAGER_KEYBOARD_MARKUP
        )
        await state.set_state(None)


@form_router.message(F.text.casefold() == "delete account")
async def process_check_accounts(message: Message, state: FSMContext):
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text="Enter your account adspower-ID",
            reply_markup=CANCEL_KEYBOARD_MARKUP
        )
        await state.set_state(Form.delete_account)


@form_router.message(Form.delete_account)
async def process_check_accounts(message: Message, state: FSMContext):
    is_logged_in = await state.get_value("logged_in")

    if not is_logged_in:
        await message.answer(
            "You have not logged in yet.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        ads_id = message.text
        res = db.delete_reddit_account(ads_id)
        await message.answer(
            "Account was successfully deleted."
            if res else "Failed to delete account.",
            reply_markup=SUBSCRIPTIONS_MANAGER_KEYBOARD_MARKUP
        )
        await state.set_state(None)


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
