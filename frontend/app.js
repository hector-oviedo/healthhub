require('dotenv').config();

const express = require('express');
const cors = require('cors');
const app = express();
const port = process.env.FRONTEND_PORT || 3000;
const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000';

// Enable CORS for all routes
app.use(cors({origin: '*'}));

// Set the view engine to ejs
app.set('view engine', 'ejs');

// Serve static files from the public directory
app.use(express.static('public'));

// Route for homepage (user)
app.get('/', (req, res) => { res.render('index', { backendUrl: backendUrl }); });

// Route for admin
app.get('/admin', (req, res) => { res.render('admin', { backendUrl: backendUrl }); });

// Start the server
app.listen(port, () => { console.log('Frontend running at ' + (process.env.FRONTEND_PUBLIC_URL || ('http://localhost:' + port))); });