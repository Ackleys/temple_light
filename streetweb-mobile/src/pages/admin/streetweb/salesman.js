"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {  Button, Menu,  Icon, Modal,Input,Table,Form ,Radio,Select,message,Alert,Tree,Card } from 'antd';
import {MyLayout}     from '../common/layout.js';
const FormItem = Form.Item;
const RadioGroup = Radio.Group;
const { Option, OptGroup } = Select;
const TreeNode = Tree.TreeNode;
var SalesMan = React.createClass({
	getInitialState: function() {
		return{
			records:[],
			loading:true,
			show:false,
			visible:false,
			key:0,
			required:true,
			title:'',
			errormsg:null,
			slevel:2,
			btn_loading:false,
			disabled:false,
			setting:false,
			adsetting:false,
			levelchange:3,
			name:'',
			cardtitle:'详细信息',
			address:'',
			phone:'',
			remark:'',
			email:'',
			le   :'',
			expandable:'',
			firstdata:{}
		}
			 
	},
	componentWillMount:function(){
		this.get_msg();
		this.get_agent();
	},
	componentDidMount:function(){
	 
	},
	get_agent:function(){
		let self = this;
		const pager = this.state.pagination;
		let url = window.API_PREFIX+'/agent/sub_salesman/fetch';
		var callback = function(err,res){
			if(err){
				console.log(err);
			}else{
				console.log(res.body);	
				self.setState({records:res.body.data.salesmen,loading:false});
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
			return '三级业务员';
		}else if(n === 2){
			return '二级业务员';
		}else if(n === 1){
			return '一级业务员';
		}
	},
	expandable:function(n){
		if(n === 1){
			return '是';
		}else if(n === 0){
			return '否';
		}
	},
	
	show_fn:function(){
		this.setState({visible:true,title:'添加',required:true,disabled:false,setting:false,adsetting:false});
	},
	handleCancel:function(){
		this.setState({visible:false,key:Math.random(),btn_loading:false,setting:false,adsetting:false,errormsg:null});
	},
	handleSubmit:function(e){
		let self = this;
		e.preventDefault();
		this.props.form.validateFieldsAndScroll((err, values) => {
			if (!err) {
					console.log('Received values of form: ', values);

					let url,type,data;
					if(self.state.title==='添加'){
						url= window.API_PREFIX+"/agent/add";
						type = 'PUT';
						values.slevel = values.slevel-0;
						if(values.slevel == 3){
							values.expandable = 0;
						}
						data = values;
						data.salesman = 1;
						data.level = 1;
						data.email = data.phone+'@mafu.com';
					}else if(self.state.title==='修改'){
						url= window.API_PREFIX+"/agent/update";
						type = 'PATCH';
						for (let i in values){
							if(!values[i]&&values[i]!==0){
								delete values[i];
							}
							if(values.slevel){
								delete values.slevel;
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
								self.get_agent();
								if(self.state.title==='修改'){

									self.onSelect();
								}
								message.success('成功');
								self.setState({errormsg:null,visible:false,key:Math.random(),btn_loading:false});
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
                self.setState({slevel:res.body.data.slevel});
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
						message.success('成功');
						self.setState({errormsg:null,visible:false,key:Math.random(),btn_loading:false,setting:false,adsetting:false});
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

		switch(self.state.slevel){
			case 0:se =  (
							<OptGroup label='等级'>
								<Option value='1'>一级业务员</Option>
								{/*<Option value='2'>二级业务员</Option>
								<Option value='3'>三级业务员</Option>*/}
							</OptGroup>
				      );
			break;
			case 1:se =  (
							<OptGroup label='等级'>
								<Option value='2'>二级业务员</Option>
								{/*<Option value='3'>三级业务员</Option>*/}
							</OptGroup>
				      );
			break;
			case 2:se =  (
							<OptGroup label='等级'>
								<Option value='3'>三级业务员</Option>
							</OptGroup>
				      );
			break;
		}
		return se;
	},
	onCellClick:function(){
		let self = this;
		if(!self.state.agent_id){
			alert('请选择业务员后点击该按钮');
			return false;
		}
		if(self.state.slevel===3){
			self.setState({setting:false,levelchange:3});
		}else{
			self.setState({setting:true,levelchange:1});
		}
		const {  setFieldsValue } = this.props.form;
		self.setState({required:false,disabled:true,visible:true,title:'修改'},function(){
			setFieldsValue(self.state.firstdata);
		});
	},
	levelChange:function(v){
		console.log(v);
		this.setState({levelchange:v});
	},
	renderTreeNodes : function(data) {
	    return data.map((item) => {
	      	if (item.children) {
	      		if(item.children.length>0){
			        return (
			          	<TreeNode className='treenode' title={item.title} key={item.key} dataRef={item}>
			            	{this.renderTreeNodes(item.children)}
			          	</TreeNode>
			        );
	      		}else{
	      			return <TreeNode className='treenode' title={item.title} key={item.key} />;
	      		}
	      	}
	      	return <TreeNode className='treenode' title={item.title} key={item.key} />;
	    });
	},
	onSelect:function(v=this.state.agent_id){
		var self = this;
		let id = 0;
		if(v.length === undefined){
			id = v;
		}else{
			id = v[0]-0;     
			self.setState({agent_id:id});
		}
	    var url = window.API_PREFIX+"/agent/fetch";
	    const {  setFieldsValue } = this.props.form;
	    var callback = function(err,res){
	      if(err){

	      }else{
	          console.log(res.body);
	          self.setState({name:res.body.data.name,
				          	address:res.body.data.address,
				          	phone:res.body.data.phone,
				          	remark:res.body.data.remark,
				          	email:res.body.data.email,
				          	le:self.level(res.body.data.slevel),
				          	expandable:self.expandable(res.body.data.expandable),
				          	withdrawable:self.expandable(res.body.data.withdrawable),
				          	firstdata:res.body.data
				          });
	      }
	    };
	    var xhr  = new XMLHttpRequest();
	    xhr.open("POST", url);
	    xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
	    xhr.send(JSON.stringify({agent_id:id}));
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
		const { getFieldDecorator, getFieldValue } = this.props.form;
		
		if(self.state.levelchange!=3){
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
		if(self.state.setting&&self.state.slevel===0){
			btn = (
				<div>
				<Button onClick={()=>{self.setState({adsetting:false},()=>{
					const {  setFieldsValue } = this.props.form;
					setFieldsValue(self.state.firstdata);
				})}} >业务员设置</Button>
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
						{getFieldDecorator('slevel', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							}]
						})(
							<Select onChange={self.levelChange} disabled={self.state.disabled} placeholder='请选择业务员级别'>
								{self.option()}
							</Select>
							
						)}
					</FormItem>
					<FormItem>
						{getFieldDecorator('phone', {
							
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							},{
								pattern:/^1[34578][0-9]{9}$/, message: '请填写正确的手机号',
							}]
						})(
							<Input type='text' disabled={self.state.disabled} placeholder="请填写手机号" />
						)}
					</FormItem>
					{/*<FormItem>
						{getFieldDecorator('email', {
							
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							},{pattern:/^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$/, message: '请填写正确的邮箱',}]
						})(
							<Input type='text' disabled={self.state.disabled} placeholder="请填写邮箱" />
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
					{levelc}
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
					<Button type="primary" ghost onClick = {self.show_fn}>添加</Button>
					<span style={{color: '#aaa', marginLeft: 10}}>添加业务员后会在下方树状显示，点击业务员可查看详细信息</span>
				</div>
				<div style={{display:'flex'}}>
					<div style={{flex:1.5,minHeight:'70vh',fontSize:18}}>
						<Tree
					        showLine
					        //defaultExpandedKeys={['0-0-0']}
					        onSelect={this.onSelect}
					    >
					    	{self.renderTreeNodes(self.state.records)}
					    </Tree>
					</div>
					<div style={{flex:4,minHeight:'70vh'}}>
						<Card title={self.state.name+self.state.cardtitle} extra={<a href="#" style={{fontSize:18}} onClick={self.onCellClick}>修改</a>} style={{ width: '100%' }}>
						    <table className='cardtable'>
						    	<tbody>
							    	<tr><td>姓名：</td><td>{self.state.name}</td></tr>
							    	<tr><td>手机号：</td><td>{self.state.phone}</td></tr>
							    	<tr><td>地址：</td><td>{self.state.address}</td></tr>
							    	<tr><td>邮箱：</td><td>{self.state.email}</td></tr>
							    	<tr><td>等级：</td><td>{self.state.le}</td></tr>
							    	<tr><td>是否可发展下级：</td><td>{self.state.expandable}</td></tr>
							    	<tr><td>充值是否立即到账：</td><td>{self.state.withdrawable}</td></tr>
							    	<tr><td>备注：</td><td>{self.state.remark}</td></tr>
						    	</tbody>
						    </table>
						</Card>
					</div>
				</div>
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

SalesMan = Form.create()(SalesMan);
export default SalesMan;
export { SalesMan };