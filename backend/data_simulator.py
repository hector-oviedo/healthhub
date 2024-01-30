import datetime
import random
import json
from werkzeug.security import generate_password_hash
from pymongo import MongoClient, errors

from classes.mongodb_handler import MongoDBHandler
from classes.habit_tracker import HabitTracker

class DataSimulator:
    def __init__(self, mongo_uri, mongo_db_name, config_file='data/test_data_config.json', success_probability=0.8, interactions_path='data/interactions.json'):
        self.config_file = config_file
        self.success_probability = success_probability
        self.interactions_path = interactions_path
        self.mongo_uri = mongo_uri
        self.mongo_db_name = mongo_db_name
    def load_test_data_config(self, config_file):
        try:
            with open(config_file, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    def create_predefined_habits(self, db_handler, habits):
        required_fields = {'name', 'type', 'category', 'subcategory', 'description'}
        valid_types = {'daily', 'weekly'}
        try:
            for habit in habits:
                if not required_fields.issubset(habit):
                    missing_fields = required_fields - habit.keys()
                    print(f"Error (create_predefined_habits): Habit missing required fields: {', '.join(missing_fields)}")
                    return False
                if habit['type'] not in valid_types:
                    print(f"Error (create_predefined_habits): Invalid habit type '{habit['type']}'. Type must be either 'daily' or 'weekly'.")
                    return False
                if not db_handler.find_document('habits', {'name': habit['name']}):
                    added_habit = db_handler.add_document('habits', habit)
                    print(f"INFO: Habit '{habit['name']}' created: {added_habit['_id']}")
                else:
                    print(f"ERROR: Habit '{habit['name']}' already exists.")
                    return False
            print("INFO: Predefined habits processing completed.")
            return True
        except Exception as e:
            print(f"Error (create_predefined_habits): {e}")
            return False
    def create_user(self, mongo_db, user_data):
        required_keys = {'username', 'password', 'email', 'name'}
        if not required_keys.issubset(user_data):
            print("Error (create_user): User data in JSON config must contain username, password, email, and name.")
            return False
        user_collection = mongo_db['users']
        try:
            user = user_collection.find_one({'username': user_data['username']})
            if not user:
                hashed_password = generate_password_hash(user_data['password'], method='pbkdf2:sha256')
                user_data['password'] = hashed_password

                user_collection.insert_one(user_data)
                print("INFO: User created.")
                return True
            else:
                print("ERROR: User already exists.")
                return False
        except Exception as e:
            print(f"Error (create_user) creating test user: {e}")
            return False
    def simulate_daily_interactions(self, config, db_handler, habit_tracker, success_probability):
        def random_success_probability(success_rate):
            return random.random() < success_rate
        def get_appropriate_completion_date(current_date, habit, is_successful):
            start_range = datetime.datetime.strptime(habit['start_range'], '%Y-%m-%d %H:%M')
            end_range = datetime.datetime.strptime(habit['end_range'], '%Y-%m-%d %H:%M')

            if is_successful:
                successful_completion_date = start_range + datetime.timedelta(minutes=1)
                return successful_completion_date.strftime('%Y-%m-%d %H:%M')
            else:
                failed_completion_date = end_range + datetime.timedelta(hours=1)
                return failed_completion_date.strftime('%Y-%m-%d %H:%M')
        def get_datetime_range(start_time, end_time):
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            start_range = datetime.datetime.now().replace(hour=start_hour, minute=start_minute)
            end_range = datetime.datetime.now().replace(hour=end_hour, minute=end_minute)
            return start_range.strftime('%Y-%m-%d %H:%M'), end_range.strftime('%Y-%m-%d %H:%M')
        user_data = config['test_user']
        simulation_config = config['simulation']
        user = db_handler.find_document('users', {'username': user_data['username']})
        if not user:
            print("Error: Test user not found.")
            return False
        interactions_log = []
        predefined_habits = db_handler.list_documents('habits')
        for habit in predefined_habits:
            time_range = simulation_config['habit_time_ranges'][habit['name']]
            start_time, end_time = time_range['start'], time_range['end']
            start_range, end_range = get_datetime_range(start_time, end_time)
            habit_tracker.assign_habit(user_data['username'], habit['_id'], start_range, end_range)
        for habit in simulation_config['custom_habits']:
            start_time, end_time = habit['start'], habit['end']
            start_range, end_range = get_datetime_range(start_time, end_time)
            habit_tracker.assign_custom_habit(user_data['username'], habit['name'], habit['type'], start_range, end_range, habit['category'], habit['subcategory'], habit['description'])
        for day in range(simulation_config['expected_simulated_time']):
            assigned_habits = habit_tracker.list_user_habits(user_data['username'])['habits']
            for habit in assigned_habits:
                if habit['type'] == 'daily' or (habit['type'] == 'weekly' and day % 7 == 0):
                    is_successful = random_success_probability(success_probability)
                    current_date = datetime.datetime.strptime(habit['start_range'], '%Y-%m-%d %H:%M')
                    continue_enabled = True
                    completion_date = get_appropriate_completion_date(current_date, habit, is_successful)
                    completion_method = habit_tracker.update_daily_habit if habit['type'] == 'daily' else habit_tracker.update_weekly_habit
                    completion_result = completion_method(user_data['username'], habit['_id'], completion_date, continue_enabled)
                    interactions_log.append({'action': 'complete', 'habit': habit['name'], 'result': completion_result})
        return interactions_log
    def run_simulation(self):
        def save_interactions_to_json(interactions, filename):
            with open(filename, 'w') as file:
                json.dump(interactions, file, indent=4)
            print(f"Interactions saved to {filename}.")
        mongo_client = MongoClient(self.mongo_uri)
        mongo_db = mongo_client[self.mongo_db_name]

        db_handler = MongoDBHandler(self.mongo_uri, self.mongo_db_name)
        habit_tracker = HabitTracker(db_handler)

        config = self.load_test_data_config(self.config_file)

        if not config:
            print("(data_simulator) Failed to load configuration.")
            return False
        if not self.create_user(mongo_db, config['test_user']):
            print("(data_simulator) Failed to create user.")
            return False
        if not self.create_predefined_habits(db_handler, config['habits']):
            print("(data_simulator) Failed to create predefined habits.")
            return False
        interactions = self.simulate_daily_interactions(config, db_handler, habit_tracker, self.success_probability)
        if not interactions:
            print("(data_simulator) Failed to simulate daily interactions.")
            return False
        save_interactions_to_json(interactions, self.interactions_path)
        return True

def main():
    simulator = DataSimulator()
    if simulator.run_simulation():
        print("Simulation completed successfully")
    else:
        print("Simulation encountered errors")

if __name__ == "__main__":
    main()