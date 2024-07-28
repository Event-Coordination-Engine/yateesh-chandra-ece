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

      loginSuccessSwal(tag) {
        Swal.fire({
          position: 'center',
          allowOutsideClick: false,
          html: `<div class="animation">${tag}<span class="dot1">.</span><span class="dot2">.</span><span class="dot3">.!</span></div>`,
          showConfirmButton: false,
          background: "rgb(240, 240, 240)",
          timer: 1800,
          width: 500,
          timerProgressBar: true,
          backdrop: `linear-gradient(90deg, rgba(156,255,251,1) 0%, rgba(238,255,167,1) 35%, rgba(150,255,158,1) 100%)`,
          customClass: {
            timerProgressBar: "custom-swal-timer",
          },
        });
      };
}

export default new SweetAlert();