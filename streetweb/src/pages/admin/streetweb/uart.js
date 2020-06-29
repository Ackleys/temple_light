"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {  Button, Menu,  Icon, Modal,Input,message,Alert,Popconfirm, Radio } from 'antd';
import {MyLayout}     from '../common/layout.js';

const Uart = React.createClass({
    getInitialState: function() {
        return{
            product:[],
            visible:false,
            data:{body:''},
            key:0,
            errormsg:null,
            loading:false,
            title:"",
            ddata:{},
        }  
    },
    componentWillMount:function(){
        this.product_list();
    },
    componentDidMount:function(){
     
    },
    product_list:function(){
        let url = window.API_PREFIX+'/device/product/fetch';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body);           
                self.setState({product:res.body.data});
            }
        };
        let data = {
            cat:2
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
            url = window.API_PREFIX+"/device/product/update";
            type = "PATCH";
            data = {
              product_id:self.state.id-0,
              update:da
            }
        }else{
              data = da;
              data.cat=2;
              data.body = '';
              let arr = Object.keys(data);
              if(arr.length<5){
                  self.setState({errormsg:"请填写完毕后提交"});
                  return false;
              }
              url = window.API_PREFIX+'/device/product/add';
              type = 'PUT';
        }
        if(da.price<1){
            self.setState({errormsg:"非法的金额"});
            return false;
        }
        if(da.price !== undefined && isNaN(da.price-0)){
            self.setState({errormsg:"价格不可填入非数字"});
            return false;
        }
        self.setState({loading:true});
        var callback = function(err,res){
            if(err){
                self.setState({errormsg:err.err.msg,loading:false});

            }else{
                console.log(res.body); 
               
                self.product_list();
                if(self.state.id){

                    message.success('修改成功');         
                }else{
                    message.success('添加成功');         

                }
                self.setState({errormsg:null,visible:false,key:Math.random(),data:{},id:null,loading:false,ddata:{}});
            }
        };
        
       
        var xhr  = new XMLHttpRequest();
        xhr.open(type, url);
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
        this.setState({visible:false,key:Math.random(),data:{},id:null,ddata:{},errormsg:null});
    },
    show_modal:function(){
        this.setState({visible:true,key:Math.random(),data:{},id:null,title:'添加套餐'});

    },
    inputChange:function(type,e){
        if(type === 'title'){
            this.state.data.title = e.target.value;
        }else if(type === 'body'){
            this.state.data.body = e.target.value;
        }
        else if(type === 'price'){
            this.state.data.price = +e.target.value * 100;
        }
        else if(type === 'uart_val'){
            this.state.data.uart_val = e.target.value;
        }
        else if(type === 'uart_exp') {
            this.state.data.uart_exp = e.target.value;
        }
        console.log(this.state.data);
    },
    update:function(id){
        console.log(id);
        let data={}
        this.state.product.map((q)=>{
            if(id === q.id){
                data = q;
            }
        })
        this.setState({id:id+'',visible:true,title:'修改套餐',ddata:data});
    },
    delete:function(id){
        console.log(id);
        let url = window.API_PREFIX+'/device/product/delete';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body);           
                self.product_list();
                message.success('删除成功');  
            }
        };
        let data = {
            product_id:id
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
    render: function (){
        let self = this;
        let alerts = null;
        let price = '',uart_val = '', uart_exp = '';
        if(self.state.ddata.price){
            price=self.state.ddata.price/100;
        }
        if(self.state.ddata.uart_val){
            uart_val = self.state.ddata.uart_val;
        }
        if(self.state.ddata.uart_exp){
            uart_exp = self.state.ddata.uart_exp;
        }
        const product = self.state.product.map((q,i)=>{
            return (
                <div key={i} className='product_box chair_box' >
                  <span>
                    <p>{q.price/100}元</p>
                    <p>数据: {q.uart_val}</p>
                  </span>
                  <span>
                    <p>{q.title}</p>
                  </span>
                  <p>
                        <span className='update' onClick={self.update.bind(self,q.id)}>修改</span>
                        <Popconfirm title="确定要删除吗?" onConfirm={self.delete.bind(self,q.id)} okText="是" cancelText="否">
                            <span className='delete'>删除</span>
                        </Popconfirm>
                  </p>
                </div>
              )
        })
        if(self.state.errormsg){
            alerts = (<Alert type='error' message={self.state.errormsg} />)
        }
        return (
            <MyLayout>
                <p className='doll_title'>串口类型机器可选套餐
                    <Button onClick = {self.show_modal}>添加</Button>
                </p>
                <div className='flexbox'>
                    {product}
                </div>
                <Modal 
                    width="300px"
                    title={self.state.title}
                    visible={this.state.visible}
                    onOk={this.handleOk}
                    onCancel={this.handleCancel}
                    key={self.state.key}
                    footer={[<Button onClick = {this.handleCancel}>取消</Button>,
                            <Button type='primary' onClick = {this.handleOk} loading={self.state.loading}>提交</Button>
                            ]}
                >
                    <Input defaultValue={self.state.ddata.title} placeholder='商品名' onChange={self.inputChange.bind(self,'title')} />
                    {/*<Input placeholder='请输入套餐描述，例如：放松一下' onChange={self.inputChange.bind(self,'body')} />*/}
                    <Input defaultValue={price} placeholder='默认价格（单位元）' onChange={self.inputChange.bind(self,'price')} />
                    <Input defaultValue={uart_val} placeholder='发送的数据' onChange={self.inputChange.bind(self,'uart_val')} />
                    <Input defaultValue={uart_exp} placeholder='期望接收的数据' onChange={self.inputChange.bind(self,'uart_exp')} />
                    {alerts}
                </Modal>
            </MyLayout>
        );
    }
});


export default Uart;
export { Uart };
