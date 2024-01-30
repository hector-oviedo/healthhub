from classes.mongodb_handler import MongoDBHandler
from bson import ObjectId
import uuid
import datetime

class HabitTracker:
    def __init__(self, db_handler):
        """
        Initialize HabitTracker with a MongoDBHandler instance.

        Args:
            db_handler (MongoDBHandler): An instance of MongoDBHandler to interact with the database.
        """
        self.db_handler = db_handler
    # list habits
    def list_user_habits(self, username, habit_type=None, status=None):
        """
        List all habits assigned to a user, with optional filtering by habit type and status.

        Args:
            username (str): The username of the user whose habits to list.
            habit_type (str, optional): The type of the habits to filter (e.g., 'daily', 'weekly'). Defaults to None.
            status (str, optional): The status of the habits to filter (e.g., 'in progress', 'completed', 'failed'). Defaults to None.

        Returns:
            dict: A dictionary containing the result of the operation.
                The dictionary includes keys 'success' (bool) indicating if the operation was successful,
                'habits' (list): An array of habit objects assigned to the user, filtered by the specified criteria,
                'message' (str) describing the result, and 'error' (str) in case of an error.
        Note:
            If the user has no habits or no habits match the filters, 'success' will be True and 'habits' will be an empty array.
        """
        # Validate user
        user = self.db_handler.find_document('users', {'username': username})
        if not user:
            return {'success': False, 'habits': [], 'message': 'User not found'}

        user_habits = user.get('habits', [])

        # Apply filters if provided
        if habit_type:
            user_habits = [habit for habit in user_habits if habit.get('type') == habit_type]
        if status:
            user_habits = [habit for habit in user_habits if habit.get('status') == status]

        return {'success': True, 'habits': user_habits, 'message': 'Habits retrieved successfully'}
    # assign habit (from pre setted habits)
    def assign_habit(self, username, habit_id, start_range, end_range):
        """
        Assign a habit to a user.

        Args:
            username (str): The username of the user to assign the habit to.
            habit_id (str): The ID of the habit to assign.
            start_range (str): The start date range for the habit.
            end_range (str): The end date range for the habit.

        Returns:
            dict: A dictionary containing the result of the assignment operation.
                The dictionary includes keys 'success' (bool) indicating if the operation was successful,
                'message' (str) describing the result, and 'error' (str) in case of an error.
        """
        # Validate dates
        try:
            start_datetime = datetime.datetime.strptime(start_range, '%Y-%m-%d %H:%M')
            end_datetime = datetime.datetime.strptime(end_range, '%Y-%m-%d %H:%M')

            # Check if end_range is greater than start_range
            if end_datetime <= start_datetime:
                return {'success': False, 'error': 'End date range must be later than start date range.'}
        except ValueError:
            return {'success': False, 'error': 'Invalid date format. Dates should be in YYYY-MM-DD HH:MM format.'}
        except TypeError:
            return {'success': False, 'error': 'Missing start_range or end_range.'}
        
        # Validate user
        user = self.db_handler.find_document('users', {'username': username})
        if not user:
            return {'success': False, 'error': 'User not found'}

        # Validate habit
        habit = self.db_handler.find_document('habits', {'_id': ObjectId(habit_id)})
        if not habit:
            return {'success': False, 'error': 'Habit not found'}

        # Creation/Assign datetime
        creation_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        # Create habit
        habit_data = {
            '_id': str(uuid.uuid4()),
            'habit_id': habit_id,
            'name': habit['name'],
            'type': habit['type'],
            'category': habit.get('category', ''),
            'subcategory': habit.get('subcategory', ''),
            'description': habit.get('description', ''),
            'start_range': start_range,
            'end_range': end_range,
            'status': 'in progress',
            'creation_datetime': creation_datetime
        }

        # Validate habit type
        valid_types = ['daily', 'weekly']
        if habit_data.get('type') not in valid_types:
            return {'success': False, 'error': 'Invalid habit type. Type must be either "daily" or "weekly"'}

        try:
            # Append the habit to the user's list
            user_habits = user.get('habits', [])
            user_habits.append(habit_data)
            self.db_handler.update_document('users', user['_id'], {'habits': user_habits})

            return {'success': True, 'message': 'Habit assigned successfully'}
        except Exception as e:
            return {'success': False, 'error': f'An error occurred: {str(e)}'}
    # assign custom habit
    def assign_custom_habit(self, username, name, type, start_range, end_range, category='', subcategory='', description=''):
        """
        Assign a custom habit to a user by creating a new habit entry.

        Args:
            username (str): The username of the user to assign the habit to.
            name (str): Name of the habit.
            type (str): Type of the habit (e.g., 'daily', 'weekly').
            start_range (str): The start date range for the habit.
            end_range (str): The end date range for the habit.
            category (str, optional): Category of the habit.
            subcategory (str, optional): Subcategory of the habit.
            description (str, optional): Description of the habit.

        Returns:
            dict: A dictionary containing the result of the assignment operation.
                The dictionary includes keys 'success' (bool) indicating if the operation was successful,
                'message' (str) describing the result, and 'error' (str) in case of an error.
        """
        user = self.db_handler.find_document('users', {'username': username})
        if not user:
            return {'success': False, 'error': 'User not found'}

        # Validate date ranges
        try:
            start_datetime = datetime.datetime.strptime(start_range, '%Y-%m-%d %H:%M')
            end_datetime = datetime.datetime.strptime(end_range, '%Y-%m-%d %H:%M')

            # Check if end_range is greater than start_range
            if end_datetime <= start_datetime:
                return {'success': False, 'error': 'End date range must be later than start date range.'}
        except ValueError:
            return {'success': False, 'error': 'Invalid date format. Dates should be in YYYY-MM-DD HH:MM format.'}
        except TypeError:
            return {'success': False, 'error': 'Missing start_range or end_range.'}
        
        # Validate habit type
        valid_types = ['daily', 'weekly']
        if type not in valid_types:
            return {'success': False, 'error': 'Invalid habit type. Type must be either "daily" or "weekly"'}
        
        # Creation/Assign datetime
        creation_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        # Prepare custom habit data
        habit_data = {
            '_id': str(uuid.uuid4()),
            'name': name,
            'type': type,
            'category': category,
            'subcategory': subcategory,
            'description': description,
            'start_range': start_range,
            'end_range': end_range,
            'status': 'in progress',
            'creation_datetime': creation_datetime
        }

        try:
            # Append the habit to the user's list
            user_habits = user.get('habits', [])
            user_habits.append(habit_data)
            self.db_handler.update_document('users', user['_id'], {'habits': user_habits})

            return {'success': True, 'message': 'Habit assigned successfully'}
        except Exception as e:
            return {'success': False, 'error': f'An error occurred: {str(e)}'}
    # dissociate/remove habit from habits list of user
    def remove_habit(self, username, habit_id):
        """
        Remove a habit from a user's list of habits.

        Args:
            username (str): The username of the user.
            habit_id (str): The ID of the habit to remove.

        Returns:
            dict: A dictionary containing the result of the assignment operation.
                The dictionary includes keys 'success' (bool) indicating if the operation was successful,
                'message' (str) describing the result, and 'error' (str) in case of an error.
        """
        user = self.db_handler.find_document('users', {'username': username})
        if not user:
            return {'success': False, 'error': 'User not found'}

        # Check if the habit exists for the user
        user_habits = user.get('habits', [])
        if not any(habit['_id'] == habit_id for habit in user_habits):
            return {'success': False, 'error': 'Habit not found'}

        try:
            # Filter out the habit to be removed
            updated_habits = [habit for habit in user_habits if habit['_id'] != habit_id]
            self.db_handler.update_document('users', user['_id'], {'habits': updated_habits})
        except Exception as e:
            return {'success': False, 'error': f'An error occurred: {str(e)}'}

        return {'success': True, 'message': 'Habit removed successfully'}
    # update daily habit and proceed with app logic
    def update_daily_habit(self, username, habit_id, completion_date, continue_enabled):
        """
        Update a daily habit for a user.

        Args:
            username (str): The username of the user.
            habit_id (str): The ID of the habit to update.
            completion_date (str): The date when the habit was completed.
            continue_enabled (bool): Whether the habit should continue or not.

        Returns:
            dict: A dictionary containing the following keys:
                - 'success' (bool): Indicates whether the operation was successful.
                - 'message' (str): A message indicating the result of the operation.
                - 'error' (str, optional): An error message if the operation failed.

        Note:
            The method updates the habit's streak, longest streak, and status. 
            If the habit is not found or the user does not exist, it returns an error.
        """
        user = self.db_handler.find_document('users', {'username': username})
        if not user:
            return {'success': False, 'error': 'User not found'}

        # LOGIC

        habit_found = False
        user_habits = user.get('habits', [])
        for habit in user_habits:
            if habit['_id'] == habit_id:
                habit_found = True

                # Check if habit type is 'daily'
                if habit.get('type') != 'daily':
                    return {'success': False, 'error': 'Habit type is not daily'}

                # Logic for checking the date range and updating the streak
                start_range, end_range = habit.get('start_range'), habit.get('end_range')
                completed_in_range = start_range <= completion_date <= end_range

                # Logic to increase both range dates by one day if continue_enabled is true
                if continue_enabled:
                    start_datetime = datetime.datetime.strptime(start_range, '%Y-%m-%d %H:%M')
                    end_datetime = datetime.datetime.strptime(end_range, '%Y-%m-%d %H:%M')

                    # Increment both dates by one day
                    new_start_range = (start_datetime + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
                    new_end_range = (end_datetime + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M')

                    # Update the habit's start and end ranges
                    habit['start_range'] = new_start_range
                    habit['end_range'] = new_end_range

                # Update streak and longest_streak logic
                if completed_in_range:
                    habit['streak'] = habit.get('streak', 0) + 1
                    habit['longest_streak'] = max(habit.get('longest_streak', 0), habit['streak'])
                    habit['status'] = 'in progress' if continue_enabled else 'completed'
                    current_status = 'completed' if continue_enabled else 'in progress'
                else:
                    # Longest streak logic
                    habit['longest_streak'] = max(habit.get('longest_streak', 0), habit.get('streak', 0))
                    habit['streak'] = 0
                    habit['status'] = 'failed'
                    current_status = 'failed'

                habit['completion_datetime'] = completion_date

                 # Add entry to completion_datetimes array
                completion_entry = {
                    'datetime': completion_date,
                    'status': current_status,
                    'streak': habit['streak'],
                    'longest_streak': habit['longest_streak']
                }
                habit.setdefault('completion_datetimes', []).append(completion_entry)

                break
        
        if not habit_found:
            return {'success': False, 'error': 'Habit not found'}

        try:
            self.db_handler.update_document('users', user['_id'], {'habits': user_habits})
        except Exception as e:
            return {'success': False, 'error': f'An error occurred: {str(e)}'}

        return {'success': True, 'message': 'Habit updated successfully'}
    # update weekly habit and proceed with app logic
    def update_weekly_habit(self, username, habit_id, completion_date, continue_enabled):
        """
        Update a weekly habit for a user.

        Args:
            username (str): The username of the user.
            habit_id (str): The ID of the habit to update.
            completion_date (str): The date when the habit was completed.
            continue_enabled (bool): Whether the habit should continue or not.

        Returns:
            dict: A dictionary containing the following keys:
                - 'success' (bool): Indicates whether the operation was successful.
                - 'message' (str): A message indicating the result of the operation.
                - 'error' (str, optional): An error message if the operation failed.

        Note:
            The method updates the habit's streak, longest streak, and status. 
            If the habit is not found or the user does not exist, it returns an error.
        """
        user = self.db_handler.find_document('users', {'username': username})
        if not user:
            return {'success': False, 'error': 'User not found'}

        # LOGIC

        habit_found = False
        user_habits = user.get('habits', [])
        for habit in user_habits:
            if habit['_id'] == habit_id:
                habit_found = True

                # Check if habit type is 'weekly'
                if habit.get('type') != 'weekly':
                    return {'success': False, 'error': 'Habit type is not daily'}

                # Logic for checking the date range and updating the streak
                start_range, end_range = habit.get('start_range'), habit.get('end_range')
                completed_in_range = start_range <= completion_date <= end_range

                # Logic to increase both range dates by one day if continue_enabled is true
                if continue_enabled:
                    start_datetime = datetime.datetime.strptime(start_range, '%Y-%m-%d %H:%M')
                    end_datetime = datetime.datetime.strptime(end_range, '%Y-%m-%d %H:%M')

                    # Increment both dates by one week
                    new_start_range = (start_datetime + datetime.timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M')
                    new_end_range = (end_datetime + datetime.timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M')

                    # Update the habit's start and end ranges
                    habit['start_range'] = new_start_range
                    habit['end_range'] = new_end_range

                # Update streak and longest_streak logic
                if completed_in_range:
                    habit['streak'] = habit.get('streak', 0) + 1
                    habit['longest_streak'] = max(habit.get('longest_streak', 0), habit['streak'])
                    habit['status'] = 'in progress' if continue_enabled else 'completed'
                    current_status = 'completed' if continue_enabled else 'in progress'
                else:
                    # Longest streak logic
                    habit['longest_streak'] = max(habit.get('longest_streak', 0), habit.get('streak', 0))
                    habit['streak'] = 0
                    habit['status'] = 'failed'
                    current_status = 'failed'

                habit['completion_datetime'] = completion_date

                 # Add entry to completion_datetimes array
                completion_entry = {
                    'datetime': completion_date,
                    'status': current_status,
                    'streak': habit['streak'],
                    'longest_streak': habit['longest_streak']
                }
                habit.setdefault('completion_datetimes', []).append(completion_entry)

                break
        
        if not habit_found:
            return {'success': False, 'error': 'Habit not found'}

        try:
            self.db_handler.update_document('users', user['_id'], {'habits': user_habits})
        except Exception as e:
            return {'success': False, 'error': f'An error occurred: {str(e)}'}

        return {'success': True, 'message': 'Habit updated successfully'}
    # get the longest streak habit
    def longest_streak_habit(self, username, type):
        """
        Find the habit with the longest streak for a given user.

        Args:
            username (str): The username of the user.

        Returns:
            dict: The habit with the longest streak or an error message.
        """
        user = self.db_handler.find_document('users', {'username': username})
        if not user:
            return {'success': False, 'error': 'User not found'}

        user_habits_raw = user.get('habits', [])
        
        # Apply type filter if type is defined
        if type:
            user_habits = [habit for habit in user_habits_raw if habit.get('type') == type]
        else:
            user_habits = user_habits_raw
        
        if not user_habits:
            return {'success': False, 'error': 'No habits found for user'}

        # LOGIC

        # Use 'max' as a 'for each' to iterate over 'user_habits'
        # For each habit, the 'lambda' function extracts 'longest_streak', using 0 as default if it's not present
        # This approach (lambda) avoids the need for an extra method just to get 'longest_streak'
        # 'max' then finds the habit with the highest 'longest_streak' value

        habit = max(user_habits, key=lambda h: h.get('longest_streak', 0))
        return {'success': True, 'habit': habit}
    # get the worst habit
    def strugglest_habit(self, username, type):
        """
        Find the habit with the most recent failure for a given user.

        Args:
            username (str): The username of the user.

        Returns:
            dict: The habit with the most recent failure or an error message.
        """
        user = self.db_handler.find_document('users', {'username': username})
        if not user:
            return {'success': False, 'error': 'User not found'}

        user_habits_raw = user.get('habits', [])
        
        # Apply type filter if type is defined
        if type:
            user_habits = [habit for habit in user_habits_raw if habit.get('type') == type]
        else:
            user_habits = user_habits_raw

        if not user_habits:
            return {'success': False, 'error': 'No habits found for user'}

        # LOGIC

        # Use 'min' as a 'for each' to iterate over 'user_habits'
        # For each habit, the 'lambda' function extracts the 'streak' value, using 0 as default if it's not present
        # This approach avoids the need for an extra method to get 'streak'
        # 'min' then finds the habit with the lowest 'streak' value, which represents the worst habit
        habit = min(user_habits, key=lambda h: h.get('streak', 0))
        return {'success': True, 'habit': habit}