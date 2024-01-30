import unittest
from unittest.mock import patch
from werkzeug.security import generate_password_hash
from classes.user import User

class TestUser(unittest.TestCase):

    def setUp(self):
        """
        Setup User with predefined attributes for testing.
        """
        self.username = "testuser"
        self.password = "testpass"
        self.email = "test@example.com"
        self.name = "Test User"
        self.hashed_password = generate_password_hash(self.password)
        self.user_data = {
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'password': self.hashed_password
        }

    @patch('classes.user.MongoDBHandler')
    def test_register_successful(self, mock_db_handler):
        """
        Test register method with valid data results in successful user registration.
        """
        mock_db = mock_db_handler.return_value
        mock_db.find_document.side_effect = [None, None]  # No existing user or email
        mock_db.add_document.return_value = {'_id': 'user_id', **self.user_data}

        user = User(username=self.username, password=self.password, email=self.email, name=self.name)
        response = user.register(mock_db)

        mock_db.add_document.assert_called_once()
        self.assertTrue(response['success'])
        self.assertIn('data', response)

    @patch('classes.user.MongoDBHandler')
    def test_login_successful(self, mock_db_handler):
        """
        Test login method with valid credentials results in successful login.
        """
        mock_db = mock_db_handler.return_value
        mock_db.find_document.return_value = self.user_data

        user = User(username=self.username, password=self.password)
        response = user.login(mock_db)

        self.assertTrue(response['success'])
        self.assertIn('data', response)

    @patch('classes.user.MongoDBHandler')
    def test_delete_successful(self, mock_db_handler):
        """
        Test delete method with valid user_id results in successful user deletion.
        """
        user_id = 'user_id'
        mock_db = mock_db_handler.return_value
        mock_db.delete_document.return_value = True

        user = User()
        response = user.delete(mock_db, user_id)

        mock_db.delete_document.assert_called_once_with('users', user_id)
        self.assertTrue(response['success'])

    @patch('classes.user.MongoDBHandler')
    def test_list_all_users(self, mock_db_handler):
        """
        Test list_all method retrieves all users.
        """
        mock_db = mock_db_handler.return_value
        mock_db.list_documents.return_value = [self.user_data]

        response = User.list_all(mock_db)

        mock_db.list_documents.assert_called_once_with('users')
        self.assertTrue(response['success'])
        self.assertIn('users', response)
        self.assertEqual(len(response['users']), 1)

if __name__ == '__main__':
    unittest.main()