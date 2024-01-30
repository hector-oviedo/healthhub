from classes.mongodb_handler import MongoDBHandler

class Habit:
    def __init__(self, name=None, type=None, category=None, subcategory=None, description=None, _id=None):
        """
        Initialize a new habit object.

        Args:
            name (str): The name of the habit.
            type (str): The type of the habit (e.g., 'daily', 'weekly').
            category (str): The category of the habit.
            subcategory (str): The subcategory of the habit.
            description (str): A description of the habit.
            _id (str): The unique identifier of the habit.
        """
        self.name = name
        self.type = type
        self.category = category
        self.subcategory = subcategory
        self.description = description
        self._id = _id
    # add pre setted habit to habits (admin only)
    def add_habit(self, db_handler, habit_data):
        """
        Add a new habit to the database.

        This method inserts a new habit record into the database based on the provided habit data.

        Args:
            db_handler (MongoDBHandler): The database handler for interacting with the database.
            habit_data (dict): Data of the habit to add, including necessary fields such as name, type, etc.

        Returns:
            dict: A dictionary containing the following keys:
                - 'success' (bool): Indicates whether the habit addition was successful.
                - 'data' (dict, optional): The added habit data if the addition is successful.
                - 'error' (str, optional): An error message if the addition fails.

        Note:
            The function attempts to add a new habit record to the 'habits' collection. 
            In case of a failure (e.g., database connectivity issues, schema validation errors), 
            it returns an error message.
        """
        # Validate required fields
        required_fields = ['name', 'type', 'description']
        if not all(field in habit_data for field in required_fields):
            missing_fields = [field for field in required_fields if field not in habit_data]
            return {'success': False, 'error': f'Missing required fields: {", ".join(missing_fields)}'}

        # Validate habit type
        valid_types = ['daily', 'weekly']
        if habit_data['type'] not in valid_types:
            return {'success': False, 'error': 'Invalid habit type. Type must be either "daily" or "weekly"'}

        try:
            added_habit = db_handler.add_document('habits', habit_data)
            return {'success': True, 'data': added_habit}
        except Exception as e:
            return {'success': False, 'error': f'An error occurred: {str(e)}'}
    # remove pre setted habit from habits (admin only)
    def remove(self, db_handler, habit_id):
        """
        Remove a habit from the database.

        This method deletes a habit record from the database based on the provided habit ID.

        Args:
            db_handler (MongoDBHandler): The database handler for interacting with the database.
            habit_id (str): The unique identifier of the habit to remove.

        Returns:
            dict: A dictionary containing the following keys:
                - 'success' (bool): Indicates whether the habit removal was successful.
                - 'message' (str, optional): A message indicating the result of the removal.
                - 'error' (str, optional): An error message if the removal fails.

        Note:
            The function attempts to remove a habit record from the 'habits' collection.
            If the habit is found and successfully removed, it returns a success message.
            If the habit is not found, it returns an error message indicating the habit was not found.
        """
        try:
            removal_result = db_handler.delete_document('habits', habit_id)
            if removal_result:
                return {'success': True, 'message': 'Habit successfully removed'}
            else:
                return {'success': False, 'error': 'Habit not found'}
        except Exception as e:
            return {'success': False, 'error': f'An error occurred: {str(e)}'}
    #list all habits
    @staticmethod
    def list_all(db_handler, type=None):
        """
        List all habits in the database.

        This method retrieves all habit records from the database.

        Args:
            db_handler (MongoDBHandler): The database handler for interacting with the database.

        Returns:
            dict: A dictionary containing the following keys:
                - 'success' (bool): Indicates whether the retrieval of habits was successful.
                - 'habits' (list, optional): A list of all habits if retrieval is successful.
                - 'error' (str, optional): An error message if the operation fails.

        Note:
            The function attempts to retrieve all habit records from the 'habits' collection.
            It returns a list of habits on successful retrieval or an error message if there's an issue.
        """
        try:
            if type:
                print(type)
                query = {'type': type}
                habits = db_handler.list_documents('habits', query)
            else:
                habits = db_handler.list_documents('habits')
            return {'success': True, 'habits': habits}
        except Exception as e:
            return {'success': False, 'error': f'An error occurred: {str(e)}'}