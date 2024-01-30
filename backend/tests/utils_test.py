import unittest
from unittest.mock import patch, MagicMock
from classes.utils import Utils

class TestUtils(unittest.TestCase):
    def test_serialize_document_with_id(self):
        """
        Test serialize_document method with a document containing '_id'
        """
        doc = {'_id': 123, 'name': 'Test Name'}
        expected = {'_id': '123', 'name': 'Test Name'}
        result = Utils.serialize_document(doc)
        self.assertEqual(result, expected)

    def test_serialize_document_without_id(self):
        """
        Test serialize_document method with a document not containing '_id'
        """
        doc = {'name': 'Test Name'}
        expected = {'name': 'Test Name'}
        result = Utils.serialize_document(doc)
        self.assertEqual(result, expected)

    @patch('base64.b64decode')
    def test_normalize_auth_credentials_with_basic_auth(self, mock_b64decode):
        """
        Test normalize_auth_credentials with a Basic Auth header
        """
        mock_request = MagicMock()
        mock_request.json = None
        mock_request.headers = {'Authorization': 'Basic encoded_credentials'}
        mock_b64decode.return_value = b'username:password'

        expected = {'username': 'username', 'password': 'password'}
        result = Utils.normalize_auth_credentials(mock_request)
        self.assertEqual(result, expected)

    def test_normalize_auth_credentials_without_auth_header(self):
        """
        Test normalize_auth_credentials without an Authorization header
        """
        mock_request = MagicMock()
        mock_request.json = {'username': 'username', 'password': 'password'}
        mock_request.headers = {}

        expected = {'username': 'username', 'password': 'password'}
        result = Utils.normalize_auth_credentials(mock_request)
        self.assertEqual(result, expected)

    @patch('classes.utils.Utils.normalize_auth_credentials')
    @patch('classes.user.User.login')
    def test_authenticate_user_with_valid_credentials(self, mock_login, mock_normalize):
        """
        Test authenticate_user with valid credentials
        """
        mock_request = MagicMock()
        mock_normalize.return_value = {'username': 'valid_user', 'password': 'valid_pass'}
        mock_login.return_value = True  # Simulating successful login

        expected = ('valid_user', None)
        result = Utils.authenticate_user(mock_request, MagicMock())
        self.assertEqual(result, expected)

    @patch('classes.utils.Utils.normalize_auth_credentials')
    @patch('classes.user.User.login')
    def test_authenticate_user_with_invalid_credentials(self, mock_login, mock_normalize):
        """
        Test authenticate_user with invalid credentials
        """
        mock_request = MagicMock()
        mock_normalize.return_value = {'username': 'invalid_user', 'password': 'invalid_pass'}
        mock_login.return_value = False  # Simulating failed login

        expected = (None, 'Invalid credentials')
        result = Utils.authenticate_user(mock_request, MagicMock())
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()