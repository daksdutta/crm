import { useState } from "react";
import { loginUser } from "../services/authService";
import { useNavigate } from "react-router-dom";

function Login() {
    const navigate = useNavigate();
    
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleLogin = async (e) => {
    e.preventDefault();

    try {
        const res = await loginUser({ email, password });

        // store token
        localStorage.setItem("token", res.access);

        navigate("/dashboard");
    } catch (error) {
        console.error("Login failed", error);
    }
    };

    return (
        <div style={{ padding: "50px" }}>
        <h2>Login</h2>

        <form onSubmit={handleLogin}>
            <div>
            <input
                type="email"
                placeholder="Enter Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />
            </div>

            <div>
            <input
                type="password"
                placeholder="Enter Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            </div>

            <button type="submit">Login</button>
        </form>
        </div>
    );
}

export default Login;