import { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { Link, useNavigate } from "react-router-dom";

const Register = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [password_1, setNewPassword] = useState("");
    const [email, setEmail] = useState("");
    const { RegisterUser, verifyCodeUser, resendCode, user } = useAuth();
    const [errorMsg, setErrorMessage] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [verified, setVerified] = useState<boolean | undefined>(undefined);
    const [verificationCode, setVerificationCode] = useState("");
    const [timeLeft, setTimeLeft] = useState(120);
    const [timerKey, setTimerKey] = useState(0);

    const userRef = useRef<HTMLInputElement>(null);
    const errRef = useRef<HTMLParagraphElement>(null);
    const navigate = useNavigate();

    useEffect(() => {
        userRef.current?.focus();
    }, []);

    useEffect(() => {
        if (user?.verified === false && verified === undefined) {
            setUsername(user.username);
            setEmail(user.email);
        }
    }, [])

    // useEffect(() => {
    //     if (verified === false) {
    //         setVerified(false)
    //     }
    // }, [])

    // useEffect(() => {
    //     if (verified === false) {
    //         setTimeLeft(120); // Reset on verified
    //         const interval = setInterval(() => {
    //             setTimeLeft((prev) => {
    //                 if (prev <= 1) {
    //                     clearInterval(interval);
    //                     return 0;
    //                 }
    //                 return prev - 1;
    //             });
    //         }, 1000);

    //         return () => clearInterval(interval);
    //     }
    // }, [verified]);

    useEffect(() => {
        if (verified === false) {
            setTimeLeft(120);
            setTimerKey(prev => prev + 1); // restart interval logic
        }
    }, [verified]);

    useEffect(() => {
        const interval = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    clearInterval(interval);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(interval);
    }, [timerKey]);

    useEffect(() => {
        setErrorMessage("");
    }, [username, email, password, password_1]);

    const handleVerificationCode = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const res = await verifyCodeUser(username, verificationCode);
            if (res) {
                setVerified(true);
                navigate('/chat');
            } else {
                setErrorMessage("Verification code is not correct");
            }
        } catch (err) {
            setVerificationCode("");
            setErrorMessage("Verification code is not correct");
            errRef.current?.focus();
        } finally {
            setIsLoading(false);
        }
    }

    const rescendCode = async () => {
        setIsLoading(true);
        try {
            await resendCode(username, email);
            setTimeLeft(120);
            setTimerKey(prev => prev + 1);
        } catch (err) {
            setErrorMessage("Something went wrong");
            errRef.current?.focus();
        } finally {
            setIsLoading(false);
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        if (password === password_1) {
            try {
                await RegisterUser(username, password_1, email);
                setVerified(false);
                setPassword("");
                setNewPassword("");
            } catch (err) {
                setUsername("");
                setPassword("");
                setNewPassword("");
                setEmail("")
                setErrorMessage("Login failed. Please check your credentials.");
                errRef.current?.focus();
            } finally {
                setIsLoading(false);
            }
        } else {
            setErrorMessage("Registration failed. Passwords do not match");
        }
    };

    if (verified === false || user?.verified === false) {
        return (
            <div className="min-h-screen bg-gray-100 text-gray-800 px-4 py-8">
                <div className="w-full max-w-md bg-white shadow-lg rounded-xl p-10 mx-auto mt-16">
                    <h1 className="text-3xl font-semibold text-center mb-6">Verify Your Email</h1>

                    {errorMsg && (
                        <p
                            ref={errRef}
                            className="text-red-700 bg-red-100 border border-red-300 p-3 rounded text-sm mb-4"
                            aria-live="assertive"
                        >
                            {errorMsg}
                        </p>
                    )}

                    <form onSubmit={handleVerificationCode} className="space-y-5">
                        <p>A verification code has been sent to your email. It will expire in {timeLeft} seconds.</p>
                        <div>
                            <label htmlFor="verification_code" className="block text-sm font-medium mb-1">
                                Verification code
                            </label>
                            <input
                                type="text"
                                name="verification_code"
                                id="verification_code"
                                autoComplete="off"
                                required
                                ref={userRef}
                                value={verificationCode}
                                onChange={(e) => {
                                    setVerificationCode(e.target.value);
                                    if (errorMsg) setErrorMessage("");
                                }}
                                className="w-full px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Enter your verification code"
                            />
                        </div>

                        <div className="pt-2 flex flex-col gap-3">
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded transition-transform transform hover:scale-105 cursor-pointer text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isLoading ? "Verifying..." : "Verify"}
                            </button>

                            <button
                                type="button"
                                disabled={isLoading || timeLeft > 0}
                                onClick={rescendCode}
                                className="w-full py-3 px-6 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded transition-transform transform hover:scale-105 cursor-pointer text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {timeLeft > 0 ? `Resend available in ${timeLeft}s` : "Resend Verification Code"}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        );
    }
    if (verified === undefined) {
        return (
            <div className="min-h-screen bg-gray-100 text-gray-800 px-4 py-8">
                {/* Login Form */}
                <div className="w-full max-w-md bg-white shadow-lg rounded-xl p-10 mx-auto mt-16">
                    <h1 className="text-3xl font-semibold text-center mb-6">Sign In</h1>

                    {errorMsg && (
                        <p
                            ref={errRef}
                            className="text-red-700 bg-red-100 border border-red-300 p-3 rounded text-sm mb-4"
                            aria-live="assertive"
                        >
                            {errorMsg}
                        </p>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label htmlFor="username" className="block text-sm font-medium mb-1">
                                Username
                            </label>
                            <input
                                type="text"
                                name="username"
                                id="username"
                                autoComplete="off"
                                required
                                ref={userRef}
                                value={username}
                                onChange={(e) => {
                                    setUsername(e.target.value);
                                    if (errorMsg) setErrorMessage("");
                                }}
                                className="w-full px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Enter your username"
                            />
                        </div>

                        <div>
                            <label htmlFor="email" className="block text-sm font-medium mb-1">
                                Email
                            </label>
                            <input
                                type="email"
                                name="email"
                                id="email"
                                autoComplete="off"
                                required
                                value={email}
                                onChange={(e) => {
                                    setEmail(e.target.value);
                                    if (errorMsg) setErrorMessage("");
                                }}
                                className="w-full px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Enter your email"
                            />
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium mb-1">
                                Password
                            </label>
                            <input
                                type="password"
                                name="password"
                                id="password"
                                autoComplete="off"
                                required
                                value={password}
                                onChange={(e) => {
                                    setPassword(e.target.value);
                                    if (errorMsg) setErrorMessage("");
                                }}
                                className="w-full px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Enter your password"
                            />
                        </div>

                        <div>
                            <label htmlFor="new_password" className="block text-sm font-medium mb-1">
                                Password verification
                            </label>
                            <input
                                type="password"
                                name="password_"
                                id="password_1"
                                autoComplete="off"
                                required
                                value={password_1}
                                onChange={(e) => {
                                    setNewPassword(e.target.value);
                                    if (errorMsg) setErrorMessage("");
                                }}
                                className="w-full px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Verify your password"
                            />
                        </div>

                        <div>
                            <ul style={{ fontSize: '0.9rem', marginTop: '8px' }}>
                                <li>At least 10 characters</li>
                                <li>At least 1 uppercase letter</li>
                                <li>At least 1 lowercase letter</li>
                                <li>At least 1 number</li>
                                <li>At least 1 special character (e.g. !@#$%)</li>
                            </ul>

                        </div>

                        <div className="pt-2">
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded transition-transform transform hover:scale-105 cursor-pointer text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isLoading ? "Signing Up..." : "Submit"}
                            </button>
                        </div>
                        <div className="pt-2">
                            If you do have an account just Sign In <Link to='/login'>here</Link>
                        </div>
                    </form>
                </div>
            </div>
        )
    }
};

export default Register;
