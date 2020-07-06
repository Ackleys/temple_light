"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';
import moment       from 'moment';
import {  Button, Menu,  Icon,  Table, Input,Alert,Tabs,DatePicker,Form,Select,message,Popconfirm} from 'antd';
import {MyLayout}     from '../common/layout.js';
const { MonthPicker, RangePicker } = DatePicker;
import 'moment/locale/zh-cn';
moment.locale('zh-cn');
const FormItem = Form.Item;
const Option = Select.Option;
const dateFormat = 'YYYY-MM-DD HH:mm:ss';


var Order = require('create-react-class')({

	getInitialState: function() {
	   return{
        "records":[],
        address_data:[],
        imei_data:[],
        num_data:[],
        'value':'',
        address:'',
        imei:'',
        loading:false,
        errormsg:null,
        "pagination": {
            "showSizeChanger":true,
            //defaultPageSize: 10,
            //defaultCurrent : 1,
            "current"        : 1,
            "pageSize"       : 10,
            "pageSizeOptions": ['10', '25', '50', '100','10000']
        },
        idTmr:null
	   }
	},
	componentWillMount:function(){
		let data = {};
		let self = this;
		data.end = parseInt(new Date().getTime()/1000);
        data.start = data.end-60*60*24;
        data.pay_mode = 0;
		this.setState({data:data},function(){self.order_list(1,10)});
		

	},
	handleSubmit:function(e){
		let self = this;
	    e.preventDefault();
	    this.props.form.validateFieldsAndScroll((err, values) => {
	    	if (!err) {
	        	console.log('Received values of form: ', values);
	        	let data = {};
	        	for (let i in values) {
	        		
        			if(i === 'time'){
        				if(values.time !== undefined&&values.time !== []){
	        				data.start = parseInt(new Date(values.time[0].format()).getTime()/1000)	;
	        				data.end = parseInt(new Date(values.time[1].format()).getTime()/1000)	;
        				}else{
        					data.end = parseInt(new Date().getTime()/1000);
        					data.start = data.end-60*60*24;
        				}
        			}else{
        				if(values[i]){
        					data[i] = values[i];
        				}
        				if(i === 'pay_mode'){
        					data.pay_mode = data.pay_mode-0;
        				}
        			}
	        		
	        	}
	        	self.setState({data:data},function(){self.order_list(1,10);});
	        	
	        }
	    })
	},
	handleChange:function(value,num){
	    const { setFieldsValue } = this.props.form;
	    if(value === 'address'){
	      setFieldsValue({'address':num});
	      
	      	this.fruzzy_seach_add(num);
	      
	    }else if(value === 'imei'){
	      setFieldsValue({'imei':num});
	     
	      	this.fruzzy_seach_imei(num);
	      
	    }else if(value === 'number'){
	      setFieldsValue({'number':num});
	    }
    },
    fruzzy_seach_add:function(num){
	    let self = this;
	    let url = window.API_PREFIX+'/device/address/fuzzy_query/address';
	    var callback = function(err,res){
	        if(err){

	        }else{
	            console.log(res.body);
	            let data={};
	            data['address_data'] = res.body.data;
	            self.setState(data);
	        }
	    };
	    let data={};
	    data.address = num;
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
	    let url = window.API_PREFIX+'/device/fuzzy_query/imei';
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
	handleReset:function ()  {
	    this.props.form.resetFields();
	},
	order_list:function(page,psize){
		let self = this;
		const pager = this.state.pagination;
		let url = window.API_PREFIX+'/economic/order/query?page='+page+'&psize='+psize;
		var callback = function(err,res){
	        if(err){
	        	self.setState({errormsg:err.err.msg});
	        }else{
	            console.log(res.body);
	            self.setState({errormsg:null});
	            pager.total = res.body.data.count;
	            if(res.body.data.orders.length === 0){
	            	message.info('暂无数据');
	            	self.setState({records:res.body.data.orders})

	            	return false;
	            }
	            res.body.data.orders.forEach((d,i)=>{
	            	d.key = i;
	            	d.status = self.status(d.status);
	            	d.time = self.getdate(new Date(d.time*1000));
	            	d.cat = self.cat(d.cat);
	            	d.total_fee = d.total_fee/100;
	            })
	            self.setState({pagination:pager,records:res.body.data.orders})
	        }
	    };
	    console.log(self.state.data);
	    if(!self.state.data.pay_mode){
			delete self.state.data.pay_mode;
		}
	    var xhr  = new XMLHttpRequest();
	    xhr.open("POST", url);
	    xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
	    xhr.send(JSON.stringify(self.state.data));
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
	getdate:function (now) {
        let y = now.getFullYear();
        let m = now.getMonth() + 1;
        let d = now.getDate();
        return y + "-" + (m < 10 ? "0" + m : m) + "-" + (d < 10 ? "0" + d : d) + " " + now.toTimeString().substr(0, 8);
    },
	status:function(n){
		if(n === 0){
			return '未支付'
		}else if(n === 1){
			return '已支付'
		}else if(n === 2){
			return '支付失败'
		}else if(n === 3){
			return '已退款'
		}
	},
	cat:function(i){
		if(i === 0){
			return '倒计时'
		}else if(i === 1){
			return '投币器'
		}
	},
	getExplorer:function(){
	    var explorer = window.navigator.userAgent ;
	    //ie 
	    if (explorer.indexOf("MSIE") >= 0) {
	        return 'ie';
	    }
	    else if(explorer.indexOf("Edge") >= 0){
	        return 'Edge';
	    }
	    //firefox 
	    else if (explorer.indexOf("Firefox") >= 0) {
	        return 'Firefox';
	    }
	    //Chrome
	    else if(explorer.indexOf("Chrome") >= 0){
	        return 'Chrome';
	    }
	    //Opera
	    else if(explorer.indexOf("Opera") >= 0){
	        return 'Opera';
	    }
	    //Safari
	    else if(explorer.indexOf("Safari") >= 0){
	        return 'Safari';
	    }
	},
	method1:function(){
	    let self = this;
	    
	    if(self.getExplorer()=='ie'||self.getExplorer()=='Edge'){
	      	var curTbl = document.getElementsByTagName('table')[0];
	      	var oXL;
	      	try{  
	      	  	oXL = new ActiveXObject("Excel.Application"); //创建AX对象excel  
	      	}catch(e){  
	      	  	alert("无法启动Excel!\n\n如果您确信您的电脑中已经安装了Excel，"+"那么请调整IE的安全级别。\n\n具体操作：\n\n"+"工具 → Internet选项 → 安全 → 自定义级别 → 对没有标记为安全的ActiveX进行初始化和脚本运行 → 启用");  
	      	  	return false;  
	      	} 
	      	//创建AX对象excel 
	      	var oWB = oXL.Workbooks.Add();
	      	//获取workbook对象 
	      	var xlsheet = oWB.Worksheets(1);
	      	//激活当前sheet 
	      	var sel = document.body.createTextRange();
	      	sel.moveToElementText(curTbl);
	      	//把表格中的内容移到TextRange中 
	      	sel.select;
	      	//全选TextRange中内容 
	      	sel.execCommand("Copy");
	      	//复制TextRange中内容  
	      	xlsheet.Paste();
	      	//粘贴到活动的EXCEL中       
	      	oXL.Visible = true;
	      	//设置excel可见属性
	
	      	try {
	      	    var fname = oXL.Application.GetSaveAsFilename("Excel.xls", "Excel Spreadsheets (*.xls), *.xls");
	      	} catch (e) {
	      	    print("Nested catch caught " + e);
	      	} finally {
	      	    oWB.SaveAs(fname);
	
	      	    oWB.Close(savechanges = false);
	      	    //xls.visible = false;
	      	    oXL.Quit();
	      	    oXL = null;
	      	    //结束excel进程，退出完成
	      	    //window.setInterval("Cleanup();",1);
	      	    self.state.idTmr = window.setInterval(function(){self.Cleanup()}, 1);
	      	}
	    }else{
	    	var tableToExcel = (function() {  
	            var uri = 'data:application/vnd.ms-excel;base64,',  
	                    template = "<html><head><meta charset=\"UTF-8\"></head><body><table style=\"mso-number-format:'\@';\">{table}</table></body></html>",  
	                    base64 = function(s) { return window.btoa(unescape(encodeURIComponent(s))) },  
	                    format = function(s, c) {  
	                        return s.replace(/{(\w+)}/g,  
	                                function(m, p) { return c[p]; }) }  
	            return function(table, name) {  
	               	table = document.getElementsByTagName('table')[0];
	               	$('.order').attr('style',"mso-number-format:'\@';");
	               	$('.username').attr('style',"mso-number-format:'\@';") 
	                var ctx = {worksheet: name || 'Worksheet', table: table.innerHTML}  
	                window.location.href = uri + base64(format(template, ctx))  
	            }  
	        })() 
	        tableToExcel();
	    }
	},
	Cleanup:function(){
	    let self = this;
	    window.clearInterval(self.state.idTmr); 
	},
	backmoney:function(id){
		let self = this;
		self.setState({id:id});
		let url = window.API_PREFIX+'/economic/manual_refund';
		var callback = function(err,res){
	        if(err){
	        	message.error(err.err.msg);
	        	self.setState({id:''});
	        }else{
	            console.log(res.body);
	            self.setState({id:''});
	            self.order_list(1,10);
	        }
	    };
	    var xhr  = new XMLHttpRequest();
	    xhr.open("POST", url);
	    xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
	    xhr.send(JSON.stringify({pay_id:id}));
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
		const { getFieldDecorator, getFieldValue } = this.props.form;
		const add_options = this.state.address_data.map((d,i) => <Option key={i} value={d}>{d}</Option>);
		const imei_options = this.state.imei_data.map((d,i) => <Option key={i} value={d}>{d}</Option>);
		//const num_options = this.state.num_data.map(d => <Option key={d.text}>{d.text}</Option>);
		const columns = [{
                title: '序号',
                dataIndex: 'id',
            },{
                title: '时间',
                dataIndex: 'time',
            },{
                title: '单号',
                dataIndex: 'trade_no',
                className:'order',
            },{
                title: '运营商',
                dataIndex: 'operator',
            },{
                title: '金额（元）',
                dataIndex: 'total_fee',
            }, {
                title: '支付方式',
                dataIndex: 'pay_way', 
            }, {
                title: '订单状态',
                dataIndex: 'status',
            }, {
                title: '退款按钮',
                dataIndex: 'back',
                render:(text,re)=>{
                	console.log(re);
                	if(re.status==='已支付'){

                		return (
                			<Popconfirm title="确定要退款吗?" onConfirm={self.backmoney.bind(self,re.id)} okText="是" cancelText="否">
							    <Button type='primary' loading={self.state.id===re.id?true:false}>退款</Button>
							 </Popconfirm>
                			)
                		
                	}else{
                		return <Button type='primary' disabled >退款</Button>
                	}
                	
                }
            }, {
                title: '自编号',
                dataIndex: 'device_id',
            }, {
                title: '设备',
                dataIndex: 'cat',
            }, {
                title: '地点',
                dataIndex: 'address',
            },{
                title: '用户',
                dataIndex: 'username',
                className:'username', 
            }];
		let alert = null;
		if(self.state.errormsg){
			alert = (<Alert type = 'error' message={self.state.errormsg} />)
		}
		return(
			<MyLayout>
				<div className='home_head'>
		            <Form onSubmit={this.handleSubmit}>
		            	<FormItem className='formitem'>
					   		{getFieldDecorator('time',  {
						      initialValue:[moment(new Date(parseInt(new Date().getTime())-86400000),dateFormat),moment(new Date(parseInt(new Date().getTime())),dateFormat)]
						    })(
					            <RangePicker showTime format="YYYY-MM-DD HH:mm:ss" style={{width:'50%',marginRight:10,float:'left'}}/>
					        )}
					         <Button type="primary" className='right' style={{visibility:'hidden'}}>隐藏</Button>
					   		<Button type="primary" className='right' style={{marginRight:'5%'}} htmlType='submit'>查询</Button>
				        </FormItem>
				        <FormItem className='formitem' >
				        	{getFieldDecorator('address',  {

						    })(
					            <Select
							        combobox={true}
							        placeholder='地址(可模糊搜索)'
							        notFoundContent=""
							        defaultActiveFirstOption={false}
							        showArrow={false}
							        filterOption={false}
							        onChange={this.handleChange.bind(self,'address')}
							        style={{width:'25%',marginRight:10,float:'left'}}
							      >
							        {add_options}
							      </Select>
					        )}
					        {getFieldDecorator('imei',  {
				        		
						    })(
					            <Select
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
							)}
					        {getFieldDecorator('pay_mode',  {
								 initialValue:'0'
							})(
								<Select
									placeholder='付款方式'
									style={{width:'15%',marginRight:10,float:'left'}}
								>
									<Option value={'0'}>全部</Option>
									<Option value={'1'}>微信</Option>
									<Option value={'2'}>支付宝</Option>
									<Option value={'3'}>钱包</Option>
								</Select>
							)}
					        <Button type="primary" className='right' onClick={self.handleReset}>清除</Button>
					        <Button type="primary" className='right' onClick={self.method1} style={{marginRight:'5%'}}>导出</Button>
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
Order = Form.create()(Order);
export default Order;
export { Order };