from sqlalchemy.orm import Session
from sqlalchemy import select

from typing import Type
from datetime import date, timedelta
from secrets import token_hex

from database.database_model import engine, User, RedditAccount

session = Session(engine)


def clear_db():
    for user in get_all_users():
        delete_user_by_email(str(user.email))


def check_user_exists(email: str) -> bool:
    return not (get_user_by_email(email=email) is None)


def check_user_confirmed(email: str) -> bool:
    return get_user_by_email(email=email).confirmed_status


def check_reddit_account_exists(email: str) -> bool:
    return not (get_reddit_account_by_email(email=email) is None)


def check_user_password(email: str, password: str) -> bool:
    if not check_user_exists(email=email):
        return False
    return bool(get_user_by_email(email=email).user_password == password)


def check_reddit_password(email: str, password: str) -> bool:
    if not check_reddit_account_exists(email=email):
        return False
    return bool(get_reddit_account_by_email(email).password == password)


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


def check_user_subscription(email: str):
    if not check_user_exists(email):
        return False

    subscription_end_date = get_user_by_email(email).subscription_end_date
    return (subscription_end_date is not None) and\
           (subscription_end_date >= date.today())


def get_user_by_email(email: str) -> User | None:
    return session.scalar(select(User).where(User.email == email))


def get_reddit_account_by_email(email: str) -> RedditAccount | None:
    return session.scalar(
        select(RedditAccount).where(RedditAccount.email == email)
    )


def get_user_active_subscription_price(email: str) -> float:
    if not check_user_exists(email):
        return -1
    return get_user_by_email(email).active_subscription_price


def get_all_users() -> list[Type[User]]:
    return session.query(User).all()


def get_proxy(email: str) -> dict[str, str | int]:
    acc = get_reddit_account_by_email(email=email)
    proxy_dict = {'host': acc.proxy_host,
                  'port': acc.proxy_port,
                  'user': acc.proxy_user,
                  'password': acc.proxy_password}
    return proxy_dict


def get_reddit_accounts(user_email: str) -> list[RedditAccount]:
    user = get_user_by_email(user_email)
    return user.reddit_accounts


def add_new_user(email: str, user_password: str) -> bool:
    if check_user_exists(email):
        return False

    session.add(User(
        email=email,
        user_password=user_password,
        confirmed_status=False)
    )

    session.commit()
    return True


def add_new_reddit_account(
    user_email: str,
    reddit_email: str,
    reddit_password: str,
    host: str,
    port: int,
    user: str,
    password: str
) -> bool:
    if not check_user_exists(user_email) or\
            check_reddit_account_exists(reddit_email):
        return False

    user_from_db = get_user_by_email(user_email)
    session.add(RedditAccount(
        owner_id=user_from_db.id,
        email=reddit_email,
        password=reddit_password,
        proxy_host=host,
        proxy_port=port,
        proxy_user=user,
        proxy_password=password
    ))
    session.commit()
    return True


def renew_subscription(email: str) -> bool:
    if not check_user_exists(email):
        return False

    user = get_user_by_email(email)

    end_date = user.subscription_end_date
    if end_date is None:
        end_date = date.today() + timedelta(days=33)
    else:
        end_date += timedelta(days=30)
    
    session.query(User).filter_by(email=email).\
        update({"subscription_end_date": end_date})

    session.commit()
    return True


def confirm_email_code(email: str) -> bool:
    if not check_user_exists(email):
        return False

    session.query(User).filter_by(email=email).\
        update({"confirmed_status": True})

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


def update_telegram_id(email: str, new_id: int) -> bool:
    if not check_user_exists(email):
        return False

    session.query(User).filter_by(email=email).\
        update({"telegram_id": new_id})

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


def delete_user_by_email(email: str) -> None:
    if not check_user_exists(email=email):
        return False

    session.query(User).filter_by(email=email).delete()
    session.commit()
    return True


def delete_reddit_account_by_email(email: str) -> None:
    if check_reddit_account_exists(email=email):
        session.query(RedditAccount).filter_by(email=email).delete()
        session.commit()


def show_db(db_name) -> None:
    print(*session.query(db_name).all(), sep='\n')


if __name__ == "__main__":
    show_db(User)
