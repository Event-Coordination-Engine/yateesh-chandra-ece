import React, { useState } from "react";
import { FaEye, FaEyeSlash } from "react-icons/fa"; 
import SweetAlert from "../sweetalerts/SweetAlert";
import userService from "../services/userService";
import { useNavigate } from "react-router-dom";
import Swal from "sweetalert2";

const Login = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [emailError, setEmailError] = useState("");
    const [passwordError, setPasswordError] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();

    const redirect = () => {
        navigate("/")
    }

    const handleEmailChange = (e) => {
        setEmail(e.target.value);
    };

    const handlePasswordChange = (e) => {
        setPassword(e.target.value);
    };

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    const validateForm = () => {
        let isValid = true;

        if (!email) {
            setEmailError("Email is required");
            isValid = false;
        }
        
        if (!password) {
            setPasswordError("Password is required");
            isValid = false;
        }

        return isValid;
    };

    const handleFormSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            SweetAlert.registrationFailureFireAlert("Please Modify all error credentials");
            return;
        }

        try {
            const data = {
                email,
                password
            };
            const response = await userService.loginUser(data);
            localStorage.setItem("role", response.data.body.privilege);
            localStorage.setItem("id", response.data.body.user_id);
            localStorage.setItem("name", response.data.body.name);
            localStorage.setItem("email", response.data.body.email);
            localStorage.setItem("phone", response.data.body.phone);
            localStorage.setItem("log_id", response.data.body.log_id);
            SweetAlert.loginSuccessSwal("Signing you in")
            setTimeout( async () => {
                navigate("/dashboard");
            }, 1000)
            

        } catch (error) {
            console.error(error);
            if(error.response.data.detail == "Unregistered Email"){
                Swal.fire({
                    title : "Unauthorised",
                    icon : "error",
                    timer : 2000,
                })
                setEmailError(error.response.data.detail)
            }
            if(error.response.data.detail == "Invalid Credentials"){
                Swal.fire({
                    title : error.response.data.detail,
                    icon : "error",
                    timer : 2000,
                })
                setEmailError(error.response.data.detail)
            }
                
        }
    };

    return (
        <div className="login-form-container">
            <h1 className="h1-cool">Login</h1>
            <form onSubmit={handleFormSubmit} className="registration-form">

                <div className="form-group">
                    <label htmlFor="email">Email *</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={email}
                        onChange={handleEmailChange}
                        required
                    />
                    {emailError && <div className="error">{emailError}</div>}
                </div>

                <div className="form-group">
                    <label htmlFor="password">Password *</label>
                    <input
                        type={showPassword ? "text" : "password"}
                        id="password"
                        name="password"
                        value={password}
                        onChange={handlePasswordChange}
                        required
                    />
                    <button
                        type="button"
                        className="password-toggle-button"
                        onClick={togglePasswordVisibility}
                    >
                        {showPassword ? <FaEyeSlash /> : <FaEye />}
                    </button>
                    {passwordError && <div className="error">{passwordError}</div>}
                </div>

                <div className="button-group">
                    <button type="submit" className="login-submit-button">Login</button>
                    <button type="button" className="home-button" onClick={redirect}>Home</button>
                </div>
            
                <h3 className="h3-heading text">New to ECE? <a className = "cursor-pointer" onClick={() => {navigate("/register")}}>Enroll now</a></h3>
            </form>
        </div>
    );
}

export default Login;
