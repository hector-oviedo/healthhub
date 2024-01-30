from werkzeug.security import check_password_hash, generate_password_hash
from classes.mongodb_handler import MongoDBHandler
from classes.utils import Utils

class User:
    def __init__(self, username=None, password=None, email=None, name=None, _id=None):
        """
        Initialize a new user object.

        Args:
            username (str): The username of the user.
            password (str): The account password.
            email (str): The email of the user.
            name (str): The name of the user.
            _id (str): The unique identifier of the user.
        """
        self.username = username
        self.password = password
        self.email = email
        self.name = name
        self._id = _id
    # register User
    def register(self, db_handler):
        """
        Register a new user in the database.

        Args:
            db_handler (MongoDBHandler): The database handler for interacting with the database.

        Returns:
            dict: A dictionary containing the following keys:
                - 'success' (bool): Indicates whether the registration was successful.
                - 'data' (dict, optional): The registered user data if registration succeeds.
                - 'error' (str, optional): An error message if registration fails.

        Note:
            The method checks for missing fields, existing username or email, and then registers the user.
            It returns a user data object on successful registration or an error message on failure.
        """

        # Check for missing fields directly in request data
        if not all([self.username, self.email, self.name, self.password]):
            return {'success': False, 'error': 'All fields (username, email, name, password) are required'}
        
        # Check if username already exists
        if db_handler.find_document('users', {'username': self.username}):
            return {'success': False, 'error': 'Username already exists'}
        
        # Check if email already exists
        if db_handler.find_document('users', {'email': self.email}):
            return {'success': False, 'error': 'Email already exists'}

        # Hash the password for security
        hashed_password = generate_password_hash(self.password, method='pbkdf2:sha256')

        # Prepare User object
        user_data = {
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'password': hashed_password
        }

        # Add the new user to the database
        try:
            result = db_handler.add_document('users', user_data)
            return {
                'success': True,
                'data': {
                    '_id': result.get('_id'),
                    'name': result.get('name'),
                    'username': result.get('username')
                }
            }
        except Exception as e:
            return {'success': False, 'error': f'An error occurred during registration: {str(e)}'}
    # log-in User
    def login(self, db_handler):
        """
        Login a user.

        Args:
            db_handler (MongoDBHandler): The database handler for interacting with the database.

        Returns:
            dict: A dictionary containing the following keys:
                - 'success' (bool): Indicates whether the login was successful.
                - 'data' (dict, optional): The logged-in user's data if login succeeds.
                - 'error' (str, optional): An error message if login fails.

        Note:
            The method checks the provided credentials against the database.
            It returns user data on successful login or an error message on failure.
        """
        
        user_data = db_handler.find_document('users', {'username': self.username})
        if not user_data or not check_password_hash(user_data['password'], self.password):
            return {'success': False, 'error': 'Invalid credentials'}

        return {
            'success': True,
            'data': {
                '_id': user_data.get('_id'),
                'name': user_data.get('name'),
                'username': user_data.get('username')
            }
        }
    # delete user
    def delete(self, db_handler, user_id):
        """
        Delete a user from the database.

        Args:
            db_handler (MongoDBHandler): The database handler for interacting with the database.
            user_id (str): The unique identifier of the user to delete.

        Returns:
            dict: A dictionary containing the following keys:
                - 'success' (bool): Indicates whether the deletion was successful.
                - 'message' (str): A message indicating the result of the deletion.
                - 'error' (str, optional): An error message if the deletion fails.

        Note:
            The method attempts to delete a user based on the provided user_id.
            It returns a success status and message on successful deletion or an error message if the user is not found.
        """
        
        try:
            deletion_result = db_handler.delete_document('users', user_id)
            if deletion_result:
                return {'success': True, 'message': 'User successfully deleted'}
            else:
                return {'success': False, 'error': 'User not found'}
        except Exception as e:
            return {'success': False, 'error': f'An error occurred: {str(e)}'}
    # list all users
    @staticmethod
    def list_all(db_handler):
        """
        List all users in the database.

        Args:
            db_handler (MongoDBHandler): The database handler for interacting with the database.

        Returns:
            dict: A dictionary containing the following keys:
                - 'success' (bool): Indicates whether the retrieval of users was successful.
                - 'users' (list, optional): A list of all users if retrieval is successful.
                - 'error' (str, optional): An error message if the operation fails.

        Note:
            The method retrieves a list of all users from the database.
            It returns the list of users on successful retrieval or an error message if there's an issue.
        """
        try:
            users = db_handler.list_documents('users')
            return {'success': True, 'users': users}
        except Exception as e:
            return {'success': False, 'error': f'An error occurred: {str(e)}'}