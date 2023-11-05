function redirectToLogin() {
    // remove all commands which have been chosen
    document.getElementById('mail-content-box').innerHTML = ``;

    // redirect to login page
    window.location.href = "{{  url_for('login')  }}";
}

function insert(btn)
{
    const box=document.getElementById('a');
    box.value += btn.className;
}

function show(btn)
{
    const caret = btn.closest('.caret');
    //caret.classList.toggle('caret-rotate');
}