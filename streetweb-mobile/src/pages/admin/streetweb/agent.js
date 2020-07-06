"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import { Form, Icon } from '@ant-design/compatible';
import {  Button, Menu, Modal,Input,Table,Radio,Select,message,Alert} from 'antd';
import {MyLayout}     from '../common/layout.js';
const FormItem = Form.Item;
const RadioGroup = Radio.Group;
const InputGroup = Input.Group;
const { Option, OptGroup } = Select;
const Search = Input.Search;
var Agent = require('create-react-class')({
	getInitialState: function() {
		return{
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
			key:0,
			required:true,
			title:'',
			errormsg:null,
			level:2,
			btn_loading:false,
			disabled:false,
			setting:false,
			adsetting:false,
			levelchange:1,
			type:'name'
		}
			 
	},
	componentWillMount:function(){
		this.get_msg();
		this.get_agent(1,10);
	},
	componentDidMount:function(){
	 
	},
	get_agent:function(page,psize){
		let self = this;
		const pager = this.state.pagination;
		let url = window.API_PREFIX+'/agent/sub_agent/fetch?page='+page+'&psize='+psize;
		var callback = function(err,res){
					if(err){
						 console.log(err);
					}else{
							console.log(res.body);
							pager.total = res.body.data.count;
							res.body.data.agents.forEach((d,i)=>{
								d.key = i;
								d.level = self.level(d.level);
								
								d.change ='';
							})
							self.setState({records:res.body.data.agents,pagination:pager,loading:false});
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
	level:function(n){
		if(n === 3){
			return '省级代理';
		}else if(n === 2){
			return '市县代理';
		}else if(n === 1){
			return '运营商';
		}
	},
	expandable:function(n){
		 if(n == 1){
			return '是';
		}else if(n == 0){
			return '否';
		}
	},
	onTableChange:function(pagination, filters, sorter) {
			const pager = this.state.pagination;
			pager.current = pagination.current;
			pager.pageSize = pagination.pageSize;
			this.setState({
					pagination: pager,
			});
			this.get_agent(pager.current,pager.pageSize);
	},
	onSelectChange:function (selectedRowKeys,selectedRows) {
		console.log('selectedRowKeys changed: ', selectedRowKeys);
		console.log('selectedRows changed: ', selectedRows);
		this.setState({ selectedRowKeys });
	},
	onSelect:function(record,select,selectedRows){
		if(select){
			//this.update(record.imei,1);
		}else{
			//this.update(record.imei,0);

		}
		console.log(record);
		console.log(select);
	},
	show_fn:function(){
		this.setState({visible:true,title:'添加',required:true,disabled:false,setting:false,adsetting:false});
	},
	handleCancel:function(){
		this.props.form.resetFields();
		this.setState({visible:false,btn_loading:false,setting:false,adsetting:false,errormsg:null});
	},
	handleSubmit:function(e){
		let self = this;
		e.preventDefault();
		const pager = this.state.pagination;
		this.props.form.validateFieldsAndScroll((err, values) => {
			if (!err) {
					console.log('Received values of form: ', values);

					let url,type,data;
					if(self.state.title==='添加'){
						url= window.API_PREFIX+"/agent/add";
						type = 'PUT';
						values.level = values.level-0;
						if(values.level == 1){
							values.expandable = 0;
						}
						data = values;
						data.salesman = 0;
						data.slevel = 0;
						data.email = data.phone+'@mafu.com';
					}else if(self.state.title==='修改'){
						url= window.API_PREFIX+"/agent/update";
						type = 'PATCH';
						for (let i in values){
							if(!values[i]&&values[i]!==0){
								delete values[i];
							}
							if(values.level){
								delete values.level;
							}
							if(values.phone){
								delete values.phone;
							}
							if(values.email){
								delete values.email;
							}
						}
						data={
							agent_id:self.state.agent_id-0,
							update:values
						}
					}
					self.setState({btn_loading:true});
					var callback = function(err,res){
						if(err){
								console.log(err);
								
								self.setState({errormsg:err.err.msg,btn_loading:false});
						}else{
								console.log(res.body);
								self.get_agent(pager.current,pager.pageSize);
								message.success('成功');
								self.props.form.resetFields();
								self.setState({errormsg:null,visible:false,btn_loading:false});
						}
					};
					var xhr  = new XMLHttpRequest();
					xhr.open(type, url);
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
				}
		})
	},
	get_msg:function(){
     let url = window.API_PREFIX+'/agent/cur';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body);           
                self.setState({level:res.body.data.level});
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
  	getData:function(){
	    var self = this;
	    var url = window.API_PREFIX+"/agent/setting/fetch";
	    const {  setFieldsValue } = this.props.form;
	    var callback = function(err,res){
	      if(err){

	      }else{
	          console.log(res.body);
	          res.body.data.min_withdraw = res.body.data.min_withdraw/100; 
	          setFieldsValue(res.body.data)
	      }
	    };
	    var xhr  = new XMLHttpRequest();
	    xhr.open("POST", url);
	    xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
	    xhr.send(JSON.stringify({target_agent_id:self.state.agent_id}));
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
  	settingSubmit:function(e){
  		let self = this;
		e.preventDefault();
		let url = window.API_PREFIX+'/agent/setting/update';
		const pager = this.state.pagination;
		this.props.form.validateFieldsAndScroll((err, values) => {
			if (!err) {
				console.log('Received values of form: ', values);
				values.min_withdraw = values.min_withdraw*100;
				values.withdraw_fee = values.withdraw_fee-0;
				if(values.min_withdraw<200){
					self.setState({errormsg:'取现最小金额不能小于2元'});
					return false;
				}
				if(values.withdraw_fee<0.006){
					self.setState({errormsg:'微信提现费用不能小于0.006'});
					return false;
				}
				self.setState({btn_loading:true});
				var callback = function(err,res){
					if(err){
						console.log(err);
						
						self.setState({errormsg:err.err.msg,btn_loading:false});
					}else{
						console.log(res.body);
						self.get_agent(pager.current,pager.pageSize);
						message.success('成功');
						self.setState({errormsg:null,visible:false,btn_loading:false,setting:false,adsetting:false});
					}
				};
				let data = {target_agent_id:self.state.agent_id,
							update:values
				};
				var xhr  = new XMLHttpRequest();
				xhr.open('PATCH', url);
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
			}
		})
  	},
	option:function(){
		let self = this;
		let se = null;

		switch(self.state.level){
			case 4:se =  (
							<OptGroup label='等级'>
								<Option value='3'>省级代理</Option>
								<Option value='2'>市县代理</Option>
								<Option value='1'>运营商</Option>
							</OptGroup>
				      );
			break;
			case 3:se =  (
							<OptGroup label='等级'>
								<Option value='2'>市县代理</Option>
								<Option value='1'>运营商</Option>
							</OptGroup>
				      );
			break;
			case 2:se =  (
							<OptGroup label='等级'>
								<Option value='1'>运营商</Option>
							</OptGroup>
				      );
			break;
		}
		return se;
	},
	levelChange:function(v){
		console.log(v);
		this.setState({levelchange:v});
	},
	typeSelect:function(v){
		this.setState({type:v});
	},
	search:function(v){
        var self = this;
        var url  = window.API_PREFIX+'/agent/search';
        var callback = function(err,res){
            if(err){
                message.error(err.err.msg);    
            }else{
                console.log(res.body);
                const pager = self.state.pagination;
                pager.total = res.body.data.count;
                res.body.data.agents.map((d,i)=>{
                	d.key = i;
                	d.level = self.level(d.level);
                })
                self.setState({records:res.body.data.agents,loading:false,pagination:pager});   
            }
        };
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
        let data = {[self.state.type]:v};
        data.salesman = 0;
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
	render: function (){
		let self = this;
		let alert = null;
		let btn = null;
		let content = null;
		let levelc = null;
		const { getFieldDecorator, getFieldValue ,setFieldsValue} = this.props.form;
		const columns = [ {
								title: '姓名',
								dataIndex: 'name',
						}, {
								title: '级别',
								dataIndex: 'level',
						},{
								title: '手机号',
								dataIndex: 'phone',
						},{
								title: '联系地址',
								dataIndex: 'address',
						},{
								title: '是否可发展下线',
								dataIndex: 'expandable',
								render:t => self.expandable(t)
						},{
								title: '会员充值是否立即到账',
								dataIndex: 'withdrawable',
								render:t =>self.expandable(t)
						},{
								title: '备注',
								dataIndex: 'remark',
						},{
								title: '修改',
								dataIndex: 'change',
								onCellClick:function(t,r){
									if(self.state.level===4){
										self.setState({setting:true})
									}
									let ex = 1;
									if(t.level !== '运营商'){
										ex = 2;
									}
									console.log(t)
									setFieldsValue(t);
									self.setState({firstdata:t,visible:true,required:false,title:'修改',agent_id:t.id,disabled:true,levelchange:ex})
								},
								render:text => <a style={{"fontWeight":"bolder"}}><Icon type="setting" /></a>
						}];
		const rowSelection = {
			selectedRowKeys:self.state.selectedRowKeys,
			onChange: self.onSelectChange,
			onSelect: self.onSelect,
		};
		if(self.state.levelchange!=1){
			levelc = <FormItem label={'是否可发展下线'}>
						{getFieldDecorator('expandable', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							}]
						})(
							<RadioGroup>
								<Radio value={1}>可以</Radio>
							<Radio value={0}>不可以</Radio>
								
							</RadioGroup>
						)}
					</FormItem>
		}
		if(self.state.errormsg){
			alert = <Alert message={self.state.errormsg} type='error'/>
		}
		if(self.state.setting){
			btn = (
				<div>
				<Button onClick={()=>{self.setState({adsetting:false})}} >代理商设置</Button>
				<Button style={{marginLeft:5}} onClick={()=>{this.getData();self.setState({adsetting:true})}} >高级设置</Button>
				</div>
			)
		}
		if(self.state.adsetting){
			content = (
				<Form onSubmit={self.settingSubmit} >
					<FormItem extra='最小取现金额不得小于2元'>
						{getFieldDecorator('min_withdraw', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							}]
						})(
							<Input type='number' placeholder="请输入最小取现金额" />
						)}
					</FormItem>
					<FormItem extra='手续费不能小于0.6%，填写格式为：0.006'>
						{getFieldDecorator('withdraw_fee', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							}]
						})(
							<Input type='number' placeholder="请填写微信取现手续费" />
						)}
					</FormItem>
					{alert}
					<Button key="back" size="large" onClick={self.handleCancel}>取消</Button>
					<Button key="submit" style={{marginLeft:5}} type="primary" size="large" htmlType='submit' loading={self.state.btn_loading}>提交</Button>
				</Form>
				)
		}else{
			content = (
				<Form onSubmit={self.handleSubmit} >
					<FormItem >
						{getFieldDecorator('name', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							}]
						})(
							<Input type='text' placeholder="请输入姓名" />
						)}
					</FormItem>
					<FormItem>
						{getFieldDecorator('level', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							}]
						})(
							<Select onChange={self.levelChange} disabled={self.state.disabled} placeholder='请选择代理级别'>
								{self.option()}
							</Select>
							
						)}
					</FormItem>
					<FormItem>
						{getFieldDecorator('phone', {
							
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							},{
								pattern:/^1[345789][0-9]{9}$/, message: '请填写正确的手机号',
							}]
						})(
							<Input disabled={self.state.disabled} type='text' placeholder="请填写手机号" />
						)}
					</FormItem>
					{/*<FormItem>
						{getFieldDecorator('email', {
							
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							},{pattern:/^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$/, message: '请填写正确的邮箱',}]
						})(
							<Input disabled={self.state.disabled} type='text' placeholder="请填写邮箱" />
						)}
					</FormItem>*/}
					<FormItem>
						{getFieldDecorator('address', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							}]
						})(
							<Input type='text' placeholder="请输入地址" />
						)}
					</FormItem>
					<FormItem label={'是否可发展下线'}>
						{getFieldDecorator('expandable', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							}]
						})(
							<RadioGroup>
								<Radio value={1}>可以</Radio>
							<Radio value={0}>不可以</Radio>
								
							</RadioGroup>
						)}
					</FormItem>
					<FormItem label={'会员充值是否立即到账'}>
						{getFieldDecorator('withdrawable', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							}]
						})(
							<RadioGroup>
								<Radio value={1}>可以</Radio>
								<Radio value={0}>不可以</Radio>
								
							</RadioGroup>
						)}
					</FormItem>
					<FormItem>
						{getFieldDecorator('remark', {
							initialValue:''
							
						})(
							<Input type='text' placeholder="请输入备注" />
						)}
					</FormItem>
					{alert}
					<Button key="back" size="large" onClick={self.handleCancel}>取消</Button>
					<Button key="submit" style={{marginLeft:5}} type="primary" size="large" htmlType='submit' loading={self.state.btn_loading}>提交</Button>
				</Form>
			)
		}
		return (
			<MyLayout level={(l)=>{self.setState({level:l})}}>
				<div style = {{height:'8vh'}}>
					<div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
		                <Select style={{ width: 100}} value={self.state.type} onChange={self.typeSelect}>
		                    <Option value='phone'>手机号搜索</Option>
		                    <Option value='name'>姓名搜索</Option>
		                </Select>
		                <Search placeholder="请输入"
		                    style={{ width: 200,marginRight:20 }}
		                    onSearch={self.search} />
					<Button onClick = {self.show_fn}>添加</Button>
				</div>
				<Table
					loading={self.state.loading}
					columns={columns} 
					dataSource={self.state.records} 
					onChange={self.onTableChange} 
					pagination={self.state.pagination}
				/>
				<Modal 
						width="400px"
						title={self.state.title} 
						visible={self.state.visible}
						onCancel={self.handleCancel}
						key={self.state.key}
						footer={null}
				>	{btn}
					{content}
				
				</Modal>
			</MyLayout>
		);
	}
});

Agent = Form.create()(Agent);
export default Agent;
export { Agent };