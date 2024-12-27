from sqlalchemy.orm import Session
from sqlalchemy import select

from datetime import date, timedelta
from secrets import token_hex
from itertools import chain

try:
    from database.database_model import engine, User, RedditAccount, Subscription
except ModuleNotFoundError:
    from database_model import engine, User, RedditAccount, Subscription

session = Session(engine)


def check_user_exists(email: str) -> bool:
    return not (get_user_by_email(email=email) is None)


def check_user_confirmed(email: str) -> bool:
    return get_user_by_email(email=email).status_confirmed


def check_reddit_account_exists(ads_id: str) -> bool:
    return not (get_reddit_account(ads_id) is None)


def check_subscription_exists(subscription_id: int) -> bool:
    return session.scalar(select(Subscription).where(Subscription.id == subscription_id))


def check_user_password(email: str, password: str) -> bool:
    if not check_user_exists(email=email):
        return False
    return bool(get_user_by_email(email=email).user_password == password)


def check_authorization_code(email: str, authorization_code: str) -> bool:
    if not check_user_exists(email):
        return False
    return\
        bool(get_user_by_email(email).authorization_code == authorization_code)


def check_user_credentials(email: str, password: str, token: str) -> bool:
    if not check_user_exists(email):
        return False

    user = get_user_by_email(email)
    return user.token == token and user.user_password == password


def check_user_used_trial(email: str) -> bool:
    if not check_user_exists(email):
        return False
    return get_user_by_email(email).status_used_trial


def get_user_by_email(email: str) -> User | None:
    return session.scalar(select(User).where(User.email == email))


def get_reddit_account(ads_id: str) -> RedditAccount | None:
    return session.scalar(
        select(RedditAccount).where(RedditAccount.ads_id == ads_id)
    )


def get_user_active_subscription_price(email: str) -> float:
    if not check_user_exists(email):
        return -1
    return get_user_by_email(email).active_subscription_price


def get_all_users() -> list[User]:
    return session.query(User).all()


def get_reddit_accounts(user_email: str) -> list[RedditAccount]:
    refresh_subscriptions(user_email)

    user = get_user_by_email(user_email)
    subscriptions: list[Subscription] = user.subscriptions

    accounts = list(chain.from_iterable(
        [[acc for acc in sub.reddit_accounts] for sub in subscriptions]
    ))

    return accounts


def get_amount_active_reddit_acounts(user_email: str) -> int:
    return len(get_reddit_accounts(user_email))


def get_subscriptions(user_email: str) -> list[Subscription]:
    refresh_subscriptions(user_email)
    return get_user_by_email(user_email).subscriptions


def add_new_user(email: str, user_password: str) -> bool:
    if check_user_exists(email):
        return False

    session.add(User(
        email=email,
        user_password=user_password,
        status_confirmed=False,
        status_used_trial=False)
    )

    session.commit()
    return True


def add_subscription(user_email: str, amount: int) -> bool:
    if not check_user_exists(user_email):
        return False

    user = get_user_by_email(user_email)
    session.add(Subscription(
        owner_id=user.id,
        end_date=date.today() + timedelta(30),
        amount_accounts_limit=amount

    ))
    session.commit()
    return True


def add_trial_subscription(user_email: str) -> bool:
    if not check_user_exists(user_email) or check_user_used_trial(user_email):
        return False

    user = get_user_by_email(user_email)
    session.add(Subscription(
        owner_id=user.id,
        end_date=date.today() + timedelta(3),
        amount_accounts_limit=1

    ))
    session.commit()
    return True


def add_reddit_account(user_email: str, ads_id: str) -> bool:
    if not check_user_exists(user_email):
        return False

    if check_reddit_account_exists(ads_id):
        return False

    subscriptions = get_subscriptions(user_email)
    new_reddit_account = None

    for sub in subscriptions:
        accounts: list[RedditAccount] = sub.reddit_accounts
        if len(accounts) < sub.amount_accounts_limit:
            new_reddit_account = RedditAccount(
                subscription_id=sub.id,
                ads_id=ads_id
            )
            break

    if new_reddit_account is None:
        return False

    session.add(new_reddit_account)
    session.commit()
    return True


def confirm_email_code(email: str) -> bool:
    if not check_user_exists(email):
        return False

    session.query(User).filter_by(email=email).\
        update({"status_confirmed": True})

    session.commit()
    return True


def update_email_code(email: str, code: str) -> bool:
    if not check_user_exists(email):
        return False

    session.query(User).filter_by(email=email).\
        update({"authorization_code": code})

    session.commit()
    return True


def update_subscription_price(email: str, price: float) -> bool:
    if not check_user_exists(email):
        return False

    session.query(User).filter_by(email=email).\
        update({"active_subscription_price": price})

    session.commit()
    return True


def update_user_token(email: str) -> str | None:
    if not check_user_exists(email):
        return None

    new_token = token_hex(40)
    session.query(User).filter_by(email=email). \
        update({"token": new_token})

    session.commit()
    return new_token


def refresh_subscriptions(email: str) -> None:
    subscriptions = get_user_by_email(email).subscriptions
    for sub in subscriptions:
        if sub.end_date < date.today():
            delete_subscription(sub.id)


def delete_user(email: str) -> None:
    if not check_user_exists(email=email):
        return False

    session.query(User).filter_by(email=email).delete()
    session.commit()
    return True


def delete_subscription(subscription_id: int) -> None:
    session.query(Subscription).filter_by(id=subscription_id).delete()
    session.commit()


def delete_reddit_account(ads_id: str) -> None:
    if not check_reddit_account_exists(ads_id):
        return False

    session.query(RedditAccount).filter_by(ads_id=ads_id).delete()
    session.commit()
    return True


def show_db(db_name) -> None:
    print(*session.query(db_name).all(), sep='\n')


if __name__ == "__main__":
    ...
    # a = "alexandr_flexer"
    # b = session.query(User).filter_by(email=a)
    # print(b.count())
    # print(check_subscription_exists(90))
    # add_subscription("alexandr_flexer", 3)
    # show_db(User)
    # show_db(Subscription)
