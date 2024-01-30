import os
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from classes.mongodb_handler import MongoDBHandler
from classes.user import User
from classes.habit import Habit
from classes.utils import Utils
from classes.habit_tracker import HabitTracker
from data_simulator import DataSimulator

# BACKEND PORT
backend_port = os.environ.get('BACKEND_PORT', '5000')

# Admin account details
admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
admin_password = os.environ.get('ADMIN_PASSWORD', 'admin1234')
admin_password_hash = generate_password_hash(admin_password, method='pbkdf2:sha256')

# Database configuration
mongo_auth_enabled = os.environ.get('MONGO_AUTH_ENABLED', 'false').lower() == 'true'
mongo_username = os.environ.get('MONGO_USERNAME', 'admin')
mongo_password = os.environ.get('MONGO_PASSWORD', 'admin1234')
mongo_host = os.environ.get('MONGO_HOST', 'localhost')
mongo_port = os.environ.get('MONGO_PORT', '27017')
mongo_db_name = os.environ.get('DB_NAME', 'healthhub')
mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db_name}?authSource=admin" if mongo_auth_enabled else f"mongodb://{mongo_host}:{mongo_port}/{mongo_db_name}"

# Simulation settings
config_file = os.environ.get('SIMULATION_CONFIG_FILE', 'data/test_data_config.json')
success_probability = float(os.environ.get('SIMULATION_SUCCESS_PROBABILITY', '0.8'))
interactions_path = os.environ.get('SIMULATION_INTERACTIONS_PATH', 'data/interactions.json')

# Utility function
def is_admin_authenticated(request):
    """
    Check if the admin credentials provided in the request are valid.

    This function extracts the username and password from the authorization header of the HTTP request.
    It then compares these credentials against predefined admin credentials.

    Args:
        request (Request): The Flask request object, containing the authorization header.

    Returns:
        bool: True if the provided credentials match the admin credentials, False otherwise.

    Note:
        It expects the credentials to be provided in the standard HTTP Basic Auth format.
    """
    admin_user = request.authorization.username if request.authorization else ''
    admin_pass = request.authorization.password if request.authorization else ''
    return admin_user == admin_username and check_password_hash(admin_password_hash, admin_pass)

# Flask app initialization and CORS setup
app = Flask(__name__)

# TODO: This should allow only the correct origin
CORS(app, resources={r"/*": {"origins": "*"}})

# create instance of mongodb handler
db_handler = MongoDBHandler(mongo_uri, mongo_db_name)

###############
# ADMIN methods
###############

# Verifies ADMIN
@app.route('/admin/validate', methods=['POST'])
def validate_admin():
    """
    Endpoint to validate admin access.

    This function checks if the request contains valid admin credentials and responds with a success status.
    It is used as an access control mechanism for admin-specific operations.

    Utilizes the `is_admin_authenticated` utility to verify credentials in the request's authorization header.

    Returns:
        JSONResponse: A JSON response indicating the result of the validation. The response contains:
                      - 'success' (bool): True if credentials are valid, False if invalid.
                      - 'error' (str, optional): Error message if access is unauthorized.

    Note:
        This endpoint is protected and requires HTTP Basic Auth credentials for access.
        Credentials must be those of an administrator. Responses include HTTP status code 401 (Unauthorized)
        for invalid credentials.
    """
    if not is_admin_authenticated(request):
        return jsonify({"success": False, "error": "Unauthorized access"}), 401
    return jsonify({"success": True})

# API Delete User
@app.route('/user/delete', methods=['DELETE'])
def delete_user():
    if not is_admin_authenticated(request):
        return jsonify({"success": False, "error": "Unauthorized access"}), 401
    data = Utils.normalize_auth_credentials(request)
    user_id = data.get('_id')
    return jsonify(User().delete(db_handler, user_id))

# API Users List
@app.route('/users', methods=['GET'])
def list_users():
    if not is_admin_authenticated(request):
        return jsonify({"success": False, "error": "Unauthorized access"}), 401
    return jsonify(User().list_all(db_handler))

# API Add Habit
@app.route('/habit/add', methods=['POST'])
def add_habit():
    if not is_admin_authenticated(request):
        return jsonify({"success": False, "error": "Unauthorized access"}), 401
    data = Utils.normalize_auth_credentials(request)
    habit = Habit()
    return jsonify(habit.add_habit(db_handler, data))

