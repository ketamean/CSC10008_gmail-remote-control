let command_set = [
    {
        title: "Key logger",
        id: "button-keylogger",
        child_command: [],
        command_content: "[key_logger]"
    },

    {
        title: "Shutdown/Logout",
        id: "button-shutdown",
        child_command: [
            {
                title: "Shutdown computer",
                id: "sub-button-shutdown",
                child_command: [],
                command_content: "[shut_down]"
            },

            {
                title: "Logout computer",
                id: "sub-button-logout",
                child_command: [],
                command_content: "[log_out]"
            },
        ]
    },

    {
        title: "Screenshot",
        id: "button-screenshot",
        child_command: [],
        command_content: "[screen_capture]"
    },

    {
        title: "Application",
        id: "button-application",
        child_command: [
            {
                title: "List applications",
                id: "sub-button-list-apps",
                child_command: [],
                command_content: "[list_apps]"
            },

            {
                title: "Start an application",
                id: "sub-button-start-app",
                child_command: [],
                command_content: "[start_app]"
            },
        ],
    },

    {
        title: "List processes",
        id: "button-process",
        child_command: [
            // {
            //     title: "List processes",
            //     id: "sub-button-list-processes",
            //     child_command: [],
            // },

            // {
            //     title: "Kill a process",
            //     id: "sub-button-kill-a-process",
            //     child_command: [],
            // },

            // {
            //     title: "Kill all processes",
            //     id: "sub-button-kill-all-processes",
            //     child_command: [],
            // },
        ],
        command_content: "[list_processes]"
    }
]

function createButton() {
    let command_container = ``;
    for (let i = 0; i < command_set.length; ++i) {
        command_container +=
            `
                <button
                    type="button"
                    class="command-button"
                    id="command-button-${i}"
                    onmouseover="hoverCommandButtons_In(${i})"
                    onmouseout="hoverCommandButtons_Out(${i})"
            `;
        
        if (command_set[i].child_command.length > 0) {
            // the button has child commands

            // open div tag
            command_container +=
                `
                        onclick="updateChildCommandBoard(${i})"
                    >
                        ${command_set[i].title}
                    </button>
                    <div
                        class="child-command-board d-none"
                        id="child-command-board-${i}"
                        style="border-radius: 0px 0px 10px 10px;"
                    >
                `;
            for (let j = 0; j < command_set[i].child_command.length; j++) {
                command_container += 
                    `
                        <button
                            type="button"
                            class="round-border child-command-button"
                            id="child-command-button-${i}"
                            onclick="chooseCommand(${i}, ${j})"
                        >
                            ${command_set[i].child_command[j].title}
                        </button>
                    `;
            }

            // close div tag
            command_container +=
                `
                    </div>
                `;
        } else {
            command_container +=
                `
                        onclick="chooseCommand(${i}, -1)"
                    >
                        ${command_set[i].title}
                    </button>
                `
        }
    }
    document.getElementById('command-container').innerHTML = command_container;
}

function renderElementsOnLoad() {
    createButton();
}
window.onload = renderElementsOnLoad;

let child_command_board = 0;            // keep the child command board which is opening
const hoverColor = '#1e221f';           // color of the command buttons when being hovered
const childCommandBoardColor = '';      // color of the child command button boards when being displayed

function clearAllCommandButtons() {
    document.getElementById('command-container').innerHTML = ``;
}

let childCommandBoardOpening = [0,0,0,0,0];  // mark opening child command board
                                                // only idx 1 3 4 could be opened

function updateChildCommandBoard(idx) {
    let btn = document.getElementById('command-button-' + String(idx));
    let board = document.getElementById('child-command-board-' + String(idx));
    if (childCommandBoardOpening[idx] == 0) {
        // was closing ==>> need to be opened
        childCommandBoardOpening[idx] = 1;
        btn.style.borderRadius = '10px 10px 0px 0px'
        btn.style.backgroundColor = hoverColor;
        board.classList.remove("d-none");
    } else {
        // was opening ==>> need to be closed
        childCommandBoardOpening[idx] = 0;
        btn.style.borderRadius = '10px 10px 10px 10px'
        btn.style.backgroundColor = 'transparent';
        board.classList.add("d-none");
    }
}

function hoverCommandButtons_In(idx) {
    document.getElementById('command-button-' + String(idx)).style.backgroundColor = hoverColor;
}

function hoverCommandButtons_Out(idx) {
    if (childCommandBoardOpening[idx] == 0) {
        document.getElementById('command-button-' + String(idx)).style.backgroundColor = 'transparent';
    } else {
        hoverCommandButtons_In(idx);
    }
}

function redirectToLogin() {
    // remove all commands which have been chosen
    document.getElementById('mail-content-box').innerHTML = ``;

    // redirect to login page
    window.location.href = "{{  url_for('login')  }}";
}

// each command can be chosen multiple times
/*  idx_i: command i
    idx_j: child command j of command i     */
let chosenCommands = [];
function chooseCommand(idx_i, idx_j) {
    // content = ``;
    if (idx_j < 0) {
        document.getElementById('mail-content-box').value += `${command_set[idx_i].command_content}\n`;
    } else {
        document.getElementById('mail-content-box').value += `${command_set[idx_i].child_command[idx_j].command_content}\n`;
    }
}

function getMessage() {
    let s = document.getElementById('mail-content-box').value;  // copy
    return s;
}

function sendMessage() {
    let s = getMessage();
    {{ sendMail(s) }}
}