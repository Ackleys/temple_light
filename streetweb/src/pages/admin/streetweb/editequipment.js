"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';
import { browserHistory} from 'react-router';
import {
    Button,
    Menu,
    Table,
    Input,
    Alert,
    Select,
    Checkbox,
    message,
    Modal,
    Radio,
    Tabs,
} from 'antd';
import {MyLayout}     from '../common/layout.js';
const Option = Select.Option;
const CheckboxGroup = Checkbox.Group;
const RadioGroup = Radio.Group;
const TabPane = Tabs.TabPane;
const EditEquipment = require('create-react-class')({

	getInitialState: function() {
	    return {
	    	add_option:[],
	    	option:[],
	    	start_imei:'',
	    	num:'1',
	    	address:'',
	    	type:'',
	    	product:[],
	    	values:[],
	    	errormsg:null,//套餐提醒
	    	error:null,//提交时提醒
	    	show:true,//高级设置显示
	    	pulse_width:50,
	    	pulse_period:50,
	    	visible:false,
	    	key:0,
	    	defaultcat:'',
	    	defaultadd:'',
	    	remark:'',
	    	disabled:false,
	    	reid:null,
	    	nopay:0,
	    	product_min_money:0,
	    	product_unit:'',
	    	//product_unit_price:0,
	    	product_unit_pluse:0,
	    	num_disabled:false
	    };
	},
	componentWillMount:function(){
		this.type();
		let num;
		console.log(sessionStorage.getItem('re'));
		if(sessionStorage.getItem('re')){
			let re = JSON.parse(sessionStorage.getItem('re'));
			this.address(re.address);
			if(re.cats === '倒计时'){
		        this.product(0,re.id);
		        let time_ = ['断电恢复后，不运行','','断电恢复后，继续运行','断电后继续计时，恢复后根据剩余时间决定是否继续运行'][re.cat];
		        this.setState({type:0,time_type:time_});
		    }else if(re.cats === '投币器') {
		        this.product(1,re.id);
		        this.setState({type:1});
		    }else if(re.cats === '串口') {
					this.product(2,re.id);
					this.setState({type:2});
				}else if(re.cats === '烛灯1.0') {
					this.product(3,re.id);
					this.setState({type:3});
				}
			if(re.nopay>=1){
				num = 1;
			}else{
				num = 0;
				this.setState({num_disabled:true});
			}
			this.setState({defaultcat:re.cats,
							start_imei:re.imei,
							defaultadd:re.address,
							remark:re.remark,
							disabled:true,
							reid:re.id,
							nopay:re.nopay,
							first_nopay:num,
							pulse_width:re.pulse_width,
							pulse_period:re.pulse_period,
							product_min_money:re.product_min_money,
							product_unit:re.product_unit,
							product_unit_pluse:re.product_unit_pluse,
							coupon:re.coupon,
							//product_unit_price:re.product_unit_price/100
						});
		}
	},
	componentWillUnmount() {
       sessionStorage.removeItem('re');
    },
	show_tc:function(id){
  		let url = window.API_PREFIX+'/device/product/fetch';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body);
                let arr = [];
                res.body.data.forEach((q)=>{
                	arr.push(q.id);
                })
                self.setState({values:arr}) ;          
            }
        };
        let data = {
            device_id:id-0
        }
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify(data));
        xhr.onreadystatechange = function() {
            if(xhr.readyState === XMLHttpRequest.DONE) {
                if(xhr.status === 200) {
                    callback(null,{body:JSON.parse(xhr.responseText)});
                } else {
                    callback({err:JSON.parse(xhr.responseText)},null);
                }
            }
        };
  	},
	address:function(add){
		let url = window.API_PREFIX+'/device/address/fetch';
		var self = this;
        var callback = function(err,res){
	        if(err){

	        }else{
	            //console.log(res.body);	         
	            self.setState({add_option:res.body.data});
	            if(add){
	            	res.body.data.forEach((q)=>{
	            		if(q.address === add){
	            			self.setState({address:q.id});
	            		}
	            	})
	            }
	        }
        };
        var xhr  = new XMLHttpRequest();
        xhr.open("GET", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(null);
        xhr.onreadystatechange = function() {
            if(xhr.readyState === XMLHttpRequest.DONE) {
                if(xhr.status === 200) {
                    callback(null,{body:JSON.parse(xhr.responseText)});
                } else {
                    callback(JSON.parse(xhr.responseText),null);
                }
            }
        };
	},
	type:function(){
    
        var self = this;
        var url  = window.API_PREFIX+"/device/cat";
        var callback = function(err,res){
        if(err){

        }else{
          let arr = [];
          for(let i in res.body.data){
            let data={
              num:i,
              value:res.body.data[i]
            };
            arr.push(data);
          }
          self.setState({option:arr});
        }
      };
      var xhr  = new XMLHttpRequest();
      xhr.open("GET", url);
      xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
      xhr.send(null);
      xhr.onreadystatechange = function() {
          if(xhr.readyState === XMLHttpRequest.DONE) {
              if(xhr.status === 200) {
                callback(null,{body:JSON.parse(xhr.responseText)});
              } else {
                callback(JSON.parse(xhr.responseText),null);
              }
          }
      };
    },
    select:function(id,value,a){
    	let self = this;
    	console.log(id);
    	console.log(value)

    	if(id === 'add'){
    		this.setState({address:value});
    	}else if(id === 'type'){
    		this.setState({type:value,values:[],defaultcat:a.props.children});
    		this.product(value)
    	}else if(id === 'time_type'){
    		this.setState({type:value})
    	}
    },
    product:function(type,id){
		let url = window.API_PREFIX+'/device/product/fetch';
		var self = this;
        var callback = function(err,res){
	        if(err){

	        }else{
	            console.log(res.body);
	            let arr = []
	            res.body.data.map(q=>{
	            	let data={
	            		label:q.title,
	            		value:q.id
	            	};
	            	arr.push(data);
	            })	         
	            self.setState({product:arr},()=>{

		            if(id){
		            	self.show_tc(id);
		            }
	            });
	        }
        };
        let data={
        	cat:type-0
        }
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify(data));
        xhr.onreadystatechange = function() {
            if(xhr.readyState === XMLHttpRequest.DONE) {
                if(xhr.status === 200) {
                    callback(null,{body:JSON.parse(xhr.responseText)});
                } else {
                    callback(JSON.parse(xhr.responseText),null);
                }
            }
        };
	},
	checkonChange:function(values){
		let type = this.state.type-0;
		console.log(values);
		this.setState({errormsg:null});
		if(values.length<=6){
			this.setState({values:values});
		}else{
			this.setState({errormsg:'该设备类型最多选择6种套餐'});
		}
	},
	show_setting:function(){
		this.setState({show:true})
	},
	inputchange:function(t,e){
		if(t === 'imei'){
			this.setState({start_imei:e.target.value});
		}else if(t === 'num'){
			this.setState({num:e.target.value});
		}else if(t === 'pulse_period'){
			this.setState({pulse_period:e.target.value-0});
		}else if(t === 'pulse_width'){
			this.setState({pulse_width:e.target.value-0});
		}else if(t === 'add'){
			this.setState({add:e.target.value});
		}else if(t === 'remark'){
			this.setState({remark:e.target.value});
		}else if(t === 'product_unit'){
			this.setState({product_unit:e.target.value});
		}else if(t === 'product_unit_pluse'){
			this.setState({product_unit_pluse:e.target.value-0});
		}else if(t === 'nopay_num'){
			this.setState({nopay:e.target.value});
		}
	},
	edit:function(){
		let url = window.API_PREFIX+'/device/update';
		var self = this;
		self.setState({errormsg:null});
        var callback = function(err,res){
	        if(err){
	        	self.setState({errormsg:err.msg});
	        }else{
	            message.success('编辑成功！');
	            /*sessionStorage.setItem('key',2);
			    sessionStorage.setItem('subkey','2_2');*/
			    //sessionStorage.removeItem('re');
			    //browserHistory.push(window.URL_PREFIX+'/equipmentstate');
	        }
        };
        if(self.state.type===''||!self.state.address||self.state.start_imei.length!==15){
        	self.setState({errormsg:'请填选择投放地点后提交'});
        	return false;
        }
        if(!(/^[\u4e00-\u9fa5]+$/.test(self.state.product_unit))){
        	self.setState({errormsg:'请填写正确的单位,例如：桶，个'});
        	return false;
        }
        let update = {};
        if(self.state.defaultcat === '投币器'){
        	update = {
	        	cat:self.state.type-0,
	        	address_id:self.state.address-0,
	        	product_list:self.state.values,
	        	remark:self.state.remark,
	        	nopay:self.state.nopay-0,
	        	//product_unit_price:self.state.product_unit_price*100,
	        	product_min_money:self.state.product_min_money,
	        	product_unit_pluse:self.state.product_unit_pluse ,
	        	product_unit:self.state.product_unit,
	        	coupon:self.state.coupon
	        }
        }else if (self.state.defaultcat === '倒计时'){
        	update = {
	        	cat:self.state.type-0,
	        	address_id:self.state.address-0,
	        	product_list:self.state.values,
	        	remark:self.state.remark,
	        	nopay:self.state.nopay-0,
	        	coupon:self.state.coupon
	        }
        }else if(self.state.defaultcat === '串口') {
					update = {
	        	cat:self.state.type-0,
	        	address_id:self.state.address-0,
	        	product_list:self.state.values,
	        	remark:self.state.remark,
	        	nopay:self.state.nopay-0,
	        	coupon:self.state.coupon
	        }
				}else if(self.state.defaultcat === '烛灯1.0') {
					update = {
	        	cat:self.state.type-0,
	        	address_id:self.state.address-0,
	        	product_list:self.state.values,
	        	remark:self.state.remark,
	        	nopay:self.state.nopay-0,
	        	coupon:self.state.coupon
	        }
				}
        console.log(update);
        if(self.state.pulse_width>255){
        	self.setState({errormsg:'脉冲周期和间隔不可大于255'});
        	return false;
        }else if(self.state.pulse_period>255){
        	self.setState({errormsg:'脉冲周期和间隔不可大于255'});
        	return false;
        }
        let advanced = {
        	pulse_width:self.state.pulse_width,
	    	pulse_period:self.state.pulse_period,
        }
        let data={
        	imeis:[self.state.start_imei],
        	//num:self.state.num-0,
        	update:update,
        	advanced:advanced
        }
        var xhr  = new XMLHttpRequest();
        xhr.open("PATCH", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify(data));
        xhr.onreadystatechange = function() {
            if(xhr.readyState === XMLHttpRequest.DONE) {
                if(xhr.status === 200) {
                    callback(null,{body:JSON.parse(xhr.responseText)});
                } else {
                    callback(JSON.parse(xhr.responseText),null);
                }
            }
        };
	},
	abandon:function(){
		/*sessionStorage.setItem('key',2);
	    sessionStorage.setItem('subkey','2_2');*/
	    
	    browserHistory.goBack();
	},
	handleOk:function(){
	    let url = window.API_PREFIX+'/device/address/add';
		var self = this;
		self.setState({error:null});
        if(!self.state.add){
        	self.setState({error:'请填写完毕后提交'});
        	return false;
        }
        var callback = function(err,res){
	        if(err){
	        	self.setState({error:err.msg});
	        }else{
	        	self.address();
	        	self.setState({visible:false,error:null,key:Math.random()});
	            message.success('地址添加成功！');
	        }
        };
        let data={
        	address:self.state.add,
        	region:'',
        }
        var xhr  = new XMLHttpRequest();
        xhr.open("PUT", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify(data));
        xhr.onreadystatechange = function() {
            if(xhr.readyState === XMLHttpRequest.DONE) {
                if(xhr.status === 200) {
                    callback(null,{body:JSON.parse(xhr.responseText)});
                } else {
                    callback(JSON.parse(xhr.responseText),null);
                }
            }
        };
	},
	handleCancel:function(){
	    this.setState({visible:false,key:Math.random()});
	},
	add_address:function(){
	    this.setState({visible:true,key:Math.random()});
	},
	jump:function(){
		let self = this;
		if(self.state.defaultcat === '倒计时'){
			browserHistory.push(window.URL_PREFIX+'/chair');
			sessionStorage.setItem('key',3);
			sessionStorage.setItem('subkey','3_0');
		}else if(self.state.defaultcat === '投币器'){
			browserHistory.push(window.URL_PREFIX+'/doll');
			sessionStorage.setItem('key',3);
			sessionStorage.setItem('subkey','3_1');
		}else if(self.state.defaultcat === '串口'){
			browserHistory.push(window.URL_PREFIX+'/uart');
			sessionStorage.setItem('key',3);
			sessionStorage.setItem('subkey','3_2');
		}
	},
	radioChange:function(e){
		console.log('radio checked', e.target.value);
		let num;
		if(e.target.value==1){
			this.setState({coupon: 0,num_disabled:false});
		}else{
			this.setState({num_disabled:true,nopay:0});
		}
	    this.setState({
	      first_nopay:e.target.value,
	    });
	},
	radioChange1:function(e){
		console.log('radio checked', e.target.value);
		if(e.target.value==1){
			this.setState({first_nopay: 0,num_disabled:true,nopay:0});
		}
	    this.setState({
	      coupon: e.target.value,
	    });
	},
	moneyChange:function(e){
		console.log('radio checked', e.target.value);
    this.setState({
      product_min_money: e.target.value,
    });
	},
	render:function(){
		let self = this;
		let alert = null;
		let err_alert = null;
		let check = null;
		let setting = null;
		let doll = null;
		let nopay_input = null;
		let time_type = null;
		if(self.state.defaultcat === '投币器'){
			doll = (
				<div>
					<p style={{fontSize:16,margin:'20px 0'}}>设备产品的单位，例如：桶，次，分钟</p>
					<Input defaultValue={self.state.product_unit} placeholder='请输入单位' style={{width:'60%',marginRight:'6%',height:40}} onChange={self.inputchange.bind(self,'product_unit')}/>
					<p style={{fontSize:16,margin:'20px 0'}}>设备产品的单位对应脉冲数：</p>
					<Input defaultValue={self.state.product_unit_pluse} placeholder='请输入脉冲个数' style={{width:'60%',marginRight:'6%',height:40}} onChange={self.inputchange.bind(self,'product_unit_pluse')}/>
					<p style={{fontSize:16,margin:'20px 0'}}>是否支持五角投币：</p>
					<RadioGroup onChange={this.moneyChange} value={this.state.product_min_money}>
				        <Radio value={50}>是</Radio>
				        <Radio value={100}>否</Radio> 
				    </RadioGroup>
			    </div>
				)
		}else if(self.state.defaultcat === '倒计时'){
			time_type = <div>
							<p style={{fontSize:16,margin:'20px 0'}}>倒计时类型：</p>
							<Select style={{width:'60%',display:'block'}} defaultValue={self.state.time_type} placeholder='请选择倒计时类型' onSelect={self.select.bind(self,'time_type')}>
								<Option value={'0'} >断电恢复后，不运行</Option>
	                            <Option value={'2'} >断电恢复后，继续运行</Option>
	                            <Option value={'3'} >断电后继续计时，恢复后根据剩余时间决定是否继续运行</Option>
							</Select>
						</div>
								
							
		}
		if(self.state.show){
			setting = (
					<div>
						<p style={{fontSize:16,margin:'20px 0'}}>脉冲周期：</p>
						<Input defaultValue={self.state.pulse_period} placeholder='默认50毫秒' style={{width:'60%',marginTop:10,height:40}} onChange={self.inputchange.bind(self,'pulse_period')}/><br />
						<p style={{fontSize:16,margin:'20px 0'}}>脉冲间隔：</p>
						<Input defaultValue={self.state.pulse_width} placeholder="默认50毫秒" style={{width:'60%',marginTop:10,height:40}} onChange={self.inputchange.bind(self,'pulse_width')}/>
					</div>
				)
		}
		if(self.state.product.length>0){
			check = <CheckboxGroup className='checkbox' options={self.state.product} value={self.state.values} onChange={self.checkonChange} />
		}else if(self.state.type!==''){
			check = <Button type='primary' onClick={self.jump}>请添加套餐</Button>
		}else{
			check = <Alert style={{width:'60%'}} message='选择设备类型后出现套餐' type="info" />
		}
		if(self.state.errormsg){
	        alert = <Alert style={{width:'60%'}} message={self.state.errormsg} type="error" />
	    }
	    if(self.state.error){
	        err_alert = <Alert style={{width:'60%'}} message={self.state.error} type="error" />
	    }
		const option = self.state.option.map((q,i)=>{return (<Option key={i} value={q.num}>{q.value}</Option>)})
		const add_option = self.state.add_option.map((q,i)=>{return <Option key={i} value={q.id+''}>{q.region+q.address}</Option>})
		return(
			<MyLayout>
			<div style={{margin:'10vh auto',width:'60%'}}>
				<p style={{fontSize:16,margin:'20px 0'}}>编辑设备：</p>
				<Tabs defaultActiveKey="基础设置" tabPosition={'left'}>
					<TabPane tab="基础设置" key="基础设置">
						<p style={{fontSize:16,margin:'20px 0'}}>设备imei：</p>
                        <Input disabled={self.state.disabled} defaultValue={self.state.start_imei} placeholder='请输入IMEI' style={{width:'60%',marginRight:'6%',height:40}} onChange={self.inputchange.bind(self,'imei')}/>
						{/*<Input placeholder='设备数量' style={{width:'24%',height:40}} onChange={self.inputchange.bind(self,'num')}/>*/}
						<p style={{fontSize:16,margin:'20px 0'}}>设备投放地址：</p>
						<Select defaultValue={self.state.defaultadd} placeholder='请选择地址' notFoundContent='暂无地址，请点击添加按钮添加地址' style={{width:'60%',display:'block',margin:'20px 0'}} onSelect={self.select.bind(self,'add')}>
							{add_option}
						</Select>
						<Button type='primary' style={{marginBottom:20}} onClick={self.add_address}>添加地址</Button>
						<p style={{fontSize:16,margin:'20px 0'}}>设备类型：</p>
						<Select defaultValue={self.state.defaultcat} style={{width:'60%',display:'block'}} placeholder='请选择设备类型' onSelect={self.select.bind(self,'type')}>
							{option}
						</Select>
						
						{time_type}
                    </TabPane>
                    <TabPane tab="推广设置" key="推广设置">
                        {doll}
						<div>
							<p style={{fontSize:16,margin:'20px 0'}}>是否设置为关注公众号免费体验：</p>
							<RadioGroup onChange={this.radioChange} value={this.state.first_nopay}>
						        <Radio value={1}>是</Radio>
						        <Radio value={0}>否</Radio> 
						    </RadioGroup>
						    <p style={{fontSize:16,margin:'20px 0'}}>是支持电子传单：</p>
							<RadioGroup onChange={this.radioChange1} value={this.state.coupon}>
						        <Radio value={1}>是</Radio>
						        <Radio value={0}>否</Radio> 
						    </RadioGroup>
						    <div>
								<p style={{fontSize:16,margin:'20px 0'}}>关注公众号免费体验次数：</p>
						 		<Input defaultValue={self.state.nopay} disabled={self.state.num_disabled} value={self.state.first_nopay?self.state.nopay:self.state.first_nopay} placeholder='请输入免费体验的人数' style={{width:'60%',marginRight:'6%',height:40}} onChange={self.inputchange.bind(self,'nopay_num')}/>
							</div>
					    </div>
                    </TabPane>
                    <TabPane tab="套餐及备注" key="套餐及备注">
                        <p style={{fontSize:16,margin:'20px 0'}}>备注：</p>
												<Input defaultValue={self.state.remark} placeholder='请输入备注' style={{width:'60%',marginRight:'6%',height:40}} onChange={self.inputchange.bind(self,'remark')}/>
												<p style={{fontSize:16,margin:'20px 0'}}>为所选设备配备套餐：</p>
												{check}
                    </TabPane>
                    <TabPane tab="高级设置" key="高级设置">
                        {setting}
                    </TabPane>
				</Tabs>
				
				
				
				{alert}
				<Button style={{width:200,height:40,marginTop:20,marginRight:20}} onClick={self.abandon}>返回</Button>
				<Button type='primary' style={{width:200,height:40,marginTop:20,marginRight:20}} onClick={self.edit}>提交</Button>
				{/*<div className='setting'>
					<Button style={{border:'0'}} onClick={self.show_setting}>高级设置</Button>
				</div>*/}
				
			</div>
			<Modal 
	          width="300px"
	          title="添加地址" 
	          visible={this.state.visible}
	          onOk={this.handleOk}
	          onCancel={this.handleCancel}
	          key={self.state.key}
	        >
	          <Input placeholder='请输入地址' onChange={self.inputchange.bind(self,'add')} />
	          {err_alert}
	        </Modal>
			</MyLayout>
		)
	}
})
      export default EditEquipment;
export { EditEquipment };