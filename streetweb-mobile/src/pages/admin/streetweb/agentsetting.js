"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import { Form, Icon } from '@ant-design/compatible';
import {  Button, Menu,  Modal,Input, message} from 'antd';
import {MyLayout}     from '../common/layout.js';
const FormItem = Form.Item;
var AgentSetting = require('create-react-class')({
  getInitialState: function() {
    return{
      min_withdraw:2,
      l1:0.05,
      l2:0.10,
      l3:0.15,
      withdraw_fee:0.006,

    }
       
  },
  componentWillMount:function(){
    this.get_msg();
  },
  componentDidMount:function(){
   
  },
  get_msg:function(){
        let url = window.API_PREFIX+'/agent/cur';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body); 
                self.setState({id:res.body.data.id});
                self.getData(res.body.data.id);
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
            values.min_withdraw = values.min_withdraw*100;
            let url = window.API_PREFIX+"/agent/setting/update";
            var callback = function(err,res){
              if(err){
                  message.error(err.msg);
              }else{
                  console.log(res.body);
                  message.success('修改成功！');
              }
            };
            let data = {target_agent_id:self.state.id,update:values}
            var xhr  = new XMLHttpRequest();
            xhr.open("PATCH", url);
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
          }
      })
  },
  getData:function(id){
    var self = this;
    var url = window.API_PREFIX+"/agent/setting/fetch";
    const {  setFieldsValue } = this.props.form;
    var callback = function(err,res){
      if(err){

      }else{
          console.log(res.body);
          res.body.data.min_withdraw = res.body.data.min_withdraw/100; 
          setFieldsValue(res.body.data);
      }
    };
    var xhr  = new XMLHttpRequest();
    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
    xhr.send(JSON.stringify({target_agent_id:id}));
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
  handleConfirmPassword :function (rule, value, callback) {
      if(value<2){
        callback('请输入大于2的数值')
      }


        // Note: 必须总是返回一个 callback，否则 validateFieldsAndScroll 无法响应
      callback()
 },
  render: function (){
    let self = this;
    let btn = null;
    if(self.state.level===4){
      btn = <Button  htmlType='submit'>修改</Button>
    }
    const { getFieldDecorator, getFieldValue } = this.props.form;
    return (
      <MyLayout level={(l)=>{this.setState({level:l})}}>
        <Form onSubmit={this.handleSubmit} className='agentsetting' >
          <FormItem label='最小提现金额' extra='最小提现金额为2元'>
            {getFieldDecorator('min_withdraw', {
              //initialValue:self.state.min_withdraw
              rules: [{
                required: true, message: '请填写完毕后提交',
              },{
                  validator: this.handleConfirmPassword
            }]
            })(
              <Input type='number' placeholder="请输入整数" />
            )}
          </FormItem>
         
          <FormItem label='提现手续费' extra='微信平台收取0.6%'>
            {getFieldDecorator('withdraw_fee', {
              //initialValue:self.state.withdraw_fee
              rules: [{
                required: true, message: '请填写完毕后提交',
              }]
            })(
              <Input type='number' placeholder="" />
            )}
          </FormItem>

          {btn}

        </Form>
       
      </MyLayout>
    );
  }
});
AgentSetting = Form.create()(AgentSetting);

export default AgentSetting;
export { AgentSetting };