window.onload = renderOnLoad;

function renderOnLoad() {
    document.getElementById('modal__overlay__loading').style.display = 'none'
}

function openUserManualModal() {
    document.getElementById('modal__overlay__manual').style.display = 'flex'
}

function closeUserManualModal() {
    document.getElementById('modal__overlay__manual').style.display = 'none'
}