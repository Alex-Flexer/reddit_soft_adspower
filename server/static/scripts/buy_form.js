var crypto_token = null;
let email = null;

window.onload = async function () {
    if (!localStorage.getItem("email")) {
        window.location.replace("/login");
        return;
    }

    if (!localStorage.getItem("code_confirmed") || localStorage.getItem("code_confirmed") == "false") {
        window.location.replace("/confirm-code");
        return;
    }

    email = localStorage.getItem("email");
    document.querySelector(".section:nth-child(1) > h2:nth-child(2)").innerHTML = email;

    json_crypto_token = await get_crypto_token();
    if (json_crypto_token == -1) {
        mark_error("Network error");
    }
    else if (!json_crypto_token["result"]) {
        mark_error(json_crypto_token["message"]);
    }
    else {
        crypto_token = json_crypto_token["token"];
        set_price(email);
    }

}

async function get_crypto_token() {
    const URL = "/get/crypto-token/";

    const params = {
        "method": "GET",
        "headers": { "Content-Type": "application/json" },
    };
    try {
        let response = await fetch(URL, params);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const json = await response.json();
        return json;
    }
    catch (error) {
        console.log(error);
        return -1;
    }
}

function copy_token() {
    const tempInput = document.createElement('input');
    tempInput.value = crypto_token;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
}

function mark_error(error_message) {
    let error_place = document.getElementById("error_place");
    error_place.innerHTML = error_message;
}

function reset_error() {
    mark_error("");
}

async function get_user_price(email, price) {
    const URL = "/get/price/"

    const params = {
        "method": "POST",
        "headers": { "Content-Type": "application/json" },
        "body": JSON.stringify({ "email": email, "price": price })
    };
    try {
        let response = await fetch(URL, params);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const json = await response.json();
        return json;
    }
    catch (error) {
        console.log(error);
        return -1;
    }
}

async function check_user_transaction(email) {
    const URL = "/check/transaction/"

    const params = {
        "method": "POST",
        "headers": { "Content-Type": "application/json" },
        "body": JSON.stringify({ "email": email })
    };
    try {
        let response = await fetch(URL, params);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const json = await response.json();
        return json;
    }
    catch (error) {
        console.log(error);
        return -1;
    }
}

async function set_price(email) {
    let price_element = document.getElementById("price");
    let json_price = await get_user_price(email, 299);
    if (json_price == -1) {
        mark_error("Network error");
    }
    else if (!json_price["result"]) {
        mark_error(json_price["message"]);
    }
    else {
        price_element.innerHTML = json_price["price"];
    }
}

async function check_transaction() {
    let b1 = document.querySelector(".continue_button.valiable");
    let b2 = document.querySelector(".alternative_button.valiable");

    if (!(b1 && b2))
        return;

    b1.classList.replace("valiable", "unavailable");
    b2.classList.replace("valiable", "unavailable");

    let email = localStorage.getItem("email");
    json_checking_transaction = await check_user_transaction(email);

    if (json_checking_transaction == -1) {
        mark_error("Network error");
    }
    else if (!json_checking_transaction["result"]) {
        mark_error(json_checking_transaction["message"]);
    }
    else {
        sessionStorage.setItem("purchase", true);
        window.location.replace("/successful-purchase");
    }

    b1.classList.replace("unavailable", "valiable");
    b2.classList.replace("unavailable", "valiable");
}

function redirect_to_login() {
    if (document.querySelector(".alternative_button").classList.contains("valiable")) {
        localStorage.clear()
        window.location.replace("/login");
    }
}