import base64

class Utils:

    # used for valid string in API responses
    @staticmethod
    def serialize_document(doc):
        """
        Convert MongoDB document ObjectId to string for JSON serialization

        Args:
            doc (dict): MongoDB document

        Returns:
            dict: Document with serialized '_id'
        """
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
        return doc
    # extracts username and password from the authorization header of the HTTP request
    @staticmethod
    def normalize_auth_credentials(request):
        """
        Extracts and normalizes the username and password from the request's JSON data and Authorization header.

        Args:
            request (Request): The Flask request object.

        Returns:
            dict: A dictionary containing the 'username' and 'password'.
        """
        result = request.json.copy() if request.json else {}
        auth_header = request.headers.get('Authorization')

        # Initialize username and password as empty strings
        username = ''
        password = ''

        # Decode Basic Auth header if present
        if auth_header and auth_header.startswith('Basic '):
            auth_header = auth_header[6:]  # Remove 'Basic ' prefix
            try:
                credentials = base64.b64decode(auth_header).decode('utf-8')
                username, password = credentials.split(':', 1)
            except ValueError:
                # This happens if the password is not present
                username = credentials

            # Normalize username and password
            result.setdefault('username', username)
            result.setdefault('password', password)

        return result
    # authenticate user credentials from the HTTP Header, notice is here to be used also on app.py if needed
    @staticmethod
    def authenticate_user(request, db_handler):
        """
        Authenticate a user based on credentials provided in the request.

        Args:
            request: Flask request object.
            db_handler: Instance of MongoDBHandler for database operations.

        Returns:
            Tuple: (username, error message)
        """
        from classes.user import User

        data = Utils.normalize_auth_credentials(request)

        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return None, 'Username and password are required'

        user = User(username=username, password=password)

        user_data = user.login(db_handler)

        if not user_data:
            return None, 'Invalid credentials'

        return username, None