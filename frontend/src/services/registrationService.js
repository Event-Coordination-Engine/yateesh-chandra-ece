import axios from "axios"

const ATTENDEE_URL = "http://127.0.0.1:8083"

class RegistrationServices{

    getRegisteredEventsByUser(user_id){
        return axios.get(ATTENDEE_URL + "/registered_event/users/" + user_id);
    }

    registerEvent(body){
        return axios.post(ATTENDEE_URL + "/register_event", body);
    }

    availableEvents(user_id){
        return axios.get(ATTENDEE_URL + "/available-events/" + user_id)
    }

    approvedEvents(){
        return axios.get(ATTENDEE_URL + "/approved-events")
    }
    
    getAllRegistrations(){
        return axios.get(ATTENDEE_URL + "/all_registered_events")
    }

}

export default new RegistrationServices();