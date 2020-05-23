"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {  Button, Menu,  Icon,  Table } from 'antd';
import {MyLayout}     from './common/layout.js';
import createG2 from 'g2-react';
import { Stat } from 'g2';
import {browserHistory } from 'react-router';


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
				console.log('未登录')
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
		return (
			<MyLayout>
				<div className='home_head'>
					<span className='span'>设备总数：{this.state.machine.numbers}台</span>
					<span className='span'>在线：{this.state.machine.onlines}台</span>
					<span className='span'>离线：{this.state.machine.offlines}台</span>
					<span className='span'>异常：{this.state.machine.unknown}台</span>
				</div>
				<div className='today'>
					<h1>￥{this.state.money.today_wallet_income/100}</h1>
					<p>今日收益</p>
				</div>
				<div className='money'>
					<p>
						<span>线上收益：￥{this.state.money.today_online_income/100}</span>
						<span>机器营业额：￥{this.state.money.today_total_income/100}</span>
					</p>
					<p>
						<span>投币收益(仅供参考)：￥{this.state.money.today_offline_coin}</span>
						<span>投币个数：{this.state.money.today_offline_coin}</span>
					</p>
				</div>
				<Chart
					data={this.state.data}
					width={0}
					height={this.state.height}
					forceFit={this.state.forceFit} />
				<div>
					<Button onClick = {self.times.bind(self,'week')}>近一周</Button>
					<Button onClick = {self.times.bind(self,'month')}>近30天</Button>
					<Button onClick = {self.times.bind(self,'year')}>近一年</Button>
				</div>
			</MyLayout>
		);
	}
});


export default HomeIndex;
export { HomeIndex };
