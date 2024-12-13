window.onload = () => {
    if (!sessionStorage.getItem("purchase")) {
        window.history.go(-1);
    }
}

function get_installer() {
    const url = '/get/installer';
    let filename = null;
    fetch(url)
        .then(res => {
            const disposition = res.headers.get('Content-Disposition');
            filename = disposition.split(/;(.+)/)[1].split(/=(.+)/)[1];
            if (filename.toLowerCase().startsWith("utf-8''"))
                filename = decodeURIComponent(filename.replace("utf-8''", ''));
            else
                filename = filename.replace(/['"]/g, '');

            return res.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
        });
}

function get_instruction() {
    const url = '/get/instruction';
    let filename = null;
    fetch(url)
        .then(res => {
            const disposition = res.headers.get('Content-Disposition');
            filename = disposition.split(/;(.+)/)[1].split(/=(.+)/)[1];
            if (filename.toLowerCase().startsWith("utf-8''"))
                filename = decodeURIComponent(filename.replace("utf-8''", ''));
            else
                filename = filename.replace(/['"]/g, '');

            return res.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
        });
}