# API Remove Habit
@app.route('/habit/remove', methods=['DELETE'])
def remove_habit():
    if not is_admin_authenticated(request):
        return jsonify({"success": False, "error": "Unauthorized access"}), 401
    data = Utils.normalize_auth_credentials(request)
    habit_id = data.get('_id')
    return jsonify(Habit().remove(db_handler, habit_id))

##############
# User Methods
##############

# API Register
@app.route('/register', methods=['POST'])
def register_user():
    data = Utils.normalize_auth_credentials(request)
    # Check if email and name are present
    if not data.get('email') or not data.get('name'):
        return jsonify({"success": False, "error": "Missing email or name"}), 400 # Bad Request error

    
    new_user = User(username=data.get('username'), password=data.get('password'), email=data.get('email'), name=data.get('name'))
    return jsonify(new_user.register(db_handler))

# API Login
@app.route('/login', methods=['POST'])
def login_user():
    data = Utils.normalize_auth_credentials(request)
    user = User(username=data.get('username'), password=data.get('password'))
    return jsonify(user.login(db_handler))

# API List pre setted habits (no auth required)
@app.route('/habits', methods=['GET'])
def list_habits():
    habit_type = request.args.get('type')
    if habit_type:
        return jsonify(Habit.list_all(db_handler, type=habit_type))
    else:
        return jsonify(Habit.list_all(db_handler))

##########################################
# User Engine Methods (habitTracker Class)
##########################################

# List habits assigned to User
@app.route('/user/habits', methods=['POST'])
def list_habits_from_user():
    try:
        username, error = Utils.authenticate_user(request, db_handler)
        if error:
            return jsonify({"success": False, "error": error}), 401

        habit_tracker = HabitTracker(db_handler)

        data = Utils.normalize_auth_credentials(request)
        type = data.get('type')
        return jsonify(habit_tracker.list_user_habits(username,type))
    except Exception as e:
        return jsonify({"success": False, 'error': 'An error occurred', 'details': str(e)}), 500

# Assign Habit (pre setted habit) to User Endpoint
@app.route('/user/assign_habit', methods=['POST'])
def assign_habit_to_user():
    """ Assign a pre setted habit to a user. """
    username, error = Utils.authenticate_user(request, db_handler)
    if error:
        return jsonify({"success": False, "error": error}), 401

    data = Utils.normalize_auth_credentials(request)
    habit_id = data.get('habit_id')
    start_range = data.get('start_range')
    end_range = data.get('end_range')

    if not all([username, habit_id, start_range, end_range]):
        return jsonify({"success": False, 'error': 'Missing required fields (username, habit_id, start_range, end_range)'}), 400

    habit_tracker = HabitTracker(db_handler)
    return jsonify(habit_tracker.assign_habit(username, habit_id, start_range, end_range))

# Assign Custom Habit to User Endpoint
@app.route('/user/assign_custom_habit', methods=['POST'])
def assign__custom_habit_to_user():
    """Assign a custom habit to a user."""
    username, error = Utils.authenticate_user(request, db_handler)
    if error:
        return jsonify({"success": False, "error": error}), 401
    
    data = Utils.normalize_auth_credentials(request)

    # Habit content
    name = data.get('name') # required
    type = data.get('type') # required (verify habit_tracker.py)
    start_range = data.get('start_range')
    end_range = data.get('end_range')
    category = data.get('category', '') # optional
    subcategory = data.get('subcategory', '') # optional
    description = data.get('description', '') # optional

    if not all([username, name, type, start_range, end_range]):
        return jsonify({"success": False, 'error': 'Missing required fields (username, name, type, start_range, end_range)'}), 400

    habit_tracker = HabitTracker(db_handler)
    result = habit_tracker.assign_custom_habit(username, name, type, start_range, end_range, category, subcategory, description)
    return jsonify(result)

# Remove Habit from User Endpoint
@app.route('/user/remove_habit', methods=['POST'])
def remove_habit_from_user():
    """Remove a habit from a user."""
    username, error = Utils.authenticate_user(request, db_handler)
    if error:
        return jsonify({"success": False, "error": error}), 401

    data = Utils.normalize_auth_credentials(request)

    habit_id = data.get('habit_id')

    if not username or not habit_id:
        return jsonify({"success": False, 'error': 'Username and habit_id are required'}), 400

    habit_tracker = HabitTracker(db_handler)
    result = habit_tracker.remove_habit(username, habit_id)

    return jsonify(result)

