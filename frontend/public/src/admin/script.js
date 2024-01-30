backendService = new BackendService(backendUrl);
contentGenerator = new ContentGenerator();

var admin_username = "admin";
var admin_password = "admin1234";
var admin_validated = true;

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
    let sections = ['home','users', 'habits'];

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
    let containerBody = document.getElementById('body-container');
    containerBody.innerHTML = 'Loading...';

    let content;
    switch (section) {
        default:
            updateHeader("Section not Available");
            content = await genericContent();
            break;
        case 'home':
            content = await generateHomeContent();
            break;
        case 'users':
            content = await generateUsersContent();
            break;
        case 'habits':
            content = await generateHabitsContent();
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
async function onAdminLogIn(response) {
    console.log('response',response.validated)
    if (response.validated) admin_validated = true;
    else admin_validated = false;

    loadSection('home')
}
// Home
async function generateHomeContent() {
    updateHeader("Home");
    let content = document.createElement('div');

    let loginFormData = {
        type: 'form',
        action: 'admin/validate',
        inputs: [
            { type: 'text', name: 'username', placeholder: 'Admin Username' },
            { type: 'password', name: 'password', placeholder: 'Admin Password' }
        ],
        buttonLabel: 'Login',
        onSuccess: function(response) { onAdminLogIn(response) }
    };
    // Generate and render content
    if (!admin_validated) contentGenerator.renderContent(content, [{type:'title', text:"LOG IN"},{type:'separator'},loginFormData]);
    else contentGenerator.renderContent(content, [{type:'title', text:"ADMIN AUTHORIZED"},{type:'separator'},{type:"parragraph",text:"<i class='fa-solid fa-circle-check' style='color:#73c66f'></i> LOGGED IN"}]);
    return content;
}

// Users
async function generateUsersContent() {
    updateHeader("Users Manager");
    let content = document.createElement('div');

    let contentData = {
        "type": "table",
        "headers": ["User Name","Email","Name","Action"],
        "rows": await updateUsersTable()
    };

     // Render the form and the initially empty table
     if (!admin_validated) contentGenerator.renderContent(content, [{type:'title', text:"Not logged in"},{type:'separator'},{type:'parragraph', text:"Please log in"}]);
     else contentGenerator.renderContent(content, [{type:'title', text:"Users"}, contentData]);
     return content;
}
// Remove User
async function onUserRemove(userId) {
    let containerBody = document.getElementById('body-container');
    containerBody.innerHTML = 'Loading...';
    try {
        await backendService.sendRequest('/user/delete', 'DELETE', { _id: userId, username:admin_username, password:admin_password });
        loadSection('users');  // Refresh the users list
    } catch (error) {
        console.error('Error removing user:', error);
        loadSection('users');  // Refresh the users list
    }
}
// Users
async function updateUsersTable() {
    return new Promise((resolve, reject) => {
        backendService.sendRequest('/users', 'GET', { username:admin_username, password: admin_password })
            .then(response => {
                let rows = response.users.map(user => [
                    {type:'text',value:user.username},
                    {type:'text',value:user.email},
                    {type:'text',value:user.name},
                    {type:'action',value:user._id, label:"Remove", action:onUserRemove}
                ]);  
                resolve(rows);
            })
            .catch(error => {
                console.error('Error fetching habits:', error);
                reject([]); // Reject with an empty array in case of an error
            });
    });
}

// Habits
async function generateHabitsContent() {
    updateHeader("Habits Manager");
    let content = document.createElement('div');

    let habitFormData = {
        type: 'form',
        action: '/habit/add',
        inputs: [
            { type: 'hidden', name: 'username', value: admin_username },
            { type: 'hidden', name: 'password', value: admin_password },
            { type: 'text', name: 'name', placeholder: 'Habit Name' },
            { type: 'select', name: 'type', placeholder: 'Habit Type', options:[{value:'daily',label:'Daily'},{value:'weekly',label:'Weekly'}]},
            { type: 'text', name: 'category', placeholder: 'Habit Category' },
            { type: 'text', name: 'subcategory', placeholder: 'Habit Sub Category' },
            { type: 'text', name: 'description', placeholder: 'Habit Description' }
        ],
        buttonLabel: 'Create',
        onSuccess: function(response) { loadSection('habits'); }
    };

    let contentData = {
        "type": "table",
        "headers": ["Name","Type","Description","Category","Sub-Category","Action"],
        "rows": await updateHabitsTable()
    };

     // Render the form and the initially empty table
     if (!admin_validated) contentGenerator.renderContent(content, [{type:'title', text:"Not logged in"},{type:'separator'},{type:'parragraph', text:"Please log in"}]);
     else contentGenerator.renderContent(content, [{type:'title', text:"Create new Habit", align:"left"}, habitFormData, {type:'title', text:"Actual Habits"}, contentData]);
     return content;
}

// Remove Habit
async function onHabitRemove(habitId) {
    let containerBody = document.getElementById('body-container');
    containerBody.innerHTML = 'Loading...';
    try {
        await backendService.sendRequest('/habit/remove', 'DELETE', { _id: habitId, username:admin_username, password:admin_password });
        loadSection('habits');  // Refresh the habits list
    } catch (error) {
        console.error('Error removing habit:', error);
        loadSection('habits');  // Refresh the habits list
    }
}
// Function to update the habits table
async function updateHabitsTable() {
    return new Promise((resolve, reject) => {
        backendService.sendRequest('/habits', 'GET')
            .then(response => {
                let rows = response.habits.map(habit => [
                    {type:'text',value:habit.name},
                    {type:'text',value:habit.type},
                    {type:'text',value:habit.description},
                    {type:'text',value:habit.category},
                    {type:'text',value:habit.subcategory},
                    {type:'action',value:habit._id, label:"Remove", action:onHabitRemove}
                ]);  
                resolve(rows);
            })
            .catch(error => {
                console.error('Error fetching habits:', error);
                reject([]); // Reject with an empty array in case of an error
            });
    });
}



//
// END OF CODE
//

$(document).ready(function () { loadSection('home') });