import unittest
from unittest.mock import patch, MagicMock
from classes.habit import Habit

class TestHabit(unittest.TestCase):

    def setUp(self):
        """
        Setup Habit for testing without needing actual database interaction.
        """
        self.habit = Habit(name="Test Habit", type="daily", description="Test Description")
        self.habit_data = {'name': 'Test Habit', 'type': 'daily', 'description': 'Test Description'}
        self.habit_id = '507f1f77bcf86cd799439011'

    @patch('classes.habit.MongoDBHandler')
    def test_add_habit_successful(self, mock_db_handler):
        """
        Test add_habit method with valid data results in successful habit addition.
        """
        mock_db_handler_instance = mock_db_handler.return_value
        mock_db_handler_instance.add_document.return_value = {**self.habit_data, '_id': self.habit_id}

        response = self.habit.add_habit(mock_db_handler_instance, self.habit_data)
        
        mock_db_handler_instance.add_document.assert_called_once_with('habits', self.habit_data)
        self.assertTrue(response['success'])
        self.assertIn('data', response)
        self.assertEqual(response['data']['_id'], self.habit_id)

    @patch('classes.habit.MongoDBHandler')
    def test_remove_habit_successful(self, mock_db_handler):
        """
        Test remove method with valid habit_id results in successful habit removal.
        """
        mock_db_handler_instance = mock_db_handler.return_value
        mock_db_handler_instance.delete_document.return_value = True

        response = self.habit.remove(mock_db_handler_instance, self.habit_id)
        
        mock_db_handler_instance.delete_document.assert_called_once_with('habits', self.habit_id)
        self.assertTrue(response['success'])
        self.assertEqual(response['message'], 'Habit successfully removed')

    @patch('classes.habit.MongoDBHandler')
    def test_list_all_habits_successful(self, mock_db_handler):
        """
        Test list_all method retrieves all habits.
        """
        mock_db_handler_instance = mock_db_handler.return_value
        mock_db_handler_instance.list_documents.return_value = [self.habit_data]

        response = Habit.list_all(mock_db_handler_instance)
        
        mock_db_handler_instance.list_documents.assert_called_once_with('habits')
        self.assertTrue(response['success'])
        self.assertIn('habits', response)
        self.assertEqual(len(response['habits']), 1)
        self.assertEqual(response['habits'][0]['name'], 'Test Habit')

if __name__ == '__main__':
    unittest.main()