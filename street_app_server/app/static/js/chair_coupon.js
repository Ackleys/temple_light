$(function(){
	var url = window.location.href;
	localStorage.setItem('url',url);
	var url1 = url.split('?')[0];
	var url2 = url.split('?')[1];
	var agent_id = parseInt(url1.split('/')[url1.split('/').length-2]);
	var machine_id = type(url1.split('/')[url1.split('/').length-3]);
	var imei = url2.split('&')[0].split('=')[1];
	var total,etime,stime,date1,date2,s=60,num_nopay=1,timer = null;
	var t_f = true;
	function type (type) {
		var id = 0;
		switch (type) {
			case 'doll_nopay': id = 1; break;
			case 'chair_nopay': id = 0; break;
		}
		return id;
	};
	var ua = window.navigator.userAgent.toLowerCase();
	if ( ua.match(/MicroMessenger/i) == 'micromessenger' ) {  
          
    }else{
    	$('body').html('<h1 style="margin-top:40vh;text-align:center;color: #fff;">设备仅支持微信扫码</h1>');
    	return false;
    }
	$.ajax({
		url:$SCRIPT_ROOT+'/api/title/fetch',
		type:"POST", 
		contentType: "application/json; charset=utf-8",
		data:JSON.stringify({imei:imei}),
		dataType:'json',
		success:function(d){
			$('title').html(d.data.title);
			$('#title').html(d.data.title);
		},
		error:function(data){

	    }
	})
	function get_coupon(){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/coupon_receipt/random',
			type:"POST", 
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({imei:imei}),
			dataType:'json',
			success:function(d){
				var src = d.data.img;
				var code = d.data.code;
				var data={"image":[src]},imgPath;
				var len=data.image.length;
				var mycanvas=document.createElement('canvas');
				mycanvas.width=600;
				mycanvas.height=1200;
				if(mycanvas.getContext){
					var context=mycanvas.getContext('2d');
					context.fillStyle='#fff';
					context.fillRect(0,0,mycanvas.width,mycanvas.height);
					var r=d.data.color[0];
					var g=d.data.color[1];
					var b=d.data.color[2];
					function drawing(num){
						if(num<len){
							var img=new Image;
							img.src=data.image[num];
							img.onerror=function(){
								drawing(num+1);
							}
							img.onload=function(){
								context.drawImage(img,0,0,mycanvas.width,mycanvas.height);
								drawing(num+1);
							}
						}else{
							
							context.font='26px Adobe Ming Std';
							context.fillStyle='rgba('+r+','+g+','+b+','+'1'+')';
							context.fillText(code,425,1185); 
							imgPath=mycanvas.toDataURL("image/jpeg");
							document.getElementById('coupon_img').src=imgPath;
							$('.coupon').css('display','block');
							$('#coupon_body').css('display','block');
							/*$('#coupon_btn').html('保存图片60秒后可使用');
							timer = setInterval(function(){
								s--;
								$('#coupon_btn').html('保存图片'+s+'秒后可使用');
								if(s === 0){
									clearInterval(timer);
									$('#coupon_btn').html('保存图片后可使用');
								}
							},1000);*/
						}
					}
					drawing(0);
				}
			},
			error:function(data){
				$.alert(data.responseJSON.msg);
		    }
		})
	}
	if(localStorage.getItem('etime')-parseInt(new Date().getTime()/1000)>0){
		$('#state').html('正在使用');
		$.ajax({
			url:$SCRIPT_ROOT+'/api/machine/record_coupon_nopay',
			type:"POST",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({record_id:localStorage.getItem('record_id')-0}),
			dataType:'json',
			success:function(d){
				$('#coupon_body').css('display','block');
				products(1);
			},
			error:function(data){
		    	console.log(data.msg);
		    }
		})
	}else{
		$.ajax({
			url:$SCRIPT_ROOT+'/api/device_status',
			type:"POST",
			async:false, 
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({imei:imei}),
			dataType:'json',
			success:function(d){
				if(d.data.status === 1){
					get_coupon();
				}else{
					$('body').html('<h1 style="margin-top:40vh;text-align:center;color: #fff;">设备暂时不可用，请使用其他机器</h1>');
				}
			},
			error:function(data){
		    	console.log(data.msg);
		    }
		})	
	}
	function start (d) {
		$.ajax({
			url:$SCRIPT_ROOT+'/api/machine/start_coupon_nopay',
			type:"PUT",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({cat:machine_id,value:30,imei:imei}),
			dataType:'json',
			success:function(da){
				num_nopay--;
    			etime = da.data.etime;
				stime = da.data.stime;
				localStorage.setItem('record_id',da.data.id);
	            $('#chair_pay').css('display','none');
				timeCounter(0,etime-stime);
			},
			error:function(da){
				layer.closeAll();
				t_f = true;
				$.alert(da.responseJSON.msg);
		    }
		})
	}
	var timeCounter = function(n,se) {
	 	var int ;
	 	stime = parseInt(new Date().getTime()/1000);
	 	if(!n){
	 		//stime = parseInt(new Date().getTime()/1000); 
	 		//etime = stime+se;
	 		localStorage.setItem('etime',etime);
	 	}else{

	 		etime = localStorage.getItem('etime')-0;
	 	}
	 	total = etime-stime;

	  	if(isNaN(etime)||total <= 0) {
	  		$('#state').html('请使用');
	  		$('#chair_money').html('') ;
	  		localStorage.removeItem('etime');
	  		localStorage.removeItem('record_id')
	  		clearTimeout(int);
	  	}else{
	  		layer.closeAll();
		  	$('#chair_pay').css('display','none');
		  	var s = (total%60) < 10 ? ('0' + total%60) : total%60;
		  	var h = total/3600 < 10 ? ('0' + parseInt(total/3600)) : parseInt(total/3600);
		  	var m = (total-h*3600)/60 < 10 ? ('0' + parseInt((total-h*3600)/60)) : parseInt((total-h*3600)/60);
		  	s = s > 0 ? s+'秒' : '';
		  	m = m > 0 ? m+'分' : '';
		  	h = h > 0 ? h+'时' : '';
		  	$('#chair_money').html('剩余时间：' + h + m + s ) ;
		  	int = setTimeout(timeCounter.bind(this,1), 1000);	  		
	  	};	
	}
	function products (con) {
		if(con === 1){
			timeCounter(1,null);
		}
	};
	$('#coupon_btn').click(function(){
		if(s > 0){
			$.alert('您还未保存图片');
			return false;
		}
		$('.coupon').css('display','none');
	})
	$('#chair_pay').click(function(){
		if(num_nopay<=0){
			$.alert('免费次数已用尽');
			return false;
		}
		layer.open({
		    type: 2,
		    shadeClose:false,
		    content: '请稍等，正在启动'
		});
		start();
	})
	$("#coupon_img").on({
		touchstart: function(e){
			date1 = new Date().getTime();
		},
		touchmove: function(e){
		},
		touchcancel:function(){
			date2 = new Date().getTime();
			if(date2-date1>300){
				s=0;
			}
		},
		touchend: function(){
			date2 = new Date().getTime();
			if(date2-date1>500){
				s=0;
			}
		}
	})
})