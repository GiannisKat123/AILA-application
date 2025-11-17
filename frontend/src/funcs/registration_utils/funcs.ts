import { useEffect, useRef, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router";

const useRegisterLogic = () => {
    // ------------------ State ------------------
    const [username, setUsername] = useState("");
    const [pass1, setPass1] = useState("");
    const [pass2, setPass2] = useState("");
    const [role, setRole] = useState("");
    const [email, setEmail] = useState("");
    const [errorMsg, setErrorMessage] = useState("");
    const [verificationCode, setVerificationCode] = useState("");
    const [timeLeft, setTimeLeft] = useState(120);
    const [timerKey, setTimeKey] = useState(0);

    let isLoading = false;
    let verified = undefined;

    const {
        RegisterUser,
        verifyCodeUser,
        sendCode,
        user
    } = useAuth();

    // ------------------ Refs ------------------
    const userRef = useRef<HTMLInputElement>(null);
    const errRef = useRef<HTMLParagraphElement>(null);

    const navigate = useNavigate();
    useEffect(() => { userRef.current?.focus(); }, []);

    const handleVerificationCode = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            console.log(user?.username, verificationCode);
            if (!user) return;
            const res = await verifyCodeUser(user?.username, verificationCode);
            isLoading = true;
            if (typeof res === 'boolean' && res === true) {
                verified = true;
                navigate('/login');
            } else if (typeof res === 'object' && 'error_message' in res) {
                setVerificationCode("");
                setErrorMessage(res.error_message);
            }
            else {
                setVerificationCode("");
                setErrorMessage("User Verification failed");
            }
        } catch (err) {
            setVerificationCode("");
            setErrorMessage("User Verification failed");
            errRef.current?.focus();
        } finally {
            isLoading = false;
        }
    }

    /**
     * Resend verification code.
     * - Only available once timer has expired
     */
    const resendCode = async () => {
        isLoading = true;
        if (!user) return;
        try {
            await sendCode(user.username, user.email, user.role);
            setTimeLeft(120);
            setTimeKey(prev => prev + 1);
        } catch (err) {
            setErrorMessage("Something went wrong");
            errRef.current?.focus();
        } finally {
            isLoading = false;
        }
    }

    /**
     * Handle registration form submission.
     * - Validates password match
     * - Calls backend RegisterUser
     * - Sets verification state if registration successful
     * - Displays error if failure
     */
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (pass1 === pass2) {
            try {
                const res = await RegisterUser(username, pass1, email, role);
                if (res === true) {
                    verified = false;
                    setPass1("");
                    setPass2("");
                    setRole("");
                }
                else if (res && "error_message" in res) {
                    setUsername("");
                    setPass1("");
                    setPass2("");
                    setEmail("");
                    setRole("");
                    setErrorMessage(res.error_message);
                    errRef.current?.focus();
                }
                else {
                    setUsername("");
                    setPass1("");
                    setPass2("");
                    setEmail("");
                    setRole("");
                    setErrorMessage("Registratiion failed. Something happened");
                    errRef.current?.focus();
                }

            } catch (err) {
                setUsername("");
                setPass1("");
                setPass2("");
                setRole("");
                setEmail("")
                setErrorMessage(`Registratiion failed. Something happened ${err}`);
                errRef.current?.focus();
            } finally {
                isLoading = false;
            }
        } else {
            setUsername("");
            setPass1("");
            setPass2("");
            setEmail("")
            setRole("");
            setErrorMessage("Registration failed. Passwords do not match");
            errRef.current?.focus();
            isLoading = false;
        }
    };

    return {
        username, setUsername,
        pass1, setPass1,
        pass2, setPass2,
        role, setRole,
        email, setEmail,
        errorMsg, setErrorMessage,
        isLoading,
        verified,
        verificationCode, setVerificationCode,
        userRef,
        errRef,
        handleVerificationCode,
        resendCode,
        handleSubmit,
        user,
        timeLeft, setTimeLeft,
        timerKey, setTimeKey
    }
}

export default useRegisterLogic;