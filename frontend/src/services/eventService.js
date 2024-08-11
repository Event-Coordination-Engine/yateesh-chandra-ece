import axios from "axios"

const EVENT_URL = "http://127.0.0.1:8083"

class EventServices{

    getEventByUserId(user_id){
        return axios.get(EVENT_URL + "/event_by_user/" + user_id);
    }

    getPendingEventsByUserId(user_id){
        return axios.get(EVENT_URL + "/event_by_user/pending/" + user_id);
    }

    createEvent(body){
        return axios.post(EVENT_URL + "/create-event", body);
    }

    deleteEvent(id){
        return axios.delete(EVENT_URL + "/delete-event/" + id);
    }

    updateEvent(id, body){
        return axios.put(EVENT_URL + "/event/" + id, body)
    }

    getEventById(id){
        return axios.get(EVENT_URL + "/event/" + id)
    }
}

export default new EventServices();