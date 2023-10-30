let list_commands = [
    {
        title: "Key logger",
        id: "button-keylogger",
        child_command: [],
    },

    {
        title: "Shutdown/Logout",
        id: "button-shutdown",
        child_command: [
            {
                title: "Shutdown computer",
                id: "sub-button-shutdown",
                child_command: [],
            },

            {
                title: "Logout computer",
                id: "sub-button-logout",
                child_command: [],
            },
        ]
    },

    {
        title: "Screenshot",
        id: "button-screenshot",
        child_command: [],
    },

    {
        title: "Application",
        id: "button-application",
        child_command: [
            {
                title: "List applications",
                id: "sub-button-list-apps",
                child_command: [],
            },

            {
                title: "Start an application",
                id: "sub-button-start-app",
                child_command: [],
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
    }
]

function createButton() {
    let command_container = ``;
    for (let i = 0; i < list_commands.length; ++i) {
        command_container +=
            `
                <button
                    type="button"
                    class="command-button"
                    id="command-button-${i}"
                    onmouseover="hoverCommandButtons_In(${i})"
                    onmouseout="hoverCommandButtons_Out(${i})"
            `;
        
        if (list_commands[i].child_command.length > 0) {
            // the button has child commands

            // open div tag
            command_container +=
                `
                        onclick="updateChildCommandBoard(${i})"
                    >
                        ${list_commands[i].title}
                    </button>
                    <div
                        class="child-command-board d-none"
                        id="child-command-board-${i}"
                        style="border-radius: 0px 0px 10px 10px;"
                    >
                `;
            for (let j = 0; j < list_commands[i].child_command.length; j++) {
                command_container += 
                    `
                        <button
                            type="button"
                            class="round-border child-command-button"
                            id="child-command-button-${i}"
                            onclick="chooseCommand(${i}, ${j})"
                        >
                            ${list_commands[i].child_command[j].title}
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
                        onclick="chooseCommand(${i}, 0)"
                    >
                        ${list_commands[i].title}
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
const hoverColor = '#e7d6d6';           // color of the command when being hovered

function clearAllCommandButtons() {
    document.getElementById('command-container').innerHTML = ``;
}

let child_command_board_opening = [0,0,0,0,0];  // mark opening child command board
                                                // only idx 1 3 4 could be opened

function updateChildCommandBoard(idx) {
    let btn = document.getElementById('command-button-' + String(idx));
    let board = document.getElementById('child-command-board-' + String(idx));
    if (child_command_board_opening[idx] == 0) {
        // was closing ==>> need to be opened
        child_command_board_opening[idx] = 1;
        btn.style.borderRadius = '10px 10px 0px 0px'
        btn.style.backgroundColor = hoverColor;
        board.classList.remove("d-none");
    } else {
        // was opening ==>> need to be closed
        child_command_board_opening[idx] = 0;
        btn.style.borderRadius = '10px 10px 10px 10px'
        btn.style.backgroundColor = 'transparent';
        board.classList.add("d-none");
    }
}

function hoverCommandButtons_In(idx) {
    document.getElementById('command-button-' + String(idx)).style.backgroundColor = hoverColor;
}

function hoverCommandButtons_Out(idx) {
    if (child_command_board_opening[idx] == 0) {
        document.getElementById('command-button-' + String(idx)).style.backgroundColor = 'transparent';
    } else {
        hoverCommandButtons_In(idx);
    }
}

function redirectToLogin() {
    window.location.href = "{{  url_for('login')  }}";
}

let chosen = [[0], [0, 0], [0], [0, 0], [0, 0, 0]]; // mark commands which were chosen
/*  idx_i: command i
    idx_j: child command j of command i     */
function chooseCommand(idx_i, idx_j) {
    if (chosen[idx_i][idx_j] == 1) {
        // selected ==>> need to deselect
        chosen[idx_i][idx_j] = 0;
    } else {
        chosen[idx_i][idx_j] = 1;
    }
}