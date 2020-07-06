"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import { Form, Icon } from '@ant-design/compatible';
import {  Button, Menu, Modal,Input,Tabs,Alert,Radio} from 'antd';
import {MyLayout}     from '../common/layout.js';
const TabPane = Tabs.TabPane;
const FormItem = Form.Item;
const RadioGroup = Radio.Group;
var Test = require('create-react-class')({
    getInitialState: function() {
        return{
            tab:'基本信息',
            pluse_required:true,
            relay_required:false,
            errormsg:null,
            alert:'',
            name:'',
            address:'',
            phone:'',
            remark:'',
            email:'',
            le   :'',
            expandable:'',
            salesman:0
        }
         
    },
    componentWillMount:function(){
        this.get_msg();
    },
    componentDidMount:function(){
     
    },
    tabsChange:function(key){
        console.log(key);
        let self = this;
        if(key === '代理设置'){
            this.setState({tab:key,pluse_required:true,relay_required:false,errormsg:null},function(){
                const {  setFieldsValue } = self.props.form;
                console.log(self.state.data);
                setFieldsValue(self.state.data);  
            });
        }else if(key === '高级设置'){
            this.getData(this.state.id);
            this.setState({tab:key,pluse_required:false,relay_required:true,errormsg:null});
        }
    },
    onSubmit:function(e){
        let self = this;
        let url,data,type = 'PATCH';
        e.preventDefault();
        this.props.form.validateFieldsAndScroll((err, values) => {
            if (!err) {
                console.log('Received values of form: ', values); 
                let data={};
                if(self.state.pluse_required){
                    self.setState({loading_pluse:true});
                    url= window.API_PREFIX+"/agent/update";
                    data={
                            agent_id:self.state.id-0,
                            update:values
                        } 
                    self.post(data,url,type);
                }else{
                    self.setState({loading_relay:true});
                    values.withdraw_fee = values.withdraw_fee-0;
                    values.min_withdraw = values.min_withdraw*100;
                    url = window.API_PREFIX+"/agent/setting/update";
                    data = {target_agent_id:self.state.id,update:values};
                    self.post(data,url,type);
                }                  
            }
        })
    },
    level:function(n){
        if(n === 4){
            return '总代理';
        } else if(n === 3){
            return '省级代理';
        }else if(n === 2){
            return '市县代理';
        }else if(n === 1){
            return '运营商';
        }
    },
    slevel:function(n){
        if(n === 3){
            return '三级业务员';
        }else if(n === 2){
            return '二级业务员';
        }else if(n === 1){
            return '一级业务员';
        }
    },
    expandable:function(n){
        if(n === 1){
            return '是';
        }else if(n === 0){
            return '否';
        }
    },
    get_msg:function(){
     let url = window.API_PREFIX+'/agent/cur';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body);   
                        
                self.setState({name:res.body.data.name,
                            address:res.body.data.address,
                            phone:res.body.data.phone,
                            remark:res.body.data.remark,
                            email:res.body.data.email,
                            salesman:res.body.data.salesman,
                            le:res.body.data.salesman?self.slevel(res.body.data.slevel):self.level(res.body.data.level),
                            expandable:self.expandable(res.body.data.expandable),
                            withdrawable:self.expandable(res.body.data.withdrawable),
                            trans_url:self.expandable(res.body.data.trans_url),
                            id:res.body.data.id
                          },function(){
                            if(res.body.data.level){

                            }
                          });
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
    post:function(data,urls,type){
        var self = this;
        self.setState({errormsg:null});
        var callback = function(err,res){
            if(err){
                self.setState({errormsg:err.msg,alert:'error',loading_relay:false,loading_pluse:false});
            }else{
                self.setState({errormsg:'提交成功',alert:'success',loading_relay:false,loading_pluse:false});
            }
        };                
        var xhr  = new XMLHttpRequest();
        xhr.open(type, urls);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify(data));
        xhr.onreadystatechange = function() {
            if(xhr.readyState === XMLHttpRequest.DONE) {
                if(xhr.status === 200) {
                    callback(null,{body:JSON.parse(xhr.responseText)});
                } else {
                    callback(JSON.parse(xhr.responseText),null);
                }
            }
        };
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
     handleCheckHttp :function (rule, value, callback) {
        if( value.toLowerCase().indexOf('http://') === 0 ){
            callback()
        }
        if( value.toLowerCase().indexOf('https://') === 0 ){
            callback()
        }
            // Note: 必须总是返回一个 callback，否则 validateFieldsAndScroll 无法响应
        callback('url 输入有误')
     },
    render: function (){
        let self = this;
        const { getFieldDecorator, getFieldValue } = this.props.form;
        let alert = null;
        if(self.state.errormsg){
            alert = <Alert message={self.state.errormsg} type={self.state.alert} />
        }
        let tab1 = null;
        let tab2 = null;
        let btn1 = self.state.salesman?null:<Button type='primary' style={{width:'30%'}} htmlType='submit' loading={self.state.loading_pluse}>提交</Button>;
        let btn2 = self.state.le !== '总代理'?null:<Button type='primary' style={{width:'30%'}} htmlType='submit' loading={self.state.loading_relay}>提交</Button>;
        if(self.state.pluse_required){
            tab1 = (
                <Form onSubmit={self.onSubmit} >
                    <FormItem label={'是否可发展下线'}>
                        {getFieldDecorator('expandable', {
                            
                        })(
                            <RadioGroup>
                                <Radio value={1}>可以</Radio>
                                <Radio value={0}>不可以</Radio>
                            </RadioGroup>
                        )}
                    </FormItem>
                    <FormItem label={'会员充值是否立即到账'}>
                        {getFieldDecorator('withdrawable', {
                            
                        })(
                            <RadioGroup>
                                <Radio value={1}>可以</Radio>
                                <Radio value={0}>不可以</Radio>  
                            </RadioGroup>
                        )}
                    </FormItem>
                   
                    {alert}
                    {btn1}
                </Form>
                )
        }else if(self.state.relay_required){
            tab2 = (
                <Form onSubmit={self.onSubmit} >
                    <FormItem label='最小提现金额' extra='最小提现金额为2元'>
                        {getFieldDecorator('min_withdraw', {
                           rules: [{
                                validator: this.handleConfirmPassword
                            }]
                        })(
                            <Input type='number' placeholder="请输入整数" />
                        )}
                    </FormItem>
                    <FormItem label='提现手续费' extra='微信平台收取0.6%'>
                        {getFieldDecorator('withdraw_fee', {
                            
                        })(
                            <Input type='text' placeholder="" />
                        )}
                    </FormItem>
                    <FormItem label={'是否使用会员套餐'}>
                        {getFieldDecorator('wallet_pay_enable', {
                            
                        })(
                            <RadioGroup>
                                <Radio value={1}>是</Radio>
                                <Radio value={0}>否</Radio>  
                            </RadioGroup>
                        )}
                    </FormItem>
                    <FormItem label='透传回调地址' extra='请填写以http://或者https://开头的url'>
                        {getFieldDecorator('trans_url', {
                            rules: [{
                                validator: this.handleCheckHttp
                            }]
                        })(
                            <Input type='string' placeholder="" />
                        )}
                    </FormItem>
                    {alert}
                    {btn2}
                </Form>
                )
        }
        return (
            <MyLayout data={(d)=>{self.setState({data:d})}}>
                <Tabs style={{width:'50%',margin:'0 auto',marginTop:'20vh'}} defaultActiveKey="基本信息" onChange={self.tabsChange}>
                    <TabPane style={{padding:'0 10%'}} tab="基本信息" key="基本信息">
                        <table className='cardtable'>
                            <tbody>
                                <tr><td>姓名：</td><td>{self.state.name}</td></tr>
                                <tr><td>手机号：</td><td>{self.state.phone}</td></tr>
                                <tr><td>地址：</td><td>{self.state.address}</td></tr>
                                <tr><td>邮箱：</td><td>{self.state.email}</td></tr>
                                <tr><td>等级：</td><td>{self.state.le}</td></tr>
                                <tr><td>备注：</td><td>{self.state.remark}</td></tr>
                            </tbody>
                        </table>
                    </TabPane>
                    <TabPane style={{padding:'0 10%'}} tab="代理设置" key="代理设置">
                        {tab1}
                    </TabPane>
                    <TabPane style={{padding:'0 10%'}} tab="高级设置" key="高级设置">
                        {tab2}
                    </TabPane>   
                </Tabs>
            </MyLayout>
        );
    }
});

Test = Form.create()(Test);
export default Test;
export { Test };