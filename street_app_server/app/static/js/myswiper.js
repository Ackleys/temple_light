/*var mySwiper = new Swiper ('.swiper-container', {
    direction: 'vertical',
    loop: true,
    autoplay:true,
    // 如果需要分页器
    pagination: {
      el: '.swiper-pagination',
    },
})*/
$(function(){
    var url = window.location.href;
    var url1 = url.split('?')[0];
    var url2 = url.split('?')[1];
    var imei = url2.split('&')[0].split('=')[1];
    var content = $('.swiper-wrapper');
    $.ajax({
        url:$SCRIPT_ROOT+'/api/ad/fetch',
        type:"POST", 
        contentType: "application/json; charset=utf-8",
        data:JSON.stringify({imei:imei}),
        dataType:'json',
        success:function(data){
            if(data.data.length===0){
                return false;
            }
            var slide = '';
            data.data.map(function(q,i){
                slide += "<div class='swiper-slide'><a href='"+q.url+"'><img src='"+q.img+"' /></a></div>"
            })
            content.html(slide);
            var mySwiper = new Swiper ('.swiper-container', {
                autoplay:true,
                // 如果需要分页器
                pagination: {
                  el: '.swiper-pagination',
                },
            })
        },
        error:function(data){

        }
    })
})        