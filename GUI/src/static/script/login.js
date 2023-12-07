function createModal(title) {

}

function login(type) {
    // {{ func() }}
    if (type == 'anonymous') {
        window.location.href = "{{ url_for('control') }}"
    } else {

    }
}