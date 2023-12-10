window.onload = renderElementsOnLoad;

class Info {
    static hoverColor = '#aae49f'; // color of the command buttons when being hovered
    static command_set = [
        {
            title: "Key logger",
            id: "button-keylogger",
            child_command: [],
            command_content: "" // special case
        },
        
        {
            title: "Screenshot",
            id: "button-screenshot",
            child_command: [],
            command_content: "[screen_capture]"
        },
    
        {
            title: "List applications",
            id: "sub-button-list-apps",
            child_command: [],
            command_content: "[list_apps]"
        },
    
        {
            title: "List processes",
            id: "button-process",
            child_command: [],
            command_content: "[list_processes]"
        }
    ];

    static childCommandBoardOpening = [0,0,0,0]
}

function createButton() {
    let command_container = ``;
    for (let i = 0; i < Info.command_set.length; ++i) {
        if (i == 0) {
            command_container += `
                <button
                    type="button"
                    class="command-button"
                    id="command-button-0"
                    onclick="pressKeyloggerBtn()";
                    onmouseover="hoverCommandButtons_In(0)"
                    onmouseout="hoverCommandButtons_Out(0)"
                >
                    Key logger
                </button>
            `;
        } else {
            command_container += `
                <button
                    type="button"
                    class="command-button"
                    id="command-button-${i}"
                    onmouseover="hoverCommandButtons_In(${i})"
                    onmouseout="hoverCommandButtons_Out(${i})"
                    onclick="chooseCommand(${i})"
                >
                    ${Info.command_set[i].title}
                </button>
            `;
        }
    }
    document.getElementById('command-container').innerHTML = command_container;
}

function renderElementsOnLoad() {
    createButton();
    Info.show_alert_application = true;
}

function clearAllCommandButtons() {
    document.getElementById('command-container').innerHTML = ``;
}

function hoverCommandButtons_In(idx) {
    document.getElementById('command-button-' + String(idx)).style.backgroundColor = Info.hoverColor;
}

function hoverCommandButtons_Out(idx) {
    if (Info.childCommandBoardOpening[idx] == 0) {
        document.getElementById('command-button-' + String(idx)).style.backgroundColor = '#7f9f94e1';
    } else {
        hoverCommandButtons_In(idx);
    }
}

function pressKeyloggerBtn() {
    if (checkKeyloggerExisted() == true) {
        alert("only one valid key-logger command is allowed for each mail");
    } else {
        document.getElementById('modal__overlay__keylog').style.display = 'flex';
    }
}

function closeKeyLoggerModal() {
    document.getElementById('textbox-keylog').value = ``;
    document.getElementById('modal__overlay__keylog').style.display = 'none';
}

function chooseCommand(i) {
    if (document.getElementById('mail-content-box').value != "") {
        document.getElementById('mail-content-box').value += "\n";
    }

    if (i == 0) {
        let str = document.getElementById('textbox-keylog').value;
        if (isNaN(str) == true || str.length > 3 || str.length == 0 || str < 0) {
            // input validation
            alert("invalid input: only accept numbers from 0 to 99 (in seconds)");
        } else {
            document.getElementById('mail-content-box').value += "[key_logger] " + str;
            closeKeyLoggerModal();
        }
    } else {
        document.getElementById('mail-content-box').value += `${Info.command_set[i].command_content}`;  
    }
    document.getElementById('mail-content-box').value = document.getElementById('mail-content-box').value.replace(/\n+/g, '\n')
}

function checkKeyloggerExisted() {
    let msg = document.getElementById('mail-content-box').value;
    cmds = getListCommands(msg);
    for (let i = 0; i < cmds.length; i++) {
        if (cmds[i].search(/^\[key_logger\] (\d|\d\d)$/) >= 0) {
            return true;
        }
    }
    return false;
}

function getListCommands(msg) {
    return msg.split(/\r|\n/);
}

function keypressModal_timekeylog(obj) {
    if ( obj.value.length > 2 || !(obj.value[obj.value.length-1] >= '0' && obj.value[obj.value.length-1] <= '9') )
        return false;
    return true;
}