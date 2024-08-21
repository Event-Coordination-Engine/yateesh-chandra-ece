import axios from "axios"

const EVENT_URL = "http://127.0.0.1:8083"

class RegistrationServices{

    getRegisteredEventsByUser(user_id){
        return axios.get(EVENT_URL + "/registered_event/users/" + user_id);
    }

    createEvent(body){
        return axios.post(EVENT_URL + "/create-event", body);
    }

}

export default new RegistrationServices();