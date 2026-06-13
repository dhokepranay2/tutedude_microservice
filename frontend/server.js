const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

const FLASK_BASE_URL = process.env.FLASK_API_URL || 'http://backend:5000';

// --- HTML Page Routes ---
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'views', 'index.html'));
});

app.get('/grades', (req, res) => {
    res.sendFile(path.join(__dirname, 'views', 'grades.html'));
});

// --- API Forwarding Routes ---
app.post('/submit-todo', async (req, res) => {
    try {
        const response = await axios.post(`${FLASK_BASE_URL}/process_todo`, req.body);
        res.send(`
            <h2 style="color: green;">Success!</h2>
            <p>${response.data.message}</p>
            <a href="/">Add another To-Do</a> | <a href="/grades">Go to Grades</a>
        `);
    } catch (error) {
        res.status(500).send(`Error communicating with Flask: ${error.message}`);
    }
});

app.post('/submit-grade', async (req, res) => {
    try {
        const response = await axios.post(`${FLASK_BASE_URL}/process_grade`, req.body);
        res.send(`
            <h2 style="color: green;">Success!</h2>
            <p>${response.data.message}</p>
            <a href="/grades">Add another Grade</a> | <a href="/">Go to To-Dos</a>
        `);
    } catch (error) {
        res.status(500).send(`Error communicating with Flask: ${error.message}`);
    }
});

// --- API Proxy Routes for GET calls ---
app.get('/api/grades', async (req, res) => {
    try {
        const response = await axios.get(`${FLASK_BASE_URL}/api/grades`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "Failed to fetch grades from backend." });
    }
});

app.get('/api/todos', async (req, res) => {
    try {
        const response = await axios.get(`${FLASK_BASE_URL}/api/todos`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "Failed to fetch todos from backend." });
    }
});

app.listen(3000, () => {
    console.log('Frontend server is running on port 3000');
});