"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import { Form, Icon } from '@ant-design/compatible';
import {  Button, Menu, Modal,Input,Tabs,Alert,Select} from 'antd';
import {MyLayout}     from '../common/layout.js';
const TabPane = Tabs.TabPane;
const FormItem = Form.Item;
const Option = Select.Option;
var Test = require('create-react-class')({
    getInitialState: function() {
      return{
        tab:'脉冲',
        pluse_required:true,
        relay_required:false,
        errormsg:null,
        alert:'',
        loading_pluse:false,
        loading_relay:false,
      }
         
    },
    componentWillMount:function(){
  
    },
    componentDidMount:function(){
     
    },
    tabsChange:function(key){
        console.log(key);
        if(key === '脉冲'){
            this.setState({tab:key,pluse_required:true,relay_required:false,errormsg:null});
        }else{
            this.setState({tab:key,pluse_required:false,relay_required:true,errormsg:null});
        }
    },
    pulse:function(){

    },
    onSubmit:function(e){
        let self = this;
        e.preventDefault();
        this.props.form.validateFieldsAndScroll((err, values) => {
            if (!err) {
                console.log('Received values of form: ', values); 
                let data={};
                if(self.state.pluse_required){
                    self.setState({loading_pluse:true});
                    if(values.pulse_imei.length<15){
                        data.device_id = values.pulse_imei-0;
                    }else{
                        data.imei = values.pulse_imei;
                    }
                    data.low = values.low-0;
                    data.high = values.high-0;
                    //data.key = values.key1;
                    data.pulse = values.pulse-0;
                    self.post(data,'launch_pulse_signal_deivce');
                }else{
                    self.setState({loading_relay:true});
                    if(values.relay_imei.length<15){
                        data.device_id = values.relay_imei-0;
                    }else{
                        data.imei = values.relay_imei;
                    }
                    data.duration = values.duration-0;
                    data.device_type = values.device_type
                    //data.key = values.key2;
                    self.post(data,'launch_relay_signal_deivce');

                }                  
            }
        })
    },
    post:function(data,urls){
        let url = window.API_PREFIX+'/event/'+urls;
        var self = this;
        self.setState({errormsg:null});
        var callback = function(err,res){
            if(err){
                self.setState({errormsg:err.msg,alert:'error',loading_relay:false,loading_pluse:false});
            }else{
                self.setState({errormsg:'调用成功',alert:'success',loading_relay:false,loading_pluse:false});
            }
        };                
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
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
    validatorNum1:function(r,v,callback){
        if(v>255){
            console.log(v%1);
            callback('请输入小于255的整数');
        }else{
            if(v%1>0){
                callback('请输入整数');
            }else{
                callback();
            }        
        }
    },
    validatorNum2:function(r,v,callback){
        if(v>20){
            console.log(v%1);
            callback('请输入小于20的整数');
        }else{
            if(v%1>0){
                callback('请输入整数');
            }else{
                callback();
            }        
        }
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
        if(self.state.pluse_required){
            tab1 = (
                <Form onSubmit={self.onSubmit} >
                    <FormItem>
                        {getFieldDecorator('pulse_imei', {
                            validateTrigger:'onBlur',
                            rules: [{
                                required: self.state.pluse_required, message: '请填入正确的内容',
                            }]
                        })(
                            <Input type='number' placeholder='请输入imei或自编号' addonBefore='imei或自编号' addonAfter='' />
                        )}
                    </FormItem>
                    <FormItem>
                        {getFieldDecorator('low', {
                                validateTrigger:'onBlur',
                                initialValue:50,
                                rules: [{
                                    required: self.state.pluse_required, message: '请填入正确的内容',
                                },{
                                    validator:self.validatorNum1
                                }]
                            })(
                            <Input type='number' placeholder='请输入大于0小于255的整数' addonBefore='高电平' addonAfter='毫秒（ms）' />
                        )}
                    </FormItem>
                    <FormItem>
                        {getFieldDecorator('high', {
                                validateTrigger:'onBlur',
                                initialValue:50,
                                rules: [{
                                    required: self.state.pluse_required, message: '请填入正确的内容',
                                },{
                                    validator:self.validatorNum1
                                }]
                            })(
                            <Input type='number' placeholder='请输入大于0小于255的整数' addonBefore='低电平' addonAfter='毫秒（ms）' />
                        )}
                    </FormItem>
                    <FormItem>
                        {getFieldDecorator('pulse', {
                                validateTrigger:'onBlur',
                                initialValue:1,
                                rules: [{
                                    required: self.state.pluse_required, message: '请填入正确的内容',
                                },{
                                    validator:self.validatorNum2
                                }]
                            })(
                            <Input type='number' placeholder='请输入大于0小于20的整数' addonBefore='脉冲个数' addonAfter='个' />
                        )}
                    </FormItem>
                   
                    {alert}
                    <Button type='primary' style={{width:'30%'}} htmlType='submit' loading={self.state.loading_pluse}>提交</Button>
                </Form>
                )
        }else if(self.state.relay_required){
            tab2 = (
                <Form onSubmit={self.onSubmit} >
                    <FormItem label='imei或自编号'>
                        {getFieldDecorator('relay_imei', {
                            validateTrigger:'onBlur',
                            rules: [{
                                required: self.state.relay_required, message: '请填入正确的内容',
                            }]
                        })(
                            <Input type='number' placeholder='请输入imei或自编号'/>
                        )}
                    </FormItem>
                    <FormItem label='继电器类型'>
                        {getFieldDecorator('device_type', {
                                rules: [{
                                    required: self.state.relay_required, message: '请选择继电器类型',
                                }]
                            })(
                            <Select placeholder='请选择继电器类型'>
                                <Option value={0} >断电恢复后，不运行</Option>
                                <Option value={2} >断电恢复后，继续运行</Option>
                                <Option value={3} >断电后继续计时，恢复后根据剩余时间决定是否继续运行</Option>
                            </Select>
                        )}
                    </FormItem>
                    <FormItem label='时长'>
                        {getFieldDecorator('duration', {
                                validateTrigger:'onBlur',
                                initialValue:1,
                                rules: [{
                                    required: self.state.relay_required, message: '请填入正确的内容',
                                }]
                            })(
                            <Input type='number' placeholder='请输入大于0的整数' addonBefore='时长' addonAfter='秒' />
                        )}
                    </FormItem>
                    
                    {alert}
                    <Button type='primary' style={{width:'30%'}} htmlType='submit' loading={self.state.loading_relay}>提交</Button>
                </Form>
                )
        }
        return (
            <MyLayout>
                <Tabs style={{width:'50%',margin:'0 auto',marginTop:'20vh'}} defaultActiveKey="脉冲" onChange={self.tabsChange}>
                    <TabPane style={{padding:'0 10%'}} tab="脉冲" key="脉冲">
                        {tab1}
                    </TabPane>
                    <TabPane style={{padding:'0 10%'}} tab="继电器" key="继电器">
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