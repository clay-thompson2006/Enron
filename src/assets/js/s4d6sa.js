
function success(){
    Swal.fire({
        icon: 'success',
        title: 'Your account has been Verified!',
    }).then((result) => {
        /* Read more about isConfirmed, isDenied below */
        if (result.isConfirmed) {
          Swal.fire('', 'Click on verify button in server again!', 'success')
        }
    })
}