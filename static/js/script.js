function open_right_sidenav() {
  document.getElementById("my_right_sidenav").style.width = "350px";
}

function close_right_sidenav() {
  document.getElementById("my_right_sidenav").style.width = "0";
}

$(".sidebar-dropdown > a").click(function() {
  $(".sidebar-submenu").slideUp(200);
  if (
    $(this)
      .parent()
      .hasClass("active")
  ) {
    $(".sidebar-dropdown").removeClass("active");
    $(this)
      .parent()
      .removeClass("active");
  } else {
    $(".sidebar-dropdown").removeClass("active");
    $(this)
      .next(".sidebar-submenu")
      .slideDown(200);
    $(this)
      .parent()
      .addClass("active");
  }
});

$("#close-sidebar").click(function() {
  $(".page-wrapper").removeClass("toggled");
});
$("#show-sidebar").click(function() {
  $(".page-wrapper").addClass("toggled");
});



$(document).ready(function(){
//     $.ajax({
//     url: 'add_product',
//     type: "GET",
//     dataType: "html",
//     //data: {'option_id':option_id},
//     success: function(data){
//       $('#modal_body').html(data)
//      /* HERE I WANT TO ITERATE THROUGH THE data LIST OF OBJECTS */
//     },
//     error: function(xhr){
//     alert('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText);
//     $('#my_account_data').html(xhr.responseText)
//     }
//
//   });
//
//    $('#sidebarCollapse').on('click', function () {
//        $('#sidebar').toggleClass('active');
//    });
$('.product-detail').click(function(event) {
event.preventDefault();
var product =  $(this).attr('data-modal');
$.ajax({
     url: '/product_detail/',
     type: "POST",
     dataType: "html",
     contentType: 'json',
     data: product,
     success: function(data){
       $('#product_details_modal_body').html(data)
      /* HERE I WANT TO ITERATE THROUGH THE data LIST OF OBJECTS */
     },
     error: function(xhr){
     alert('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText);
     }

   });
  });
});