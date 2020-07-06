"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';

import { Form, Icon } from '@ant-design/compatible';
import {  Button, Menu,  Table, Input,Alert,Tabs,DatePicker,Select,message } from 'antd';
import {MyLayout}     from '../common/layout.js';
const { MonthPicker, RangePicker } = DatePicker;
const FormItem = Form.Item;
const Option = Select.Option;

var DeviceRecyle = require('create-react-class')({

	getInitialState: function() {
	   return{
        "records":[],
        imei_data:[],
        imei:'',
        errormsg:null,
        "pagination": {
            "showSizeChanger":true,
            //defaultPageSize: 10,
            //defaultCurrent : 1,
            "current"        : 1,
            "pageSize"       : 10,
            "pageSizeOptions": ['10', '25', '50', '100']
        },
        id:'device_id',
	   }
	},
	componentWillMount:function(){

	},
	handleSubmit:function(e){
		let self = this;
	    e.preventDefault();
	    this.props.form.validateFieldsAndScroll((err, values) => {
	    	if (!err) {
	        	console.log('Received values of form: ', values);
	        	let data = {};
	        	for (let i in values) {               
    				if(values[i]){
    					data[i] = values[i];
    				}
    				if(i === 'device_id'){
    					data[i] = values[i]-0;
    				}
	        	}
	        	self.get_device(data);	
	        }
	    })
	},
	handleChange:function(value,num){
	    const { setFieldsValue } = this.props.form;
	    if(value === 'imei'){
	      	setFieldsValue({'imei':num});
	      	this.fruzzy_seach_imei(num);
	    }
    },
    get_device:function(data){
    	let self = this;
	    let url = window.API_PREFIX+'/god/device/query';
	    var callback = function(err,res){
	        if(err){
	          	message.error(err.err.msg);
	        }else{
	            console.log(res.body);
	            res.body.data.key=0;
	            self.setState({records:[res.body.data]});
	        }
	    };
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
    fruzzy_seach_imei:function(num){
	    let self = this;
	    let url = window.API_PREFIX+'/god/device/fuzzy_query/imei';
	    var callback = function(err,res){
	          if(err){

	          }else{
	            console.log(res.body);
	            let data={};
	            data['imei_data'] = res.body.data;
	            self.setState(data);
	          }
	    };
	    let data={};
	    data.imei= num;
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
        //console.log('params', pagination, filters, sorter);
        const pager = this.state.pagination;
        pager.current = pagination.current;
        pager.pageSize = pagination.pageSize;
        this.setState({
            pagination: pager,
        });
        this.order_list(pagination.current,pagination.pageSize);
    },
    recycle:function(re){
        let url = window.API_PREFIX+'/god/device/recycle';
        let self = this;
        var callback = function(err,res){
            if(err){
                message.error(err.err.msg);
            }else{
               message.success('收回成功！');
               self.setState({records:[]});
            }
        };       
        var xhr  = new XMLHttpRequest();
        xhr.open("PATCH", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify({imei:re.imei}));
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
    typeChange:function(v){
    	this.setState({id:v});
    },
	render:function(){
		let self = this;
		const columns = [{
                title: 'imei',
                dataIndex: 'imei',
            },{
                title: '自编号',
                dataIndex: 'id',
            },{
                title: '运营商',
                dataIndex: 'operator',
            },{
                title: '投放地点',
                dataIndex: 'address',
            },{
                title: '备注',
                dataIndex: 'remark',
            },{
                title: '收回设备',
                dataIndex: 'recyle',
                render:(text,re)=>{
                    return <Button onClick = {self.recycle.bind(self,re)}>收回</Button>
                }
            }];
		const { getFieldDecorator, getFieldValue } = this.props.form;
		const imei_options = this.state.imei_data.map((d,i) => <Option key={i} value={d}>{d}</Option>);
		let alert = null;
		let input = <Input style={{width:'25%',marginRight:10,float:'left'}} placeholder='请输入自编号' />
		if(self.state.errormsg){
			alert = (<Alert type = 'error' message={self.state.errormsg} />)
		}
		if(self.state.id === 'imei'){
			
			input = <Select
				        combobox={true}
				        placeholder='IMEI(可模糊搜索)'
				        notFoundContent=""
				        defaultActiveFirstOption={false}
				        showArrow={false}
				        filterOption={false}
				        onChange={this.handleChange.bind(self,'imei')}
				        style={{width:'25%',marginRight:10,float:'left'}}
				    >
				        {imei_options}
				    </Select>
		}
		return(
			<MyLayout level={(l)=>{self.setState({level:l})}}>
				<div className='home_head'>
		            <Form onSubmit={this.handleSubmit}>
				        <FormItem className='formitem' >
				        	<Select defaultValue='device_id' style = {{width:100,float:'left'}} onChange={self.typeChange}>
				        		<Option value='imei'>imei</Option>
				        		<Option value='device_id'>自编号</Option>
				        	</Select>
					        {getFieldDecorator(self.state.id,  {
				    		})(
				    			input
				    		)}
					        <Button type="primary" style={{marginRight:'5%'}} htmlType='submit'>查询</Button>
				        </FormItem>
				        {alert}
	       			</Form>
		        </div>
		        <Table columns={columns}                      
                dataSource={this.state.records} 
                onChange={self.onTableChange} 
                pagination={self.state.pagination}
                style={{'marginTop':20}}
            /> 
			</MyLayout>
		)
	}
})
DeviceRecyle = Form.create()(DeviceRecyle);
export default DeviceRecyle;
export { DeviceRecyle };