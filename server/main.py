import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from random import random
from secrets import token_hex

from functions.check_transaction import check_transaction
import database.database_functions as db

app = FastAPI()

app.mount(
    path="/static",
    app=StaticFiles(directory="../server/static", html=True),
    name="static"
)


@app.get("/")
async def send_home_page() -> FileResponse:
    return FileResponse("../server/static/html/index.html")


# @app.get("/sign-up/")
# async def send_registration_page() -> FileResponse:
#     return FileResponse("../server/static/html/sign_up.html")


@app.get("/confirm-code/")
async def check_email_code() -> FileResponse:
    return FileResponse("../server/static/html/check_email_code.html")


# @app.get("/login/")
# async def send_login_page() -> FileResponse:
#     return FileResponse("../server/static/html/login.html")


@app.get("/tariffs/")
async def send_tariffs() -> FileResponse:
    return FileResponse("../server/static/html/tariffs.html")


@app.get("/buy-form/")
async def send_buy_form() -> FileResponse:
    return FileResponse("../server/static/html/buy_form.html")


@app.get("/successful-purchase/")
async def send_purchase_page() -> FileResponse:
    return FileResponse("../server/static/html/successful_purchase.html")


@app.get("/get/installer")
async def send_installer() -> FileResponse:
    headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}

    return FileResponse(
        "../server/private_resources/installer.pyw",
        filename="RS-installer.pyw", headers=headers)


@app.get("/get/instruction")
async def send_instruction() -> FileResponse:
    headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}

    return FileResponse(
        "../server/private_resources/instruction.pdf",
        filename="RS-instruction.pdf", headers=headers)


@app.post("/get/software")
async def send_software(request: Request) -> FileResponse:
    headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}

    json: dict = await request.json()
    status_code = 400

    if {"email", "password"}.issubset(json.keys()):
        email = json["email"]
        password = json["password"]

        if db.check_user_exists(email):
            is_valid_password = db.check_user_password(email, password)

            status_code = 200 if is_valid_password else 403
        else:
            status_code = 404

    if status_code == 200:
        return FileResponse("./private_resources/source.zip",
                            filename="RedditSyndicate.zip",
                            status_code=200, headers=headers)
    else:
        return FileResponse("./private_resources/empty.txt",
                            status_code=status_code, headers=headers)


@app.post("/get/reddit-accounts/")
async def get_reddit_accounts(request: Request) -> JSONResponse:
    json: dict = await request.json()
    response_json: dict = {"result": False, "message": "Incorrect request"}

    if {"email"}.issubset(json.keys()):
        email = json['email']
        if db.check_user_exists(email):
            reddit_accounts = db.get_reddit_accounts(email)
            response_json['result'] = True
            response_json["message"] = ""
            response_json["accounts"] = [acc.ads_id for acc in reddit_accounts]
        else:
            response_json["message"] = "User with this tg-nickname does not exist"
    return JSONResponse(content=response_json, status_code=200)


# @app.post("/get/proxy/")
# async def get_proxy(request: Request) -> JSONResponse:
#     json: dict = await request.json()
#     response_json: dict = {"result": False, "message": "Incorrect request"}

#     if {"email"}.issubset(json.keys()):
#         email = json['email']
#         if db.check_reddit_account_exists(email=email):
#             proxy_info = db.get_proxy(email)
#             response_json["proxy"] = proxy_info
#             response_json["massage"] = ""
#             response_json['result'] = True
#         else:
#             response_json['massage'] =\
#                 'Reddit account with this email does not exist'
#     return JSONResponse(content=response_json, status_code=200)


# @app.post("/get/price/")
# async def send_price(request: Request) -> JSONResponse:
#     json: dict = await request.json()
#     response_json: dict = {"result": False, "message": "Incorrect request"}

#     if {"email"}.issubset(json.keys()):
#         email = json["email"]
#         price =\
#         299 if db.get_user_by_email(email).subscription_end_date is None\
#         else 349

#         new_price = price + round(random(), 3)

#         db.update_subscription_price(email, new_price)

#         response_json["result"] = True
#         response_json["price"] = new_price
#         response_json["message"] = ""

#     return JSONResponse(content=response_json, status_code=200)


@app.get("/get/crypto-token/")
async def send_crypto_token() -> JSONResponse:
    response_json: dict = {"result": False,
                           "message": "Crypto-token was not found"}

    crypto_token = "TMPYVBkVZj5pboTAW3VqsW29QMNq6F9Bwq"

    if crypto_token is not None:
        response_json["result"] = True
        response_json["token"] = crypto_token
        response_json["message"] = ""

    return JSONResponse(content=response_json, status_code=200)


# @app.post("/sign-up/user/")
# async def add_user(request: Request) -> JSONResponse:
#     json = await request.json()

#     response_json = {"result": False, "message": "Incorrect request"}

#     if {"email", "password"}.issubset(json.keys()):
#         email = json["email"]
#         password = json["password"]

