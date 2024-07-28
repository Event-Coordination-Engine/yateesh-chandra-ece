import React, { useState } from "react";
import { FaEye, FaEyeSlash } from "react-icons/fa";  // Importing eye icons
import SweetAlert from "../sweetalerts/SweetAlert";
import userService from "../services/userService";
import { useNavigate } from "react-router-dom";
import Swal from "sweetalert2";

const Registration = () => {
    const [first_name, setfirst_name] = useState("");
    const [last_name, setlast_name] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [phone, setphone] = useState("");

    const [nameError, setNameError] = useState("");
    const [emailError, setEmailError] = useState("");
    const [passwordError, setPasswordError] = useState("");
    const [confirmPasswordError, setConfirmPasswordError] = useState("");
    const [phoneError, setphoneError] = useState("");

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const navigate = useNavigate()

    const redirect = () => {
        navigate("/")
    }

    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    const handleNameChange = (e) => {
        setfirst_name(e.target.value);
        if (nameError) {
            setNameError("");
        }
    };

    const handlelast_nameChange = (e) => {
        setlast_name(e.target.value);
    };

    const handleEmailChange = (e) => {
        const newEmail = e.target.value;
        setEmail(newEmail);
        if (!newEmail) {
            setEmailError("Email is required");
        } else if (!emailPattern.test(newEmail)) {
            setEmailError("Invalid Email Format");
        } else {
            setEmailError("");
        }
    };

    const handlePasswordChange = (e) => {
        setPassword(e.target.value);
        if (!password) {
            setPasswordError("Password is required ");
        } else if (password.length < 6) {
            setPasswordError("Password must be at least 7 characters");
        } else {
            setPasswordError("");
        }
    };

    const handleConfirmPasswordChange = (e) => {
        const newConfirmPassword = e.target.value;
        setConfirmPassword(newConfirmPassword);

        if (!newConfirmPassword) {
            setConfirmPasswordError("Confirm Password is required");
        } else if (password !== newConfirmPassword) {
            setConfirmPasswordError("Passwords do not match");
        } else {
            setConfirmPasswordError("");
        }
    };

    const handlephoneChange = (e) => {
        const numericInput = e.target.value.replace(/\D/g, "");
        setphone(numericInput);
        if (numericInput.length < 10) {
            setphoneError("Phone number must be 10 digits");
        } else {
            setphoneError("");
        }
    };

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    const toggleConfirmPasswordVisibility = () => {
        setShowConfirmPassword(!showConfirmPassword);
    };

    const validateForm = () => {
        let isValid = true;
        if (!first_name) {
            setNameError("User Name is required");
            isValid = false;
        } else if (first_name.startsWith(" ")){
            setNameError("Name cannot start with spaces");
            isValid = false;
        } else{
            setNameError("");
        }

        if (!email) {
            setEmailError("Email is required");
            isValid = false;
        } else if (!emailPattern.test(email)) {
            isValid = false;
            setEmailError("Invalid Email Format detected");
        } else {
            setEmailError("");
        }
        
        if (!password) {
            setPasswordError("Password is required");
            isValid = false;
        }
        if (!confirmPassword) {
            setConfirmPasswordError("Write Password to confirm");
            isValid = false;
        } else {
            setConfirmPasswordError("");
        }

        if (password !== confirmPassword) {
            setConfirmPasswordError("Passwords did not match");
            isValid = false;
        }

        if (!phone) {
            setphoneError("Phone Number is required");
            isValid = false;
        } else if (phone.length < 10 ) {
            setphoneError("Phone number must be atleast 10 digits.");
            isValid = false;
        } else {
            setphoneError("");
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
                first_name,
                last_name : last_name || null,
                email,
                password,
                phone,
            };
            console.log(data);
            await userService.registerUser(data);
            SweetAlert.registrationSuccessFireAlert();
            navigate("/login");

        } catch (error) {
            console.log(error);
            if (error.response.data.detail === "User with same Email already exists") {
                Swal.fire({
                    timer : 2000,
                    titleText : "Oops.! Duplicate Email not allowed",
                    icon : "warning"
                })
                setEmailError(error.response.data.detail);
            }
        }
    };

    return (
        <div className="registration-form-container">
            <h1 className="h1-cool">Enrollment Form</h1>
            <form onSubmit={handleFormSubmit} className="registration-form">
                <div className="form-group">
                    <label htmlFor="first_name">First Name</label>
                    <input
                        type="text"
                        id="first_name"
                        name="first_name"
                        value={first_name}
                        onChange={handleNameChange}
                        required
                    />
                    {nameError && <div className="error">{nameError}</div>}
                </div>
                
                <div className="form-group">
                    <label htmlFor="last_name">Last Name</label>
                    <input
                        type="text"
                        id="last_name"
                        name="last_name"
                        value={last_name}
                        onChange={handlelast_nameChange}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="email">Email</label>
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
                    <label htmlFor="password">Password</label>
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

                <div className="form-group">
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <input
                        type={showConfirmPassword ? "text" : "password"}
                        id="confirmPassword"
                        name="confirmPassword"
                        value={confirmPassword}
                        onChange={handleConfirmPasswordChange}
                        required
                    />
                    <button
                        type="button"
                        className="password-toggle-button"
                        onClick={toggleConfirmPasswordVisibility}
                    >
                        {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                    </button>
                    {confirmPasswordError && <div className="error">{confirmPasswordError}</div>}
                </div>

                <div className="form-group">
                    <label htmlFor="phone">Phone number</label>
                    <input
                        type="phone"
                        id="phone"
                        name="phone"
                        pattern="[0-9]*"
                        value={phone}
                        onChange={handlephoneChange}
                        required
                    />
                    {phoneError && <div className="error">{phoneError}</div>}
                </div>

                <div className="button-group">
                    <button type="submit" className="submit-button">Register</button>
                    <button type="button" className="home-button" onClick={redirect}>Home</button>
                </div>
            
                <h3 className="h3-heading text">Already our Subscriber? <a className = "cursor-pointer" onClick={() => {navigate("/login")}}>Login Now</a></h3>
            </form>
        </div>
    );
}

export default Registration;
