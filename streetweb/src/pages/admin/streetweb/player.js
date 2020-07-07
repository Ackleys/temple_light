"use strict";;
import React        from 'react';
import ReactDOM     from 'react-dom';
import { DeleteOutlined, SettingOutlined, UploadOutlined } from '@ant-design/icons';
import { Button, Modal, Input, Table, Upload, Alert, Popconfirm, message, Switch } from 'antd';
import {MyLayout}     from '../common/layout.js';

const Player = require('create-react-class')({
    getInitialState: function() {
        return{
            records:[],
            data:{},
            visible:false,
            imgvisible:false,
            key:0,
            fileList:[],
            loading:false,
            errormsg:null,
            src:'',

        }
       
    },
    componentWillMount:function(){
        this.get_ad();
    },
    componentDidMount:function(){
   
    },
    handleOk:function(){
        let self = this;

    },
    handleCancel:function(){
        this.setState({errormsg:null,visible:false,key:Math.random(),data:{},id:null,loading:false,fileList:[]});
    },
    customRequest(info){
        console.log(info.file);
        if(info.file.size/1024>50){
            this.setState({errormsg:'请上传小于50KB的图片'});
        }else{
            if(info.file.type!=='image/jpeg'){
                this.setState({errormsg:'请上传jpg/jpeg格式的图片'});
            }else{
            this.setState({fileList:[info.file],errormsg:null});
            this.state.data['0'] = info.file;
            }
        }
    },
    handleChange:function(t,v){
        this.setState({t:v.target.value})
    },
    get_ad:function(){
        let url = window.API_PREFIX+'/device/ad/fetch';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body.data);
                res.body.data.forEach((q,i)=>{
                    q.key = i;
                })
                self.setState({records:res.body.data});
            }
        };
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify({}));
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
    handleOk:function(){
        var self = this;
        let url,type,data;
        let da = self.state.data;
        if(self.state.id){
            url = window.API_PREFIX+"/device/ad/update";
            type = "PATCH";
            data = {
              ad_id:self.state.id-0,
            }
            for(let i in da){
                data[i] = da[i];
            }
        }else{
            data = da;
            let arr = Object.keys(data);
            if(arr.length<4){
                self.setState({errormsg:"请填写完毕后提交"});
                return false;
            }
            url = window.API_PREFIX+'/device/ad/add';
            type = 'PUT';
        }
        let myForm = new FormData();
        for(let i in data){
            myForm.append(i,data[i]);
        }
        self.setState({loading:true});
        var callback = function(err,res){
            if(err){
                self.setState({errormsg:err.err.msg,loading:false});
            }else{
                console.log(res.body); 
                self.get_ad();
                if(self.state.id){
                    message.success('修改成功');         
                }else{
                    message.success('添加成功');         
                }
                self.setState({errormsg:null,visible:false,key:Math.random(),data:{},id:null,loading:false});
            }
        };
        var xhr  = new XMLHttpRequest();
        xhr.open(type, url); 
        xhr.send(myForm);
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
    delete:function(id){
        console.log(id);
        let url = window.API_PREFIX+'/device/ad/delete';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body);           
                self.get_ad();
                message.success('删除成功');  
            }
        };
        let data = {
            ad_id:id
        }
        var xhr  = new XMLHttpRequest();
        xhr.open("DELETE", url);
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
    SwitchChange:function(id,check){
        var self = this;
        let url,type,data;
        url = window.API_PREFIX+"/device/ad/update";
        type = "PATCH";
        let msg = '';
        data = {
            ad_id:id,
        }
        if(check){
            data.using = 1;
            msg = '投放成功';
        }else{
            data.using = 0;
            msg = '取消成功';
        }
        var callback = function(err,res){
            if(err){
                message.error(err.err.msg);
                self.get_ad();
            }else{
                console.log(res.body); 
                self.get_ad();
                message.success(msg);         
            }
        };
        let myForm = new FormData();
        for(let i in data){
            myForm.append(i,data[i]);
        }
        var xhr  = new XMLHttpRequest();
        xhr.open(type, url); 
        xhr.send(myForm);
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
    inputChange:function(type,e){
        if(type === 'name'){
            this.state.data.name = e.target.value;
            ///this.setState({title:e.target.value});
        }else if(type === 'desc'){
            this.state.data.desc = e.target.value;
            //this.setState({body:e.target.value});
        }
        else if(type === 'url'){
            this.state.data.url = e.target.value;
            //this.setState({price:e.target.value});
        }
        console.log(this.state.data);
    },
    render: function (){
        let self = this;
        let errormsg = null;
        let columns = [ {
                            title: '广告标题',
                            dataIndex: 'name',
                        }, {
                            title: '广告描述',
                            dataIndex: 'desc',
                        }, {
                            title: '广告链接',
                            dataIndex: 'url',
                        }, {
                            title: '广告图片',
                            dataIndex: 'img',
                            render:(t)=><Button onClick={()=>{this.setState({imgvisible:true,src:t})}}>查看图片</Button>
                        }, {
                            title: '投放开关',
                            dataIndex: 'using',
                            render:(t,re) => <Switch defaultChecked={re.using?true:false} onChange={self.SwitchChange.bind(self,re.id)} />
                        }, {
                            title: '编辑',
                            dataIndex: 'edit',
                            render:(text,re) => <a onClick={()=>{this.setState({visible:true,id:re.id})}}><SettingOutlined /></a>,
                        }, {
                            title: '删除',
                            dataIndex: 'delete',
                            render:(text,re) => <Popconfirm title="确定删除该条广告吗" onConfirm={self.delete.bind(self,re.id)} okText="是" cancelText="否">
                                                    <a ><DeleteOutlined /></a>
                                                </Popconfirm>
                        }
                        ];
        if ( self.state.errormsg ) {
            errormsg = <Alert message={this.state.errormsg} type="error" />;
        }
        return (
            <MyLayout>
                <div style = {{height:'8vh'}}>
                    <div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
                    <Button type={self.state.btn1} onClick = {()=>{this.setState({visible:true})}}>添加广告</Button>
                </div>
                <Table
                    columns={columns} 
                    dataSource={self.state.records} 
                />
                <Modal 
                    width="500px"
                    title="添加广告" 
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
                    <div style={{marginTop:10}}><Input addonBefore={'标题'} type="text" placeholder="请输入这条广告的名称" onBlur={this.inputChange.bind(self,'name')} /></div>
                    <div style={{marginTop:10}}><Input addonBefore={'描述'} type="text" placeholder="请输入这条广告的描述" onBlur={this.inputChange.bind(self,'desc')} /></div>
                    <div style={{marginTop:10}}><Input addonBefore={'网址'} type="text" placeholder="点击此广告进入的链接网址" onBlur={this.inputChange.bind(self,'url')} /></div>
                    <div style={{marginTop:10}}>
                        <Upload name="img" fileList={self.state.fileList} customRequest={self.customRequest} onRemove={()=>{this.setState({fileList:[]})}}>
                            <Button>
                                <UploadOutlined /> 请上传500x200尺寸且不得大于50KB的jpg图片
                            </Button>
                        </Upload>
                    </div>
                    {errormsg}
                </Modal>
                <Modal 
                    width="550px"
                    title="图片" 
                    visible={this.state.imgvisible}
                    onCancel={()=>{this.setState({imgvisible:false})}}
                    footer={[
                      <Button key="back" type="ghost" size="large" onClick={()=>{this.setState({imgvisible:false})}}>取消</Button>,
                    ]}
                >
                    <img src={self.state.src} />
                </Modal>
            </MyLayout>
        );
    }
});
export default Player;
export { Player };