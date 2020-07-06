"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';

import { browserHistory} from 'react-router';
import { Form, Icon } from '@ant-design/compatible';
import { Alert, Input, Button, Checkbox } from 'antd';
const FormItem = Form.Item;


var Login = require('create-react-class')({
  	getInitialState: function() {
		return { 'errormsg': null };
  	},
  	handleSubmit(e) {
		var self   = this;
		var url    =  window.API_PREFIX+"/auth/login";
		var values = this.props.form.getFieldsValue();
		e.preventDefault();
		var data = {
		  	"phone":values.name,
		  	"pswd":values.password
		};
		var xhr = new XMLHttpRequest();
		xhr.open("POST", url);
		xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ;
		xhr.send(JSON.stringify(data));
		xhr.onreadystatechange = function () {
		  	if (xhr.readyState === XMLHttpRequest.DONE) {
				if (xhr.status === 200) {
				  	var user_data = JSON.parse(xhr.responseText);
				  	localStorage.setItem("role", user_data.data.role);
				  	if(user_data.data.role === 3){
						browserHistory.push(window.URL_PREFIX+'/ad_list');
						return false;
					}else if(user_data.data.role === 2){
						localStorage.setItem("salesman", user_data.data.agent.salesman);
						localStorage.setItem("level", user_data.data.agent.level);
						localStorage.setItem("slevel", user_data.data.agent.slevel);
						browserHistory.push(window.URL_PREFIX+'/');
						return false;
					}else if(user_data.data.role === 1){
						if(user_data.data.god.level === 2){
							browserHistory.push(window.URL_PREFIX+'/admin');
						}else{
							browserHistory.push(window.URL_PREFIX+'/level1');
						}
						return false;
					}else{
						if(user_data.data.role === 0){
							browserHistory.push(window.URL_PREFIX+'/error');
							return false;
						}
					}
				} else {
					var msg = null;
					try{
						msg = JSON.parse(xhr.responseText)["msg"];
					}catch(e){
						msg = "unknow";
					}
					  self.setState({'errormsg': msg});
				}
		  	}
		};
  	},
  	render: function() {
		const { getFieldDecorator } = this.props.form;
		var errormsg = null;
		if ( this.state.errormsg ) {
		  	errormsg = <Alert style={{padding:0}} message={this.state.errormsg} type="error" />;
		}
		return (
		  	<div className='login_all'>
				<div className="login_wrap">

				  	<Form onSubmit={this.handleSubmit} className="login-form">
						<h2>管理后台</h2>
						<FormItem>
							{getFieldDecorator('name',{
								validateTrigger:'onBlur',
								rules:[{pattern:/^admin|1[345789][0-9]{9}$/,message:'请输入正确的手机号'}]
							})(
								<Input className='login_input' placeholder="请输入手机号" />
							)}
						</FormItem>
						<FormItem>
							{getFieldDecorator('password')(
								<Input className='login_input' type="password" placeholder="请输入密码" />
							)}
						</FormItem>
						{errormsg}
						<Button type="primary" htmlType="submit" className="login_button">
						  	登录
						</Button>
				  	</Form>
				</div>
		  	</div>
		);
  	}
});
Login = Form.create()(Login);
export default Login;
export {Login};
