import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from classes.mongodb_handler import MongoDBHandler

class TestMongoDBHandler(unittest.TestCase):

    @patch('classes.mongodb_handler.MongoClient')
    def setUp(self, mock_mongo_client):
        """
        Setup MongoDBHandler with a mocked MongoClient for testing.
        """
        self.uri = 'mock_uri'
        self.db_name = 'mock_db'
        self.handler = MongoDBHandler(self.uri, self.db_name)
        self.mock_db = mock_mongo_client.return_value[self.db_name]

    @patch('classes.mongodb_handler.Utils.serialize_document')
    @patch('classes.mongodb_handler.MongoClient')
    def test_add_document(self, mock_mongo_client, mock_serialize):
        collection_name = 'test_collection'
        document = {'name': 'test'}
        inserted_id = ObjectId('507f1f77bcf86cd799439011')
        mock_result = MagicMock(inserted_id=inserted_id)
        self.mock_db[collection_name].insert_one.return_value = mock_result

        # Mock serialize_document to return a document dict with '_id' serialized
        mock_serialize.return_value = {'_id': str(inserted_id), 'name': 'test'}

        result = self.handler.add_document(collection_name, document)

        self.mock_db[collection_name].insert_one.assert_called_once_with(document)
        mock_serialize.assert_called()  # Ensure serialize_document was called
        self.assertEqual(result['_id'], str(inserted_id))
        self.assertEqual(result['name'], 'test')


    def test_delete_document(self):
        """
        Test delete_document method deletes a document and returns True if successful.
        """
        collection_name = 'test_collection'
        document_id = '507f1f77bcf86cd799439011'
        mock_result = MagicMock(deleted_count=1)
        self.mock_db[collection_name].delete_one.return_value = mock_result

        result = self.handler.delete_document(collection_name, document_id)

        self.mock_db[collection_name].delete_one.assert_called_once_with({"_id": ObjectId(document_id)})
        self.assertTrue(result)

    def test_find_document(self):
        """
        Test find_document method finds and returns a document with a serialized '_id'.
        """
        collection_name = 'test_collection'
        query = {'name': 'test'}
        document = {'_id': ObjectId('507f1f77bcf86cd799439011'), 'name': 'test'}
        self.mock_db[collection_name].find_one.return_value = document

        with patch('classes.mongodb_handler.Utils.serialize_document', side_effect=lambda x: x):
            result = self.handler.find_document(collection_name, query)

        self.mock_db[collection_name].find_one.assert_called_once_with(query)
        self.assertEqual(result, document)

    def test_update_document(self):
        """
        Test update_document method updates a document and returns the updated document.
        """
        collection_name = 'test_collection'
        document_id = '507f1f77bcf86cd799439011'
        update_values = {'name': 'updated'}
        self.mock_db[collection_name].find_one.return_value = {'_id': ObjectId(document_id), 'name': 'updated'}

        with patch('classes.mongodb_handler.Utils.serialize_document', side_effect=lambda x: x):
            result = self.handler.update_document(collection_name, document_id, update_values)

        self.mock_db[collection_name].update_one.assert_called_once_with({'_id': ObjectId(document_id)}, {'$set': update_values})
        self.assertEqual(result['name'], 'updated')

    def test_list_documents(self):
        """
        Test list_documents method lists all documents in a collection.
        """
        collection_name = 'test_collection'
        documents = [
            {'_id': ObjectId('507f1f77bcf86cd799439011'), 'name': 'test1'},
            {'_id': ObjectId('507f1f77bcf86cd799439012'), 'name': 'test2'}
        ]
        self.mock_db[collection_name].find.return_value = documents

        with patch('classes.mongodb_handler.Utils.serialize_document', side_effect=lambda x: x):
            result = self.handler.list_documents(collection_name)

        self.mock_db[collection_name].find.assert_called_once_with({})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'test1')
        self.assertEqual(result[1]['name'], 'test2')

if __name__ == '__main__':
    unittest.main()