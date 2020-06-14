"use strict";

require("./prelude.js");

import React        from 'react';
import ReactDOM     from 'react-dom';

import {
	IndexRoute, Redirect,
	browserHistory, 
	Router, Route, Link 
} from 'react-router';
window.ENV        = require('./environ.json');
window.React      = React;
window.ReactDOM   = ReactDOM;

if ( window.ENV.production ) {
		window.URL_PREFIX = "/adminpage";      // http://dw.airm2m.com
		window.API_PREFIX = '/admin';
		window.QRcode_url = 'http://server.fzstack.com/'
} else { 
		window.QRcode_url = 'http://server.fzstack.com/';
		window.API_PREFIX = "/admin"; // http://dw.airm2m.com
		window.URL_PREFIX = '';
}
var App = React.createClass({
	getInitialState: function () {
		return null;
	},
	componentWillMount: function() {
		
	},
	render: function () {
		var self = this;
		return (
			<div>
				{this.props.children}
			</div>
		);
	}
});

import Admin from './pages/admin/index.js';

var init = function (){
	const ReactContainer = document.getElementById('react-container');
	if ( !ReactContainer ) return null;

	ReactDOM.render((
		<Router history={browserHistory}>
			<Route path={window.URL_PREFIX+"/login"} component={App}>
				<IndexRoute component={Admin.Login} />
			</Route>
			<Route onEnter={({params}, replace)=>{
				if(localStorage.getItem('role')==='3'){
					replace(window.URL_PREFIX+'/ad_list');
				}else if(!localStorage.getItem('role')-0){
					replace(window.URL_PREFIX+'/login');
				}
			}} path={window.URL_PREFIX+"/"} component={App}>
				<IndexRoute component={Admin.HomeIndex} />
			</Route> 
			<Route path={window.URL_PREFIX+"/turnover"} component={App}>
				<IndexRoute component={Admin.TurnOver} />
			</Route>
			<Route path={window.URL_PREFIX+"/online"} component={App}>
				<IndexRoute component={Admin.OnLine} />
			</Route>
			<Route path={window.URL_PREFIX+"/withdraw"} component={App}>
				<IndexRoute component={Admin.WithDraw} />
			</Route>
			<Route path={window.URL_PREFIX+"/addequipment"} component={App}>
				<IndexRoute component={Admin.AddEquipment} />
			</Route>
			<Route path={window.URL_PREFIX+"/order"} component={App}>
				<IndexRoute component={Admin.Order} />
			</Route>
			 <Route path={window.URL_PREFIX+"/editequipment"} component={App}>
				<IndexRoute component={Admin.EditEquipment} />
			</Route>
			<Route path={window.URL_PREFIX+"/equipmentstate"} component={App}>
				<IndexRoute component={Admin.EquipmentState} />
			</Route>
			<Route path={window.URL_PREFIX+"/group"} component={App}>
				<IndexRoute component={Admin.Group} />
			</Route>
			<Route path={window.URL_PREFIX+"/doll"} component={App}>
				<IndexRoute component={Admin.Doll} />
			</Route>
			<Route path={window.URL_PREFIX+"/chair"} component={App}>
				<IndexRoute component={Admin.Chair} />
			</Route>
			<Route path={window.URL_PREFIX+"/uart"} component={App}>
				<IndexRoute component={Admin.Uart} />
			</Route>
			<Route path={window.URL_PREFIX+"/player"} component={App}>
				<IndexRoute component={Admin.Player} />
			</Route>
			<Route path={window.URL_PREFIX+"/agent"} component={App}>
				<IndexRoute component={Admin.Agent} />
			</Route>
			<Route path={window.URL_PREFIX+"/agentsetting"} component={App}>
				<IndexRoute component={Admin.AgentSetting} />
			</Route>
			<Route path={window.URL_PREFIX+"/wechat"} component={App}>
				<IndexRoute component={Admin.WeChat} />
			</Route>
			<Route path={window.URL_PREFIX+"/admin"} component={App}>
				<IndexRoute component={Admin.AddAdmin} />
			</Route>
			<Route path={window.URL_PREFIX+"/level1"} component={App}>
				<IndexRoute component={Admin.AddL1} />
			</Route>
			<Route path={window.URL_PREFIX+"/error"} component={App}>
				<IndexRoute component={Admin.Errors} />
			</Route>
			<Route path={window.URL_PREFIX+"/test"} component={App}>
				<IndexRoute component={Admin.Test} />
			</Route>
			<Route path={window.URL_PREFIX+"/adminlist"} component={App}>
				<IndexRoute component={Admin.AdminList} />
			</Route>
			<Route path={window.URL_PREFIX+"/l1list"} component={App}>
				<IndexRoute component={Admin.L1List} />
			</Route>
			<Route path={window.URL_PREFIX+"/admin_dlist"} component={App}>
				<IndexRoute component={Admin.Level1Dlist} />
			</Route>
			<Route path={window.URL_PREFIX+"/member"} component={App}>
				<IndexRoute component={Admin.Member} />
			</Route>
			<Route path={window.URL_PREFIX+"/alipay"} component={App}>
				<IndexRoute component={Admin.Alipay} />
			</Route>
			<Route path={window.URL_PREFIX+"/device_recyle"} component={App}>
				<IndexRoute component={Admin.DeviceRecyle} />
			</Route>
			<Route path={window.URL_PREFIX+"/api"} component={App}>
				<IndexRoute component={Admin.Api} />
			</Route>
			<Route path={window.URL_PREFIX+"/salesman"} component={App}>
				<IndexRoute component={Admin.SalesMan} />
			</Route>
			<Route path={window.URL_PREFIX+"/myequipments"} component={App}>
				<IndexRoute component={Admin.MyEquipments} />
			</Route>
			<Route path={window.URL_PREFIX+"/distribution"} component={App}>
				<IndexRoute component={Admin.Distribution} />
			</Route>
			<Route path={window.URL_PREFIX+"/advertiser"} component={App}>
				<IndexRoute component={Admin.Advertiser} />
			</Route>
			<Route path={window.URL_PREFIX+"/ad_list"} component={App}>
				<IndexRoute component={Admin.AdList} />
			</Route>
			<Route path={window.URL_PREFIX+"/ad_device"} component={App}>
				<IndexRoute component={Admin.AdDevice} />
			</Route>
			<Route path={window.URL_PREFIX+"/coupon_receipt"} component={App}>
				<IndexRoute component={Admin.CouponReceipt} />
			</Route>
			<Route path={window.URL_PREFIX+"/usermsg"} component={App}>
				<IndexRoute component={Admin.UserMsg} />
			</Route>
			<Route path={window.URL_PREFIX+"/start"} component={App}>
				<IndexRoute component={Admin.Start} />
			</Route>
			<Route path={window.URL_PREFIX+"/sim"} component={App}>
				<IndexRoute component={Admin.SimCard} />
			</Route>
      <Route path={window.URL_PREFIX+"/admin_update"} component={App}>
        <IndexRoute component={Admin.AdminUpdate} />
      </Route>
    </Router>
  ), ReactContainer );
};

// document.ondomcontentready
// document.ondomcontentloaded
window.onload = init;
