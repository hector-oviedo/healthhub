import os
from data_simulator import DataSimulator

mongo_auth_enabled = os.environ.get('MONGO_AUTH_ENABLED', 'false').lower() == 'true'
mongo_username = os.environ.get('MONGO_USERNAME', 'admin')
mongo_password = os.environ.get('MONGO_PASSWORD', 'admin1234')
mongo_host = os.environ.get('MONGO_HOST', 'localhost')
mongo_port = os.environ.get('MONGO_PORT', '27017')
mongo_db_name = os.environ.get('DB_NAME', 'healthhub')
mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db_name}?authSource=admin" if mongo_auth_enabled else f"mongodb://{mongo_host}:{mongo_port}/{mongo_db_name}"

class InteractiveDataSimulator:
    def __init__(self):
        self.config_file = self.get_input("Path to test data config file [default: 'data/test_data_config.json']:", 'data/test_data_config.json')
        self.success_probability = float(self.get_input("Success probability on simulated habits Float (0 - 1) [default: '0.8']: ", '0.8'))
        self.interactions_path = self.get_input("Path of Log file for storage all interactions simulating: habits assignment and completion for test user: [default: 'data/interactions.json']: ", 'data/interactions.json')
        self.mongo_host = self.get_input("MongoDB Host [default: 'localhost']: ", 'localhost')
        self.mongo_port = self.get_input("MongoDB Port [default: '27017']: ", '27017')
        self.mongo_db_name = self.get_input("Database Name [default: 'healthhub']: ", 'healthhub')

    def get_input(self, prompt, default):
        return input(f"{prompt} [default: '{default}']: ") or default

    def run(self):
        print("Please wait, this process may take a while. Do not close the application...")
        simulator = DataSimulator(
            mongo_uri=mongo_uri,
            mongo_db_name=mongo_db_name,
            config_file=self.config_file,
            success_probability=self.success_probability,
            interactions_path=self.interactions_path
        )
        success = simulator.run_simulation()
        if success:
            print("Data simulation completed successfully.")
        else:
            print("Data simulation encountered errors.")

if __name__ == "__main__":
    print("Press Enter to use default values in each interaction.")
    interactive_simulator = InteractiveDataSimulator()
    interactive_simulator.run()