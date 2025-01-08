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

TOKEN = "7869269231:AAHTo6xfN8Dj-AKbJ3VkXvEJKURHk2hOuHI"

BOT_COMMANDS = [
    BotCommand(command="start", description="Start bot"),
    BotCommand(command="help", description="Find out everything you need about us"),
    BotCommand(command="support", description="Contact our support team"),
    BotCommand(command="sign_up", description="Create an account your account to get more functionality"),
    BotCommand(command="trial", description="Try a trial period"),
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
                KeyboardButton(text="Verify Transaction"),
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
    come_up_password = State()
    set_amount_accounts = State()
    add_account = State()
    delete_account = State()
    verify_transaction = State()
    verifying_transaction = State()


async def check_user_exists(message: Message) -> bool:
    username = message.from_user.username
    verdict = db.check_user_exists(username)
    if not verdict:
        await message.answer(f"User with username \"{username}\" does not exist.")
    return verdict


@form_router.message(CommandStart())
async def command_start(message: Message) -> None:
    username = message.from_user.username
    await message.answer(
        "You are welcomed by Karma-Master! Some about as:\n\n"
        "Karma Master is a powerful automation tool tailored for "
        "users, businesses, and creators who want to promote their Reddit accounts.\n\n"
        "With a single software you can handle millions of tasks at once — from content "
        "scheduling and posting to data gathering and community engagement.",
        reply_markup=(MAIN_KEYBOARD_MARKUP if db.check_user_exists(username) else ReplyKeyboardRemove())
    )


@form_router.message(Command("help"))
async def command_help(message: Message) -> None:
    await message.answer(
        "How can I help you?\n\n"
        "If you don't have an account please use command /sign_up to create it. "
        "Then you will get more functionality inside the chatbot.\n\n"
        "When subscribing, you purchase slots for accounts, after which you can add accounts to these slots and remove them as needed.\n\n"
        "During the trial period, you are provided with one account slot for 3 days (to try a trial period use command /trial)\n\n"
        f"Source links:  {html.link('Installer', 'https://thekarmamaster.com/get/installer')}   {html.link('Instruction', 'https://thekarmamaster.com/get/instruction')}\n\n"
        f"Also if you have some software problem or some other questions you can contact our support team."
    )


@form_router.message(Command("support"))
async def command_support(message: Message) -> None:
    await message.answer(
        "Contact our support team (reddsyndicate@mail.ru) "
        "if you have any software problems or any other questions."
    )


@form_router.message(Command("sign_up"))
async def command_sign_up(message: Message, state: FSMContext) -> None:
    username = message.from_user.username
            
    if db.check_user_exists(username):
        await message.answer(f"User with username \"{username}\" already exists.")
    else:
        await state.set_state(Form.come_up_password)
        await message.answer(
            "Please, come up with a strong password:",
            reply_markup=CANCEL_KEYBOARD_MARKUP
        )


@form_router.message(Command("trial"))
async def command_sign_up(message: Message) -> None:
    if not await check_user_exists(message):
        return

    username = message.from_user.username
    if not db.check_user_used_trial(username):
        res = db.add_trial_subscription(username)
        if res:
            await message.answer(f"Trial period is successfully acrivated! ({html.link('find out more about trial version', '/help')})")
        else:
            await message.answer("Failed to activate trial period.")
    else:
        await message.answer("Trial period has already been used.")


@form_router.message(F.text.casefold() == "get confirmation code")
async def command_get_confirmation_code(message: Message) -> None:
    if not await check_user_exists(message):
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
            if (current_state in {Form.set_amount_accounts, Form.verify_transaction, Form.add_account, Form.delete_account})
            else ReplyKeyboardRemove()
    )


@form_router.message(Form.come_up_password)
async def process_password(message: Message, state: FSMContext) -> None:
    username = message.from_user.username
    if db.check_user_exists(username):
        await message.answer(f"User with username {username} already exists.")        
    else:
        password: str = message.text

        if len(password) > 32:
            await message.answer("Your password too cool for me! Please, make it a little bit shorter. (maximum 32 character)")
        elif len(password) < 6:
            await message.answer("Even my younger sister has a longer password! Please, make it a little bit longer. (minimum 6 character)")
        else:
            verdict = db.add_new_user(username, password)
            if verdict:
                db.confirm_email_code(username)
                await message.answer(
                    f"Congratulations! You have successfully signed up.",
                    reply_markup=MAIN_KEYBOARD_MARKUP
                )
            else:
                await message.answer("Something went wrong, contact our support.")
            await state.set_state(None)
                
    

