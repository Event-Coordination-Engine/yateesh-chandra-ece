import React, { useState } from "react";
// import {useNavigate} from 'react-router-dom';
import SweetAlert from "../sweetalerts/SweetAlert";
import userService from "../services/userService";

const Registration = () => {

    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");

    const [nameError, setNameError] = useState("");
    const [lastNameError, setLastNameError] = useState("");
    const [emailError, setEmailError] = useState("");
    const [passwordError, setPasswordError] = useState("");
    const [confirmPasswordError, setConfirmPasswordError] = useState("");
    const [phoneNumberError, setPhoneNumberError] = useState("");

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    // const navigate = useNavigate()

    const handleNameChange = (e) => {
        setFirstName(e.target.value);
        if (nameError) {
        setNameError("");
        }
    };

    const handleLastNameChange = (e) => {
        setLastName(e.target.value);
        if (lastNameError) {
        setLastNameError("");
        }
    };

    const handleEmailChange = (e) => {
        const newEmail = e.target.value;
        setEmail(newEmail);
        if (!newEmail) {
            setEmailError("Email is required");
        } else if (!newEmail.endsWith("@nucleusteq.com")) {
            setEmailError("Email must be in the form of @nucleusteq.com domain");
        } else {
            setEmailError("");
        }
    };

    const handlePasswordChange = (e) => {
        setPassword(e.target.value);
        if (!password) {
            setPasswordError("Password is required ");
        } else if (password.length < 7) {
            setPasswordError("Password must be at least 8 characters");
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
        setPhoneNumber(numericInput);
        if (numericInput.length < 10) {
            setPhoneNumberError("Phone number must be 10 digits");
        } else {
            setPhoneNumberError("");
        }
    };

    // const togglePasswordVisibility = () => {
    //     setShowPassword(!showPassword);
    // };

    // const toggleConfirmPasswordVisibility = () => {
    //     setShowConfirmPassword(!showConfirmPassword);
    // };

    const validateForm = () => {
        let isValid = true;
        if (!firstName) {
            setNameError("User Name is required");
            isValid = false;
        } else if (firstName.startsWith(" ")){
            setNameError("Name cannot start with spaces");
            isValid = false;
        } else{
            setNameError("");
        }

        if (!email) {
            setEmailError("Email is required");
            isValid = false;
        } else if (!email.endsWith("@nucleusteq.com")) {
            isValid = false;
            setEmailError("Email must be in the form of @nucleusteq.com domain");
        } else {
            setEmailError("");
        }

        if (!password) {
            setPasswordError("Password is required ");
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

        if (!phoneNumber) {
            setPhoneNumberError("Phone Number is required");
            isValid = false;
        } else if (phoneNumber.length < 10 || phoneNumber.length > 10) {
            setPhoneNumberError("Phone number must be 10 digits.");
            isValid = false;
        } else {
            setPhoneNumberError("");
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
                firstName,
                lastName,
                email,
                password,
                phoneNumber,
            };

            await userService.registerUser(data);
            SweetAlert.registrationSuccessFireAlert();
            // navigate("/login");

        } catch (error) {
            if(error.response.data.password === "Password must contain at least one uppercase letter and one digit"){
                SweetAlert.registrationFailureFireAlert(error.response.data.password);
                setPasswordError("Password must contain atleast one uppercase and number");
            }

            if(error.response.data.message === "Email already Exists"){
                SweetAlert.registrationFailureFireAlert(error.response.data.message);
                setEmailError(error.response.data.message);
            }
        }
    };

    return(
        <div className="registration-form-container">
            <h1>Register</h1>
            <form onSubmit={handleFormSubmit} className="registration-form">
                <div className="form-group">
                <label htmlFor="firstName">First Name</label>
                    <input
                    type="text"
                    id="firstName"
                    name="firstName"
                    value={firstName}
                    onChange={handleNameChange}
                    required
                    />
                    {nameError && <div className="error">{nameError}</div>}
                </div>
                
                <div className="form-group">
                <label htmlFor="lastName">Last Name</label>
                    <input
                    type="text"
                    id="lastName"
                    name="lastName"
                    value={lastName}
                    onChange={handleLastNameChange}
                    required
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
                    {passwordError && <div className="error">{passwordError}</div>}

                    {/* <ButtonComponent
                        type = "button"
                        className = "password-toggle-button"
                        onClick={togglePasswordVisibility}
                        text = {showPassword ? <FaEyeSlash/> : <FaEye/>} 
                        /> */}
                </div>
    

                <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                    <input
                    type={showConfirmPassword ? "text" :"password"}
                    id="confirmPassword"
                    name="confirmPassword"
                    value={confirmPassword}
                    onChange={handleConfirmPasswordChange}
                    required
                    />
                    {/* <ButtonComponent
                        type = "button"
                        className = "password-toggle-button"
                        onClick={toggleConfirmPasswordVisibility}
                        text = {showConfirmPassword ? <FaEyeSlash/> : <FaEye/>} 
                        /> */}
                    {confirmPasswordError && <div className="error">{confirmPasswordError}</div>}
                </div>

                <div className="form-group">
                <label htmlFor="phone">Phone number</label>
                    <input
                    type="phone"
                    id="phoneNumber"
                    name="phoneNumber"
                    pattern="[0-9]*"
                    value={phoneNumber}
                    onChange={handlephoneChange}
                    required
                    />
                    {phoneNumberError && <div className="error">{phoneNumberError}</div>}
                </div>
    

                <button type="submit" className="submit-button">Register</button>
            
                <h3 className = "h3-heading text" text = "Already our Subscriber? " to = "/login" link = "Login Now"/>
            
            </form>
        </div>
    );
}

export default Registration;