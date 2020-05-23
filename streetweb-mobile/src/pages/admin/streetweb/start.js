"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Button,Menu, Icon, Modal,Input,Table,message,Alert} from 'antd';
import {MyLayout}     from '../common/layout.js';
const Search = Input.Search;
const List = React.createClass({
	getInitialState: function() {
		return{
			records:[],
			"pagination": {
				"showSizeChanger":true,
				"current"        : 1,
				"pageSize"       : 10,
				"pageSizeOptions": ['10', '25', '50', '100']
			},
			loading:true,
			imei:''
		}	 
	},
	componentWillMount:function(){
		this.get_start(1,10);
	},
	componentDidMount:function(){
	 	
	},
	get_start:function(page,psize){
		let self = this;
		const pager = this.state.pagination;
		let url = window.API_PREFIX+'/device/nopay/record/fetch?page='+page+'&psize='+psize;
		var callback = function(err,res){
			if(err){
				//console.log(err);
			}else{
				//console.log(res.body);
				pager.total = res.body.data.count;
				res.body.data.records.forEach((d,i)=>{
					d.key = i;
					d.stime =self.getdate(new Date(d.stime*1000));
					d.etime =self.getdate(new Date(d.etime*1000));
				})
				self.setState({records:res.body.data.records,pagination:pager,loading:false});
			}
		};
		var xhr  = new XMLHttpRequest();
		xhr.open("POST", url);
		xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
		xhr.send(JSON.stringify({imei:self.props.imei}));
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
		this.get_start(pager.current,pager.pageSize);
	},
	getdate:function (now) {
        let y = now.getFullYear();
        let m = now.getMonth() + 1;
        let d = now.getDate();
        return y + "-" + (m < 10 ? "0" + m : m) + "-" + (d < 10 ? "0" + d : d) + " " + now.toTimeString().substr(0, 8);
    },
	render:function(){
		let self = this;
		const columns = [ {
							title: 'imei',
							dataIndex: 'imei',
						},{
							title: '启动时间',
							dataIndex: 'stime',
						},{
							title: '结束时间',
							dataIndex: 'etime',
						}];
		return(
			<div>
				<div style = {{height:'8vh'}}>
					<div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
					<Button style={{marginLeft:10}} type='primary' onClick = {()=>{if(typeof self.props.show === 'function'){self.props.show(false)}}}>返回</Button>
				</div>
				<Table
					loading={self.state.loading}
					columns={columns} 
					dataSource={self.state.records} 
					onChange={self.onTableChange} 
					pagination={self.state.pagination}
				/>
			</div>
		)
	}
});
const Start = React.createClass({
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
			startlist_show:false,
			imei:'',
			type:[],
			data:{},
			salesman:''
		}	 
	},
	componentWillMount:function(){
		
	},
	componentDidMount:function(){

	},
	type:function(t){
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
				self.get_nopay(1,10,t);
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
		return a;
	},
	get_nopay:function(page,psize,t){
		let self = this;
		const pager = this.state.pagination;
		let url;
		if(t === 0){
			url = window.API_PREFIX+'/device/nopay/fetch?page='+page+'&psize='+psize;
		}else{
			url = window.API_PREFIX+'/device/nopay/salesman/fetch?page='+page+'&psize='+psize;
		}
		var callback = function(err,res){
			if(err){
				console.log(err);
			}else{
				console.log(res.body);
				pager.total = res.body.data.count;
				res.body.data.devices.forEach((d,i)=>{
					d.key = i;
					d.cat = self.cat_change(d.cat);
				})
				self.setState({records:res.body.data.devices,pagination:pager,loading:false});
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
		const pager = this.state.pagination;
		pager.current = pagination.current;
		pager.pageSize = pagination.pageSize;
		this.setState({
			pagination: pager,
		});
		this.get_nopay(pager.current,pager.pageSize,this.state.salesman);
	},
	show_fn:function(){
		this.setState({visible:true});
	},
	search:function(v){
		let self = this;
		let url = window.API_PREFIX+'/device/nopay/search';
		var callback = function(err,res){
			if(err){
				message.error(err.err.msg);
			}else{
				console.log(res.body);
				let d = res.body.data;
				d.key = d.imei;
				d.cat = self.cat_change(d.cat);
				self.setState({records:[d],loading:false});
			}
		};
		var xhr  = new XMLHttpRequest();
		xhr.open("POST", url);
		xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
		let type = '';
		if(v.length<15){
			type = 'device_id';
		}else if(v.length===15){
			type = 'imei';
		}
		xhr.send(JSON.stringify({[type]:v}));
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
		const columns = [ {
							title: '自编号',
							dataIndex: 'id',
						},{
							title: 'imei（点击查看启动记录）',
							dataIndex: 'imei',
							onCellClick:(t)=>{ console.log(t);self.setState({imei:t.imei,startlist_show:true})},
							render:text => <a>{text}</a>
						},{
							title: '投放地址',
							dataIndex: 'address',
						},{
							title: '设备类型',
							dataIndex: 'cat',
						},{
							title: '启动次数',
							dataIndex: 'nopay_count',
						},{
							title: '备注',
							dataIndex: 'remark',
						}];
		if(!self.state.startlist_show){
			content = (<div><div style = {{height:'8vh'}}>
							<div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
							<Search placeholder="请输入imei或自编号"
							    style={{ width: 200,marginLeft:20 }}
							    onSearch={self.search} />
						</div>
						<Table
							loading={self.state.loading}
							columns={columns} 
							dataSource={self.state.records} 
							onChange={self.onTableChange} 
							pagination={self.state.pagination}
						/></div>)
		}else{
			content = <List imei={self.state.imei} show={(s)=>{self.setState({startlist_show:s})}} />
		}
		return (
			<MyLayout data={(d)=>{self.setState({salesman:d.salesman});this.type(d.salesman)}}>
				{content}
			</MyLayout>
		);
	}
});

export default Start;
export { Start };