"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';

import {Link}       from 'react-router';

const Errors = require('create-react-class')({
  getInitialState: function() {
    return{}
       
  },
  componentWillMount:function(){

  },
  componentDidMount:function(){
   
  },
  render: function (){
    
    return (
      <div>
        <h1>您暂时没有权限使用码夫后台管理系统</h1>
        <h1><Link to={window.URL_PREFIX+'/login'}>返回登录页面</Link></h1>
      </div>
    );
  }
});


export default Errors;
export { Errors };
