from json import dumps
from requests import post


def get_reddit_accounts(user_email: str) -> tuple[list[str] | None, str]:
    result = None, "Network error"
    data = dumps({"email": user_email})
    try:
        response = post(
            "https://thekarmamaster.com/get/reddit-accounts", data=data)
        data = response.json()
        if data["result"]:
            result = data["accounts"], None
        else:
            result = None, data["message"]
    finally:
        return result