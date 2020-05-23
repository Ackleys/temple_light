"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {  Button, Menu,  Icon, Modal,Input,Table,Form ,message,Alert} from 'antd';
import {MyLayout}     from '../common/layout.js';
const FormItem = Form.Item;
import { browserHistory} from 'react-router';
var AdminList = React.createClass({
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
			show:false,
		}
			 
	},
	componentWillMount:function(){
		
	},
	componentDidMount:function(){
	 	this.get_agent(1,10);
	},
	get_agent:function(page,psize){
		let self = this;
		const pager = this.state.pagination;
		let url = window.API_PREFIX+'/god/god_devices/fetch?page='+page+'&psize='+psize;
		var callback = function(err,res){
			if(err){
				console.log(err);
				message.error(err.err.msg);
				self.setState({loading:false});
			}else{
				console.log(res.body);
				pager.total = res.body.data.count;
				res.body.data.devices.forEach(function(q,i){
		            if(q.cat){
		            	q.cat = '投币器';
		            }else{
		            	q.cat = '倒计时';
		            }
		            q.key = i;
		            if(q.use_state){
		            	q.use_state = '使用中';
		            }else if(!q.use_state){
		            	q.use_state = '空闲';
		            }
		            if(q.comm_state){
		            	q.comm_state = '在线';
		            }else if(!q.comm_state){
		            	q.comm_state = '关机';
		            }
		        })
				self.setState({records:res.body.data.devices,pagination:pager,loading:false});
			}
		};
		let data = {god_id:sessionStorage.getItem('getlist')-0};
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
	onTableChange:function(pagination, filters, sorter) {
		const pager = this.state.pagination;
		pager.current = pagination.current;
		pager.pageSize = pagination.pageSize;
		this.setState({
				pagination: pager,
		});
		this.get_agent(pager.current,pager.pageSize);
	},
	render: function (){
		let self = this;
		const columns = [ {
                title: '自编号',
                dataIndex: 'id',
            }, {
                title: 'IMEI',
                dataIndex: 'imei',
            },{
                title: '设备类型',
                dataIndex: 'cat',
            },{
                title: '设备状态',
                dataIndex: 'use_state',
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
            }];
		return (
			<MyLayout>
				<div style = {{height:'8vh'}}>
					<div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
					<Button onClick = {function(){browserHistory.push(window.URL_PREFIX+'/admin')}}>返回</Button>
				</div>
				<Table
					loading={self.state.loading}
					columns={columns} 
					dataSource={self.state.records} 
					onChange={self.onTableChange} 
					pagination={self.state.pagination}
				/>
			</MyLayout>
		);
	}
});

AdminList = Form.create()(AdminList);
export default AdminList;
export { AdminList };