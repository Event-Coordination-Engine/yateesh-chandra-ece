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
          color: "#297c02",
          html: `<div class="animation">${tag}<span class="dot1">.</span><span class="dot2">.</span><span class="dot3">.!</span></div>`,
          showConfirmButton: false,
          background: "#fafafa",
          timer: 2000,
          width: 500,
          timerProgressBar: true,
          backdrop: `#b5faff`,
          customClass: {
            timerProgressBar: "custom-swal-timer",
          },
        });
      };

      signOutAlert(method, tag){
        Swal.fire({
          title : 'Sign Out ?',
          text : 'Are you sure you want to Sign out?',
          icon : 'warning',
          showConfirmButton : true,
          confirmButtonText : "Yes, Signout",
          showDenyButton : true,
          denyButtonText : 'Nope, Hold on',
          timerProgressBar: true,
          customClass: {
            timerProgressBar: "custom-swal-timer",
          },
      }).then((result) => {
          if(result.isConfirmed){
            method()  
            this.loginSuccessSwal(tag);
          } 
      })
      }
}

export default new SweetAlert();