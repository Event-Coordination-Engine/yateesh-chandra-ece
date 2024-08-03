import axios from "axios"

const EVENT_URL = "http://127.0.0.1:8083"

class EventServices{

    // registerUser(User){
    //     return axios.post(USER_URL + "/register", User);
    // }

    // loginUser(User){
    //     return axios.post(USER_URL + "/login", User);
    // }

    getEventByUserId(user_id){
        return axios.get(EVENT_URL + "/event_by_user/" + user_id);
    }
}

export default new EventServices();