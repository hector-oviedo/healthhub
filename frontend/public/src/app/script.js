backendService = new BackendService(backendUrl);
contentGenerator = new ContentGenerator();

var username = "";
var password = "";
logged = false;

function createVerticalMenu(menuItems) {
    const div = document.createElement('div');
    const menuList = document.createElement('ul');
    menuList.className = 'list-unstyled d-flex flex-column align-items-center';
    menuList.style.paddingTop = "10px";
    menuList.style.paddingBottom = "10px";
    menuList.style.backgroundColor = "#202123";

    menuItems.forEach(item => {
        const menuItem = document.createElement('li');
        menuItem.className = 'my-2 text-center';
        menuItem.style.fontSize = '0.8em';
        menuItem.style.cursor = 'pointer';
        menuItem.style.paddingTop = "10px";
        menuItem.style.paddingBottom = "10px";
        menuItem.onclick = () => { item.action(item.type) };

        const icon = document.createElement('i');
        icon.className = item.icon;
        icon.setAttribute('aria-hidden', 'true');
        icon.style.fontSize = '24px';

        const label = document.createElement('p');
        label.innerHTML = item.label; // Using innerHTML to allow HTML content like <br>
        label.className = 'm-0';

        menuItem.appendChild(icon);
        menuItem.appendChild(label);

        menuList.appendChild(menuItem);
    });

    div.appendChild(menuList);
    return div;
}


// Refresh title
function updateHeader(title) {
    const header = document.getElementById('page-title');
    header.classList.add('fade-out');
    setTimeout(() => {
        header.textContent = title;
        header.classList.remove('fade-out');
        header.classList.add('fade-in');
    }, 200);
}

// Refresh content
function updateContent(content) {
    let container = document.getElementById('body-container');
    container.innerHTML = '';
    container.appendChild(content);
    container.classList.add('fade-in');
}

// Refresh nav
function updateMenuSelection(selectedSection) {
    let sections = ['home', 'habitsReview', 'habitsDayReview', 'habitsWeekReview'];

    sections.forEach(section => {
        let icon = document.getElementById(section);
        if (icon) {
            if (section === selectedSection) {
                icon.classList.add('selected-menu-item');
            } else {
                icon.classList.remove('selected-menu-item');
            }
        }
    });
}

// Load sections
async function loadSection(section) {
    let content;
    switch (section) {
        case 'home':
            content = await generateHomeContent();
            break;
        case 'habitsReview':
            content = await generateHabitsContent();
            break;
        case 'habitsDayReview':
            content = await generateHabitsContent('daily');
            break;
        case 'habitsWeekReview':
            content = await generateHabitsContent('weekly');
            break;
        default:
            updateHeader("Section not Available");
            content = genericContent();
            break;
    }
    updateContent(content);
    updateMenuSelection(section);
}

/////////////////////////////////////////

/*
//
// SECTIONS
//
*/

/////////////////////////////////////////

// Generic
function genericContent() {
    let content = document.createElement('div');
    content.textContent = 'Not Available Content, under construction';
    return content;
}

// LOGIN
function handleLogin(result) {
    if (result.success) logged = true;    
    else logged = false;
    loadSection('home'); // Reload the home section to show welcome message
}
// Home
async function generateHomeContent() {
    updateHeader("Home");
    let content = document.createElement('div');

    let loginFormData = {
        type: 'form',
        action: '/login',
        inputs: [
            { type: 'text', name: 'username', placeholder: 'Username' },
            { type: 'password', name: 'password', placeholder: 'Password' },
        ],
        buttonLabel: 'Login',
        onSuccess: function(response) { handleLogin(response) }
    };

    let registerFormData = {
        type: 'form',
        action: '/register',
        inputs: [
            { type: 'text', name: 'username', placeholder: 'Username' },
            { type: 'password', name: 'password', placeholder: 'Password' },
            { type: 'text', name: 'name', placeholder: 'Your Name' },
            { type: 'email', name: 'email', placeholder: 'Email' },
        ],
        buttonLabel: 'Register',
        onSuccess: function(response) { handleLogin(response) }
    }

    // Generate and render content
    if (!logged) contentGenerator.renderContent(content, [{type:'title', text:"Log In"},loginFormData,{type:'separator'},{type:'title', text:"or"},{type:'separator'},{type:'title', text:"Register"}, registerFormData]);
    else contentGenerator.renderContent(content, [{type:'title', text:"WELCOME "+username},{type:'separator'},{type:"parragraph",text:"<i class='fa-solid fa-circle-check' style='color:#73c66f'></i> LOGGED IN"}]);
    return content;
    
}
function generateWelcomeContent(username) {
    let content = document.createElement('div');
    let welcomeMessage = document.createElement('h2');
    welcomeMessage.textContent = `Welcome, ${username}!`;
    content.appendChild(welcomeMessage);
    return content;
}

