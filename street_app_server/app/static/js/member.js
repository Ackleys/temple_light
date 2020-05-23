$(function(){

	var url = window.location.href;
	//localStorage.setItem('url',url);
	var url1 = url.split('?')[0];
	var url2 = url.split('?')[1];
	var agent_id = parseInt(url1.split('/')[url1.split('/').length-2]);
	var machine_id = type(url1.split('/')[url1.split('/').length-3]);
	var imei = url2.split('&')[0].split('=')[1];
	var balance,paytype,pid;
	var num = 0;
	var ua = window.navigator.userAgent.toLowerCase();
	start();
	if ( ua.match(/MicroMessenger/i) == 'micromessenger' ) {  
          paytype = 'wechat'
    }else if (ua.match(/AlipayClient/i) == 'alipayclient') {
          paytype = 'alipay'
    }else{
    	paytype = 'alipay'
    }
	function type (type) {
		var id = 0;
		switch (type) {
			case 'doll': id = 1; break;
			case 'chair': id = 0; break;
		}
		return id;
	};
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
	function start(){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/wallet_products',
			type:"POST",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({imei:imei}),
			dataType:'json',
			success:function(data){
				$('.chair_model').off('click');
				$('#chair_pay').off('click');
				products(data.data);
			},
			error:function(data){
		    	console.log(data.responseJSON.msg);
		    }
		})
		money();
	}
	function money (){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/wallet/fetch',
			type:"POST",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({imei:imei}),
			dataType:'json',
			success:function(data){
				balance = data.data.balance;
				$('#balance').html(balance/100+'元');
			},
			error:function(data){
		    	console.log(data.responseJSON.msg);
		    }
		})
	}
	
	function products (da) {
		var product = '';
		da.map(function(re,i){
			if(i === 0){
				pid = re.id;
				$('#chair_money').html('本次支付：￥'+re.price/100);
			}
			return product+="<div class = 'chair_model' p_id = '"+re.id+"'>"
								+"<img class = 'choose' src="+$SCRIPT_ROOT+"/static/img/choose.png" +"/>"
								+"<span>"
									+"<p><label class='price'>"+re.price/100+"</label>元</p>"
									+"<p>"+re.value/100+"元</p>"
								+"</span>"
								+"<span><p>"+re.title+"</p></span>"
							+"</div>";
		})
		$('.flex_box').html(product);
		$('.chair_model').on('click',function(e){
			var price = $(this).find('.price').html()-0;
			pid = $(this).attr('p_id');
			//price = $(this).attr('num');
			$('#chair_money').html('本次支付：￥'+price);
			$(this).children('img').css('display','block');
			$(this).siblings().children('img').css('display','none');
			
		})
		$('#chair_pay').on('click',function(){
			if(!pid){
				$.alert('请选择套餐');
			}else{
				pay();
			}
		})
		
	};
	function pay() {
		//t_f = false;
		if(paytype === 'wechat'){
			localStorage.setItem('data',JSON.stringify({product_id:pid,agent_id:agent_id,trade_type:'JSAPI',imei:imei}));
			localStorage.setItem('member','member');
			window.location.href = $SCRIPT_ROOT+'/pay';
		}else{
			var test;
			$.ajax({
				url:$SCRIPT_ROOT+'/api/pay',
				type:"PUT",
				contentType: "application/json; charset=utf-8",
				data:JSON.stringify({product_id:pid-0,trade_type:'JSAPI',pay_mode:2,imei:imei,url:localStorage.getItem('url')}),
				dataType:'json',
				success:function(data){
					localStorage.setItem('member','member');
					localStorage.setItem('pay_id',data.data.id);
					for (var i in data.data.pay_request){
	                	test+="<input type='hidden' name='"+i+"' value='"+data.data.pay_request[i]+"' />";	
	                }
	                document.getElementById('myform').innerHTML = test;
	                document.getElementById('myform').submit();
				},
				error:function(data){
			    	$.alert('不要太着急，请休息一下');
			    }
			})
		}	
	}
})

