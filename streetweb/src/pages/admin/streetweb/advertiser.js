"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import { Form, Icon } from '@ant-design/compatible';
import {  Button, Menu, Modal,Input,Table ,Radio,Select,message,Alert} from 'antd';
import {MyLayout}     from '../common/layout.js';
import List      from './ad_list.js';
const FormItem = Form.Item;
const RadioGroup = Radio.Group;
const { Option, OptGroup } = Select;
var Advertiser = require('create-react-class')({
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
			loading:true,
			visible:false,
			key:0,
			required:true,
			title:'',
			errormsg:null,
			level:2,
			btn_loading:false,
			disabled:false,
			id:0,
			adlist_show:false,
			advertiser_id:0
		}	 
	},
	componentWillMount:function(){
		
	},
	componentDidMount:function(){
	 	
	},
	get_advertiser:function(page,psize){
		let self = this;
		const pager = this.state.pagination;
		let url = window.API_PREFIX+'/advertiser/agent_sub/fetch?page='+page+'&psize='+psize;
		var callback = function(err,res){
			if(err){
				console.log(err);
			}else{
				console.log(res.body);
				pager.total = res.body.data.count;
				res.body.data.advertisers.forEach((d,i)=>{
					d.key = i;
					d.change ='';
				})
				self.setState({records:res.body.data.advertisers,pagination:pager,loading:false});
			}
		};
		var xhr  = new XMLHttpRequest();
		xhr.open("POST", url);
		xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
		xhr.send(JSON.stringify({agent_id:self.state.id}));
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
		const pager = this.state.pagination;
		pager.current = pagination.current;
		pager.pageSize = pagination.pageSize;
		this.setState({
			pagination: pager,
		});
		this.get_advertiser(pager.current,pager.pageSize);
	},
	show_fn:function(){
		this.setState({visible:true,title:'添加',required:true,disabled:false});
	},
	handleCancel:function(){
		this.setState({visible:false,key:Math.random(),btn_loading:false,errormsg:null,advertiser_id:''});
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
					url= window.API_PREFIX+"/advertiser/add";
					type = 'PUT';
					values.level = values.level-0;
					if(values.level == 1){
						values.expandable = 0;
					}
					data = values;
					data.salesman = 0;
					data.slevel = 0;
				}else if(self.state.title==='修改'){
					url= window.API_PREFIX+"/advertiser/update";
					type = 'PATCH';
					for (let i in values){
						if(!values[i]&&values[i]!==0){
							delete values[i];
						}
						if(values.level){
							delete values.level;
						}
					}
					data={
						advertiser_id:self.state.advertiser_id-0,
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
						self.get_advertiser(pager.current,pager.pageSize);
						message.success('成功');
						self.setState({errormsg:null,visible:false,key:Math.random(),btn_loading:false,advertiser_id:''});
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
	levelChange:function(v){
		console.log(v);
		this.setState({levelchange:v});
	},
	render: function (){
		let self = this;
		let alert = null;
		let btn = null;
		let content = null;
		let levelc = null;
		const { getFieldDecorator, getFieldValue } = this.props.form;
		const columns = [ {
							title: '姓名(点击查看投放传单)',
							dataIndex: 'name',
							onCellClick:(t)=>{self.setState({advertiser_id:t.id,adlist_show:true})},
							render:text => <a>{text}</a>
						},{
							title: '手机号',
							dataIndex: 'phone',
						},{
							title: '联系地址',
							dataIndex: 'address',
						},{
							title: '商户信息',
							dataIndex: 'desc',
						},{
							title: '备注',
							dataIndex: 'remark',
						},{
							title: '修改',
							dataIndex: 'change',
							onCellClick:(t,r)=>{self.setState({visible:true,required:false,title:'修改',advertiser_id:t.id,disabled:true})},
							render:text => <a style={{"fontWeight":"bolder"}}><Icon type="setting" /></a>
						}];
		if(self.state.errormsg)alert = <Alert message={self.state.errormsg} type='error'/>
		if(!self.state.adlist_show){
			content = (<div><div style = {{height:'8vh'}}>
							<div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
							<Button onClick = {self.show_fn}>添加</Button>
						</div>
						<Table
							loading={self.state.loading}
							columns={columns} 
							dataSource={self.state.records} 
							onChange={self.onTableChange} 
							pagination={self.state.pagination}
						/></div>)
		}else{
			content = <List.List id={self.state.advertiser_id} show={(s)=>{self.setState({adlist_show:s})}} />
		}
		return (
			<MyLayout id={(id)=>{self.setState({id:id},()=>{self.get_advertiser(1,10)})}} level={(l)=>{self.setState({level:l})}}>
				{content}
				<Modal 
					width="400px"
					title={self.state.title} 
					visible={self.state.visible}
					onCancel={self.handleCancel}
					key={self.state.key}
					footer={null}
				>	
					<Form onSubmit={self.handleSubmit} >
					<FormItem >
						{getFieldDecorator('name', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							}]
						})(
							<Input disabled={self.state.disabled} type='text' placeholder="请输入姓名" />
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
					<FormItem>
						{getFieldDecorator('email', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							},{pattern:/^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$/, message: '请填写正确的邮箱',}]
						})(
							<Input disabled={self.state.disabled} type='text' placeholder="请填写邮箱" />
						)}
					</FormItem>
					<FormItem>
						{getFieldDecorator('address', {
							rules: [{
								required: self.state.required, message: '请填写完毕后提交',
							}]
						})(
							<Input type='text' placeholder="请输入地址" />
						)}
					</FormItem>
					<FormItem>
						{getFieldDecorator('desc', {
							initialValue:''	
						})(
							<Input type='text' placeholder="请输入商户信息" />
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
				
				</Modal>
			</MyLayout>
		);
	}
});

Advertiser = Form.create()(Advertiser);
export default Advertiser;
export { Advertiser };