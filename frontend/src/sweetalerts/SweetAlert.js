import Swal from 'sweetalert2'

class SweetAlert{
    registrationFailureFireAlert(failureText) {
        Swal.fire({
          title : "Unable to Register",
          text : failureText,
          icon : "error"
        })
      }

      registrationSuccessFireAlert(){
        Swal.fire({
          title : "Successfully Registered",
          text : "Hurray, Now you are our subscriber.!",
        //   imageUrl : img,
          imageHeight : 150,
          imageWidth : 150,
        })
      }
}

export default new SweetAlert();