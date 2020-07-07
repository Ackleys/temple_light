"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';
import QRCode       from 'qrcode.react';
import { Button, Menu, Table, Input, Alert, Modal, message } from 'antd';
import {MyLayout}     from '../common/layout.js';
import { browserHistory} from 'react-router';
const Search = Input.Search;
function accAdd(arg1,arg2){
    var r1,r2,m;
    try{r1=arg1.toString().split(".")[1].length}catch(e){r1=0}
    try{r2=arg2.toString().split(".")[1].length}catch(e){r2=0}
    m=Math.pow(10,Math.max(r1,r2))
    return (arg1*m+arg2*m)/m
}
String.prototype.times = function(n) { return (new Array(n+1)).join(this);}; 
const SimCard = require('create-react-class')({

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
			loading:true,
			url:'',
			agent_id:'',
			level:2,
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
					q.cat = self.cat_change(q.cat);
					q.key = i;
					num++;
				})
				const pager = self.state.pagination;
				pager.total = res.body.data.count;
				self.setState({records:res.body.data.devices,loading:false,pagination:pager});
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
	onSelect:function(record,select,selectedRows){
		console.log(record);
		console.log(select);
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
				q.cat = self.cat_change(q.cat);
				q.key = 0;
				const pager = self.state.pagination;
				pager.total = 1;
				self.setState({records:[q],loading:false,pagination:pager});
               
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
		/*let modal_body = null;
		if(this.state.url){
				modal_body = (<QRCode level='H' size={256} value = {this.state.url}/>);
			}*/
		const columns = [ {
							title: '自编号',
							dataIndex: 'id',
						}, {
							title: 'IMEI',
							dataIndex: 'imei',
						},{
							title: 'iccid',
							dataIndex: 'iccid',
						}];
		const rowSelection = {
					onChange: self.onSelectChange,
					onSelect: self.onSelect,
		};
		content = (
			<Table
				loading={self.state.loading}
				columns={columns} 
				dataSource={self.state.records} 
				onChange={self.onTableChange} 
				pagination={self.state.pagination}
			/>
		);
		return(
			<MyLayout level={(l)=>{this.setState({level:l})}}>
				<div style = {{height:'8vh'}}>
					<div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
					<Search placeholder="请输入imei"
					    style={{ width: 200,marginLeft:20 }}
					    onSearch={self.search.bind(self,'imei')} />
					<Search placeholder="请输入设备自编号"
					    style={{ width: 200,marginLeft:20 }}
					    onSearch={self.search.bind(self,'device_id')} />
				</div>
				{content}
			</MyLayout>
		)
	}
})
export default SimCard;
export { SimCard };