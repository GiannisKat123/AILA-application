import axios from 'axios';

const api = axios.create({
    // baseURL: "https://ailademo.fly.dev", // Update with your backend URL
    baseURL: "http://localhost:8080",
    // baseURL: "/",
    withCredentials: true
})

export default api;