"use strict";

import React        from 'react';
import {browserHistory } from 'react-router';

import {List, WhiteSpace} from 'antd-mobile';

const Item = List.Item;
const Brief = Item.Brief;

const HomeIndex = React.createClass({
	getInitialState: function() {
	  return{
		  data: [],
		  forceFit: true,
		  height: 450,
		  machine:{
			numbers:0,
			onlines:0,
			offlines:0,
			unknown:0
		  },
		  money:{
			today_total_income:0,
			today_online_income:0,
			today_offline_income:0,
			today_wallet_income:0,
			today_offline_coin:0,
			yubi:0
		  },
		  mask:'yy-mm-dd',
	  }
	},
	componentWillMount:function(){
	   	this.equipment_num();
	   	this.get_money();
	},
	componentDidMount:function(){

	},
	get_money:function(){
		let self = this;
		let url = window.API_PREFIX+'/economic/income/today';
		var callback = function(err,res){
			if(err){
				console.log(err);
			}else{
				console.log(res.body);
				let num = 60*60*24*6;
				self.setState({money:res.body.data},function(){self.money_list(1,num)});
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
	equipment_num:function(){
		let self = this;
		let url = window.API_PREFIX+'/device/fetch_num';
		var callback = function(err,res){
			if(err){
				console.log(err);

			}else{
				console.log(res.body);
				self.setState({machine:res.body.data});
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
	money_list:function(type,num){
		let self = this;
		let url = window.API_PREFIX+'/economic/income/daily';
		var callback = function(err,res){
			if(err){
				console.log('未登录');
				console.log(window.URL_PREFIX+'/login');
				browserHistory.push(window.URL_PREFIX+'/login');
			}else{
				console.log(res.body);
				res.body.data.forEach((q,i)=>{
					q.income = q.income/100;
					if(i === (res.body.data.length-1)&&q.date.length === 10){
						q.income = self.state.money.today_online_income/100;
					}
				})
				self.setState({data:res.body.data});
			}
		};
		let data={};
		data.end = parseInt(new Date().getTime()/1000);
		data.start = data.end-num;
		data.freq = type;
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
	times:function(type){
		let self = this;
		if(type === 'week'){
		  this.setState({mask:'yy-mm-dd'},function(){
			let num = 60*60*24*6;
			self.money_list(1,num);
		  });
		}else if(type === 'month'){
		  this.setState({mask:'yy-mm-dd'},function(){
			let num = 60*60*24*29;
			self.money_list(1,num);
		  });
		}else if(type === 'year'){
		  this.setState({mask:'yy-mm'},function(){
			let num = 60*60*24*365;
			self.money_list(2,num);
		  });
		}
	},
	render: function (){
		/*
		let self = this;
		const Chart = createG2(chart => {
			chart.col('date', {
				type:'time',
				alias: '时间',
				mask:self.state.mask,
				range: [0, 1]
			});
			chart.col('income', {
				alias: '金额(￥)'
			});
			chart.line().position('date*income').size(2);
			chart.render();
		});
		*/
		return (
			<div>
				<div className="header">
					<a className="today" style={{width: '100vw'}}>今日收益（元）
						<p className="today_income">{this.state.money.today_wallet_income/100}</p>
					</a>
					<div className="header_bottom flex-box">
						<a> <span>{this.state.money.today_online_income/100}元</span> <p>线上收益</p> </a>
						<a> <span>{this.state.money.today_offline_coin}个</span> <p>线下投币</p> </a>
						<a> <span>{this.state.money.today_total_income/100}元</span> <p>机器营业额</p> </a>
					</div>
				</div>

				<div className="center">
					<div className="center_list flex-box border_t">
						<a className="center_child flex-box border_r"
						   href="/adminpage-mobile/devices_list">
							<span className="center_icon"></span>
							<span className="center_title"><p>设备管理</p><p>共{this.state.machine.numbers}台，在线{this.state.machine.onlines}台</p></span>
						</a>
						<a className="center_child flex-box"
						   href="/adminpage-mobile/products">
							<span className="center_icon"></span>
							<span className="center_title"><p>套餐设置</p><p>扫码支付价格设置</p></span>
						</a>
					</div>
					<div className="center_list flex-box border_t">
						<a className="center_child flex-box border_r"
						   href="/adminpage-mobile/income_list">
							<span className="center_icon"></span>
							<span className="center_title"><p>收益统计</p><p>实时收益流水</p></span>
						</a>
						<a className="center_child flex-box"
						   href="/adminpage-mobile/order_list">
							<span className="center_icon"></span>
							<span className="center_title"><p>订单查询</p><p>查询用户订单</p></span>
						</a>
					</div>
					<div className="center_list flex-box border_t border_b">
						<a className="one_child flex-box border_r"
							href="/adminpage-mobile/distribution">
							<span className="center_icon"></span>
							<span className="center_title"><p>分销分成</p><p>查看业务员及设备</p></span>
						</a>
					</div>
				</div>

				<WhiteSpace/>
				<WhiteSpace/>
				<WhiteSpace/>
				<List>
					<Item
						arrow="horizontal"
						thumb="https://zos.alipayobjects.com/rmsportal/dNuvNrtqUztHCwM.png"
						multipleLine
						onClick={() => {}}>
						账户设置 <Brief>密码修改, 用户信息</Brief>
					</Item>
				</List>

			</div>
		);
	}
});


export default HomeIndex;
export { HomeIndex };
