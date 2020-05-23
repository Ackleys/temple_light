$(function(){
	//localStorage.clear();
	if(window.location.href.indexOf('method=alipay.trade.wap.pay.return')!==-1){
    	if(localStorage.getItem('member') === 'member'){
    		localStorage.removeItem('member');
    	}else{
    		localStorage.setItem('ok','ok');
    	}
	}
	var url = window.location.href.split('&')[0];
	localStorage.setItem('url',url);
	var url1 = url.split('?')[0];
	var url2 = url.split('?')[1];
	var agent_id = parseInt(url1.split('/')[url1.split('/').length-2]);
	var machine_id = type(url1.split('/')[url1.split('/').length-3]);
	var imei = url2.split('&')[0].split('=')[1];
	var icon_num,balance,paytype,p_id,price,wallet_pay_enable;
	var num = 0;
	//$('.machine').html(imei.substr(10,5)+'号机器');
	var ua = window.navigator.userAgent.toLowerCase();
	if ( ua.match(/MicroMessenger/i) == 'micromessenger' ) {  
          paytype = 'wechat'
    }else if (ua.match(/AlipayClient/i) == 'alipayclient') {
          paytype = 'alipay'
    }else{
    	paytype = 'alipay'
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
	if(localStorage.getItem('ok') === 'ok'){
		layer.open({
		    type: 2,
		    shadeClose:false,
		    content: '请稍等，正在启动'
		});
		datas();
		start();
		localStorage.removeItem('ok')
		
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
					if(d.data.alipay_available){
						datas();
					}else if(!d.data.alipay_available){
						if(paytype === 'wechat'){
							datas();
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
	}
	//datas();
	//判断是不是微信
	
	function type (type) {
		var id = 0;
		switch (type) {
			case 'doll': id = 1; break;
			case 'chair': id = 0; break;
		}
		return id;
	};
	function datas(){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/products',
			type:"POST",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({imei:imei}),
			dataType:'json',
			success:function(data){
				products(data.data);
			},
			error:function(data){
		    	console.log(data.responseJSON.msg);
		    }
		})

		money();
	}
	function start(){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/machine/start',
			type:"PUT",
			contentType: "application/json; charset=utf-8",
			data:JSON.stringify({cat:machine_id,pay_id:localStorage.getItem('pay_id')-0}),
			dataType:'json',
			success:function(da){
    			layer.closeAll();    			
			},
			error:function(da){
				layer.closeAll();
				if(da.responseJSON.code === 3001){

				}else{
					$.alert(da.responseJSON.msg);
				}
		    }
		})
	}
	function money (){
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
	$('#state').click(function(){
		if(wallet_pay_enable){
			window.location.href = $SCRIPT_ROOT+'/member?imei='+imei;
		}
	})
	/*function icon(){
		$.ajax({
			url:$SCRIPT_ROOT+'/api/game_coin/fetch',
			type:"GET",
			contentType: "application/json; charset=utf-8",
			data:null,
			dataType:'json',
			success:function(data){
				icon_num = data.data.coin;
				//$('#icon_num').html(icon_num);
				
			},
			error:function(data){
		    	console.log(data.responseJSON.msg);
		    }
		})
	}*/
	function alipay(){
		$.ajax({
				url:$SCRIPT_ROOT+'/api/pay',
				type:"PUT",
				contentType: "application/json; charset=utf-8",
				data:JSON.stringify({product_id:p_id-0,
									trade_type:'JSAPI',
									imei:imei,
									pay_mode:2,
									url:url
								}),
				dataType:'json',
				success:function(data){
					localStorage.setItem('pay_id',data.data.id);
					var test = ''
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
	function wallet(){
		layer.open({
				    type: 2,
				    shadeClose:false,
				    content: '请稍等，正在支付'
				});
		$.ajax({
				url:$SCRIPT_ROOT+'/api/pay',
				type:"PUT",
				contentType: "application/json; charset=utf-8",
				data:JSON.stringify({product_id:p_id-0,
									trade_type:'JSAPI',
									imei:imei,
									pay_mode:3}),
				dataType:'json',
				success:function(data){
					localStorage.setItem('pay_id',data.data.id);
					//layer.closeAll();
					money();
					start();
				},
				error:function(d){
					layer.closeAll();
					if(d.responseJSON.code === 2006){
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
			    		$.alert('不要太着急，请休息一下');
					}
			    }
			})
	}
	function products (da) {
		var product = '';
		da.map(function(re,i){
			if(i === 0){
				p_id = re.id;
				price = re.price/100;
				$('#chair_money').html('本次支付：￥'+re.price/100);
			}
			return product+="<div class = 'chair_model' p_id = '"+re.id+"'>"
								+"<img class = 'choose' src="+$SCRIPT_ROOT+"/static/img/choose.png" +"/>"
								+"<span>"
									+"<p><label class='price'>"+re.price/100+"</label>元</p>"
									+"<p>"+re.number+re.unit+"</p>"
								+"</span>"
								+"<span><p><span id='chair_model_title'>"+re.title+"</span></p></span>"
							+"</div>";
		})
		$('.flex_box').html(product);
		
		$('.chair_model').on('click',function(e){
			price = $(this).find('.price').html()-0;
			p_id = $(this).attr('p_id');
			$(this).children('img').css('display','block');
			$(this).siblings().children('img').css('display','none');
			$('#chair_money').html('本次支付：￥'+price);
			
			//localStorage.setItem('data',JSON.stringify({product_id:num-0,trade_type:'JSAPI',imei:imei}));
			//window.location.href = $SCRIPT_ROOT+'/pay';
		})
		/*$('#add').click(function(){
			if(num>=icon_num){
				return false;
			}else{
				num++;
			}
			$('#icon').html(num);
			$('#icon_num').html(icon_num-num);
		})
		$('#remove').click(function(){
			
			if(num<=0){
				return false;
			}else{
				num--;

			}
			$('#icon').html(num);
			$('#icon_num').html(icon_num-num);
		})*/
		$('#chair_pay').on('click',function(){
			/*if(num <= 0){
				$.alert('请添加次数');
			}else if(num>icon_num){
				$.alert('套餐次数不足，请充值');
			}else{
				layer.open({
				    type: 2,
				    shadeClose:false,
				    content: '请稍等，正在启动'
				});
				$.ajax({
					url:$SCRIPT_ROOT+'/api/machine/start',
					type:"PUT",
					contentType: "application/json; charset=utf-8",
					data:JSON.stringify({cat:machine_id,value:num-0,imei:imei}),
					dataType:'json',
					success:function(da){
		    			layer.closeAll();
		    			start();
		    			
					},
					error:function(da){
						//$('#spinner').css('display','none');
						layer.closeAll();
						datas();
						num = 0;
						$('#icon').html(num);
						t_f = true;
						$.alert(da.responseJSON.msg);
				    }
				})
			}*/
			if(wallet_pay_enable){	
				$.modal({
					title: "",
					text: "本次消费"+price+"元，优先从账户余额扣除",
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
					window.location.href = $SCRIPT_ROOT+'/pay';			
				}else if(paytype === 'alipay'){
					alipay();
				}
			}
		})
	};
})

