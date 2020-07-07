"use strict";

require("./prelude.js");

import React        from 'react';
import ReactDOM     from 'react-dom';

import { Route, BrowserRouter } from 'react-router-dom';
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

import Admin from './pages/admin/index.js';

var init = function (){
	const ReactContainer = document.getElementById('react-container');
	if ( !ReactContainer ) return null;

	ReactDOM.render((
		<BrowserRouter>
			<div>
				<Route path={window.URL_PREFIX+"/login"} component={Admin.Login} />
				<Route onEnter={({params}, replace)=>{
					if(localStorage.getItem('role')==='3'){
						replace(window.URL_PREFIX+'/ad_list');
					}else if(!localStorage.getItem('role')-0){
						replace(window.URL_PREFIX+'/login');
					}
					console.log('runned');
				}} path={window.URL_PREFIX+"/"} exact component={Admin.HomeIndex} />
				<Route path={window.URL_PREFIX+"/turnover"} component={Admin.TurnOver} />
				<Route path={window.URL_PREFIX+"/online"} component={Admin.OnLine} />
				<Route path={window.URL_PREFIX+"/withdraw"} component={Admin.WithDraw} />
				<Route path={window.URL_PREFIX+"/addequipment"} component={Admin.AddEquipment} />
				<Route path={window.URL_PREFIX+"/order"} component={Admin.Order} />
				<Route path={window.URL_PREFIX+"/editequipment"} component={Admin.EditEquipment} />
				<Route path={window.URL_PREFIX+"/equipmentstate"} component={Admin.EquipmentState} />
				<Route path={window.URL_PREFIX+"/group"} component={Admin.Group} />
				<Route path={window.URL_PREFIX+"/doll"} component={Admin.Doll} />
				<Route path={window.URL_PREFIX+"/chair"} component={Admin.Chair} />
				<Route path={window.URL_PREFIX+"/uart"} component={Admin.Uart} />
				<Route path={window.URL_PREFIX+"/player"} component={Admin.Player} />
				<Route path={window.URL_PREFIX+"/agent"} component={Admin.Agent} />
				<Route path={window.URL_PREFIX+"/agentsetting"} component={Admin.AgentSetting} />
				<Route path={window.URL_PREFIX+"/wechat"} component={Admin.WeChat} />
				<Route path={window.URL_PREFIX+"/admin"} component={Admin.AddAdmin} />
				<Route path={window.URL_PREFIX+"/level1"} component={Admin.AddL1} />
				<Route path={window.URL_PREFIX+"/error"} component={Admin.Errors} />
				<Route path={window.URL_PREFIX+"/test"} component={Admin.Test} />
				<Route path={window.URL_PREFIX+"/adminlist"} component={Admin.AdminList} />
				<Route path={window.URL_PREFIX+"/l1list"} component={Admin.L1List} />
				<Route path={window.URL_PREFIX+"/admin_dlist"} component={Admin.Level1Dlist} />
				<Route path={window.URL_PREFIX+"/member"} component={Admin.Member} />
				<Route path={window.URL_PREFIX+"/alipay"} component={Admin.Alipay} />
				<Route path={window.URL_PREFIX+"/device_recyle"} component={Admin.DeviceRecyle} />
				<Route path={window.URL_PREFIX+"/api"} component={Admin.Api} />
				<Route path={window.URL_PREFIX+"/salesman"} component={Admin.SalesMan} />
				<Route path={window.URL_PREFIX+"/myequipments"} component={Admin.MyEquipments} />
				<Route path={window.URL_PREFIX+"/distribution"} component={Admin.Distribution} />
				<Route path={window.URL_PREFIX+"/advertiser"} component={Admin.Advertiser} />
				<Route path={window.URL_PREFIX+"/ad_list"} component={Admin.AdList} />
				<Route path={window.URL_PREFIX+"/ad_device"} component={Admin.AdDevice} />
				<Route path={window.URL_PREFIX+"/coupon_receipt"} component={Admin.CouponReceipt} />
				<Route path={window.URL_PREFIX+"/usermsg"} component={Admin.UserMsg} />
				<Route path={window.URL_PREFIX+"/start"} component={Admin.Start} />
				<Route path={window.URL_PREFIX+"/sim"} component={Admin.SimCard} />
				<Route path={window.URL_PREFIX+"/admin_update"} component={Admin.AdminUpdate} />
				<Route path={window.URL_PREFIX+"/temple"} exact component={Admin.Temple} />
			</div>
    </BrowserRouter>
  ), ReactContainer );
};

// document.ondomcontentready
// document.ondomcontentloaded
window.onload = init;
