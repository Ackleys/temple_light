"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';
import QRCode       from 'qrcode.react';
import { Form, Icon } from '@ant-design/compatible';
import {  Button, Menu,  Table, Input,Alert,Modal,message,Tabs,Select,Checkbox,Radio } from 'antd';
import {MyLayout}     from '../common/layout.js';
import { browserHistory} from 'react-router';
const Search = Input.Search;
const TabPane = Tabs.TabPane;
const Option = Select.Option;
const CheckboxGroup = Checkbox.Group;
const RadioGroup = Radio.Group;
const FormItem = Form.Item;
function accAdd(arg1,arg2){
    var r1,r2,m;
    try{r1=arg1.toString().split(".")[1].length}catch(e){r1=0}
    try{r2=arg2.toString().split(".")[1].length}catch(e){r2=0}
    m=Math.pow(10,Math.max(r1,r2))
    return (arg1*m+arg2*m)/m
}
String.prototype.times = function(n) { return (new Array(n+1)).join(this);}; 
var Edit = require('create-react-class')({
	getInitialState: function() {
		return {
			add_option:[],
	    	option:[],
	    	address:'',
	    	type:'',
	    	product:[],
	    	values:[],
	    	errormsg:null,//套餐提醒
	    	error:null,//提交时提醒	
	    	disabled:false,
	    	key:0,
	    	visible:false,
	    	nopay_input:false,
		};
	},
	componentWillMount:function(){
		this.type();
		this.address();
	},
	/*componentWillReceiveProps:function(nextprops){
		console.log(nextprops);
		//this.setState({imei:nextprops.imei});
	},*/
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
			this.setState({nopay_input:true});
			this.props.form.setFieldsValue({coupon: 0});
		}else{
			this.setState({nopay_input:false,nopay:0});
		}
	    this.setState({
	      first_nopay:e.target.value,
	    });
	},
	radioChange1:function(e){
		console.log('radio checked', e.target.value);
		if(e.target.value==1){
			this.setState({nopay_input:false});
			this.props.form.setFieldsValue({first_nopay: 0});
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
	checkonChange:function(values){
		let type = this.state.type-0;
		console.log(values);
		this.setState({errormsg:null});
		if(type === 0){
			if(values.length<=6){
				this.setState({values:values});
			}else{
				this.setState({errormsg:'该设备类型最多选择6种套餐'});
			}
		}else if(type === 1){
			if(values.length<=6){
				this.setState({values:values});
			}else{
				this.setState({errormsg:'该设备类型最多选择6种套餐'});
			}
		}
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
	select:function(id,value,a){
    	let self = this;
    	console.log(id);
    	console.log(value)

    	if(id === 'add'){
    		this.setState({address:value});
    	}else if(id === 'type'){
    		this.setState({type:value,values:[],defaultcat:a.props.children});
    		this.product(value)
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
	            self.setState({product:arr});
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
	abandon:function(){
		this.props.show(false);
	},
	editSubmit:function(e){
		let url = window.API_PREFIX+'/device/update';
		let self = this;
		e.preventDefault();
		self.setState({errormsg:null});
		this.props.form.validateFieldsAndScroll((err, values) => {
			if (!err) {
				console.log('Received values of form: ', values);
				if(values.first_nopay===0){
					values.nopay = 0;
				}
		        var callback = function(err,res){
			        if(err){
			        	self.setState({errormsg:err.msg});
			        }else{
			            message.success('编辑成功！');
			            self.props.show(false);
			        }
		        };
		        if(values.cat===undefined||values.address_id===undefined||self.props.imei.length<1){
		        	self.setState({errormsg:'请勾选设备且填写完成基础设置'});
		        	return false;
		        }
		        if(values.product_unit){
			        if(!(/^[\u4e00-\u9fa5]+$/.test(values.product_unit))){
			        	self.setState({errormsg:'请填写正确的单位,例如：桶，个'});
			        	return false;
			        }
		        }
		        for(let i in values){
		        	if(values[i]===undefined||i === 'first_nopay'){
		        			delete values[i];
		        	}
		        	if(i === 'address'){
		        		values.address = values.address-0;
		        	}
		        }
		        if(self.state.values.length>0){
		        	values.product_list = self.state.values;
		        }
		        if(self.state.defaultcat === '倒计时'){
		        	values.cat = values.time_type-0;
		        }
		        console.log(values);
		        let advanced = {
		        	pulse_width:self.state.pulse_width,
			    	pulse_period:self.state.pulse_period,
		        }
		        let data={
		        	imeis:self.props.imei,
		        	update:values,
		        	//advanced:advanced
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
			}
	    })
	},
	inputchange:function(v){
		this.setState({add:v});
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
		const { getFieldDecorator, getFieldValue ,setFieldsValue} = this.props.form;
		if(self.state.defaultcat === '投币器'){
			doll = (
				<div>
					<FormItem label='设备产品的单位，例如：桶，次，分钟'>
						{getFieldDecorator('product_unit', {
							
						})(
							<Input placeholder='请输入单位' style={{width:'60%',marginRight:'6%',height:40}}/>
						)}
					</FormItem>
					<FormItem label='设备产品的单位对应脉冲数：'>
						{getFieldDecorator('product_unit_pluse', {
							
						})(
							<Input placeholder='请输入脉冲个数' style={{width:'60%',marginRight:'6%',height:40}}/>
						)}
					</FormItem>
					<FormItem label='是否支持五角投币：'>
						{getFieldDecorator('product_min_money', {
							
						})(
							<RadioGroup onChange={this.moneyChange}>
						        <Radio value={50}>是</Radio>
						        <Radio value={100}>否</Radio> 
						    </RadioGroup>
					    )}
					</FormItem>
			    </div>
				)
		}else if(self.state.defaultcat === '倒计时'){
			time_type = <FormItem label='倒计时类型：'>
								{getFieldDecorator('time_type', {
										initialValue:'0',
										rules: [{
											required: self.state.required, message: '请填写完毕后提交',
										}]
									})(
									<Select style={{width:'60%',display:'block'}} placeholder='请选择倒计时类型' >
										<Option value={'0'} >断电恢复后，不运行</Option>
		                                <Option value={'2'} >断电恢复后，继续运行</Option>
		                                <Option value={'3'} >断电后继续计时，恢复后根据剩余时间决定是否继续运行</Option>
									</Select>
								)}
							</FormItem>
		}
		if(self.state.nopay_input){
			nopay_input = <FormItem label='关注公众号免费体验次数：'>
						    {getFieldDecorator('nopay', {
									
								})(
					 			<Input placeholder='请输入免费体验的人数' style={{width:'60%',marginRight:'6%',height:40}}/>
							)}
						</FormItem>
		}
		if(self.state.product.length>0){
			check = <FormItem label='为所选设备配备套餐：'>
						<CheckboxGroup className='checkbox' options={self.state.product} onChange={self.checkonChange} />
					</FormItem>
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
			<div>
				<Form onSubmit={this.editSubmit} style={{margin:'2vh auto',width:'60%'}}>
					<p style={{fontSize:16,margin:'20px 0'}}>批量编辑设备：在上方列表中勾选设备后进行批量编辑</p>
					<Tabs defaultActiveKey="基础设置" tabPosition={'left'}>
						<TabPane tab="基础设置" key="基础设置">
							<FormItem label='设备投放地址：'>
								{getFieldDecorator('address_id', {
									rules: [{
										required: self.state.required, message: '请填写完毕后提交',
									}]
								})(
									<Select placeholder='请选择地址' notFoundContent='暂无地址，请点击添加按钮添加地址' style={{width:'60%',display:'block',margin:'20px 0'}}>
										{add_option}
									</Select>
								)}
							</FormItem>
							<Button type='primary' style={{marginBottom:20}} onClick={self.add_address}>添加地址</Button>
							<FormItem label='设备类型：'>
								{getFieldDecorator('cat', {
										rules: [{
											required: self.state.required, message: '请填写完毕后提交',
										}]
									})(
									<Select style={{width:'60%',display:'block'}} placeholder='请选择设备类型' onSelect={self.select.bind(self,'type')}>
										{option}
									</Select>
								)}
							</FormItem>
							{time_type}
	                    </TabPane>
	                    <TabPane tab="推广设置" key="推广设置">
	                        {doll}
							<div>
								<FormItem label='是否设置为关注公众号免费体验：'>
									{getFieldDecorator('first_nopay', {
											rules: [{
												required: self.state.required, message: '请填写完毕后提交',
											}]
										})(
										<RadioGroup onChange={this.radioChange}>
									        <Radio value={1}>是</Radio>
									        <Radio value={0}>否</Radio> 
									    </RadioGroup>
								    )}
								</FormItem>
							    <FormItem label='是支持电子传单：'>
								    {getFieldDecorator('coupon', {
											
										})(
										<RadioGroup onChange={this.radioChange1}>
									        <Radio value={1}>是</Radio>
									        <Radio value={0}>否</Radio> 
									    </RadioGroup>
								    )}
								</FormItem>
							    {nopay_input}
						    </div>
	                    </TabPane>
	                    <TabPane tab="套餐及备注" key="套餐及备注">
	                        <FormItem label='备注：'>
							    {getFieldDecorator('remark', {
										
									})(
									<Input placeholder='请输入备注' style={{width:'60%',marginRight:'6%',height:40}} />
								)}
							</FormItem>
							
							{check}
	                    </TabPane>                    
					</Tabs>
					{alert}
					<FormItem>
					<Button key="back" style={{width:200,height:40,marginTop:20,marginRight:20}} onClick={self.abandon}>返回</Button>
					<Button key="submit" type='primary' style={{width:200,height:40,marginTop:20,marginRight:20}} htmlType='submit'>提交</Button>
					</FormItem>
				</Form>
				<Modal 
		          width="300px"
		          title="添加地址" 
		          visible={this.state.visible}
		          onOk={this.handleOk}
		          onCancel={this.handleCancel}
		          key={self.state.key}
		        >
		          <Input placeholder='请输入地址' onChange={self.inputchange} />
		          {err_alert}
		        </Modal>
			</div>
		)
	}
});
Edit = Form.create()(Edit);
const EquipmentState = require('create-react-class')({

	getInitialState: function() {
		return {
			type:[],
			records:[],
			"pagination": {
					"showSizeChanger":true,
					//defaultPageSize: 10,
					//defaultCurrent : 1,
					"current"        : 1,
					"pageSize"       : 10,
					"pageSizeOptions": ['10', '25', '50', '100']
			},
			selectedRowKeys:[],
			loading:true,
			show:false,
			visible:false,
			btn:'查看地图',
			url:'',
			package:'',
			title:'',
			agent_id:'',
			level:2,
			imei:[],//批量选择保存的imei
			edit_show:false,//批量编辑界面显示
			
		};
	},
	componentWillMount:function(){
		this.get_msg();
		this.type();
		
	},
	type:function(){
		var self = this;
		console.log(window.API_PREFIX);
		var url = window.API_PREFIX+"/device/cat";
		
		var callback = function(err,res){
			if(err){

			}else{
					console.log(res.body);
					let arr = [];
					for(let i in res.body.data){
						let data={
								num:i,
								value:res.body.data[i]
						};
							arr.push(data);
					}
					console.log(arr);
					self.setState({type:arr});
					if(sessionStorage.getItem('psize')){
						let pager = self.state.pagination;
						pager.current = sessionStorage.getItem('page')-0;
						pager.pageSize = sessionStorage.getItem('psize')-0;
						self.setState({pagination:pager});
						self.equ_list(sessionStorage.getItem('page'),sessionStorage.getItem('psize'));
						sessionStorage.removeItem('page');
						sessionStorage.removeItem('psize')
					}else{
						self.equ_list(1,10);
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
								callback({err:JSON.parse(xhr.responseText)},null);
						}
				}
		};
	},
	cat_change:function(t){
		let a = '';
		this.state.type.map(q=>{
				if(q.num === t+''){
					a = q.value;
				}
		})
		if(t>3){
			a = '倒计时';
		}
		return a;
	},
	equ_list:function(page,psize,map){
		var self = this;
		var url  = window.API_PREFIX+'/device/fetch?page='+page+'&psize='+psize;
		var callback = function(err,res){
			if(err){
				message.error(err.err.msg);
				self.setState({loading:false});
			}else{
				console.log(res.body);
				let num = 0;
				let arr = []
				res.body.data.devices.forEach(function(q,i){
					q.cats = self.cat_change(q.cat);
					q.key = q.imei;
					if(q.map_display){
						arr.push(num);
					}
					if(q.use_state){
						q.use_state = '使用中';
					}else if(!q.use_state){
						q.use_state = '空闲';
					}
					/*if(q.comm_state === 1){
                        q.comm_state = '在线';
	                    if(q.signal<=10){
	                        if(q.signal<=0){
	                            q.signal = '无信号 '+q.signal;
	                        }else{
	                            q.signal = '弱 '+q.signal;
	                        }
	                    }else if(q.signal<=14){
	                        q.signal = '中 '+q.signal;
	                    }else{
	                        q.signal = '强 '+q.signal;
	                    }
                    }else {
                        q.comm_state = '关机';
                        q.signal = '无信号 '+q.signal;
                    }*/
                    if(q.comm_state === 1){
                        q.comm_state = '在线';
                    }else {
                        q.comm_state = '关机';
                    }
                    if(q.signal<=10){
                        if(q.signal<=0){
                            q.signal = '无信号 '+q.signal;
                        }else{
                            q.signal = '弱 '+q.signal;
                        }
                    }else if(q.signal<=14){
                        q.signal = '中 '+q.signal;
                    }else{
                        q.signal = '强 '+q.signal;
                    }
					num++;
				})
				if(map){
					let arrs = [];
					let content = ''; 
					let opt = {
				        width : 0,     // 信息窗口宽度
				        height: 0,     // 信息窗口高度
				        title : "信息窗口" , // 信息窗口标题
				        enableMessage:true//设置允许信息窗发送短息
				    };
					res.body.data.devices.map((d,i)=>{
						let pointArr = [];
						if(d.lng==0){
							return false;
						}
				        pointArr.push(new BMap.Point(d.lng-0,d.lat-0));
				        let marker = new BMap.Marker(GpsToBaiduPoints(pointArr)[0]);
				        arrs.push(GpsToBaiduPoints(pointArr)[0]);
				        map.addOverlay(marker);
				        marker.addEventListener("click", function(e){
					        content = 	"IMEI："+d.imei+"<br />"
                      					+"信号："+d.signal+"<br />"
                      					+"状态："+d.comm_state+"<br />"
                      					+"运营商："+d.operator+"<br />";
                      		let p = e.target;
                      		let po = new BMap.Point(p.getPosition().lng, p.getPosition().lat); 
				            let infoWindow = new BMap.InfoWindow(content,opt);  // 创建信息窗口对象 
				            map.openInfoWindow(infoWindow,po); //开启信息窗口
				        })
				        if(i === res.body.data.devices.length-1){
				        	map.setViewport(arrs);
				        }					        
					})  
				}else{
					const pager = self.state.pagination;
					pager.total = res.body.data.count;
					self.setState({
						records:res.body.data.devices,
						//selectedRowKeys:arr,
						loading:false,
						pagination:pager
					});
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
						callback({err:JSON.parse(xhr.responseText)},null);
				}
			}
		};
	},
	onTableChange:function(pagination, filters, sorter) {
			//console.log('params', pagination, filters, sorter);
			const pager = this.state.pagination;
			pager.current = pagination.current;
			pager.pageSize = pagination.pageSize;
			this.setState({
					pagination: pager,
			});
			this.equ_list(pager.current,pager.pageSize);
	},
	onSelectChange:function (selectedRowKeys,selectedRows) {
		console.log('selectedRowKeys changed: ', selectedRowKeys);
		console.log('selectedRows changed: ', selectedRows);
		this.setState({ selectedRowKeys,imei: selectedRowKeys});
	},
	onSelect:function(record,select,selectedRows){
		/*if(select){
			this.update(record.imei,1);
		}else{
			this.update(record.imei,0);

		}*/
		console.log(record);
		console.log(select);
	},
	update:function(imei,map){
		let url = window.API_PREFIX+'/device/update';
		var self = this;
		
		var callback = function(err,res){
			if(err){
				self.setState({errormsg:err.msg});
			}else{
				 self.equ_list();
			}
		};
		
		let update = {
			map_display:map
		}
		
		let data={
			start_imei:imei,
			num:1,
			update:update,
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
					callback({err:JSON.parse(xhr.responseText)},null);
				}
			}
		};
	},
	show_fn:function(){
		let self = this;
		let paper = self.state.pagination;
		self.setState({show:!self.state.show},function(){
			if(self.state.show){
				self.setState({btn:'查看列表'});
				let map = new BMap.Map("maps");
				map.centerAndZoom(new BMap.Point(116.404, 39.915), 12); 
				map.addControl(new BMap.MapTypeControl());
				let top_left_control = new BMap.ScaleControl({anchor: BMAP_ANCHOR_TOP_LEFT});// 左上角，添加比例尺
				let top_left_navigation = new BMap.NavigationControl();  //左上角，添加默认缩放平移控件
				map.addControl(top_left_control);        
				map.addControl(top_left_navigation);     
				let geolocation = new BMap.Geolocation();
				if(self.state.records.length === 0){
					geolocation.getCurrentPosition(function(r){
						if(this.getStatus() == BMAP_STATUS_SUCCESS){
							map.panTo(r.point);
							console.log('您的位置：'+r.point.lng+','+r.point.lat);
						}
						else {
						}        
					},{enableHighAccuracy: true})
				}
				map.addEventListener("tilesloaded", function() {  
						map.enableScrollWheelZoom();
				}) //启用滚轮放大缩小，默认禁用
				self.setState({mp:map})
				self.equ_list(paper.current,paper.pageSize,map);
			}else{
				self.setState({btn:'查看地图'});
			}
		});	
	},
	get_msg:function(){
	    let url = window.API_PREFIX+'/agent/cur';
		var self = this;
		var callback = function(err,res){
				if(err){

				}else{
					console.log(res.body);           
					self.setState({agent_id:res.body.data.id,agent_name:res.body.data.name});
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
					callback({err:JSON.parse(xhr.responseText)},null);
				}
			}
		};
	},
	show_ewm:function(re){
		let self = this;
		console.log(re.imei);
		let url ;

		if(re.cats === '倒计时'){
			if(re.nopay){
				url = window.QRcode_url+'chair_nopay/'+re.owner_agent_id+'/?imei='+re.imei;
			}else if(re.coupon){
				url = window.QRcode_url+'chair_coupon/'+re.owner_agent_id+'/?imei='+re.imei;
			}else{
				url = window.QRcode_url+'chair/'+re.owner_agent_id+'/?imei='+re.imei;
			}
		}else if(re.cats === '投币器'){
			if(re.nopay){
				url = window.QRcode_url+'doll_nopay/'+re.owner_agent_id+'/?imei='+re.imei;
			}else if(re.coupon){
				url = window.QRcode_url+'doll_coupon/'+re.owner_agent_id+'/?imei='+re.imei;
			}else{
				url = window.QRcode_url+'doll/'+re.owner_agent_id+'/?imei='+re.imei;
			}
		}else if(re.cats === '串口'){
			url = window.QRcode_url+'uart/'+re.owner_agent_id+'/?imei='+re.imei;
			
		}
		this.setState({visible:true,url:url,title:'二维码'},function(){
			let id = re.id+'';
			let num = 5-id.length
			if(num>0){
				id = '0'.times(num)+id;
			}
			let a = document.getElementsByTagName('canvas');
			let bb = a[0].getContext('2d');
			bb.fillStyle = '#fff';    
			bb.fillRect(156,236,100,30);
			bb.fillStyle = '#000';
			bb.font = '18px Adobe Ming Std';  
			bb.fillText(id,176,253); 
		});
	 
	},
	show_tc:function(re){
		let url = window.API_PREFIX+'/device/product/fetch';
		let self = this;
		let callback = function(err,res){
				if(err){

				}else{
					console.log(res.body);           
					self.setState({package:res.body.data,visible:true,title:'套餐'});
				}
		};
		let data = {
				device_id:re.id-0
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
	handleOk:function(){
		this.setState({visible:false,url:'',package:''});
	},
	handleCancel:function(){
		this.setState({visible:false,url:'',package:''});
	},
	modal_body:function(){
		let modal_body = null;
		if(this.state.url){
			modal_body = (<div style={{textAlign:'center'}}>
							<QRCode level='L' size={256} value = {this.state.url}/>
							<p>右键保存二维码即可</p>
						</div>);
		}else if(this.state.package){
			if(this.state.package.length === 0){
				modal_body='该设备暂无套餐';
			}else{
				modal_body = this.state.package.map((q,i)=>{
					let a;
					if(q.cat === 0 ){
						a = q.price/100+'元'+q.value/60+'分钟';
					}else{
						a = q.price/100+'元'+q.value+'个脉冲 ';
					}
					return (
						
							<p key={i} style={{textAlign:'center'}}>{i+1+'、'+a}</p>

						)
				})
			}
		}
		console.log(modal_body)
		return modal_body;
	},
	edit_equ:function(re){
		if(this.state.agent_name!==re.operator){
			alert('您只能编辑自己名下的设备');
			return false;
		}
		console.log(re);
		let pager = this.state.pagination
		sessionStorage.setItem('re',JSON.stringify(re));
		sessionStorage.setItem('page',pager.current);
		sessionStorage.setItem('psize',pager.pageSize);
		browserHistory.push(window.URL_PREFIX+'/editequipment');
		return false;
	},
	alledit:function(){
		/*sessionStorage.setItem('key',2);
		sessionStorage.setItem('subkey','2_1');*/
		this.setState({edit_show:true});
	},
	search:function(t,v){
		var self = this;
        var url  = window.API_PREFIX+'/device/search';
        var callback = function(err,res){
            if(err){
                message.error(err.err.msg);
                
            }else{
                console.log(res.body);
				let num = 0;
				let arr = []
				let q = res.body.data;
				q.cats = self.cat_change(q.cat);
				q.key = 0;
				if(q.map_display){
					arr.push(num);
				}
				if(q.use_state){
					q.use_state = '使用中';
				}else if(!q.use_state){
					q.use_state = '空闲';
				}
				/*if(q.comm_state === 1){
                    q.comm_state = '在线';
                    if(q.signal<=10){
                        if(q.signal<=0){
                            q.signal = '无信号 '+q.signal;
                        }else{
                            q.signal = '弱 '+q.signal;
                        }
                    }else if(q.signal<=14){
                        q.signal = '中 '+q.signal;
                    }else{
                        q.signal = '强 '+q.signal;
                    }
                }else {
                    q.comm_state = '关机';
                    q.signal = '无信号 '+q.signal;
                }*/
                if(q.comm_state === 1){
                        q.comm_state = '在线';
                    }else {
                        q.comm_state = '关机';
                    }
                    if(q.signal<=10){
                        if(q.signal<=0){
                            q.signal = '无信号 '+q.signal;
                        }else{
                            q.signal = '弱 '+q.signal;
                        }
                    }else if(q.signal<=14){
                        q.signal = '中 '+q.signal;
                    }else{
                        q.signal = '强 '+q.signal;
                    }
				if(self.state.show){
					let maps = self.state.mp;
					let arrs = [];
					let content = ''; 
					let opt = {
				        width : 0,     // 信息窗口宽度
				        height: 0,     // 信息窗口高度
				        title : "信息窗口" , // 信息窗口标题
				        enableMessage:true//设置允许信息窗发送短息
				    };
					if(q.lng==0){
						message.error('设备暂无经纬度');
						return false;
					}
		        	let pointArr = [];
		        	pointArr.push(new BMap.Point(q.lng-0,q.lat-0));    
			        let marker = new BMap.Marker(GpsToBaiduPoints(pointArr)[0]);
			        arrs.push(GpsToBaiduPoints(pointArr)[0]);
			        maps.addOverlay(marker);
			        marker.addEventListener("click", function(e){
				        content = 	"IMEI："+q.imei+"<br />"
                  					+"信号："+q.signal+"<br />"
                  					+"状态："+q.comm_state+"<br />"
                  					+"运营商："+q.operator+"<br />";
                  		let p = e.target;
                  		let po = new BMap.Point(p.getPosition().lng, p.getPosition().lat); 
			            let infoWindow = new BMap.InfoWindow(content,opt);  // 创建信息窗口对象 
			            maps.openInfoWindow(infoWindow,po); //开启信息窗口
			        })
			    				        
		        maps.setViewport(arrs);   
				}else{
					const pager = self.state.pagination;
					pager.total = 1;
					self.setState({records:[q],selectedRowKeys:arr,loading:false,pagination:pager});
				}
               
            }

        };
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
        let data = {};
        data[t] = v;
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
	render:function(){
		let self = this;
		let content = null;
		let edit = null;
		let btn = null
		/*let modal_body = null;
		if(this.state.url){
				modal_body = (<QRCode level='H' size={256} value = {this.state.url}/>);
			}*/
		const columns = [ {
							title: '自编号',
							dataIndex: 'id',
						}, {
							title: 'IMEI(点击查看设备套餐)',
							dataIndex: 'imei',
							render:(text,re) => <a onClick={self.show_tc.bind(self,re)}>{text}</a>,
						},{
							title: '设备类型',
							dataIndex: 'cats',
						},{
							title: '生成二维码',
							dataIndex: 'qrcode',
							render:(text,re) => <Button onClick={self.show_ewm.bind(self,re)}>生成二维码</Button>,
						},{
							title: '信号强度(强度值)',
							dataIndex: 'signal',
						},{
							title: '投放地点',
							dataIndex: 'address',
						},{
							title:'通信状态',
							dataIndex:'comm_state',
						},{
							title: '运营商',
							dataIndex: 'operator',
						},{
							title: '备注',
							dataIndex: 'remark',
						}, {
							title: '编辑',
							dataIndex: 'edit',
							render:(text,re) => <a onClick={self.edit_equ.bind(self,re)}><Icon type="setting" /></a>,
						}];
		const rowSelection = {
					selectedRowKeys:self.state.selectedRowKeys,
					onChange: self.onSelectChange,
					onSelect: self.onSelect,
			 
		};
		if(self.state.level === 1){
			columns.push({
							title: '上级分成 | 我的分成',
							dataIndex: 'l1',
							render:(text,re) => <span>
					                                <span href="#" style={{color: '#666'}}>{[re.l4,re.l2,re.l3].reduce(accAdd)*100}%</span>
					                                <span className="ant-divider" />
					                                <span href="#" style={{color: '#666'}}>{re.l1*100}%</span> 
					                            </span>
						})
		}
		if(self.state.edit_show){
			edit = <Edit imei={self.state.imei} show={(s)=>{this.setState({edit_show:s},()=>{self.equ_list(1,10)})}}/>;
		}
		if(self.state.show){
			btn = null;
			content=(<div id = 'maps' style={{height:'80vh'}}></div>)
		}else{
			btn = <Button onClick = {self.alledit}>批量编辑</Button>
			content = (
				
					<Table
						loading={self.state.loading}
						rowSelection={rowSelection} 
						columns={columns} 
						dataSource={self.state.records} 
						onChange={self.onTableChange} 
						pagination={self.state.pagination}
					/>
				)
		}
		return(
			<MyLayout level={(l)=>{this.setState({level:l})}}>
				<div style = {{height:'8vh'}}>
					<div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
					<Button onClick = {self.show_fn}>{self.state.btn}</Button>
					{btn}
					<Search placeholder="请输入imei"
					    style={{ width: 200,marginLeft:20 }}
					    onSearch={self.search.bind(self,'imei')} />
					<Search placeholder="请输入设备自编号"
					    style={{ width: 200,marginLeft:20 }}
					    onSearch={self.search.bind(self,'device_id')} />
				</div>
				{content}
				{edit}
				<Modal 
					width="300px"
					title={this.state.title} 
					visible={this.state.visible}
					onOk={this.handleOk}
					onCancel={this.handleCancel}
					>
						{self.modal_body()}
				</Modal>
			</MyLayout>
		)
	}
})
export default EquipmentState;
export { EquipmentState };