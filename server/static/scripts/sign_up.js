function mark_error(error_message) {
    let error_place = document.getElementById("error_place");
    error_place.innerHTML = error_message;
}

function reset_error() {
    mark_error("");
}

async function sign_up_user(email, password) {
    const URL = "/sign-up/user/"

    let params = {
        "method": "POST",
        "headers": { "Content-Type": "application/json" },
        "body": JSON.stringify({ "email": email, "password": password })
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

async function sign_up() {
    reset_error();

    let user_email_element = document.getElementById("user_email")
    let user_password_element = document.getElementById("user_password")
    let user_confirmed_password_element = document.getElementById("user_confirmed_password")

    let user_info_elements = [user_email_element, user_password_element, user_confirmed_password_element];
    let flag = true;

    for (const user_info_element of user_info_elements) {
        if (!user_info_element.value) {
            flag = false;
            user_info_element.style.setProperty("--place_holder_color", "red");
        }
        else {
            user_info_element.style.setProperty("--place_holder_color", "#d3dbed");
        }
    }
    if (!flag) { return; }

    let email = user_email_element.value;
    let password = user_password_element.value;

    if (user_confirmed_password_element.value != user_password_element.value) {
        mark_error("Password and Confirmed password do no match")
        return;
    }

    let json_sign_up = await sign_up_user(email, password);
    if (json_sign_up == -1) {
        mark_error("Network error");
    }
    else if (!json_sign_up["result"]) {
        mark_error(json_sign_up["message"]);
    }
    else {
        localStorage.setItem("email", email);
        localStorage.setItem("code_confirmed", false)
        window.location.replace("/confirm-code/");
    }
}
