function typeWriter(selector, text, i, speed) {
    if (i < text.length) {
        document.querySelector(selector).innerHTML += text.charAt(i);
        setTimeout(typeWriter, speed, selector, text, i + 1, speed);      
    }
}

window.onload = () => {
    
    let elements = document.getElementsByClassName("fade-in-on-scroll");
    console.log(elements);
    
    let i = 0;
    for (const element of elements) {
        setTimeout(function () {
            element.classList.add("visible");
        }, 300 * ++i)
    }
}