#
# Habit Complete Methods
# NOTE: Most important logic here, calculates streaks, modifies status, modifies dates, and other logical operations
#

# Complete daily Habit Endpoint
@app.route('/user/update_daily_habit', methods=['POST'])
def update_daily_habit_from_user():
    """Update the a user's habit."""
    username, error = Utils.authenticate_user(request, db_handler)
    if error:
        return jsonify({"success": False, "error": error}), 401

    data = Utils.normalize_auth_credentials(request)
    habit_id = data.get('habit_id') # required
    completion_date = data.get('completion_date') # required
    continue_habit = data.get('continue_habit', True) # optional

    if not all([username, habit_id, completion_date]):
        return jsonify({"success": False, 'error': 'Username, habit_id, and completion_date are required'}), 400

    # Validate date
    try:
        datetime.datetime.strptime(completion_date, '%Y-%m-%d %H:%M')
    except ValueError:
        return {'success': False, 'error': 'Invalid date format. Date should be in YYYY-MM-DD HH:MM format.'}
    except TypeError:
        return {'success': False, 'error': 'Missing completion_date.'}

    habit_tracker = HabitTracker(db_handler)
    result = habit_tracker.update_daily_habit(username, habit_id, completion_date, continue_habit)

    return jsonify(result)
# Complete weekly Habit Endpoint
@app.route('/user/update_weekly_habit', methods=['POST'])
def update_weekly_habit_from_user():
    """Update the a user's habit."""
    username, error = Utils.authenticate_user(request, db_handler)
    if error:
        return jsonify({"success": False, "error": error}), 401

    data = Utils.normalize_auth_credentials(request)
    habit_id = data.get('habit_id') # required
    completion_date = data.get('completion_date') # required
    continue_habit = data.get('continue_habit', False) # optional

    if not all([username, habit_id, completion_date]):
        return jsonify({"success": False, 'error': 'Username, habit_id, and completion_date are required'}), 400

    # Validate date
    try:
        datetime.datetime.strptime(completion_date, '%Y-%m-%d %H:%M')
    except ValueError:
        return {'success': False, 'error': 'Invalid date format. Date should be in YYYY-MM-DD HH:MM format.'}
    except TypeError:
        return {'success': False, 'error': 'Missing completion_date.'}

    habit_tracker = HabitTracker(db_handler)
    result = habit_tracker.update_weekly_habit(username, habit_id, completion_date, continue_habit)

    return jsonify(result)

#
# User Analytics Methods
#

# Get Habit with Longest Streak
@app.route('/user/longest_streak', methods=['POST'])
def longest_streak():
    try:
        username, error = Utils.authenticate_user(request, db_handler)
        if error:
            return jsonify({"success": False, "error": error}), 401

        habit_tracker = HabitTracker(db_handler)

        data = Utils.normalize_auth_credentials(request)
        type = data.get('type')
        return jsonify(habit_tracker.longest_streak_habit(username,type))
    except Exception as e:
        return jsonify({"success": False, 'error': 'An error occurred', 'details': str(e)}), 500
# Get most Struggle Habit
@app.route('/user/strugglest_habit', methods=['POST'])
def strugglest_habit():
    try:
        username, error = Utils.authenticate_user(request, db_handler)
        if error:
            return jsonify({"success": False, "error": error}), 401

        habit_tracker = HabitTracker(db_handler)

        data = Utils.normalize_auth_credentials(request)
        type = data.get('type')
        return jsonify(habit_tracker.strugglest_habit(username,type))
    except Exception as e:
        return jsonify({"success": False, 'error': 'An error occurred', 'details': str(e)}), 500
# Execute data simulation
def run_data_simulation():
    # Create and run the data simulator using global variables for MongoDB settings
    simulator = DataSimulator(mongo_uri=mongo_uri,
                              mongo_db_name=mongo_db_name,
                              config_file=config_file,
                              success_probability=success_probability,
                              interactions_path=interactions_path)
    success = simulator.run_simulation()
    if success:
        print("Data simulation completed successfully.")
    else:
        print("Data simulation encountered errors.")

# Run the data simulation before starting the Flask app
run_data_simulation()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=backend_port, debug=True)