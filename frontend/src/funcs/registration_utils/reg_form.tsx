import { Link } from "react-router-dom";
import useRegisterLogic from "./funcs";


const RegForm = () => {

    const {
        username, setUsername,
        pass1, setPass1,
        pass2, setPass2,
        role, setRole,
        email, setEmail,
        errorMsg, setErrorMessage,
        isLoading,
        userRef,
        errRef,
        handleSubmit,
    } = useRegisterLogic();

    return (
        <div className="min-h-screen bg-gray-100 text-gray-800 px-4 py-8">
            {/* Login Form */}
            <div className="w-full max-w-md bg-white shadow-lg rounded-xl p-10 mx-auto mt-16">
                <h1 className="text-3xl font-semibold text-center mb-6">Sign Up</h1>

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
                            value={pass1}
                            onChange={(e) => {
                                setPass1(e.target.value);
                                if (errorMsg) setErrorMessage("");
                            }}
                            className="w-full px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter your password"
                        />
                    </div>

                    <div>
                        <label htmlFor="password_verify" className="block text-sm font-medium mb-1">
                            Password verification
                        </label>
                        <input
                            type="password"
                            name="password_verify"
                            id="password_verify"
                            autoComplete="off"
                            required
                            value={pass2}
                            onChange={(e) => {
                                setPass2(e.target.value);
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

                    <fieldset className="space-y-2">
                        <legend className="font-medium mb-2">Select your role</legend>

                        <div className="flex items-center">
                            <input
                                type="radio"
                                id="user"
                                name="role"
                                value="user"
                                required
                                checked={role === "user"}
                                onChange={(e) => setRole(e.target.value)}
                                className="peer"
                            />
                            <label htmlFor="user" className="ml-2 cursor-pointer peer-checked:font-semibold">
                                Normal User
                            </label>
                        </div>

                        <div className="flex items-center">
                            <input
                                type="radio"
                                id="lawyer"
                                name="role"
                                value="lawyer"
                                required
                                checked={role === "lawyer"}
                                onChange={(e) => setRole(e.target.value)}
                                className="peer"
                            />
                            <label htmlFor="lawyer" className="ml-2 cursor-pointer peer-checked:font-semibold">
                                Lawyer
                            </label>
                        </div>
                    </fieldset>

                    <div className="pt-2">
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded transition-transform transform hover:scale-105 cursor-pointer text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? "Signing Up..." : "Submit"}
                        </button>
                    </div>
                    <div className="pt-4 text-sm text-center text-gray-600">
                        <span>If you do have an account just</span>{' '}
                        <Link
                            to="/login"
                            className="font-semibold text-blue-600 hover:underline hover:text-blue-800 transition-colors"
                        >
                            Sign In here
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default RegForm;