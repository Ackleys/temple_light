"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {  Button, Icon, Modal,Input,Table,Upload,Alert,Popconfirm,message,Switch} from 'antd';
import {MyLayout}     from '../common/layout.js';
import QRCode       from 'qrcode.react';
const List = require('create-react-class')({
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
            qr_visible:false,
            url:'',
            pay_id:'',
            timer:null,
            timer_l:null,
            ewm_alert:'',
            "pagination": {
                "showSizeChanger":true,
                "current"        : 1,
                "pageSize"       : 10,
                "pageSizeOptions": ['10', '25', '50', '100']
            },

        }
       
    },
    componentWillMount:function(){
        this.setState({ad_id:this.props.id});
        this.get_ad(1,10);
    },
    componentDidMount:function(){
        clearInterval(this.state.timer);
        clearInterval(this.state.timer_l);
    },
    componentWillUnmount:function(){
        clearInterval(this.state.timer);
        clearInterval(this.state.timer_l);
    },
    handleCancel:function(){
        this.setState({errormsg:null,visible:false,key:Math.random(),data:{},id:null,loading:false,fileList:[]});
    },
    customRequest(info){
        console.log(info.file);
        if(info.file.type!=='image/jpeg'){
            this.setState({errormsg:'请上传jpg/jpeg格式的图片'});
        }else{
        this.setState({fileList:[info.file],errormsg:null});
        this.state.data['0'] = info.file;
        }
        
    },
    handleChange:function(t,v){
        this.setState({t:v.target.value})
    },
    get_ad:function(page,psize){
        let url = window.API_PREFIX+'/advertiser/coupon/fetch?page='+page+'&psize='+psize;
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body.data);
                res.body.data.coupons.forEach((q,i)=>{
                    q.key = i;
                    q.time = self.getdate(new Date(q.time*1000));
                })
                const pager = self.state.pagination;
                pager.total =  res.body.data.count;
                self.setState({records:res.body.data.coupons,pagination:pager});
            }
        };
        let data={};
        if(self.props.id){
            data = {advertiser_id:self.props.id};
        }else if(self.props.device_id){
            data = {device_id:self.props.device_id};
        }
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
            data.advertiser_id = this.props.id;
            let arr = Object.keys(data);
            if(arr.length<6){
                self.setState({errormsg:"请填写完毕后提交"});
                return false;
            }
            url = window.API_PREFIX+'/advertiser/coupon/add';
            type = 'POST';
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
                const pager = self.state.pagination;
                self.get_ad(pager.current,pager.pageSize);
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
    show_ewm:function(){
        let self = this;
        this.state.timer = setInterval(function(){
            self.setState({ewm_alert:'二维码已过期，请返回重新获取'},function(){
                clearInterval(self.state.timer_l);
                clearInterval(self.state.timer);
            });
        },120000);
        this.state.timer_l = setInterval(function(){
            self.pay();
        },1000);
        this.setState({qr_visible:true}); 
    },
    qr_pay:function(id){
        let self = this;
        let url = window.API_PREFIX+'/advertiser/coupon/pay';
        var callback = function(err,res){
            if(err){
                console.log(err);
            }else{
                console.log(res.body);
                self.setState({url:res.body.data.pay_request.qrcode,pay_id:res.body.data.id},self.show_ewm);
            }
        };
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify({coupon_id:id}));
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
    pay:function(){
        let self = this;
        let url = window.API_PREFIX+'/advertiser/pay/query';
        var callback = function(err,res){
            if(err){
                console.log(err);
            }else{
                console.log(res.body);
                if(res.body.data.status === 1){
                    self.setState({ewm_alert:'付款成功',pay_id:'',qr_visible:false});
                    message.success('付款成功');
                    clearInterval(self.state.timer_l);
                    const pager = self.state.pagination;
                self.get_ad(pager.current,pager.pageSize);
                }
            }
        };
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify({pay_id:self.state.pay_id}));
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
    qrhandleCancel:function(){
        let self = this;
        clearInterval(self.state.timer);
        clearInterval(self.state.timer_l);
        this.setState({qr_visible:false,ewm_alert:'',pay_id:''});
    },
    delete:function(id){
        console.log(id);
        let url = window.API_PREFIX+'/device/ad/delete';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body);
                const pager = self.state.pagination;
                self.get_ad(pager.current,pager.pageSize);           
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
    onTableChange:function(pagination, filters, sorter) {
        const pager = this.state.pagination;
        pager.current = pagination.current;
        pager.pageSize = pagination.pageSize;
        this.setState({
            pagination: pager,
        });
        this.get_ad(pager.current,pager.pageSize);
    },
    getdate:function (now) {
        let y = now.getFullYear();
        let m = now.getMonth() + 1;
        let d = now.getDate();
        return y + "-" + (m < 10 ? "0" + m : m) + "-" + (d < 10 ? "0" + d : d) + " " + now.toTimeString().substr(0, 8);
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
        if(type === 'title'){
            this.state.data.title = e.target.value;
            ///this.setState({title:e.target.value});
        }else if(type === 'desc'){
            this.state.data.desc = e.target.value;
            //this.setState({body:e.target.value});
        }else if(type === 'price'){
            this.state.data.price = e.target.value*100;
            //this.setState({price:e.target.value});
        }else if(type === 'total'){
            this.state.data.total = e.target.value;
            //this.setState({price:e.target.value});
        }
        console.log(this.state.data);
    },
    add_btn:function(){
        let self = this;
        if(self.props.device_id){
            return null;
        }else{
            return <Button type={self.state.btn1} onClick = {()=>{this.setState({visible:true})}}>添加广告</Button>
        }
    },
    render: function (){
        let self = this;
        let errormsg = null;
        let btn = null;
        let columns = [ {
                            title: '广告标题',
                            dataIndex: 'title',
                        }, {
                            title: '广告描述',
                            dataIndex: 'desc',
                        }, {
                            title: '广告图片',
                            dataIndex: 'img',
                            render:(t)=><Button onClick={()=>{this.setState({imgvisible:true,src:t})}}>查看图片</Button>
                        }, {
                            title: '总数',
                            dataIndex: 'total',
                        }, {
                            title: '剩余数量',
                            dataIndex: 'left',
                        }, {
                            title: '创建时间',
                            dataIndex: 'time',
                        },/*, {
                            title: '投放开关',
                            dataIndex: 'using',
                            render:(t,re) => <Switch defaultChecked={re.using?true:false} onChange={self.SwitchChange.bind(self,re.id)} />
                        }, {
                            title: '编辑',
                            dataIndex: 'edit',
                            render:(text,re) => <a onClick={()=>{this.setState({visible:true,id:re.id})}}><Icon type="setting" /></a>,
                        }, {
                            title: '删除',
                            dataIndex: 'delete',
                            render:(text,re) => <Popconfirm title="确定删除该条广告吗" onConfirm={self.delete.bind(self,re.id)} okText="是" cancelText="否">
                                                    <a ><Icon type="delete" /></a>
                                                </Popconfirm>
                        }*/
                        ];
        if(localStorage.getItem('role')-0 ===3){
            columns.push({
                            title:'付款',
                            dataIndex:'pay_status',
                            render:(t,re)=>{
                                let w = '';
                                let disabled='';
                                if(t === 1){
                                    w = '已支付';
                                    disabled = true;
                                }else{
                                    w = '付款';
                                    disabled = false;
                                }
                                return <Button type='primary' disabled={disabled} onClick={()=>{self.qr_pay(re.id)}}>{w}</Button>
                            }
                        })

        }else{
            btn = <div style = {{height:'8vh'}}>
                    <div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
                    {self.add_btn()}
                    <Button style={{marginLeft:10}} type='primary' onClick = {()=>{if(typeof self.props.show === 'function'){self.props.show(false)}}}>返回</Button>
                </div>
        }
        if ( self.state.errormsg ) {
            errormsg = <Alert message={this.state.errormsg} type="error" />;
        }
        return (
            
                
                
                <div>
                {btn}
                <Table
                    columns={columns} 
                    dataSource={self.state.records} 
                    onChange={self.onTableChange} 
                    pagination={self.state.pagination}
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
                    <div style={{marginTop:10}}><Input addonBefore={'标题'} type="text" placeholder="请输入这条广告的名称" onBlur={this.inputChange.bind(self,'title')} /></div>
                    <div style={{marginTop:10}}><Input addonBefore={'描述'} type="text" placeholder="请输入这条广告的描述" onBlur={this.inputChange.bind(self,'desc')} /></div>
                    <div style={{marginTop:10}}><Input addonBefore={'总价'} type="text" placeholder="请输入购买总价" onBlur={this.inputChange.bind(self,'price')} /></div>
                    <div style={{marginTop:10}}><Input addonBefore={'数量'} type="text" placeholder="请输入优惠券数量" onBlur={this.inputChange.bind(self,'total')} /></div>
                    <div style={{marginTop:10}}>
                        <Upload name="img" fileList={self.state.fileList} customRequest={self.customRequest} onRemove={()=>{this.setState({fileList:[]})}}>
                            <Button>
                                <Icon type="upload" /> 请上传长宽比为2:1图片
                            </Button>
                        </Upload>
                    </div>
                    {errormsg}
                </Modal>
                <Modal 
                    width="350px"
                    title="图片" 
                    visible={this.state.imgvisible}
                    onCancel={()=>{this.setState({imgvisible:false})}}
                    footer={[
                      <Button key="back" type="ghost" size="large" onClick={()=>{this.setState({imgvisible:false})}}>取消</Button>,
                    ]}
                >
                    <img style={{width:315}} src={self.state.src} />
                </Modal>
                <Modal 
                    width="400px"
                    title='扫码添加/修改微信号'
                    visible={self.state.qr_visible}
                    onCancel={self.qrhandleCancel}
                    footer={[<Button key="back" type="primary" size="large" onClick={self.qrhandleCancel}>返回</Button>]}
                >
                    <div style={{textAlign:'center'}}>
                        <QRCode level='H' size={256} value = {this.state.url}/>
                        <p>{self.state.ewm_alert}</p>
                    </div>
                </Modal>
            </div>
        );
    }
});

const AdList = require('create-react-class')({
    getInitialState: function() {
        return {
            show:false,
            id:0
        }
    },
    render:function(){
        let con = null;
        if(this.state.show){
            con = <List id={this.state.id} />
        }
        return (
            <MyLayout id={(id)=>{this.setState({id:id,show:true})}}>
                {con}
            </MyLayout>
            )
    },
});

export default  { AdList ,List }  ;
export { AdList ,List };