async function fetchHabitsOptions(type) {
    try {
        let str = '';
        if (type) str = '?type='+type;
        let response = await backendService.sendRequest('/habits'+str, 'GET');
        return response.habits
            .map(habit => ({ value: habit._id, label: `${habit.name} - ${habit.category}` }));
    } catch (error) {
        console.error('Error fetching daily habits:', error);
        return [];
    }
}

function handleAssignedHabit(result) {
    if (result.success) loadSection('dayReview');
    else if (response.error) console.error('Error:', response.error);
    else console.error('Error:', response);
}

// Function to update the habits table
async function updateHabitsTable(type) {
    console.log("username",username)
    return new Promise((resolve, reject) => {
        let data = { username:username, password: password, type:type }
        if (type) data.type = type;
        backendService.sendRequest('/user/habits', 'POST', data)
            .then(response => {
                let rows = [];
                if (response.habits.length) {
                    rows = response.habits.map(habit => {
                        let row = [
                            { type: 'text', value: habit.name },
                            ...(type ? [] : [{ type: 'text', value: habit.type }]),
                            { type: 'text', value: habit.description },
                            { type: 'text', value: habit.status },
                            { type: 'text', value: habit.streak },
                            { type: 'text', value: habit.longest_streak },
                            { type: 'text', value: habit.completion_datetimes?.length || 0 },
                            { type: 'action', value: habit, label: "Manage", btnStyle: 'btn btn-outline-warning', action: onHabitClick }
                        ];
                        return row;
                    });
                }
                resolve(rows);
            })
            .catch(error => {
                console.error('Error fetching habits:', error);
                resolve([]);
            });
    });
}

