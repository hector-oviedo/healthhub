import unittest
from unittest.mock import MagicMock
from classes.habit_tracker import HabitTracker

class TestHabitTracker(unittest.TestCase):
    def setUp(self):
        self.mock_db_handler = MagicMock()
        self.habit_tracker = HabitTracker(self.mock_db_handler)

    def test_init(self):
        self.assertIsInstance(self.habit_tracker.db_handler, MagicMock)
    #
    # LIST
    #
    def test_list_user_habits_user_not_found(self):
        self.mock_db_handler.find_document.return_value = None
        result = self.habit_tracker.list_user_habits("nonexistent_user")
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'User not found')
        self.assertEqual(result['habits'], [])

    def test_list_user_habits(self):
        self.mock_db_handler.find_document.return_value = {'username': 'test_user', 'habits': [{'type': 'daily', 'status': 'completed'}]}
        result = self.habit_tracker.list_user_habits("test_user")
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Habits retrieved successfully')
        self.assertEqual(len(result['habits']), 1)
    #
    # ASSIGN HABIT
    #
    def test_assign_habit_success(self):
        self.mock_db_handler.find_document.side_effect = [
            {'_id': 'user_id', 'username': 'test_user'},  # Mock user found
            {'_id': '507f1f77bcf86cd799439011', 'name': 'Read', 'type': 'daily'}  # Mock habit found
        ]
        result = self.habit_tracker.assign_habit('test_user', '507f1f77bcf86cd799439011', '2023-01-01 10:00', '2023-01-02 10:00')
        if not result['success']:
            print(f"Test failed with error: {result.get('error') or result.get('message')}")
        self.assertTrue(result['success'], msg=f"Test failed with error: {result.get('error') or result.get('message')}")
        self.assertEqual(result['message'], 'Habit assigned successfully')


    def test_assign_habit_invalid_date_format(self):
        result = self.habit_tracker.assign_habit('test_user', '507f1f77bcf86cd799439011', 'invalid_date', '2023-01-02 10:00')
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Invalid date format. Dates should be in YYYY-MM-DD HH:MM format.')

    def test_assign_habit_end_date_before_start_date(self):
        result = self.habit_tracker.assign_habit('test_user', '507f1f77bcf86cd799439011', '2023-01-03 10:00', '2023-01-02 10:00')
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'End date range must be later than start date range.')

    def test_assign_habit_user_not_found(self):
        self.mock_db_handler.find_document.return_value = None  # Mock user not found
        result = self.habit_tracker.assign_habit('unknown_user', '507f1f77bcf86cd799439011', '2023-01-01 10:00', '2023-01-02 10:00')
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'User not found')

    def test_assign_habit_habit_not_found(self):
        self.mock_db_handler.find_document.side_effect = [
            {'username': 'test_user'},  # Mock user found
            None  # Mock habit not found
        ]
        result = self.habit_tracker.assign_habit('test_user', '507f1f77bcf86cd799439011', '2023-01-01 10:00', '2023-01-02 10:00')
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Habit not found')

    def test_assign_habit_invalid_habit_type(self):
        self.mock_db_handler.find_document.side_effect = [
            {'username': 'test_user'},  # Mock user found
            {'_id': '1234', 'name': 'Read', 'type': 'monthly'}  # Mock habit found with invalid type
        ]
        result = self.habit_tracker.assign_habit('test_user', '507f1f77bcf86cd799439011', '2023-01-01 10:00', '2023-01-02 10:00')
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Invalid habit type. Type must be either "daily" or "weekly"')
    #
    # ASSIGN CUSTOM HABIT
    #
    def test_assign_custom_habit_success(self):
        self.mock_db_handler.find_document.return_value = {'_id': 'user_id', 'username': 'test_user'}
        result = self.habit_tracker.assign_custom_habit(
            username='test_user',
            name='Custom Habit',
            type='daily',
            start_range='2023-01-01 10:00',
            end_range='2023-01-10 10:00',
            category='Health',
            subcategory='Exercise',
            description='Daily morning run'
        )
        self.assertTrue(result['success'], msg=f"Test failed with error: {result.get('error') or result.get('message')}")
        self.assertEqual(result['message'], 'Habit assigned successfully')

    def test_assign_custom_habit_invalid_date_format(self):
        self.mock_db_handler.find_document.return_value = {'username': 'test_user'}
        result = self.habit_tracker.assign_custom_habit(
            username='test_user',
            name='Custom Habit',
            type='daily',
            start_range='invalid_date',
            end_range='2023-01-02 10:00'
        )
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Invalid date format. Dates should be in YYYY-MM-DD HH:MM format.')

    def test_assign_custom_habit_end_date_before_start_date(self):
        self.mock_db_handler.find_document.return_value = {'username': 'test_user'}
        result = self.habit_tracker.assign_custom_habit(
            username='test_user',
            name='Custom Habit',
            type='daily',
            start_range='2023-01-03 10:00',
            end_range='2023-01-02 10:00'
        )
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'End date range must be later than start date range.')

    def test_assign_custom_habit_user_not_found(self):
        self.mock_db_handler.find_document.return_value = None
        result = self.habit_tracker.assign_custom_habit(
            username='unknown_user',
            name='Custom Habit',
            type='daily',
            start_range='2023-01-01 10:00',
            end_range='2023-01-10 10:00'
        )
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'User not found')

    def test_assign_custom_habit_invalid_habit_type(self):
        self.mock_db_handler.find_document.return_value = {'username': 'test_user'}
        result = self.habit_tracker.assign_custom_habit(
            username='test_user',
            name='Custom Habit',
            type='monthly',  # Invalid type
            start_range='2023-01-01 10:00',
            end_range='2023-01-10 10:00'
        )
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Invalid habit type. Type must be either "daily" or "weekly"')

    def test_assign_custom_habit_exception_during_assignment(self):
        self.mock_db_handler.find_document.return_value = {'_id': 'user_id', 'username': 'test_user'}
        self.mock_db_handler.update_document.side_effect = Exception('Database update failed')
        result = self.habit_tracker.assign_custom_habit(
            username='test_user',
            name='Custom Habit',
            type='daily',
            start_range='2023-01-01 10:00',
            end_range='2023-01-10 10:00'
        )
        self.assertFalse(result['success'])
        self.assertTrue('An error occurred' in result['error'])
    #
    #UPDATE DAILY HABIT
    #
    def test_update_daily_habit_success(self):
        habit_id = 'habit123'
        user = {
            '_id': 'user123',
            'username': 'test_user',
            'habits': [{
                '_id': habit_id,
                'type': 'daily',
                'start_range': '2023-01-01 10:00',
                'end_range': '2023-01-02 10:00',
                'streak': 0,
                'longest_streak': 0
            }]
        }
        self.mock_db_handler.find_document.return_value = user
        result = self.habit_tracker.update_daily_habit(
            username='test_user',
            habit_id=habit_id,
            completion_date='2023-01-01 10:00',
            continue_enabled=True
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Habit updated successfully')
        updated_habit = user['habits'][0]
        self.assertEqual(updated_habit['streak'], 1)
        self.assertEqual(updated_habit['longest_streak'], 1)
        self.assertEqual(updated_habit['status'], 'in progress')

    def test_update_daily_habit_user_not_found(self):
        self.mock_db_handler.find_document.return_value = None
        result = self.habit_tracker.update_daily_habit(
            username='unknown_user',
            habit_id='habit123',
            completion_date='2023-01-01 10:00',
            continue_enabled=True
        )
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'User not found')
    #
    # UPDATE WEEKLY HABIT
    #
    def test_update_weekly_habit_success(self):
        habit_id = 'habit123'
        user = {
            '_id': 'user123',
            'username': 'test_user',
            'habits': [{
                '_id': habit_id,
                'type': 'weekly',
                'start_range': '2023-01-01 10:00',
                'end_range': '2023-01-07 10:00',
                'streak': 0,
                'longest_streak': 0
            }]
        }
        self.mock_db_handler.find_document.return_value = user
        result = self.habit_tracker.update_weekly_habit(
            username='test_user',
            habit_id=habit_id,
            completion_date='2023-01-03 10:00',
            continue_enabled=True
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Habit updated successfully')
        updated_habit = user['habits'][0]
        self.assertEqual(updated_habit['streak'], 1)
        self.assertEqual(updated_habit['longest_streak'], 1)
        self.assertEqual(updated_habit['status'], 'in progress')
    
    def test_update_weekly_habit_user_not_found(self):
        self.mock_db_handler.find_document.return_value = None
        result = self.habit_tracker.update_weekly_habit(
            username='unknown_user',
            habit_id='habit123',
            completion_date='2023-01-03 10:00',
            continue_enabled=True
        )
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'User not found')

    #
    #LONGEST HABIT
    #
    def test_longest_streak_habit_with_type(self):
        user = {
            'username': 'test_user',
            'habits': [
                {'name': 'Habit1', 'type': 'daily', 'longest_streak': 5},
                {'name': 'Habit2', 'type': 'weekly', 'longest_streak': 4},  # This should be selected
                {'name': 'Habit3', 'type': 'daily', 'longest_streak': 3}
            ]
        }
        self.mock_db_handler.find_document.return_value = user
        result = self.habit_tracker.longest_streak_habit('test_user', 'weekly')
        self.assertTrue(result['success'])
        self.assertEqual(result['habit']['name'], 'Habit2')

    def test_strugglest_habit_with_type(self):
        self.mock_db_handler.find_document.return_value = {
            'username': 'test_user',
            'habits': [
                {'name': 'Habit1', 'type': 'daily', 'streak': 1},
                {'name': 'Habit2', 'type': 'weekly', 'streak': 5},
                {'name': 'Habit3', 'type': 'daily', 'streak': 2}
            ]
        }
        result = self.habit_tracker.strugglest_habit('test_user', 'daily')
        self.assertTrue(result['success'])
        self.assertEqual(result['habit']['name'], 'Habit1')

if __name__ == '__main__':
    unittest.main()