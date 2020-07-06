"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {  Button, Menu,  Icon, Modal,Input,Form ,message,Table,Alert,Popconfirm} from 'antd';
import {MyLayout}     from '../common/layout.js';
const ButtonGroup = Button.Group;
var Api = require('create-react-class')({
    getInitialState: function() {
        return{
            btn1:'primary',
            btn2:'',
            visible:false,
            loading:false,
            key:0,
            errormsg:null,
            records:[],
            appvisible:false,
            appsecret:''
        }
         
    },
    componentWillMount:function(){
        this.get_msg(5);
    },
    componentDidMount:function(){
        
    },
    get_msg:function(project){
        let url = window.API_PREFIX+'/openapp/getall';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body); 
                res.body.data.forEach((q,i)=>{
                    q.key = i;
                })
                self.setState({records:res.body.data});
            }
        };
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify({project:project}));
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
    myapp:function(){
        let self = this;
        self.setState({btn1:'primary',btn2:''});
        self.get_msg(5);
    },
    allapp:function(){
        let self = this;
        self.setState({btn1:'',btn2:'primary'});
        self.get_msg(0);
    },
    handleOk:function(){
        let self = this;
        if(!self.state.appname){
            self.setState({errormsg:'请填写名称后提交'});
            return false;
        }
        if(!self.state.appdesc){
            self.setState({errormsg:'请填写描述后提交'});
            return false;
        }
        self.setState({loading:true});
        let url = window.API_PREFIX+"/openapp/create";
        var callback = function(err,res){
          if(err){
                message.error(err.err.msg);
          }else{
                console.log(res.body);
                self.setState({errormsg:null,visible:false,loading:false,appname:'',appdesc:''});
                message.success('新建成功！');
                self.get_msg(5);
          }
        };
        let data = {appname:self.state.appname,appdesc:self.state.appdesc}
        var xhr  = new XMLHttpRequest();
        xhr.open("PUT", url);
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
    handleCancel:function(){
        let self = this;
        self.setState({visible:false,loading:false,key:Math.random(),errormsg:null,appname:'',appdesc:''});
    },
    handleChange:function(t,v){
        let self = this;
        console.log(t)
        let value = v.target.value;
        let data = {};
        data[t] = value;
        self.setState(data);
    },
    showsecret:function(appsecret){
        this.setState({appvisible:true,appsecret:appsecret});
    },
    mandateapp:function(id){
        message.loading('授权中,请稍后', 0);
        let url = window.API_PREFIX+'/openapp/copy';
        var self = this;
        var callback = function(err,res){
            if(err){
                message.destroy();
                message.error(err.err.msg);
            }else{
                console.log(res.body); 
                message.destroy();
                message.success('授权成功');
            }
        };
        var xhr  = new XMLHttpRequest();
        xhr.open("PUT", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify({appid:id}));
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
    render: function (){
        let self = this;
        var errormsg = null;
        let btn = <Button type='danger' style={{marginLeft:10}} icon='plus' onClick = {()=>{this.setState({visible:true})}}>新建应用</Button>;
        let columns = [ {
                            title: 'app名称',
                            dataIndex: 'appname',
                        }, {
                            title: 'app描述',
                            dataIndex: 'appdesc',
                        }, {
                            title: 'appkey',
                            dataIndex: 'appkey',
                        }, {
                            title: 'appsecret',
                            dataIndex: 'appsecret',
                            render:(t)=> <Popconfirm title="appsecret是用户唯一凭证密钥，请妥善保存" onConfirm={self.showsecret.bind(self,t)} okText="查看" cancelText="否">
                                            <Button>显示</Button>
                                        </Popconfirm>
                        }];
        if(self.state.btn2){
            columns = [ {
                            title: 'app名称',
                            dataIndex: 'appname',
                        }, {
                            title: 'app描述',
                            dataIndex: 'appdesc',
                        }, {
                            title: 'appkey',
                            dataIndex: 'appkey',
                        }, {
                            title: 'appsecret',
                            dataIndex: 'appsecret',
                            render:(t)=><Popconfirm title="appsecret是用户唯一凭证密钥，请妥善保存" onConfirm={self.showsecret.bind(self,t)} okText="查看" cancelText="否">
                                            <Button>显示</Button>
                                        </Popconfirm>
                        }, {
                            title: '授权到当前平台',
                            dataIndex: 'add',
                            render:(t,re)=><Popconfirm title="授权到当前平台后，可在当前平台调试原平台设备" onConfirm={self.mandateapp.bind(self,re.appid)} okText="是" cancelText="否">
                                            <Button>授权</Button>
                                        </Popconfirm>
                        }];
            btn = null;
        }
        if ( self.state.errormsg ) {
            errormsg = <Alert message={this.state.errormsg} type="error" />;
        }
        return (
            <MyLayout level={(l)=>{this.setState({level:l})}}>
                <div style = {{height:'8vh'}}>
                    <div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
                    <Button type={self.state.btn1} onClick = {self.myapp}>我的应用</Button>
                    <Button type={self.state.btn2} style={{marginLeft:10}} onClick = {self.allapp}>全部应用</Button>
                    {btn}
                    {/*<Search placeholder="请输入imei"
                        style={{ width: 200,marginLeft:20 }}
                        onSearch={self.search} />*/}
                </div>
                <Table
                    columns={columns} 
                    dataSource={self.state.records} 
                />
                <Modal 
                    width="300px"
                    title="新建应用" 
                    visible={this.state.visible}
                    onOk={this.handleOk}
                    key={self.state.key}
                    onCancel={this.handleCancel}
                    footer={[
                      <Button key="back" type="ghost" size="large" onClick={this.handleCancel}>取消</Button>,
                      <Button key="submit" type="primary" size="large" loading={this.state.loading} onClick={this.handleOk}>
                        提交
                      </Button>,
                    ]}
                >
                    <Input addonBefore={'app名称'} type="text" placeholder="请输入新建应用的名称" onBlur={this.handleChange.bind(self,'appname')} />
                    <Input addonBefore={'app描述'} type="text" placeholder="请输入新建应用的描述" onBlur={this.handleChange.bind(self,'appdesc')} />
                    {errormsg}
                </Modal>
                <Modal 
                    width="300px"
                    title="appsecret" 
                    visible={this.state.appvisible}
                    onCancel={()=>{this.setState({appvisible:false})}}
                    footer={[
                      <Button key="back" type="ghost" size="large" onClick={()=>{this.setState({appvisible:false})}}>取消</Button>,
                    ]}
                >
                   <p style={{wordWrap:'break-word'}}>{self.state.appsecret}</p>
                </Modal>
            </MyLayout>
        );
    }
});
export default Api;
export { Api };