#         if db.check_user_exists(email):
#             response_json["message"] = "User already exists"
#         else:
#             result = db.add_new_user(email, password)
#             if result:
#                 response_json["message"] = ""
#                 response_json["result"] = True
#             else:
#                 response_json["message"] = "Unknown sing up error"

#     return JSONResponse(content=response_json, status_code=200)


# @app.post("/login/user/")
# async def login_user(request: Request) -> JSONResponse:
#     json = await request.json()

#     response_json = {"result": False, "message": "Incorrect request"}

#     if {"email", "password"}.issubset(json.keys()):
#         email = json["email"]
#         password = json["password"]

#         if not db.check_user_exists(email):
#             response_json["message"] = "User with this tg-nickname does not exist"
#         elif not db.check_user_password(email, password):
#             response_json["message"] = "Incorrect password"
#         elif not db.check_user_confirmed(email):
#             response_json["result"] = True
#             response_json["message"] = "Registration email code not confirmed"
#         else:
#             response_json["result"] = True
#             response_json["message"] = ""

#     return JSONResponse(content=response_json, status_code=200)


# @app.post("/confirm/email-code")
# async def check_user_code(request: Request) -> JSONResponse:
#     json = await request.json()

#     response_json = {
#         "result": False,
#         "message": "Incorrect request"
#     }

#     if {"email", "code"}.issubset(json.keys()):
#         email = json["email"]
#         code = json["code"]

#         if not db.check_user_exists(email):
#             response_json["message"] = "User with this tg-nickname does not exist"
#         elif not db.check_authorization_code(email, code):
#             response_json["message"] = "Incorrect authorization code"
#         else:
#             db.confirm_email_code(email)

#             auth_code = token_hex(16)
#             db.update_email_code(email, auth_code)

#             response_json["message"] = ""
#             response_json["result"] = True

#     return JSONResponse(content=response_json, status_code=200)


@app.post("/update/user-token/")
async def send_email_code(request: Request) -> JSONResponse:
    json = await request.json()
    response_json = {"result": False,
                     "message": "Incorrect request", "token": None}

    if {"email"}.issubset(json.keys()):
        email = json["email"]

        if not db.check_user_exists(email):
            response_json["message"] = "User with this tg-nickname does not exist"
        else:
            new_token = db.update_user_token(email)

            response_json["result"] = True
            response_json["message"] = ""
            response_json["token"] = new_token

    return JSONResponse(content=response_json, status_code=200)


# @app.post("/check/transaction/")
# async def check_user_transaction(request: Request) -> JSONResponse:
#     json: dict = await request.json()
#     response_json = {"result": False, "message": "Incorrect request"}

#     if {"email"}.issubset(json.keys()):
#         email = json["email"]

#         if db.check_user_exists(email):
#             try:
#                 price = db.get_user_active_subscription_price(email)
#                 transaction_verdict = await check_transaction(price)
#             except Exception as e:
#                 response_json["message"] = "Unknown checking transaction Error"
#                 print(e)
#             else:
#                 if transaction_verdict:
#                     db.renew_subscription(email)
#                     response_json["result"] = True
#                     response_json["message"] = ""
#                 else:
#                     response_json["message"] = "Transaction was not found"
#         else:
#             response_json["message"] = "Users with this email does not exists"

#     return JSONResponse(content=response_json, status_code=200)


@app.post("/check/user-credentials/")
async def check_user_credentials(request: Request) -> JSONResponse:
    json: dict = await request.json()
    response_json = {"result": False, "message": "Incorrect request"}

    if {"email", "password", "token"}.issubset(json.keys()):
        email = json["email"]
        password = json["password"]
        token = json["token"]

        if db.check_user_exists(email):
            if not db.check_user_credentials(email, password, token):
                response_json["message"] = "Incorrect credentials"
            else:
                response_json["result"] = True
                response_json["message"] = ""
                response_json["token"] = db.update_user_token(email)
        else:
            response_json["message"] = "Users with this email does not exists"

    return JSONResponse(content=response_json, status_code=200)


@app.post("/add/reddit-account/")
async def add_reddit_account(request: Request) -> JSONResponse:
    json: dict = await request.json()
    response_json: dict[str, str] = {"result": False, "message": "Incorrect request"}

    params_reqirements: set[str] = {
        "user_email",
        "ads_id"
    }

    if params_reqirements.issubset(json.keys()):
        if not db.check_user_exists(json["user_email"]):
            response_json["massage"] = "Users with this email does not exists"
        elif db.check_reddit_account_exists(json["ads_id"]):
            response_json['massage'] =\
                'Reddit account with this adspower-id does not exist'
        else:
            verdict = db.add_reddit_account(**json)
            response_json['result'] = verdict
            if verdict:
                response_json["massage"] = ""
            else:
                response_json["massage"] = "Faild to add new account."


    return JSONResponse(content=response_json, status_code=200)


if __name__ == '__main__':
    uvicorn.run('main:app', host="90.156.168.186",
                port=80, reload=True, workers=12)
