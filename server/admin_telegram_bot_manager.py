import asyncio
import logging
import sys
from datetime import date

from aiogram import Bot, Dispatcher, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import (
    Message,
    BotCommand
)

import database.database_functions as db


form_router = Router()

TOKEN = "7671610516:AAHqRU8dNzaVQdu3QKxs3DCrEny0hwbKNRM"

BOT_COMMANDS = [
    BotCommand(command="start", description="Start bot"),
    BotCommand(command="add_account", description="Add users's reddit account"),
    BotCommand(command="delete_account", description="Delete users's reddit account"),
    BotCommand(command="add_subscription", description="Add subscription for user"),
    BotCommand(command="delete_subscription", description="Delete subscription for user"),
    BotCommand(command="check_db", description="Check whole database"),
    BotCommand(command="cancel", description="Cancel last action"),
    BotCommand(command="get_user_accounts", description="Get info about all user's accounts"),
]


class Form(StatesGroup):
    set_username_add_subscription = State()
    set_amount_accounts = State()
    set_period_subscription = State()

    set_username_delete_subscription = State()
    set_subscription_id = State()

    set_username_add_account = State()
    set_ads_id_add_account = State()

    set_username_delete_account = State()
    set_ads_id_delete_account = State()

    set_username_get_user_accounts = State()
    set_username_get_user_subscriptions = State()


@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    if await state.get_value("access"):
        return
    if await state.get_value("access") == False:
        await message.answer(f"You are banned by telegram-id ({message.from_user.id})")
    elif message.from_user.username == "chopper_tard":
        await message.answer(f"Hello Kolya! Your telegram id: {message.from_user.id}")
        await state.update_data(access=True)
    elif message.from_user.username == "alexandr_flexer":
        await message.answer(f"Hello Sasha! Your telegram id: {message.from_user.id}")
        await state.update_data(access=True)
    else:
        await message.answer("I don't know you.")
        await state.update_data(access=True)


@form_router.message(Command("add_account"))
async def process_check_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    await message.answer(
        text="Enter user's tg-username"
    )
    await state.set_state(Form.set_username_add_account)


@form_router.message(Form.set_username_add_account)
async def process_buy_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    await state.update_data(username=message.text)
    await message.answer(text="Enter account's ads-id:")
    await state.set_state(Form.set_ads_id_add_account)


@form_router.message(Form.set_ads_id_add_account)
async def process_buy_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    username = await state.get_value("username")
    ads_id = message.text
    res = db.add_reddit_account(username, ads_id)
    await message.answer(
        "Account was successfully added."
        if res else "Account was not added."
    )
    await state.set_state(None)


@form_router.message(Command("cancel"))
async def command_cancel(message: Message, state: FSMContext) -> None:
    if not await state.get_value("access"):
        return

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.set_state(None)
    await message.answer("Cancelled.")


@form_router.message(Command("add_subscription"))
async def process_buy_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    await message.answer(text="Enter user's tg-username:")
    await state.set_state(Form.set_username_add_subscription)


@form_router.message(Form.set_username_add_subscription)
async def process_buy_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    username = message.text
    if not db.check_user_exists(username):
        await message.answer("User with this username does not exist.")
        return

    await state.update_data(username=username)
    await message.answer(text="Enter the number of accounts you want to add:")
    await state.set_state(Form.set_amount_accounts)


@form_router.message(Form.set_amount_accounts)
async def process_set_amount_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    if not message.text.isalnum():
        await message.answer("The number of accounts must be a natural number!")
    else:
        accounts_amount = int(message.text)
        await state.update_data(amount=accounts_amount)
        await message.answer("Enter the subscription period (days):")
        await state.set_state(Form.set_period_subscription)
    

@form_router.message(Form.set_period_subscription)
async def process_set_amount_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    if not message.text.isalnum():
        await message.answer("The number of days must be a natural number!")
    else:
        username = await state.get_value("username")
        accounts_amount = await state.get_value("amount")
        period = int(message.text)

        verdict = db.add_subscription(username, accounts_amount, period)
        if not verdict:
            await message.answer("Subscriptions was not completed.")
        else:
            await message.answer("The subscription has been successfully completed!")
        await state.set_state(None)


