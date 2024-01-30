class BackendService {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async sendRequest(endpoint, method, data) {
        if (data) console.log("sendRequest data",data)
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json'
        };

        //save ADMIN data
        if (endpoint == 'admin/validate') {
            admin_username = data.username;
            admin_password = data.password;
        }
        //save USER data
        if (endpoint == '/login' || endpoint == '/register') {
            username = data.username;
            password = data.password;
        }

        // Check if 'username' and 'password' are present in the data
        if (data && data.username && data.password) {
            // Add the Authorization header for Basic Authentication
            headers['Authorization'] = 'Basic ' + btoa(data.username + ':' + data.password);
            // Remove 'username' and 'password' from the data object
            delete data.username;
            delete data.password;
        }

        // Configuring the request options
        const requestOptions = {
            method: method,
            headers: headers,
            mode: 'cors',
            body: method === 'GET' ? null : JSON.stringify(data),
        };

        try {
            const response = await fetch(url, requestOptions);
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error in sending request:', error);
            throw error;
        }
    }
}