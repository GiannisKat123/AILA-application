import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const useLoginLogic = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const { loginUser, sendCode } = useAuth();
    const [errorMsg, setErrorMessage] = useState("");

    const userRef = useRef<HTMLInputElement>(null);
    const errRef = useRef<HTMLParagraphElement>(null);
    let isLoading = false;
    const navigate = useNavigate();
    useEffect(() => { userRef.current?.focus() }, []);

    console.log("Login Form");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            const res = await loginUser(username, password);
            // Case 1: Success & verified
            if (res && "user_details" in res) {
                const { username, email, verified, role } = res.user_details;
                console.log("USER VALUES", username, email, verified, role);
                isLoading = true;
                if (verified) {
                    navigate("/chat");
                } else {
                    // Case 2: Not verified → resend code
                    await sendCode(username, email, role);
                    navigate("/register");
                }

                // Case 3: Error returned by API
            } else if (res && "error_message" in res) {
                setErrorMessage(res.error_message);
                errRef.current?.focus();
                setUsername("");
                setPassword("");
            }
            // Unknown failure
            else {
                // Login failed — wrong credentials, user not found, etc.
                setErrorMessage("Login failed. Something happened");
                errRef.current?.focus();
                setUsername("");
                setPassword("");
            }
        } catch (err) {
            console.error("Login error:", err);
            setErrorMessage(String(err));
            errRef.current?.focus();
            setUsername("");
            setPassword("");
        } finally {
            isLoading = false;
        }
    };

    return {
        // state
        username,
        setUsername,
        password,
        setPassword,
        errorMsg,
        isLoading,
        userRef,
        errRef,
        handleSubmit,
        setErrorMessage
    };
}


export default useLoginLogic;