@form_router.message(Command("get_user_accounts"))
async def process_set_username_check_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return
    
    await message.answer(text="Enter user's tg-username:")
    await state.set_state(Form.set_username_get_user_accounts)


@form_router.message(Form.set_username_get_user_accounts)
async def process_check_accounts(message: Message, state: FSMContext):
    username = message.text
    if not db.check_user_exists(username):
        await message.answer("User with this username does not exist.")
        return

    await state.set_state(None)
    accounts = db.get_reddit_accounts(username)

    answer_text = f"Information about all {username}'s active accounts:\n"
    for i, acc in enumerate(accounts, start=1):
        main_string = f"{i}) {html.code(acc.ads_id)} expires "

        time_delt = (acc.subscription.end_date - date.today()).days
        main_string += "today" if time_delt == 0 else f"in {time_delt} days"

        main_string += (";" if i < len(accounts) else ".") + "\n"
        answer_text += main_string

    if len(accounts) == 0:
        answer_text = "User does not have any active accounts."
    await message.answer(answer_text)


@form_router.message(Command("delete_account"))
async def process_set_username_check_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    await message.answer(text="Enter account's ads-id:")
    await state.set_state(Form.set_ads_id_delete_account)


@form_router.message(Form.set_ads_id_delete_account)
async def process_set_username_check_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return
    
    ads_id = message.text
    if not db.check_reddit_account_exists(ads_id):
        await message.answer("Account with this id does not exist.")
        return

    res = db.delete_reddit_account(ads_id)
    await message.answer(
        "Account was successfully deleted."
        if res else "Account was not deleted."
    )
    await state.set_state(None)


@form_router.message(Command("check_db"))
async def process_set_username_check_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    answer_text = "Information about all users:\n"
    users = db.get_all_users()
    for user in users:
        username = user.email
        amount_active_accounts = db.get_amount_active_reddit_acounts(username)
        subscriptions = db.get_subscriptions(username)
        full_amount_accounts = sum([sub.amount_accounts_limit for sub in subscriptions])
        amount_active_subscriptions = len(subscriptions)
        answer_text += f"{username} has {amount_active_accounts} out of {full_amount_accounts} active account ({amount_active_subscriptions} active subscriptions).\n\n"
    
    await message.answer(answer_text)


@form_router.message(Command("delete_subscription"))
async def process_set_username_check_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    await message.answer(text="Enter users's tg-username:")
    await state.set_state(Form.set_username_delete_subscription)


@form_router.message(Form.set_username_delete_subscription)
async def process_set_username_check_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    username = message.text
    if not db.check_user_exists(username):
        await message.answer("User with this username does not exist.")
        return

    subscriptions = db.get_subscriptions(username)
    amount_subscriptions = len(subscriptions)
    answer_text = "Enter the subscription id you want delete:\n"
    for i, sub in enumerate(subscriptions):
        main_string = f"{sub.id}: subscriptions to {sub.amount_accounts_limit} ({len(sub.reddit_accounts)} activated) expires "

        time_delt = (sub.end_date - date.today()).days
        main_string += "today" if time_delt == 0 else f"in {time_delt} days"

        main_string += (";" if i < amount_subscriptions - 1 else ".") + "\n"
        answer_text += main_string

    if amount_subscriptions == 0:
        answer_text = "User do not have any active subscriptions."
    await message.answer(answer_text)
    await state.set_state(Form.set_subscription_id)

        
@form_router.message(Form.set_subscription_id)
async def process_set_username_check_accounts(message: Message, state: FSMContext):
    if not await state.get_value("access"):
        return

    if not message.text.isalnum():
        await message.answer("The subscription id must be a natural number!")
    else:
        subscription_id = int(message.text)
        if not db.check_subscription_exists(subscription_id):
            await message.answer(f"No subscription with id \"{subscription_id}\"!")
        else:
            db.delete_subscription(subscription_id)
            await message.answer("Subscription successfully deleted.")



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
