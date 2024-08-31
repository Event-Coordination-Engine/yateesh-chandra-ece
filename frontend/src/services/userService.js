import axios from "axios"

const USER_URL = "http://127.0.0.1:8083/user"

class UserServices{

    registerUser(User){
        console.log(USER_URL + "/register", "post");
        return axios.post(USER_URL + "/register", User);
    }

    loginUser(User){
        return axios.post(USER_URL + "/login", User);
    }

    logoutUser(log_id){
        return axios.put(USER_URL + "/logout/" + log_id)
    }

}

export default new UserServices();