function onHabitClick(habitData) {
    createHabitPanel(habitData)
    .then(content => {
        const habitModal = new HabitModal('Habit Info',content);
        habitModal.openModal();
        return;
    })
    .catch(error => {
        console.error('Error creating habit panel:', error);
        return;
    });
}
function onAssignNewHabitClick(type) {
    createAssignNewHabit(type)
    .then(content => {
        const habitModal = new HabitModal('Assign New Habit ('+type+')',content);
        habitModal.openModal();
        return;
    })
    .catch(error => {console.error('Error creating habit panel:', error);return; });
}
function onAssignCustomNewHabitClick(type) {
    createAssignNewCustomHabit(type)
    .then(content => {
        const habitModal = new HabitModal('Assign New Custom Habit ('+type+')',content);
        habitModal.openModal();
        return;
    })
    .catch(error => {console.error('Error creating habit panel:', error);return; });
}
function onLongestStreakClick(type) {
    let data = { username:username, password: password, type:type }
    backendService.sendRequest('/user/longest_streak', 'POST', data)
    .then(response => {
        if (response.success)
        {
            createHabitPanel(response.habit)
            .then(content => {
                const habitModal = new HabitModal('Longest Streak Habit',content);
                habitModal.openModal();
                return;
            })
            .catch(error => {
                console.error('Error:', error);
                return;
            });
        } else console.error('Error:', error);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
function onStrugglestClick(type) {
    let data = { username:username, password: password, type:type }
    backendService.sendRequest('/user/strugglest_habit', 'POST', data)
    .then(response => {
        if (response.success)
        {
            createHabitPanel(response.habit)
            .then(content => {
                const habitModal = new HabitModal('Most Struggle Habit',content);
                habitModal.openModal();
                return;
            })
            .catch(error => {
                console.error('Error:', error);
                return;
            });
        } else console.error('Error:', error);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
function onTopHabitsClick(type) {
    
}
function onTopWorstClick(type) {
    
}
// Day Review
async function generateHabitsContent(type) {
    let titleSTR = "Habits Manager";
    if (type) titleSTR = titleSTR + " (" +type + ")";
    updateHeader(titleSTR);
    let content = document.createElement('div');

    let headers;
    if (type) headers = ["Name","Description","Status","Streak","Longest Streak","Total Completions","Expand/Manage"];
    else headers = ["Name","type","Description","Status","Streak","Longest Streak","Total Completions","Expand/Manage"];
    let contentData = {
        "type": "table",
        "headers": headers,
        "rows": logged ? await updateHabitsTable(type) : []
    };


    let menuItems = [];

    if (type) menuItems.push({ label: "Assign New<br>Habit", icon: "fas fa-calendar-plus", action: onAssignNewHabitClick, type:type });
    if (type) menuItems.push({ label: "Assign New<br>Custom Habit", icon: "fas fa-calendar-plus", action: onAssignCustomNewHabitClick, type:type });
    menuItems.push({ label: "Longest Streak<br>Habit", icon: "fas fa-hand-peace", action: onLongestStreakClick, type:type  });
    menuItems.push({ label: "Most Struggle<br>Habit", icon: "fas fa-thumbs-down", action: onStrugglestClick, type:type  });
    
    let menuIcons = createVerticalMenu(menuItems);
    // Render the form and the initially empty table
    let json = [
        {
            cols:2,content:[{type:'div', innerHTML:menuIcons}]
        },
        {
            cols:10,content:[{type:'title', text:"Actual Habits"}, contentData]
        }
    ];

    // Generate and render content
    if (!logged) await contentGenerator.renderContent(content, [{type:'title', text:"Not logged in"},{type:'separator'},{type:'parragraph', text:"Please log in"}]);
    else await contentGenerator.renderMultiColContent(content, json);
    return content;
}
/*
    creators
*/
async function createAssignNewHabit(type) {
    let content = document.createElement('div');

    if (!logged) {
        await contentGenerator.renderContent(content, [{type:'title', text:"Not logged in"},{type:'separator'},{type:'parragraph', text:"Please log in"}]);
        return content;
    } else {
        let optionsArray = await fetchHabitsOptions(type);
        let habitFormData = {
            type: 'form',
            action: '/user/assign_habit',
            inputs: [
                { type: 'hidden', name: 'username', value: username },
                { type: 'hidden', name: 'password', value: password },
                { type: 'hidden', name: 'type', value:type },
                { type: 'select', name: 'habit_id', placeholder: 'Select Habit', options:optionsArray },
                { type: 'date', name: 'start_range', placeholder: 'assign', label:'Start Range' },
                { type: 'date', name: 'end_range', placeholder: 'assign', label: 'End Range' },
            ],
            buttonLabel: 'Assign',
            onSuccess: function(response) { handleAssignedHabit(response); }
        };
        let json = [
            {
                cols:12,content:[habitFormData]
            }
        ];
        await contentGenerator.renderMultiColContent(content, json);
        return content;
    }
}
async function createAssignNewCustomHabit(type) {
    let content = document.createElement('div');

    if (!logged) {
        await contentGenerator.renderContent(content, [{type:'title', text:"Not logged in"},{type:'separator'},{type:'parragraph', text:"Please log in"}]);
        return content;
    } else {
        let habitFormData = {
            type: 'form',
            action: '/user/assign_custom_habit',
            inputs: [
                { type: 'hidden', name: 'username', value: username },
                { type: 'hidden', name: 'password', value: password },
                { type: 'hidden', name: 'type', value:type },
                { type: 'text', name: 'name', placeholder: 'Habit Name' },
                { type: 'text', name: 'category', placeholder: 'Habit Category' },
                { type: 'text', name: 'subcategory', placeholder: 'Habit Sub Category' },
                { type: 'text', name: 'description', placeholder: 'Habit Description' },
                { type: 'date', name: 'start_range', placeholder: 'assign_custom', label:'Start Range' },
                { type: 'date', name: 'end_range', placeholder: 'assign_custom', label: 'End Range' },
            ],
            buttonLabel: 'Assign',
            onSuccess: function(response) { handleAssignedHabit(response); }
        };
        let json = [
            {
                cols:12,content:[habitFormData]
            }
        ];
        await contentGenerator.renderMultiColContent(content, json);
        return content;
    }
}
async function createHabitPanel(habit) {
    let content = document.createElement('div');

    if (!logged) {
        await contentGenerator.renderContent(content, [{type:'title', text:"Not logged in"},{type:'separator'},{type:'parragraph', text:"Please log in"}]);
    } else {
        //habit table
        let habitTable = {
            "type": "table",
            "headers": [],
            "rows": getHabitTable(habit)
        };

        //remove habit
        let habitRemoveFormData = {
            type: 'form',
            action: '/user/remove_habit',
            inputs: [
                { type: 'hidden', name: 'username', value: username },
                { type: 'hidden', name: 'password', value: password },
                { type: 'hidden', name: 'habit_id', value:habit._id },
            ],
            buttonLabel: 'Remove',
            buttonStyle: 'btn btn-outline-danger',
            onSuccess: function(response) { handleHabitCallback(response, habit.type); }
        };

        //complete habit
        let completeEndpointSTR;
        switch (habit.type)
        {
            case 'daily':
                completeEndpointSTR = 'user/update_daily_habit';
                break;
            case 'weekly':
                completeEndpointSTR = 'user/update_weekly_habit';
                break;
        }

        let habitCompleteFormData = {
            type: 'form',
            action: completeEndpointSTR,
            inputs: [
                { type: 'hidden', name: 'username', value: username },
                { type: 'hidden', name: 'password', value: password },
                { type: 'hidden', name: 'habit_id', value:habit._id },
                { type: 'hidden', name: 'continue_habit', value:true },
                { type: 'date', name: 'completion_date', placeholder: 'complete', label:'Completion Date' },
            ],
            buttonLabel: 'Complete',
            buttonStyle: 'btn btn-outline-success',
            onSuccess: function(response) { handleHabitCallback(response, habit.type); }
        };

        let json = [
            {
                cols:12,content:[habitTable]
            },
            {
                cols:12,content:[{ type:'title', text:"Remove Habit", align:"left" }],
            },
            {
                cols:12,content:[habitRemoveFormData]
            },
            {
                cols:12,content:[{type:'separator'},{ type:'title', text:"Complete Habit", align:"left" }]
            },
            {
                cols:12,content:[habitCompleteFormData]
            }
        ];
        await contentGenerator.renderMultiColContent(content, json);
    }
    return content;
}
// Function to update the habits table
function getHabitTable(habit) {
    let rows = []

    if (habit.name) rows.push([{type:'text',value:"Name",align:"right"},{type:'text',value:habit.name,align:"left"}]);
    if (habit.category) rows.push([{type:'text',value:"Category",align:"right"},{type:'text',value:habit.category,align:"left"}]);
    if (habit.subcategory) rows.push([{type:'text',value:"Sub Category",align:"right"},{type:'text',value:habit.subcategory,align:"left"}]);
    if (habit.description) rows.push([{type:'text',value:"Description/Task Specification",align:"right"},{type:'text',value:habit.description,align:"left"}]);

    if (habit.creation_date) rows.push([{type:'text',value:"Creation Date",align:"right"},{type:'text',value:habit.creation_date,align:"left"}]);

    if (habit.start_range) rows.push([{type:'text',value:"Expected Start Range Date",align:"right"},{type:'text',value:habit.start_range,align:"left"}]);
    if (habit.end_range) rows.push([{type:'text',value:"Expected End Range Date",align:"right"},{type:'text',value:habit.end_range,align:"left"}]);

    if (habit.completion_datetime) rows.push([{type:'text',value:"Last Completion Date",align:"right"},{type:'text',value:habit.completion_datetime,align:"left"}]);

    if (habit.status) rows.push([{type:'text',value:"Actual Status",align:"right"},{type:'text',value:habit.status,align:"left"}]);

    if (habit.streak) rows.push([{type:'text',value:"Actual Streak",align:"right"},{type:'text',value:habit.streak,align:"left"}]);
    if (habit.longest_streak) rows.push([{type:'text',value:"Longest Streak",align:"right"},{type:'text',value:habit.longest_streak,align:"left"}]);

    if (habit.completion_datetimes) rows.push([{type:'text',value:"Total Times Completed",align:"right"},{type:'text',value:habit.completion_datetimes.length,align:"left"}]);

    return rows;
}

function handleHabitCallback(result, type) {
    if (result.success) loadSection('dayReview');
    else if (response.error) console.error('Error:', response.error);
    else console.error('Error:', response);
}

//
// END OF CODE
//

$(document).ready(function () { loadSection('home') });