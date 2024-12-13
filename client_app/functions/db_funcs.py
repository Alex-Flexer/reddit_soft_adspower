from json import dumps
from requests import post


def add_account(
        user_email: str,
        redd_email: str,
        redd_password: str,
        host: str,
        port: str,
        user: str,
        password: str,
) -> dict[str, str] | None:

    json_response = None
    json = dumps({
        "user_email": user_email,
        "reddit_email": redd_email,
        "reddit_password": redd_password,
        "host": host,
        "port": port,
        "user": user,
        "password": password,
    })
    try:
        response = post(
            "http://reddsyndicate.com/add/reddit-account/", data=json)
        json_response = response.json()
    finally:
        return json_response


def get_proxy(email: str) -> tuple[dict[str, str], str]:
    data = dumps({"email": email})
    result = None, "Network error"
    try:
        response = post("http://reddsyndicate.com/get/proxy", data=data)
        json = response.json()
        if not json["result"]:
            result = None, json["message"]
        else:
            result = json["proxy"], None
    finally:
        return result


def get_reddit_accounts(user_email: str) -> tuple[list[dict[str, str]], str]:
    result = None, "Network error"
    data = dumps({"email": user_email})
    try:
        response = post(
            "http://reddsyndicate.com/get/reddit-accounts", data=data)
        data = response.json()
        if data["result"]:
            result = data["accounts"], None
        else:
            result = None, data["message"]
    finally:
        return result
