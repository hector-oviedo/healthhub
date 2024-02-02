## HealthHub: A Habit Tracking Application
HealthHub is a university project developed for the IU University's object-oriented Python module. This habit tracking application is designed to help users establish, track, and analyze their daily habits. Built with a Python Flask backend, NodeJS frontend, and MongoDB database.

## Quick Start
This project supports setup using Docker Compose for ease of deployment, as well as manual setup for each component. Below are the instructions for both methods.

### Using Docker Compose
- Prerequisites: Ensure Docker and Docker Compose are installed on your machine.
- Configuration: Set up the required `.env` variables.
- Starting the Application: Run `docker-compose up` from the root directory to start all services.

## Manual Setup
If you prefer not to use Docker, follow these steps to manually set up each component:

### MongoDB (Version 5.0 Recommended)
- Installation: Install MongoDB and ensure it's running on your system.
- Configuration: Use the `.env` variables for MongoDB settings. When not using Docker, set `MONGO_AUTH_ENABLED=false` and `MONGO_HOST=localhost`.

### Python Backend (Python 3.12 Recommended)
- Environment: It's recommended to create a virtual environment and install dependencies from `requirements.txt`.
- Running: Execute `python app.py` in the backend directory to start the Flask server.

### NodeJS Frontend (Node 18 Stable)
- Setup: Navigate to the frontend directory and install dependencies with `npm install`.
- Running: Start the frontend by running `npm start`.

## Environmental Variables

Here's a breakdown of the .env variables used in HealthHub:

- `MONGO_*` variables are for MongoDB configuration.
- `ADMIN_USERNAME` and `ADMIN_PASSWORD` are for backend admin access.
- `BACKEND_PORT` and `FRONTEND_PORT` set the ports for the backend and frontend services.
- `SIMULATION_*` variables relate to the data simulation script for generating test data.

## Usage

Once both the backend and frontend are operational, you should see messages indicating that they are running correctly. For the frontend, look for a message similar to "Frontend running at http://localhost:3000". The backend should indicate it's running on multiple addresses, including http://127.0.0.1:5000 and potentially others, along with logs for other activities, an active debugger, and a debugger PIN.

After setup, access the application by navigating to `http://localhost:3000/admin` for the admin interface and `http://localhost:3000` for the user interface in your web browser.

## Data Simulation

To meet the project's requirement for 4 weeks of simulated data, a Python script is included (`backend/data_simulator.py`) to generate test data based on the provided configuration in `data/test_data_config.json`.

## Features

HealthHub's flexibility supports only daily and weekly habits currently, but the architecture is designed for easy expansion to include more types. The analytical component of the app provides feedback on habit performance, aiding users in their personal development journey.
HealthHub is designed to allow both administrators and users with specific functionalities to their roles:

### For Administrators:

- User Management: Remove users from the application.
- Habit Management: Add/remove pre-defined habits to better usage of the application to the user base.

### For Users:

- Account Management: Register as a new user and log in to access personalized habit tracking.
- Habit Assignment: Choose from pre-defined habits set by the admin or create custom habits unique to each user.
- Habit Tracking: Mark habits as completed with a specified completion date, enabling the app to generate data for analysis.

#### User Analysis Tools:

- Track all habits or filter by daily and weekly habits.
- Identify the habit with the highest streak and understand habit completion patterns.
- Determine which habit is most challenging, indicating areas where the user may struggle the most.

# Project Structure

## Root Directory
```
/
├── docker-compose.yml
├── envTEMPLATE
├── README.md
├── backend/
└── frontend/
```
## Backend Structure
```
backend/
│
├── classes/
│ ├── habit_tracker.py
│ ├── habit.py
│ ├── mongodb_handler.py
│ ├── user.py
│ └── utils.py
│
├── data/
│ ├── interactions.json
│ └── test_data_config.json
│
├── app.py
├── data_simulator.py
├── Dockerfile
└── requirements.txt
```
## Frontend Structure
```
frontend/
│
├── public/
│ ├── css/
│ │ ├── all.min.js
│ │ ├── bootstrap.min.css
│ │ ├── bootstrap.min.css.map
│ │ └── styles.css
│ │
│ ├── libs/
│ │ ├── all.min.js # Font Awesome 6.4.0
│ │ ├── bootstrap.min.js # Bootstrap 5.3.2
│ │ ├── bootstrap.min.js.map
│ │ ├── jquery.min.js # jQuery 3.6.4
│ │ └── jquery.min.js.map
│ │
│ ├── src/
│ │ ├── admin/
│ │ │ └── script.js
│ │ ├── app/
│ │ │ ├── habit.modal.js
│ │ │ └── script.js
│ │ ├── content.manager.js
│ │ ├── services.js
│ │ └── utils.js
│ │
│ ├── webfonts/ # Folder with web fonts
│ ├── favicon
│ └── views/
│ ├── index.ejs
│ └── admin.ejs
│
├── app.js
├── Dockerfile
├── package-lock.json
└── package.json
```
### Notes

- Ensure to review and update the Docker configurations and dependencies as per your project requirements.
- The `envTEMPLATE` file should be copied and renamed to `.env`, filling in the necessary environment variables for your application.
- Refer to the documentation within each directory for specific setup and usage instructions.
