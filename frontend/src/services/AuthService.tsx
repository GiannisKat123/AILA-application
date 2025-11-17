import axios from 'axios';
import api from '../api/axios.jsx';
import type {
    LoginAPIOutput,
    UserProfile,
    ErrorMessage,
} from '../models/Types.tsx';

const loginAPI = async (username: string, password: string): Promise<LoginAPIOutput | ErrorMessage> => {
    try {
        const response = await api.post('/login', { username: username, password: password }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (axios.isAxiosError(err)) {
            return { error_message: err.response?.data.detail };
        }
        else {
            console.error("Non-Axios error:", err);
            return { error_message: String(err) };
        }
    }
}

const registerAPI = async (username: string, password: string, email: string, role: string): Promise<boolean | ErrorMessage> => {
    try {
        const response = await api.post('/register', { username: username, password: password, email: email, role: role }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (axios.isAxiosError(err)) {
            return { error_message: err.response?.data.detail };
        }
        else {
            return { error_message: String(err) };
        }
    }
}

const verifyAPI = async (username: string, code: string): Promise<boolean | ErrorMessage> => {
    try {
        const response = await api.post('/verify', { username: username, verification_code: code }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (axios.isAxiosError(err)) {
            return { error_message: err.response?.data.detail };
        }
        else {
            return { error_message: String(err) };
        }
    }
}

const sendCodeAPI = async (username: string, email: string, role: string): Promise<boolean | undefined> => {
    try {
        const response = await api.post('/send_code', { username: username, email: email, role: role }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}


const verifyUser = async (): Promise<UserProfile | undefined> => {
    try {
        const response = await api.get('/get_user', { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}


const requestAPI = async (userQuery: string): Promise<boolean | undefined> => {
    try {
        const response = await api.post('/request', { message: userQuery }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}

const logoutAPI = async (): Promise<boolean | undefined> => {
    try {
        const response = await api.post('/logout')
        if (response) return true;
    }
    catch (err) {
        console.error("Logout failed:", err);
        return false;
    }
}



export { loginAPI, sendCodeAPI, verifyAPI, logoutAPI, registerAPI, requestAPI, verifyUser };

