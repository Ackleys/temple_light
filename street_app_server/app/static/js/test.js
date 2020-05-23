$('#pulse').click(function(){
	var self = this;
	$('#pulse_tips').html('');
	var imei = $('.pulse_imei').val();
	var high = $('.pulse_high').val()-0;
	var low = $('.pulse_low').val()-0;
	var pulse = $('.pulse_pulse').val()-0;
	var key1 = $('.key1').val();

	if(imei.length!==15 || high<50 || low<50 || pulse<=0){
		$.alert('请输入正确的参数');
		return false;
	}
	$(self).attr("disabled",true); 
	$(self).html('传输中，请稍等...');
	$.ajax({
	    url:$SCRIPT_ROOT+'/event/launch_pulse_signal_deivce',
		type:"POST",
		contentType: "application/json; charset=utf-8",
		data:JSON.stringify({
			imei:imei,
			high:high,
			low:low,
			pulse:pulse,
			key:key1
		}),
		dataType:'json',
		success:function(data){
			$(self).removeAttr("disabled");
			$(self).html('确定');
			$('#pulse_tips').html('调用成功');
		},
		error:function(data){
			$(self).removeAttr("disabled");
			$(self).html('确定');
	    	$('#pulse_tips').html(JSON.parse(data.responseText).msg);
	    }
	})
})


$('#relay').click(function(){
	var self = this;
	var key2 = $('.key2').val();
	$('#relay_tips').html('');
	var imei = $('.relay_imei').val();
	var duration = $('.relay_s').val()-0;
	if(imei.length!==15 || duration<0){
		$.alert('请输入正确的参数');
		return false;
	}
	$(self).attr("disabled",true);
	$(self).html('传输中，请稍等...');
	$.ajax({
	    url:$SCRIPT_ROOT+'/event/launch_relay_signal_deivce',
		type:"POST",
		contentType: "application/json; charset=utf-8",
		data:JSON.stringify({
			imei:imei,
			duration:duration,
			key:key2
		}),
		dataType:'json',
		success:function(data){
			$(self).removeAttr("disabled");
			$(self).html('确定');
			$('#relay_tips').html('调用成功');
		},
		error:function(data){
			$(self).removeAttr("disabled");
			$(self).html('确定');
	    	$('#relay_tips').html(JSON.parse(data.responseText).msg);
	    }
	})
})