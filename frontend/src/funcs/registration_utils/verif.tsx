import { useEffect } from 'react';
import useRegisterLogic from "./funcs";
import { useAuth } from '../../context/AuthContext';

const VerForm = () => {
    const {
        userRef,
        verificationCode,
        errorMsg,
        errRef,
        handleVerificationCode,
        setVerificationCode,
        setErrorMessage,
        isLoading,
        resendCode,
        timeLeft, setTimeLeft,
        timerKey, setTimeKey,
    } = useRegisterLogic();

    const { user } = useAuth();

    useEffect(() => {
        if (user?.verified === false) {
            setTimeLeft(120);
            setTimeKey(prev => prev + 1);
        }
    }, [user?.verified]);

    // // Timer countdown logic
    useEffect(() => {
        const interval = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    clearInterval(interval);
                    return 0;
                }
                return prev - 1;
            })
        }, 1000);
        return () => clearInterval(interval);
    }, [timerKey]);

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
                            onClick={resendCode}
                            className="w-full py-3 px-6 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded transition-transform transform hover:scale-105 cursor-pointer text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {timeLeft > 0 ? `Resend available in ${timeLeft}s` : "Resend Verification Code"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default VerForm;