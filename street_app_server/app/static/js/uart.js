$(function(){
	
	var url = window.location.href.split('&')[0];
	localStorage.setItem('url',url);
	var url1 = url.split('?')[0];
	var url2 = url.split('?')[1];
	var agent_id = parseInt(url1.split('/')[url1.split('/').length-2]);
	var machine_id = type(url1.split('/')[url1.split('/').length-3]);
	var imei = url2.split('&')[0].split('=')[1];
	var total,p_id,news,etime,stime,paytype,balance,price,wallet_pay_enable,int;
	var t_f = true;
	if(window.location.href.indexOf('method=alipay.trade.wap.pay.return')!==-1){
    	if(localStorage.getItem('member') === 'member'){
    		localStorage.removeItem('member');
    	}else{
    		start();
    	}
	}
	function IsWeixinOrAlipay(){
	    var ua = window.navigator.userAgent.toLowerCase();
	    //判断是不是微信
	    if ( ua.match(/MicroMessenger/i) == 'micromessenger' ) {  
	          paytype = 'wechat'
	    }else if (ua.match(/AlipayClient/i) == 'alipayclient') {
	          paytype = 'alipay'
	    }else{
	    	paytype = 'alipay'
	    }
	}
	IsWeixinOrAlipay();

	var timeCounter = function(total) {
	  	if(total <= 0) {
	  		$('.chair_model').on('click',function(e){
				price = $(this).attr('num');
				p_id = $(this).attr('p_id');
				$('#chair_money').html('本次支付：￥'+price/100);
				$(this).children('img').css('display','block');
				$(this).siblings().children('img').css('display','none');
			})
			$('#chair_pay').on('click',function(){
				if(!p_id){
					$.alert('请选择套餐');
				}else{
					if(t_f){
						pay();
					}
				}
			})
	  		$('#chair_money').html('本次支付：') ;
	  		$('#chair_pay').css('display','block');
	  		$('.chair_model').children('img').css('display','none');
	  		$('#stop').hide();
	  		localStorage.removeItem('pay_id');
	  		t_f = true;       
	  		clearTimeout(int);
	  	}else{
	  		layer.closeAll();
		  	$('#chair_pay').css('display','none');
		  	$('#stop').css('display','block');
		  	var s = (total%60) < 10 ? ('0' + total%60) : total%60;
		  	var h = total/3600 < 10 ? ('0' + parseInt(total/3600)) : parseInt(total/3600);
		  	var m = (total-h*3600)/60 < 10 ? ('0' + parseInt((total-h*3600)/60)) : parseInt((total-h*3600)/60);
		  	s = s > 0 ? s+'秒' : '';
		  	m = m > 0 ? m+'分' : '';
		  	h = h > 0 ? h+'时' : '';
		  	$('#chair_money').html('剩余时间：' + h + m + s ) ;
		  	
		  	int = setTimeout(timeCounter.bind(this,total-1), 1000);
	  	};
	}

	function type (type) {
		var id = 0;
		switch (type) {
			case 'uart': id = 2; break;
			case 'doll': id = 1; break;
			case 'chair': id = 0; break;
		}
		return id;
	};
	function record(id){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/machine/record',
			type:"POST",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({imei:imei}),
			dataType:'json',
			success:function(d){
				if(id === d.data.user_id){
					if(d.data.etime-d.data.now>=0){
						$('.chair_model').children('img').css('display','none');
						data();
						timeCounter(d.data.etime-d.data.now);
					}else if(d.data.etime-d.data.now<0){
						$('.chair_model').children('img').css('display','none');
						data();
						//timeCounter(d.data.etime-d.data.now);
					}
				}else{
					data();
				}
			},
			error:function(da){
		    	console.log(da.responseJSON.msg); 
		    	data();
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
				if(d.data.alipay_available){
						money();
						record(d.data.user_id);
					}else if(!d.data.alipay_available){
						if(paytype === 'wechat'){
							money();
							record(d.data.user_id);
						}else{
							$('body').html('<h1 style="margin-top:40vh;text-align:center;color: #fff;">设备只能使用微信扫码支付</h1>');
						}
					}
				
			}else{
				$('body').html('<h1 style="margin-top:40vh;text-align:center;color: #fff;">设备暂时不可用，请使用其他机器</h1>');
			}
		},
		error:function(data){
	    	$('body').html('<h1 style="margin-top:40vh;text-align:center;color: #fff;">设备暂时不可用，请使用其他机器</h1>');
	    }
	})
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
	$('#state').click(function(){
		if(wallet_pay_enable){
			window.location.href = $SCRIPT_ROOT+'/member?imei='+imei;
		}
	})
	function money(){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/wallet/fetch',
			type:"POST",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({imei:imei}),
			dataType:'json',
			success:function(data){
				wallet_pay_enable = data.data.wallet_pay_enable;
				if(!data.data.wallet_pay_enable){
				}else{
					$('#state').html('会员充值');
					balance = data.data.balance;
					$('#balance').html('账户余额：'+balance/100+'元');
				}
			},
			error:function(data){
		    	console.log(data.responseJSON.msg);
		    }
		})
	}
	function data() {//获取套餐
		$.ajax({
			url:$SCRIPT_ROOT+'/api/products',
			type:"POST",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({imei:imei}),
			dataType:'json',
			success:function(data){
				money();
				if(data.data.length>0){
					products(data.data);
				}
			},
			error:function(data){
		    	console.log(data.responseJSON.msg);
		    }
		})
	} 
	function start() {//启动接口
		layer.open({
				    type: 2,
				    shadeClose:false,
				    content: '请稍等，正在启动'
				});
		$.ajax({ 
			url:$SCRIPT_ROOT+'/api/machine/start',
			type:"PUT",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({pay_id:localStorage.getItem('pay_id')-0,cat:machine_id}),
			dataType:'json',
			success:function(da){
				localStorage.setItem('record_id',da.data.id);
	            $('#chair_pay').css('display','none');
				$('.chair_model').off('click');
				$('#chair_pay').off('click');
				timeCounter(da.data.etime-da.data.stime);
			},
			error:function(da){
				layer.closeAll();
				if(da.responseJSON.code === 3001){//已经启动
		           /* $('#chair_pay').css('display','none');
					$('.chair_model').off('click');
					$('#chair_pay').off('click');*/
					$.alert('机器已被使用，稍后退款');
				}else{
					//$('#chair_pay').off('click');					
					money();
					t_f = true;
					$.alert(da.responseJSON.msg);
				}
		    }
		})
	}
	function stop(){

		$.ajax({
			url:$SCRIPT_ROOT+'/api/machine/stop',
			type:"PATCH",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({imei:imei}),
			dataType:'json',
			success:function(d){
				clearTimeout(int);
				$('.chair_model').on('click',function(e){
					price = $(this).attr('num');
					p_id = $(this).attr('p_id');
					$('#chair_money').html('本次支付：￥'+price/100);
					$(this).children('img').css('display','block');
					$(this).siblings().children('img').css('display','none');
				})
				$('#chair_pay').on('click',function(){
					if(!p_id){
						$.alert('请选择套餐');
					}else{
						if(t_f){
							pay();
						}
					}
				})
		  		$('#chair_money').html('本次支付：') ;
		  		$('#chair_pay').css('display','block');
		  		$('.chair_model').children('img').css('display','none');
		  		$('#stop').hide();
		  		localStorage.removeItem('pay_id');
		  		t_f = true;  
			},
			error:function(da){
		    	console.log(da.responseJSON.msg); 
		    }
		})


		     
  		
	}
	$('#stop').click(function(){
		$.modal({
				  title: "提醒",
				  text: "确定要停止机器吗？强制停止后不会退款",
				  buttons: [
				    { text: "确定", onClick: function(){stop()}},
				    { text: "取消", className: "default", onClick: function(){} },
				  ]
				});
	})
	

	function products (da) {
		var product = '';
		da.map(function(re,i){
			if(i === 0){
				p_id = re.id;
				price = re.price;
				$('#chair_money').html('本次支付：￥'+re.price/100);
			}
			return product+="<div class = 'chair_model' num = '"+re.price+"' p_id = '"+re.id+"'>"
								+"<img class = 'choose' src="+$SCRIPT_ROOT+"/static/img/choose.png" +"/>"
								+"<span>"
									+"<p>"+re.price/100+"元</p>"
								+"</span>"
								+"<span><p><span id='chair_model_title'>"+re.title+"</span></p></span>"
							+"</div>";
		})
		$('.b_border').html(product);
		$('.chair_model').on('click',function(e){
			price = $(this).attr('num');
			p_id = $(this).attr('p_id');
			$('#chair_money').html('本次支付：￥'+price/100);
			$(this).children('img').css('display','block');
			$(this).siblings().children('img').css('display','none');
			
		})
		$('#chair_pay').on('click',function(){
			if(!p_id){
				$.alert('请选择套餐');
			}else{
				if(t_f){

					pay();
				}
			}
		})
			
	};
	function alipay(){
		var test;
		$.ajax({
			url:$SCRIPT_ROOT+'/api/pay',
			type:"PUT",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({product_id:p_id-0,trade_type:'JSAPI',imei:imei,pay_mode:2,url:url}),
			dataType:'json',
			success:function(data){
				localStorage.setItem('pay_id',data.data.id);
				for (var i in data.data.pay_request){
                	test+="<input type='hidden' name='"+i+"' value='"+data.data.pay_request[i]+"' />";	
                }
                document.getElementById('myform').innerHTML = test;
                document.getElementById('myform').submit();
			},
			error:function(data){
		    	$.alert('设备运行或缺料状态，请稍后再付');
		    }
		})
	}
	function wallet(){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/pay',
			type:"PUT",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({product_id:p_id-0,
								trade_type:'JSAPI',
								imei:imei,
								pay_mode:3}),
			dataType:'json',
			success:function(da){
				money();
				localStorage.setItem('pay_id',da.data.id);
				$('.chair_model').children('img').css('display','none');
				
				start();
			},
			error:function(da){
		    	if(da.responseJSON.code === 2006){
					if(paytype === 'wechat'){
						$.modal({
						  title: "余额不足",
						  text: "请选择充值或者直接支付",
						  buttons: [
						    { text: "钱包充值", onClick: function(){window.location.href = $SCRIPT_ROOT+'/member?imei='+imei} },
						    { text: "微信支付", onClick: function(){ localStorage.setItem('data',JSON.stringify({product_id:p_id-0,trade_type:'JSAPI',imei:imei,cat:machine_id}));
						window.location.href = $SCRIPT_ROOT+'/pay';} },
						    { text: "取消", className: "default", onClick: function(){} },
						  ]
						});
						
					}else if(paytype === 'alipay'){
						$.modal({
						  title: "余额不足",
						  text: "请选择充值或者直接支付",
						  buttons: [
						    { text: "钱包充值", onClick: function(){window.location.href = $SCRIPT_ROOT+'/member?imei='+imei} },
						    { text: "支付宝支付", onClick: function(){ alipay()} },
						    { text: "取消", className: "default"},
						  ]
						});
						
					}
				}else{
		    		$.alert('设备运行或缺料状态，请稍后再付');
				}
		    }
		})
	}
	function pay() {
		if(wallet_pay_enable){	
			$.modal({
				title: "",
				text: "本次消费"+price/100+"元，优先从账户余额扣除",
				buttons: [
				    { text: "确定", onClick: function(){wallet()} },
				    { text: "取消", className: "default", onClick: function(){} },
				]
			});
		}else{
			if(paytype === 'wechat'){
		    	localStorage.setItem('data',JSON.stringify({
		    		product_id:p_id-0,
		    		trade_type:'JSAPI',
		    		imei:imei,
		    		cat:machine_id
		    	}));
				window.location.href = $SCRIPT_ROOT+'/pay/';			
			}else if(paytype === 'alipay'){
				alipay();
			}
		}
	}
})