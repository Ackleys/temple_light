$(document).ready(function(){
	/*if(window.location.href.indexOf('method=alipay.trade.wap.pay.return')!==-1){
		if(localStorage.getItem('member') === 'member'){
    		localStorage.removeItem('member');
    	}else{
    		localStorage.setItem('ok','ok');
    	}
		window.location.href = localStorage.getItem('url');
		return false;
	}
	function IsWeixinOrAlipay(){
	    var ua = window.navigator.userAgent.toLowerCase();
	    //判断是不是微信
	    if ( ua.match(/MicroMessenger/i) == 'micromessenger' ) {  
	          alipay();
	    }else if (ua.match(/AlipayClient/i) == 'alipayclient') {
	          wechat();
	    }else{
	    	alipay();
	    }
	}*/
	var datas = JSON.parse(localStorage.getItem('data'));
	var data = {    product_id:datas.product_id-0,
				    trade_type:'JSAPI',
				    pay_mode:1,
				    imei:datas.imei
			};
	var cat = datas.cat-0;
	var n = 0,pay_id,int,status;
	var timeCounter = function() {
	 	console.log(n);
	  	if(n>120) { 
	  		n = 0;		
	  		clearTimeout(int);
	  	}else{	
	  		n++;
	  		query();
		  	int = setTimeout(timeCounter, 1000);	  		
	  	};				
	}
	function query(){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/pay/query',
			type:"POST",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({pay_id:pay_id}),
			dataType:'json',
			success:function(data){
				if(status === 1){

				}else{
					if(data.data.status === 1){
						status = 1;
						clearTimeout(int);
						start();
					}	
				}
			},
			error:function(data){
		    	$.alert(data.responseJSON.msg,function(){
		    		window.location.href = localStorage.getItem('url')+'&m='+Math.random();
		    	});
		    }
		})
	};
	function start () {
		$.ajax({ 
				url:$SCRIPT_ROOT+'/api/machine/start',
				type:"PUT",
				contentType: "application/json; charset=utf-8",
				data:JSON.stringify({pay_id:pay_id,cat:cat}),
				dataType:'json',
				success:function(da){
					/*if(cat === 0){
						var now = parseInt(new Date().getTime()/1000);
						now = now-da.data.now;
						localStorage.setItem('etime',da.data.etime+now);
					}*/
					window.location.href = localStorage.getItem('url')+'&m='+Math.random();
				},
				error:function(da){
					if(da.responseJSON.code === 3001){

					}else{
						$.alert(da.responseJSON.msg+',稍后退款',function(){
				    		window.location.href = localStorage.getItem('url')+'&m='+Math.random();
				    	});
				    }
			    }
			})
	}
	var callback = function (res){
	    if ( typeof res === 'string' ) {
	        try{
	            res = JSON.parse(res);
	        }catch(e){
	            res = {"err_msg": "get_brand_wcpay_request:fail"};
	        }
	    } else if ( typeof res === 'object' ){

	    }
	    var content = JSON.stringify(res);
	    if ( res.err_msg.replace("：", ":").replace(" ", "") == "get_brand_wcpay_request:ok" ) {
	    	if(localStorage.getItem('member') === 'member'){
	    		localStorage.removeItem('member');
	    		window.location.href = localStorage.getItem('url')+'&m='+Math.random();
	    	}else{
	    		/*localStorage.setItem('ok','ok');
	    		if(int){
	    			clearTimeout(int);
	    		}*/
	    	}
			//window.location.href = localStorage.getItem('url');
	    }else{
	    	if(int){
	    		clearTimeout(int);
	    	}
	    	window.location.href = localStorage.getItem('url')+'&m='+Math.random();
	    }
	} 
	$.ajax({
		url:$SCRIPT_ROOT+'/api/pay',
		type:"PUT",
		contentType: "application/json; charset=utf-8",
		data:JSON.stringify(data),
		dataType:'json',
		success:function(data){
			pay_id = data.data.id;
			localStorage.setItem('pay_id',data.data.id);
			localStorage.removeItem('data');
			if(localStorage.getItem('member')){

			}else{
				timeCounter();
			}
			function onBridgeReady (){
				WeixinJSBridge.invoke( 'getBrandWCPayRequest', data.data.pay_request, callback);
			}
			if (typeof WeixinJSBridge == "undefined"){
			   if( document.addEventListener ){
			        document.addEventListener('WeixinJSBridgeReady', onBridgeReady, false);
			    }else if (document.attachEvent){
			        document.attachEvent('WeixinJSBridgeReady', onBridgeReady); 
			        document.attachEvent('onWeixinJSBridgeReady', onBridgeReady);
			   }
			}else{
			    onBridgeReady();
			}
		},
		error:function(data){
			localStorage.removeItem('data');
			if(data.status === 500){
		    	$.alert('设备运行或缺料状态，请稍后再付',function(){
		    		window.location.href = localStorage.getItem('url')+'&m='+Math.random();
		    	});
			}else{
				$.alert(data.responseJSON.msg,function(){
		    		window.location.href = localStorage.getItem('url')+'&m='+Math.random();
		    	});
			}
	    }
	})
	
})