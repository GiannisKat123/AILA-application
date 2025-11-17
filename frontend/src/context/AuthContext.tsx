
import React, { createContext, useContext, useEffect, useState } from 'react'
import {
    loginAPI,
    sendCodeAPI,
    verifyAPI,
    logoutAPI,
    registerAPI,
    verifyUser,
} from '../services/AuthService.jsx';
import type {
    LoginAPIOutput,
    UserProfile,
    ErrorMessage,
} from '../models/Types.jsx';

export interface AuthContextType {
    user: UserProfile | null;
    loading: boolean;
    loginUser: (username: string, password: string) => Promise<LoginAPIOutput | ErrorMessage> | null;
    logoutUser: () => Promise<void>;
    RegisterUser: (username: string, password: string, email: string, role: string) => Promise<boolean | ErrorMessage>;
    verifyCodeUser: (username: string, code: string) => Promise<boolean | ErrorMessage>;
    sendCode: (username: string, email: string, role: string) => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);

    const RegisterUser = async (username: string, password: string, email: string, role: string): Promise<boolean | ErrorMessage> => {
        try {
            const res = await registerAPI(username, password, email, role);
            console.log(res);
            if (res && res === true) {
                setUser({ username: username, email: email, verified: false, role: role })
                return true;
            }
            else if (res && typeof res === 'object' && 'error_message' in res) {
                setUser(null);
                return { error_message: res.error_message }
            }
            else {
                setUser(null);
                return { error_message: 'Something went wrong in registration' }
            }
        }
        catch (err) {
            setUser(null);
            return { error_message: String(err) };
        }
    }

    const verifyCodeUser = async (username: string, code: string): Promise<boolean | ErrorMessage> => {
        try {
            const res = await verifyAPI(username, code);
            if (res === true) {
                setUser(prev => prev ? { ...prev, verified: true } : prev);
                return true;
            }
            else if (res && typeof res == 'object' && 'error_message' in res) {
                return { error_message: res.error_message }
            }
            else {
                console.log("WHAT", res);
                return { error_message: 'Something went wrong in verification' }
            }
        }
        catch (err) {
            console.error("Verification failed", err);
            setUser(null);
            return { error_message: String(err) };
        }
    }

    const sendCode = async (username: string, email: string, role: string): Promise<void> => {
        try {
            const res = await sendCodeAPI(username, email, role);
            if (res) {
                return;
            }
            else {
                throw new Error("Resend Code failed: No response from API");
            }
        }
        catch (err) {
            console.error("Resend Code failed", err);
            setUser(null);
            throw err;
        }
    }

    const loginUser = async (username: string, password: string): Promise<LoginAPIOutput | ErrorMessage> => {
        console.log("Logging in user:", username);
        try {
            const res = await loginAPI(username, password);
            if (res && typeof res === 'object' && "user_details" in res) {
                setUser({ username: res.user_details.username, email: res.user_details.email, verified: res.user_details.verified, role: res.user_details.role })
                return res;
            }
            else if (res && typeof res === 'object' && "error_message" in res) {
                setUser(null);
                return { error_message: res.error_message }
            }
            // Ensure a return value in all cases
            setUser(null);
            return { error_message: "Unknown error during login" };
        }
        catch (err) {
            console.error("Login failed", err);
            setUser(null);
            return { error_message: String(err) }
        }
    }


    const logoutUser = async () => {
        try {
            const res = await logoutAPI();
            if (res) {
                setUser(null);
            }
            else {
                setUser(null);
                console.log("Something went completely wrong");
            }

        }
        catch (err) {
            setUser(null);
            console.error("Logout failed", err);
        }
    }

    useEffect(() => {
        const initialize = async () => {
            try {
                const res = await verifyUser();
                if (res) {
                    setUser(res);
                }
            }
            catch {
                console.log("Something happened");
                setUser(null);
            }
            finally {
                setLoading(false);
            }
        };
        initialize();
    }, [])

    return (
        <AuthContext.Provider value={{ user, sendCode, verifyCodeUser, RegisterUser, loginUser, logoutUser, loading }}>
            {children}
        </AuthContext.Provider>
    )

}

export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
