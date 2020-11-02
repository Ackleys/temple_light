"use strict";;
import React from 'react';
import ReactDOM from 'react-dom';
import { Link, withRouter } from 'react-router-dom';
import { Icon as LegacyIcon } from '@ant-design/compatible';
import { DownOutlined, LockOutlined, UserOutlined } from '@ant-design/icons';

import {
	Layout,
	Button,
	Menu,
	Breadcrumb,
	Dropdown,
	Modal,
	Modalm,
	Alert,
	Input,
	message,
	Avatar,
	Space,
} from 'antd';
const { Header, Content, Footer, Sider } = Layout;
//const SubMenu = Menu.SubMenu;
const { SubMenu } = Menu;

import './style.less'

const MyLayout = withRouter(require('create-react-class')({
	getInitialState: function () {
		return {
			//"meg_num":0,
			"simcard": "",
			"liuliang": "0.000",
			yuer: '',
			"role": localStorage.getItem("role") - 0,
			passwdVisible: false,
			loading: false,
			oldpasswd: '',
			newpasswd1: '',
			newpasswd2: '',
			errormsg: '',
			collapsed: false,
			name: '',
			level: localStorage.getItem("level") - 0,
			slevel: localStorage.getItem("slevel") - 0,
			join: { ali: 0, wechat: 0 },//是否可对接，0为不可,1为可以
			joined: { ali: 0, wechat: 0 },//是否已对接，0为未对接，1为已对接
			expandable: 0,
			salesman: localStorage.getItem("salesman") - 0,
			logo: '',
		};
	},
	getDefaultProps: function () {
		return {
			breadcrumb_items: ['首页', '应用列表', '某应用', '卡信息']
		};
	},
	componentWillMount: function () {
		let self = this;
		this.get_msg();
		if (localStorage.getItem("role")) {
			if (localStorage.getItem("role") - 0 === 3) {
				//his.props.history.push("/ad_list");
				//return;
			}
		} else {
			this.props.history.push("/login");
			return;
		}
	},
	get_msg: function () {
		let url = '/admin/auth/cur';
		let self = this;
		var callback = function (err, res) {
			if (err) {
				if (err.err.code === 1003) {
					self.props.history.push("/login");
				}
			} else {
				console.log(res.body);
				localStorage.setItem("role", res.body.data.role);
				let type = { 1: 'god', 2: 'agent', 3: 'advertiser' }[res.body.data.role];
				let data = res.body.data[type];
				//$('title').html(res.body.data.common.title);
				document.title = res.body.data.common.title;
				if (res.body.data.role === 2) {
					localStorage.setItem("salesman", data.salesman);
					localStorage.setItem("level", data.level);
					localStorage.setItem("slevel", data.slevel);
				}
				sessionStorage.setItem('name', data.name);
				self.setState({
					name: data.name,
					level: data.level,
					join: data.joinup,
					joined: data.joinuped,
					expandable: data.expandable,
					slevel: data.slevel,
					salesman: data.salesman,
					role: res.body.data.role,
					logo: res.body.data.common.logo,
				});
				if (typeof self.props.level === 'function') {
					self.props.level(data.level);
				}
				if (typeof self.props.slevel === 'function') {
					self.props.slevel(data.slevel);
				}
				if (typeof self.props.id === 'function') {
					self.props.id(data.id);
				}
				if (typeof self.props.data === 'function') {
					self.props.data(data);
				}
			}
		};
		var xhr = new XMLHttpRequest();
		xhr.open("GET", url);
		xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8");
		xhr.send(null);
		xhr.onreadystatechange = function () {
			if (xhr.readyState === XMLHttpRequest.DONE) {
				if (xhr.status === 200) {
					callback(null, { body: JSON.parse(xhr.responseText) });
				} else {
					callback({ err: JSON.parse(xhr.responseText) }, null);
				}
			}
		};
	},
	handleLogout: function () {
		var self = this;
		var url = "/admin/auth/logout";
		var xhr = new XMLHttpRequest();
		xhr.open("GET", url);
		xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8");
		xhr.send(null);
		xhr.onreadystatechange = function () {
			if (xhr.readyState === XMLHttpRequest.DONE) {
				if (xhr.status === 200) {
					localStorage.clear();
					self.props.history.push("/login");
				} else {
					localStorage.clear();
					self.props.history.push("/login");
					//alert("登出失败！");
				}
			}
		};
	},
	showChangePasswd: function () {
		this.setState({ "passwdVisible": true });
	},
	mk_navs: function () {
		var self = this;
		let navs = [
			{ "title": "首页", "icon": "home", "to": "/" },
			{
				"title": "收益进账", "icon": "calendar", "children": [
					{ 'title': '订单查询', 'to': '/order' },
					{ 'title': '营业额查询', 'to': '/turnover' },
					{ 'title': '线上收益', 'to': '/online' },
					{ 'title': '提现', 'to': '/withdraw' }
				]
			},
			{
				title: '寺庙管理',
				icon: 'bank',
				to: '/temple',
			},
			{
				title: '设备管理',
				icon: 'setting',
				to: '/device',
			},
			{
				"title": "设备类型", "icon": "bars", "children": [
					{ 'title': '倒计时类型', 'to': '/chair' },
					{ 'title': '投币器类型', 'to': '/doll' },
					{ 'title': '串口类型', 'to': '/uart' },
					{ 'title': '会员套餐', 'to': '/member' },
				]
			},
			{
				"title": "代理设置", "icon": "bank", "children": [
					{ 'title': '代理商', 'to': '/agent' },
					{ 'title': '设备分组', 'to': '/group' },
				]
			},
			{
				"title": "分销分成", "icon": "usergroup-add", "children": [
					{ 'title': '业务员列表', 'to': '/salesman' },
					{ 'title': '我的设备', 'to': '/myequipments' },
					{ 'title': '设备分销', 'to': '/distribution' },
				]
			},
			{
				"title": "电子传单", "icon": "file-add", "children": [
					{ 'title': '广告商管理', 'to': '/advertiser' },
					{ 'title': '传单分发', 'to': '/ad_device' },
				]
			},
			{
				"title": "高级功能", "icon": "plus-square-o", "children": [
					{ "title": "设备调试", "icon": "user", "to": "/test" },
					{ "title": "广告投放", "icon": "shop", "to": "/player" },
					{ title: '开放api', icon: 'folder-add', to: '/api' },
					{ "title": "公众号对接", "icon": "smile-o", "to": "/wechat" },
					{ "title": "支付宝对接", "icon": "aliwangwang-o", "to": "/alipay" }]
			},
		];
		if (localStorage.getItem("role") - 0 === 1) {
			if (self.state.level === 2) {
				navs = [{ 'title': '创建管理员', 'to': '/admin' },
				{ 'title': '设备管理', 'to': '/admin_dlist' },
				{ 'title': '设备回收', 'to': '/device_recyle' }
				];
			} else {
				navs = [{ 'title': '创建总代理', 'to': '/agent' },
				{ 'title': '修改信息', 'to': '/admin_update' },
				{ 'title': '设备回收', 'to': '/device_recyle' }
				];
			}
		} else if (localStorage.getItem("role") - 0 === 2) {
			if (self.state.salesman) {
				navs = [
					{ "title": "首页", "icon": "home", "to": "/" },
					{
						"title": "收益进账", "icon": "calendar", "children": [
							{ 'title': '订单查询', 'to': '/order' },
							{ 'title': '营业额查询', 'to': '/turnover' },
							{ 'title': '线上收益', 'to': '/online' },
							{ 'title': '提现', 'to': '/withdraw' }
						]
					},
					{
						"title": "分销分成", "icon": "usergroup-add", "children": [
							{ 'title': '业务员列表', 'to': '/salesman' },
							{ 'title': '我的设备', 'to': '/myequipments' },
							{ 'title': '启动记录', 'to': '/start' },
							{ 'title': '设备分销', 'to': '/distribution' },
						]
					}
				];
				if (localStorage.getItem("slevel") - 0 === 1) {
					if (!self.state.expandable) {
						navs[2].children.pop();
					}
				} else if (localStorage.getItem("slevel") - 0 === 2) {
					if (!self.state.expandable) {
						navs[2].children.pop();
					}
				} else if (localStorage.getItem("slevel") - 0 === 3) {
					navs[2].children.pop();
					navs[2].children.shift();
				}
			} else {
				if (localStorage.getItem("level") - 0 === 4) {
					if (!self.state.join.ali && !self.state.join.wechat) {
						navs[navs.length - 1].children.pop();
						navs[navs.length - 1].children.pop();
					} else if (self.state.join.ali && !self.state.join.wechat) {
						navs[navs.length - 1].children.splice(navs[navs.length - 1].children.length - 2, 1);
						if (self.state.joined.ali) {
							navs[navs.length - 1].children.pop();
						}
					} else if (!self.state.join.ali && self.state.join.wechat) {
						navs[navs.length - 1].children.pop();
					} else {

					}
				} else if (localStorage.getItem("level") - 0 === 1) {
					navs[navs.length - 1].children.pop();
					navs[navs.length - 1].children.pop();
					navs[navs.length - 1].children.pop();
					navs[2].children.shift();
					navs[4].children.pop();
					if (self.state.expandable) {
						navs.splice(4, 1);
					} else {
						navs.splice(4, 2);
					}
				} else {
					if (self.state.expandable) {

					} else {
						navs.splice(4, 2);
					}
					navs[navs.length - 1].children.pop();
					navs[navs.length - 1].children.pop();
					navs[navs.length - 1].children.pop();
					navs[2].children.shift();
				}
			}
		} else if (localStorage.getItem("role") - 0 === 3) {
			navs = [{ 'title': '传单列表', 'to': '/ad_list' },
			{ 'title': '传单验证', 'to': '/coupon_receipt' }
			];
		}
		return navs;
	},
	user_navs: function () {
		var self = this;
		let user_navs = [
			{ "title": "修改登录密码", "icon": "unlock", "onclick": self.showChangePasswd },
			{ "title": "平台信息及设置", "icon": "user", "to": '/usermsg' },
			{ "title": "退出", "icon": "logout", "onclick": self.handleLogout },

		]
		if (localStorage.getItem("role") - 0 === 1) {
			user_navs = [
				{ "title": "修改登录密码", "icon": "unlock", "onclick": self.showChangePasswd },
				{ "title": "退出", "icon": "logout", "onclick": self.handleLogout },

			]
		}

		return user_navs;
	},
	handleOk() {
		if (this.state.newpasswd1 != this.state.newpasswd2) {
			this.setState({ errormsg: '两次密码输入不一致' });
			return
		} else if (this.state.newpasswd2.length < 6) {
			this.setState({ errormsg: '密码长度不得小于6位' });
			return
		} else {
			this.setState({ errormsg: '' });
		}
		this.setState({ loading: true });

		// 发送请求修改密码
		var self = this;
		var url = "/admin/auth/change_pswd";
		var data = {
			"old_pswd": this.state.oldpasswd,
			"new_pswd": this.state.newpasswd2
		};

		var xhr = new XMLHttpRequest();
		xhr.open("PATCH", url, true);
		xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8");
		xhr.send(JSON.stringify(data));
		xhr.onreadystatechange = function () {
			if (xhr.readyState === XMLHttpRequest.DONE) {
				if (xhr.status === 200) {
					self.setState({ loading: false, 'errormsg': '', passwdVisible: false });
					message.info('修改成功');
				} else {
					//console.error(xhr.responseText);
					var msg = null;
					try {
						msg = JSON.parse(xhr.responseText).msg;
					} catch (e) {
						msg = "unknow";
					}
					self.setState({ 'errormsg': msg, loading: false });
				}
			}
		};
	},
	handleCancel() {
		this.setState({ passwdVisible: false });
		// console.log(this.state.passwdVisible);
	},
	handleChange(event) {
		// console.log(event.target.value)
		if (event.target.id === 'old') {
			this.setState({ "oldpasswd": event.target.value })
		} else if (event.target.id === 'new1') {
			this.setState({ "newpasswd1": event.target.value })
		} else if (event.target.id === 'new2') {
			this.setState({ "newpasswd2": event.target.value })
		}
	},
	menuClick: function (e) {
		let self = this;
		sessionStorage.setItem("subkey", e.keyPath[0]);
		sessionStorage.setItem("key", e.keyPath[1]);
	},
	render() {
		let self = this;
		let NAVS = self.mk_navs();
		var USER_NAVS = self.user_navs();
		var errormsg = null;
		if (self.state.errormsg) {
			errormsg = <Alert message={this.state.errormsg} type="error" />;
		}
		var key = "";
		var subkey = "";
		if (sessionStorage.getItem("subkey")) {
			key = sessionStorage.getItem("key");
			subkey = sessionStorage.getItem("subkey");
		}
		const menu = (
			<Menu>
				{
					USER_NAVS.map(function (data, q) {
						if (data.to) {
							return (
								<Menu.Item key={q}>
									<LegacyIcon type={data.icon} />
									<Link href="#" to={data.to} style={{ display: "inline-block", marginLeft: "-12px", width: '100%' }}>{data.title}</Link>
								</Menu.Item>
							);
						} else {
							return (
								<Menu.Item key={q}>
									<LegacyIcon type={data.icon} />
									<a href="#" onClick={data.onclick} style={{ display: "inline-block", marginLeft: "-12px", width: '100%' }}>{data.title}</a>
								</Menu.Item>
							);
						}
					})
				}
			</Menu>
		);
		const menu_nav = (
			<Menu>
				{
					NAVS.map(function (data, i) {
						return (
							<Menu.Item key={i}>
								<LegacyIcon type={data.icon} />
								<Link className="nav_list" to={data.to}>
									{data.title}
								</Link>
							</Menu.Item>
						);
					})
				}
			</Menu>
		)
		return (
			<Layout>
				<Sider className='sider'>
					<div className='side-flex'>
						<div className="logo">
							<Avatar src={self.state.logo} size='large' />
							<Dropdown overlay={menu} trigger={['click']}>
								<a className="ant-dropdown-link">
									<Space size={4}>
										<UserOutlined />{self.state.name}
										<DownOutlined />
									</Space>
								</a>
							</Dropdown>
						</div>
						<Menu
							className='menu'
							mode="inline"
							defaultSelectedKeys={[subkey]}
							defaultOpenKeys={[key]}
							onClick={self.menuClick}
							selectedKeys={[this.props.history.location.pathname.match(/^\/\w*/)[0]]}
						>
							{
								NAVS.map(function (data, i) {
									if (data.children) {
										return (
											<SubMenu
												key={i}
												title={<span><LegacyIcon type={data.icon} />{data.title}</span>}
											>
												{data.children.map(function (item, q) {
													return (
														<Menu.Item key={item.to}>
															<LegacyIcon type={item.icon} />
															<Link to={item.to}>{item.title}</Link>
														</Menu.Item>
													);
												})}
											</SubMenu>
										);
									} else {
										return (
											<Menu.Item key={data.to}>
												<LegacyIcon type={data.icon} />
												<Link to={data.to}>
													<span className="nav-text">{data.title}</span>
												</Link>
											</Menu.Item>
										);
									}
								})
							}
						</Menu>
					</div>
				</Sider>
				<Layout className='site-layout'>
					<Content className='content'>
						{self.props.children}
						<Modal
							width="300px"
							title="修改密码"
							visible={this.state.passwdVisible}
							onOk={this.handleOk}
							onCancel={this.handleCancel}
							footer={[
								<Button key="back" type="ghost" size="large" onClick={this.handleCancel}>取消</Button>,
								<Button key="submit" type="primary" size="large" loading={this.state.loading} onClick={this.handleOk}>
									提交
							  </Button>,
							]}
						>
							<Input id="old" addonBefore={<LockOutlined />} type="password" placeholder="旧密码" onChange={this.handleChange} />
							<Input id="new1" addonBefore={<LockOutlined />} type="password" placeholder="新密码" onChange={this.handleChange} />
							<Input id="new2" addonBefore={<LockOutlined />} type="password" placeholder="新密码" onChange={this.handleChange} />
							{errormsg}
						</Modal>
					</Content>
					<Footer style={{ textAlign: 'center' }}>
						Copyright © 堆栈科技
					</Footer>
				</Layout>
			</Layout>
		);
	}
}));
export default MyLayout;
export { MyLayout };
