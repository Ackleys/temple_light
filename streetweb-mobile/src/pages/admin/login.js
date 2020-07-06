"use strict";

import React, {Component}        from 'react';
import ReactDOM     from 'react-dom';

import { browserHistory} from 'react-router';
//import { Alert, Form, Icon, Input, Button, Checkbox } from 'antd';
import { Icon } from '@ant-design/compatible';
import { Button, InputItem, List, Toast, WingBlank, WhiteSpace, NavBar } from 'antd-mobile';

import { createForm } from 'rc-form';
//const FormItem = Form.Item;


class Login extends Component {
	/*state = {
		type: 'money',
	}*/
	constructor(props) {
		super(props);
		this.state = {
			nameHasError: false,
			nameValue: '',
		};
	}

  	handleSubmit() {
		var self   = this;
		var url    =  window.API_PREFIX+"/auth/login";
		var values = this.props.form.getFieldsValue();

		if(values.name.length === 0 || values.pswd.length === 0) {
			Toast.fail('手机号或密码不能为空');
			return;
		}

		if(!/^admin|1[345789][0-9]{9}$/.test(values.name.replace(/\s+/g,""))) {
			Toast.fail('请输入正确的手机号');
			return;
		}

		var data = {
		  	"phone":values.name.replace(/\s+/g,""),
		  	"pswd":values.pswd
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
					Toast.fail(msg, 1);
				}
		  	}
		};
  	}

  	onNameErrorClick() {
		Toast.info('请输入正确的手机号', 1);
	}

	onNameChange(value) {
		this.setState({
			nameHasError: !/^|admin|1[345789][0-9]{9}$/.test(value.replace(/\s+/g,"")),
			nameValue: value,
		});
	}

  	render() {
	    const { getFieldProps } = this.props.form;
		return (
			<div>
				<NavBar
					mode="dark"
					icon={<Icon type="left" />}
					rightContent={[
						<Icon key="1" type="ellipsis" />,
					]}>登录
				</NavBar>
				<WhiteSpace/>
				<WingBlank>
					<List>
						<InputItem
                            {...getFieldProps('name')}
							type="phone"
							placeholder="请输入手机号">手机号
						</InputItem>
						<InputItem
                            {...getFieldProps('pswd')}
							type="password"
							placeholder="请输入密码">密码
						</InputItem>
					</List>
					<WhiteSpace/>
					<Button
						type="primary"
						onClick={this.handleSubmit.bind(this)}>登录
					</Button>
				</WingBlank>
			</div>
		);
  	}
}
const LoginWrapper = createForm()(Login);
export default LoginWrapper;

//export default createForm()(Login);
