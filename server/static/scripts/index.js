function typeWriter(selector, text, i, speed) {
    if (i < text.length) {
        document.querySelector(selector).innerHTML += text.charAt(i);
        setTimeout(typeWriter, speed, selector, text, i + 1, speed);      
    }
}

window.onload = () => {
    if(/iP(hone|ad)/.test(window.navigator.userAgent)) {
        console.log("haha");
        
        document.body.addEventListener('touchstart', function() {}, false);
    }

    typeWriter(".logo", "Karma Master", 0, 100)
    setTimeout(typeWriter, 2000, ".header > h1", "Millions of Tasks — One Software", 0, 100)
    setTimeout(typeWriter, 5700, "p", "Effortlessly Automate Your Reddit Workflow", 0, 50)
}



document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll(".fade-in-on-scroll");

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target);
            }
        });
    });

    elements.forEach(element => {
        observer.observe(element);
    });
});

