from pymongo import MongoClient
from bson import ObjectId
from classes.utils import Utils

class MongoDBHandler:
    def __init__(self, uri, db_name):
        """
        Initialize MongoDB connection.

        Args:
            uri (str): MongoDB URI.
            db_name (str): Name of the database.
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
    # add document (generic)
    def add_document(self, collection_name, document):
        """
        Add a document to a specified collection.

        Args:
            collection_name (str): The name of the collection.
            document (dict): The document to add.

        Returns:
            dict: The added document with serialized '_id'.
        """
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        return Utils.serialize_document(self.find_document(collection_name, {'_id': result.inserted_id}))
    # delete document (generic)
    def delete_document(self, collection_name, document_id):
        """
        Delete a document from a specified collection.

        Args:
            collection_name (str): The name of the collection.
            document_id (str): The ID of the document to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        collection = self.db[collection_name]
        result = collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0
    # finds document (generic)
    def find_document(self, collection_name, query):
        """
        Find a document in a specified collection.

        Args:
            collection_name (str): The name of the collection.
            query (dict): The query to find the document.

        Returns:
            dict: The found document, or None if not found.
        """
        collection = self.db[collection_name]
        document = collection.find_one(query)
        return Utils.serialize_document(document) if document else None
    # updates document (generic)
    def update_document(self, collection_name, document_id, update_values):
        """
        Update a document in a specified collection.

        Args:
            collection_name (str): The name of the collection.
            document_id (str): The ID of the document to update.
            update_values (dict): The values to update.

        Returns:
            dict: The updated document.
        """
        collection = self.db[collection_name]
        collection.update_one({'_id': ObjectId(document_id)}, {'$set': update_values})
        return Utils.serialize_document(self.find_document(collection_name, {'_id': ObjectId(document_id)}))
    # list documents (generic)
    def list_documents(self, collection_name, query=None):
        """
        List all documents in a specified collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            list: A list of all documents in the collection.
        """
        collection = self.db[collection_name]
        documents = collection.find(query or {})
        return [Utils.serialize_document(doc) for doc in documents]