"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {  Button, Menu,  Icon, Modal,Input,Form,Upload,message } from 'antd';
import {MyLayout}     from '../common/layout.js';
import {browserHistory} from 'react-router';
const FormItem = Form.Item;
var WeChat = require('create-react-class')({
  	getInitialState: function() {
		return{
			fileList0:[],
			fileList1:[],
			fileList2:[],
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
  		let url = window.API_PREFIX+"/agent/joinup_guide/wechat";
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
                
                let url = window.API_PREFIX+"/agent/wechat_config/add";
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
                	if(i === '0'||i === '1'||i === '2'){
                		myForm.append(i,values[i].fileList[0]);
                	}else{
                		myForm.append(i,values[i]);
                	}
                }
                myForm.append('txtname',values['1'].file.name);
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
    customRequest2(info){
		console.log(info.file);
	    this.setState({fileList2:[info.file]});
    },
    txt:function(rule,v,callback,source){
    	let self = this;
    	console.log(source);
    	if(source['1']){
	    	if(source['1'].file.type === "text/plain"){
	    		//self.setState({fileList1:source['1'].fileList.slice(-1)});
	    		callback()
	    	}else{
	    		callback(false);
	    	}
    	}else{
    		callback(false);
    	}
    },
    zip:function(rule,v,callback,source){
    	let self = this;
    	console.log(source);
    	if(source['0']){
	    	if(source['0'].file.name.indexOf('zip')!==-1){
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
	  				<a style={{paddingLeft:35,marginBottom: 25,fontSize:16,display:'block',background:"url('/assets/img/pdf.png') no-repeat left",backgroundSize:'contain'}} href={self.state.pdf_link} target='_blank'>微信公众号对接文档(点击可查看)</a>
		            <FormItem label='公众号名称' extra='公众号名称'>
		              {getFieldDecorator('name', {
		                //initialValue:self.state.min_withdraw
		                rules: [{
		                  required: true, message: '请填写完毕后提交',
		                }]
		              })(
		                <Input placeholder="请输入公众号名称" />
		              )}
		            </FormItem>
		            <FormItem label='公众号名称首字母缩写' extra='例如公众号名称为“码夫支付”，则输入“mfzf”'>
		              {getFieldDecorator('shortname', {
		                //initialValue:self.state.l1
		                rules: [{
		                  required: true, message: '请填写完毕后提交',
		                }]
		              })(
		                <Input placeholder="请输入公众号名称首字母缩写" />
		              )}
		            </FormItem>
		            <FormItem label='appid' extra='微信公众号的appid'>
		              {getFieldDecorator('appid', {
		                //initialValue:self.state.l2
		                rules: [{
		                  required: true, message: '请填写完毕后提交',
		                }]
		              })(
		                <Input placeholder="请输入appid" />
		              )}
		            </FormItem>
		            <FormItem label='appsecret' extra='微信公众号的appsecret'>
		              {getFieldDecorator('appsecret', {
		                //initialValue:self.state.l3
		                rules: [{
		                  required: true, message: '请填写完毕后提交',
		                }]
		              })(
		                <Input placeholder="请输入appsecret" />
		              )}
		            </FormItem>
		            <FormItem label='mchid' extra='公众号对应的商户平台id'>
		              {getFieldDecorator('mchid', {
		                //initialValue:self.state.withdraw_fee
		                rules: [{
		                  required: true, message: '请填写完毕后提交',
		                }]
		              })(
		                <Input placeholder="请输入公众号对应的商户平台id" />
		              )}
		            </FormItem>
  					<FormItem label='mchkey' extra='公众号对应的商户平台密钥'>
		              {getFieldDecorator('mchkey', {
		                //initialValue:self.state.withdraw_fee
		                rules: [{
		                  required: true, message: '请填写完毕后提交',
		                }]
		              })(
		                <Input placeholder="请输入公众号对应的商户平台密钥" />
		              )}
		            </FormItem>
		            <FormItem label='cert.zip文件' extra='cert.zip文件'>
		              {getFieldDecorator('0', {
		                //initialValue:self.state.withdraw_fee
		                  	validateTrigger:'onChange',
		                
			                rules: [{
			                  validator:self.zip, message: '请正确填写后提交',
			                }]
		                
		              })(
		                	<Upload name="file0" fileList={self.state.fileList0} customRequest={self.customRequest0}>
							    <Button>
							      	<Icon type="upload" /> 点击上传zip
							    </Button>
						  	</Upload>
		              )}
		            </FormItem>
		            <FormItem label='txt' extra='txt'>
		              {getFieldDecorator('1', {
		                validateTrigger:'onChange',
		                rules: [{
		                  validator:self.txt, message: '请正确填写后提交',
		                }]
		              })(
		                	<Upload name="file1" fileList={self.state.fileList1} customRequest={self.customRequest1}>
							    <Button>
							      	<Icon type="upload" /> 点击上传txt
							    </Button>
						  	</Upload>
		              )}
		            </FormItem>
		            <FormItem label='公众号二维码图片' extra='img,png'>
		              {getFieldDecorator('2', {
		                validateTrigger:'onChange',
		                rules: [{
		                  required: true, message: '请正确填写后提交',
		                }]
		              })(
		                	<Upload name="file2" fileList={self.state.fileList2} customRequest={self.customRequest2}>
							    <Button>
							      	<Icon type="upload" /> 点击上传图片
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

WeChat = Form.create()(WeChat);
export default WeChat;
export { WeChat };