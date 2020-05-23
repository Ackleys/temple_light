$(function(){
	var url = window.location.href;
	localStorage.setItem('url',url);
	var url1 = url.split('?')[0];
	var url2 = url.split('?')[1];
	var agent_id = parseInt(url1.split('/')[url1.split('/').length-2]);
	var machine_id = type(url1.split('/')[url1.split('/').length-3]);
	var imei = url2.split('&')[0].split('=')[1];
	var total,p_id,news,etime,stime,paytype,num_nopay;
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
	function wechat_info(){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/wechat_info/fetch',
			type:"POST",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({imei:imei}),
			dataType:'json',
			success:function(d){
				if(d.data.subscribe === 1){
					$('#chair_pay').css('display','block');
					$('.ewm_box').css('display','none');
					$('.chair_model').css('display','block');
					count();
				}else if(d.data.subscribe === 0){
					$('.qrcode').attr('src',d.data.qrcode);
					$('#chair_pay').css('display','none');
					$('.ewm_box').css('display','block');
					$('.chair_model').css('display','none');
				}
			},
			error:function(data){
		    	console.log(data.msg);
		    }
		})
	}
	function count(){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/nopay/count',
			type:"POST",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({imei:imei}),
			dataType:'json',
			success:function(d){
				num_nopay = d.data.nopay-d.data.count>0?d.data.nopay-d.data.count:0;
				$('#chair_pay').html('剩余'+num_nopay+'次');
			},
			error:function(data){
		    	console.log(data.msg);
		    }
		})
	};
	
	$.ajax({
		url:$SCRIPT_ROOT+'/api/device_status',
		type:"POST",
		async:false, 
		contentType: "application/json; charset=utf-8",
		data:JSON.stringify({imei:imei}),
		dataType:'json',
		success:function(d){
			if(d.data.status === 1){
				$.ajax({
					url:$SCRIPT_ROOT+'/api/nopay/count',
					type:"POST",
					contentType: "application/json; charset=utf-8",
					data:JSON.stringify({imei:imei}),
					dataType:'json',
					success:function(d){
						num_nopay = d.data.nopay-d.data.count>0?d.data.nopay-d.data.count:0;
						if(num_nopay === 0){
							var _url = url.replace(/_nopay/g,'');
							window.location.href = _url;
						}
						$('#chair_pay').html('剩余'+num_nopay+'次');
					},
					error:function(data){
				    	console.log(data.msg);
				    }
				})
				wechat_info();
			}else{
				$('body').html('<h1 style="margin-top:40vh;text-align:center;color: #fff;">设备暂时不可用，请使用其他机器</h1>');
			}
		},
		error:function(data){
	    	console.log(data.msg);
	    }
	})	
	
	function start (d) {
		$.ajax({
			url:$SCRIPT_ROOT+'/api/machine/start_nopay',
			type:"PUT",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({cat:machine_id,value:1,imei:imei}),
			dataType:'json',
			success:function(da){
				layer.closeAll();
				count();
				// localStorage.setItem('record_id',da.data.id);
	            $('#chair_pay').css('display','block');
			},
			error:function(da){
				layer.closeAll();
				t_f = true;
				$.alert(data.responseJSON.msg);
		    }
		})
	}
	
	function products (con) {
		
		if(con === 1){
			timeCounter(1,null);
		}else if(con === 0){
			
		}	
	};
	$('#chair_pay').click(function(){
		if(num_nopay<=0){
			$.alert('免费次数已用尽',function(){
				var _url = url.replace(/_nopay/g,'');
				window.location.href = _url;
			});
			return false;
		}
		layer.open({
		    type: 2,
		    shadeClose:false,
		    content: '请稍等，正在启动'
		});
		start();
	})
})