@form_router.message(F.text.casefold() == "account info")
async def process_account_info(message: Message) -> None:
    if not await check_user_exists(message):
        return

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
async def process_subscriptions_manager(message: Message):
    if not await check_user_exists(message):
        return

    await message.answer(
        "What would you like to do?",
        reply_markup=SUBSCRIPTIONS_MANAGER_KEYBOARD_MARKUP
    )

@form_router.message(F.text.casefold() == "home")
async def process_home(message: Message):
    if not await check_user_exists(message):
        return

    await message.answer(
        choice(["Good there where we are not.",
            "There's no place like home.",
            "East or west, home is best",
            "Home sweet home."]),
        reply_markup=MAIN_KEYBOARD_MARKUP
    )


@form_router.message(F.text.casefold() == "buy a subscription", default_state)
async def process_buy_accounts(message: Message, state: FSMContext):
    if not await check_user_exists(message):
        return

    await message.answer(
        text="Enter the number of accounts you want to buy:",
        reply_markup=ADDING_ACCOUNT_KEYBOARD_MARKUP
    )
    await state.set_state(Form.set_amount_accounts)


@form_router.message(Form.set_amount_accounts)
async def process_set_amount_accounts(message: Message, state: FSMContext):
    def calc_full_price(amount: int) -> int:
        prefix_prices = [18, 34, 48, 60]
        if amount <= 10:
            return amount * 20
        else:
            return 200 + prefix_prices[min(3, amount - 11)] + max(0, amount - 14) * 12

    if not await check_user_exists(message):
        return

    if not message.text.isalnum():
        await message.answer("The number of accounts must be a natural number!")
    else:
        accounts_amount = int(message.text)
        crypto_token = "TMPYVBkVZj5pboTAW3VqsW29QMNq6F9Bwq"
        current_price = calc_full_price(accounts_amount) + round(random(), 3)

        await message.answer(
            f"Your current subscription price: {html.code(current_price)} USDT.\n"
            f"Сrypto token for payment: {html.code(crypto_token)}.",
            reply_markup=CHECKING_TRANSACTION_KEYBOARD_MARKUP
        )
        await state.update_data(accounts_amount=accounts_amount)
        await state.set_state(Form.verify_transaction)


@form_router.message(Form.verify_transaction)
async def process_check_transaction(message: Message, state: FSMContext):
    if not await check_user_exists(message):
        return

    username: str = message.from_user.username
    active_price = db.get_user_active_subscription_price(username)

    await state.set_state(Form.verifying_transaction)

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
    finally:
        await state.set_state(None)


@form_router.message(F.text.casefold() == "check my accounts")
async def process_check_accounts(message: Message):
    if not await check_user_exists(message):
        return

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
async def process_check_subscriptions(message: Message):
    if not await check_user_exists(message):
        return

    username = message.from_user.username
    subscriptions = db.get_subscriptions(username)

    answer_text = "Information about all your active subscriptions:\n"
    for i, sub in enumerate(subscriptions, start=1):
        main_string = f"{i}) subscription to {sub.amount_accounts_limit} account expires "

        time_delt = (sub.end_date - date.today()).days
        main_string += "today" if time_delt == 0 else f"in {time_delt} days"

        main_string += (";" if i < len(subscriptions) else ".") + "\n"
        answer_text += main_string

    if len(subscriptions) == 0:
        answer_text = "You do not have any active subscriptions."
    await message.answer(answer_text)


@form_router.message(F.text.casefold() == "add account")
async def process_set_username_new_account(message: Message, state: FSMContext):
    if not await check_user_exists(message):
        return

    await message.answer(
        text="Enter your account adspower-ID",
        reply_markup=ADDING_ACCOUNT_KEYBOARD_MARKUP
    )
    await state.set_state(Form.add_account)


@form_router.message(Form.add_account)
async def process_add_account(message: Message, state: FSMContext):
    if not await check_user_exists(message):
        return

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
async def process_set_username_deletion_account(message: Message, state: FSMContext):
    if not await check_user_exists(message):
        return

    await message.answer(
        text="Enter your account adspower-ID",
        reply_markup=CANCEL_KEYBOARD_MARKUP
    )
    await state.set_state(Form.delete_account)


@form_router.message(Form.delete_account)
async def process_delete_account(message: Message, state: FSMContext):
    if not await check_user_exists(message):
        return

    ads_id = message.text
    res = db.delete_reddit_account(ads_id)
    await message.answer(
        "Account was successfully deleted."
        if res else "Failed to delete account.",
        reply_markup=SUBSCRIPTIONS_MANAGER_KEYBOARD_MARKUP
    )
    await state.set_state(None)


@form_router.message()
async def process_unknown_command(message: Message):
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
