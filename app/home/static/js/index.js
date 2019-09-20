// to top right away
if ( window.location.hash ) scroll(0,0);
// void some browsers issue
setTimeout( function() { scroll(0,0); }, 1);

//https://github.com/blueimp/Gallery
function initBlueimp(onopened){
    blueimp.Gallery(document.getElementById('links').getElementsByTagName('a'), {
        container: '#blueimp-gallery-carousel',
        carousel: true,
        onopened: onopened
    })
}

function hashScroll() {
    if(window.location.hash) {
        $('html, body').animate({
          scrollTop: $(window.location.hash).offset().top - $("#navbar").innerHeight()
        }, 1000);
    }
}

$(document).ready(function(){
    initBlueimp(hashScroll);
    
    $('.scrollTo').click(function(e) {
        e.preventDefault();
        var sectionTo = $(this).attr('href');
        $('html, body').animate({
          scrollTop: $(sectionTo).offset().top - ($("#navbar").innerHeight() - $("#navbarMenu").innerHeight())
        }, 1000);
    });
    
})
