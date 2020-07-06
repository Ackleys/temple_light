"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import { Form, Icon } from '@ant-design/compatible';
import {  Button, Menu, Modal,Input,Upload,message } from 'antd';
import {MyLayout}     from '../common/layout.js';
import {browserHistory} from 'react-router';
const FormItem = Form.Item;
var Alipay = require('create-react-class')({
  	getInitialState: function() {
		return{
			fileList0:[],
			fileList1:[],
			pdf_link:'#'
		}
	   
  	},
  	componentWillMount:function(){
  		this.pdf_link();
  	},
 	componentDidMount:function(){
   
  	},
  	pdf_link:function(){
  		let self = this;
  		let url = window.API_PREFIX+"/agent/joinup_guide/ali";
        var callback = function(err,res){
            if(err){
                console.log(err.err.msg);
            }else{
               self.setState({pdf_link:res.body.data.link});
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
  	handleSubmit:function(e){
    	let self = this;
        e.preventDefault();
        this.props.form.validateFieldsAndScroll((err, values) => {
          if (!err) {
                console.log('Received values of form: ', values);
                
                let url = window.API_PREFIX+"/agent/ali_config/add";
                var callback = function(err,res){
                    if(err){
                        message.error(err.err.msg);
                    }else{
                        console.log(res.body);
                        browserHistory.push(window.URL_PREFIX+'/');
                        message.success('添加成功！');
                    }
                };
                let myForm = new FormData();
                for (let i in values){
                	if(i === '0'||i === '1'){
                		myForm.append(i,values[i].fileList[0]);
                	}else{
                		myForm.append(i,values[i]);
                	}
                }
                var xhr  = new XMLHttpRequest();
                xhr.open("POST", url,true);
                //xhr.setRequestHeader("Content-Type", "multipart/form-data") ; 
                xhr.send(myForm);
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
    
    customRequest0(info){
		console.log(info.file);
	    this.setState({fileList0:[info.file]});
    },
    customRequest1(info){
		console.log(info.file);
	    this.setState({fileList1:[info.file]});
    },
    file:function(rule,v,callback,source){
    	let self = this;
    	console.log(source);
    	if(source[rule.field]){
	    	if(source[rule.field].file.name.indexOf('pem')!==-1){
    			//self.setState({fileList0:source['0'].fileList.slice(-1)});
    			callback()

	    	}else{
	    		callback(false);
	    	}
    	}else{
    		callback(false);
    	}
    },

  	render: function (){
		let self = this;
    	const { getFieldDecorator, getFieldValue } = this.props.form;
		return (
	  		<MyLayout>
	   			<Form onSubmit={this.handleSubmit} className='agentsetting' >
	  				<a style={{paddingLeft:35,marginBottom: 25,fontSize:16,display:'block',background:"url('/assets/img/pdf.png') no-repeat left",backgroundSize:'contain'}} href={self.state.pdf_link} target='_blank'>支付宝对接文档(点击可查看)</a>
		            <FormItem label='支付宝开放平台名称' extra='支付宝开放平台名称'>
		              {getFieldDecorator('name', {
		                //initialValue:self.state.min_withdraw
		                rules: [{
		                  required: true, message: '请填写完毕后提交',
		                }]
		              })(
		                <Input placeholder="请输入开放平台名称" />
		              )}
		            </FormItem>
		            <FormItem label='开放平台名称首字母缩写' extra='例如开放平台名称为“码夫云”，则输入“mfy”'>
		              {getFieldDecorator('shortname', {
		                //initialValue:self.state.l1
		                rules: [{
		                  required: true, message: '请填写完毕后提交',
		                }]
		              })(
		                <Input placeholder="请输入开放平台名称首字母缩写" />
		              )}
		            </FormItem>
		            <FormItem label='appid' extra='开放平台的appid'>
		              {getFieldDecorator('appid', {
		                //initialValue:self.state.l2
		                rules: [{
		                  required: true, message: '请填写完毕后提交',
		                }]
		              })(
		                <Input placeholder="请输入appid" />
		              )}
		            </FormItem>
		            <FormItem label='商户的RSA2私钥文件' extra='商户的RSA2私钥文件'>
		              {getFieldDecorator('0', {
		                //initialValue:self.state.withdraw_fee
		                  	validateTrigger:'onChange',
		                
			                rules: [{
			                  validator:self.file, message: '请正确上传后提交',
			                }]
		                
		              })(
		                	<Upload name="file0" fileList={self.state.fileList0} customRequest={self.customRequest0}>
							    <Button>
							      	<Icon type="upload" /> 商户的RSA2私钥文件
							    </Button>
						  	</Upload>
		              )}
		            </FormItem>
		            <FormItem label='支付宝的RSA2公钥文件' extra='支付宝的RSA2公钥文件'>
		              {getFieldDecorator('1', {
		                validateTrigger:'onChange',
		                rules: [{
		                  validator:self.file, message: '请正确上传后提交',
		                }]
		              })(
		                	<Upload name="file1" fileList={self.state.fileList1} customRequest={self.customRequest1}>
							    <Button>
							      	<Icon type="upload" /> 点击上传支付宝的RSA2公钥文件
							    </Button>
						  	</Upload>
		              )}
		            </FormItem>
		            <Button htmlType='submit'>提交</Button>

		        </Form>
	  		</MyLayout>
		);
  	}
});

Alipay = Form.create()(Alipay);
export default Alipay;
export { Alipay };