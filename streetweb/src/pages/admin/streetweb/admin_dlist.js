"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';
import { Button, Menu, Table, Modal, Input, Alert, message, Select } from 'antd';
import {MyLayout}     from '../common/layout.js';
const Option = Select.Option;
Array.prototype.indexOf = function(val) {
    for (var i = 0; i < this.length; i++) {
        if (this[i] == val) return i;
    }
    return -1;
};
Array.prototype.remove = function(val) {
    var index = this.indexOf(val);
    if (index > -1) {
        this.splice(index, 1);
    }
};
const AdminDlist = require('create-react-class')({
    getInitialState: function() {
        return {
            loading:true,
            records:[],
            type:[],
            "pagination": {
                "showSizeChanger":true,
                //defaultPageSize: 10,
                //defaultCurrent : 1,
                "current"        : 1,
                "pageSize"       : 10,
                "pageSizeOptions": ['10', '25', '50', '100']
            },
            selectedRowKeys:[],
            imei:[],
            agents:[],
            agent_id:'',
            visible:false,
            visible_bo:false,
            arr_bo:[],
            default_data:{l1:0,l2:0,l3:0},
            rate:0,
            input_show:false,
            level:'',
            errormsg:'请注意您选择的分成为自己获得的分成比例'
        };
    },
    componentWillMount:function(){
        this.get_msg();
        this.type();
        this.get_agent();
        this.getData();
    },
    get_agent:function(page,psize){
    let self = this;
    const pager = this.state.pagination;
    let url = window.API_PREFIX+'/agent/sub_agent/fetch?page='+1+'&psize='+999999;
    var callback = function(err,res){
          if(err){
                //console.log(err);
          }else{
                //console.log(res.body);
                self.setState({agents:res.body.data.agents});
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
    get_msg:function(){
     let url = window.API_PREFIX+'/agent/cur';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body);      
                self.setState({level:'l'+res.body.data.level});
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
    type:function(){
        var self = this;
        var url = window.API_PREFIX+"/device/cat";
        var callback = function(err,res){
          if(err){
  
          }else{
              //console.log(res.body);
              let arr = [];
              for(let i in res.body.data){
                let data={
                    num:i,
                    value:res.body.data[i]
                };
                  arr.push(data);
              }
              //console.log(arr);
              self.setState({type:arr});
              self.equ_list(1,10);
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
    cat_change:function(t){
        let a = '';
        this.state.type.map(q=>{
            if(q.num === t+''){
                a = q.value;
            }
        })
        return a;
    },
    equ_list:function(page,psize){
        var self = this;
        var url  = window.API_PREFIX+"/device/fetch?page="+page+'&psize='+psize;
        var callback = function(err,res){
          if(err){
  
          }else{
                //console.log(res.body);
                let num = 0;
                let arr = []
                let pager = self.state.pagination;
                res.body.data.devices.forEach(function(q,i){
                    q.cat = self.cat_change(q.cat);
                    q.key = i;
                    if(q.map_display){
                       arr.push(num);
                    }
                    if(q.use_state){
                        q.use_state = '使用中';
                    }else if(!q.use_state){
                        q.use_state = '空闲';
                    }
                    if(q.comm_state){
                        q.comm_state = '在线';
                    }else if(!q.comm_state){
                        q.comm_state = '关机';
                    }
                    num++;
                })
                pager.total = res.body.data.count;
                self.setState({records:res.body.data.devices,loading:false,pagination:pager});
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
  
    onTableChange:function(pagination, filters, sorter) {
        //console.log('params', pagination, filters, sorter);
        const pager = this.state.pagination;
        pager.current = pagination.current;
        pager.pageSize = pagination.pageSize;
        this.setState({
            pagination: pager,
        });
        this.equ_list(pager.current,pager.pageSize);
    },
    onSelectChange:function (selectedRowKeys,selectedRows) {
       this.setState({ selectedRowKeys });
    },
    onSelect:function(record,select,selectedRows,a){
      console.log(record);
      console.log(selectedRows);
      console.log(a);
        if(select){
            if(record.operator!==sessionStorage.getItem('name')){
                alert('您选择了已经分配的设备，请注意！')
            }
            this.state.imei.push(record.imei);
        }else{
            this.state.imei.remove(record.imei);
        }
    }, 
    seChange:function(v){
        this.setState({agent_id:v});
    },
    fcChange:function(v){
        if(v === '自定义'){
            this.setState({rate:0,input_show:true});
        }else{
            this.setState({rate:v});
        }
    },
    group:function(){
        let self = this;
        if(self.state.imei.length<=0){
            alert('请选择设备后再提交');
            return false;
        }else if(!self.state.agent_id){
             alert('请选择代理商后再提交');
            return false;
        }else{
            //弹出弹窗填写占总金额的分成比例,
            self.setState({visible:true});
            
        }
    },
    set_group:function(){
        /*self.state.imei.map((d,i)=>{
            let data={
                start_imei:d,
                num:1,
                update:{
                    agent_id:self.state.agent_id,
                    rate:self.state.rate
                },
            };
            self.update(data);
        })*/

        let url = window.API_PREFIX+'/device/multi/distribution';
        var self = this;
        self.setState({errormsg:null});
        var callback = function(err,res){
            if(err){
                self.setState({errormsg:err.err.msg});
            }else{
               message.success('分组成功！');
               self.setState({input_show:false,visible:false,selectedRowKeys:[],imei:[]});
               self.equ_list();
            }
        };
        let data = {
            imeis:self.state.imei,
            to_agent:self.state.agent_id,
            rate:self.state.rate-0
        }        
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
    },
    input_change:function(e){
        console.log(e.target.value);
        if(e.target.value<1&&e.target.value>=0){
            this.setState({rate:e.target.value,errormsg:null});
        }else{
            this.setState({errormsg:'请输入小于1大于等于零的数字'});

        }
    },
    update:function(data){
        let url = window.API_PREFIX+'/device/update';
        var self = this;
        self.setState({errormsg:null});
        var callback = function(err,res){
            if(err){
                self.setState({errormsg:err.msg});
            }else{
               message.success('编辑成功！');
               self.setState({selectedRowKeys:[]});
               self.equ_list();
            }
        };
                
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
    },
    bottom_agent:function(arr){
        this.setState({visible_bo:true,arr_bo:arr});

    },
    handleOk_bo:function(){
        this.setState({visible_bo:false,arr_bo:[]});
    },
    handleCancel_bo:function(){
        this.setState({visible_bo:false,arr_bo:[]});

    },
    handleCancel:function(){
        this.setState({visible:false,input_show:false,errormsg:null});
    },
    getData:function(){
        var self = this;
        var url = window.API_PREFIX+"/agent/setting/fetch";
        var callback = function(err,res){
          if(err){

          }else{
              console.log(res.body);
              self.setState({default_data:res.body.data});
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
    render: function (){
        let self = this;
        const columns = [{
                    title: '代理商',
                    dataIndex: 'operator',
                },{
                    title: '自编号',
                    dataIndex: 'id',
                },{
                    title: 'IMEI(点击查看设备套餐)',
                    dataIndex: 'imei',
                },{
                    title: '设备类型',
                    dataIndex: 'cat',
                },{
                    title: '分成',
                    dataIndex: ' ',
                    render:(text,re) => {
                        let top=[0,0];
                        let mid=0;
                        let bot=[0,0];
                        let data=[];
                        /*if(re.operator_level === 4){
                            data = [{agent:'省级代理','fencheng':re.l3},{agent:'市县代理','fencheng':re.l2},{agent:'运营商','fencheng':re.l1}];
                        }else if(re.operator_level === 3){
                            data = [{agent:'市县代理','fencheng':re.l2},{agent:'运营商','fencheng':re.l1}];
                        }else if(re.operator_level === 2){
                            data = [{agent:'运营商','fencheng':re.l1}];
                        }else{
                            data = [{agent:'该运营商已经是最后一级','fencheng':''}];
                        }*/
                        if(self.state.level === 'l4'){
                            mid = re.l4;
                            bot = [re.l3,re.l2,re.l1];
                            data = [{agent:'省级代理','fencheng':re.l3},{agent:'市县代理','fencheng':re.l2},{agent:'运营商','fencheng':re.l1}];
                        }else if(self.state.level === 'l3'){
                            top = [re.l4,0] 
                            mid = re.l3;
                            bot = [re.l2,re.l1];
                            data = [{agent:'市县代理','fencheng':re.l2},{agent:'运营商','fencheng':re.l1}];
                            
                        }else if(self.state.level === 'l2'){
                            top = [re.l4,re.l3]
                            mid = re.l2;
                            bot = [re.l1,0];
                            data = [{agent:'运营商','fencheng':re.l1}];
                            
                        }else{
                            data = [{agent:'该运营商已经是最后一级','fencheng':''}];
                        }
                        return(
                            <span>
                                <a href="#" style={{color: '#666'}}>上级分成：{(top.reduce(function(prev, curr,){
                                                          return prev + curr;
                                                      })*100).toFixed(2)+'%'}
                                </a>
                                <span className="ant-divider" />
                                <a href="#" style={{color: '#666'}}>我的分成：{mid*100+'%'}</a>
                                <span className="ant-divider" />
                                <a href="#" onClick={this.bottom_agent.bind(self,data)}>下级分成：{(bot.reduce(function(prev, curr,){
                                                          return prev + curr;
                                                      })*100).toFixed(2)+'%'}
                                </a>
                            </span>
                        )},
                }];
        const rowSelection = {
              selectedRowKeys:self.state.selectedRowKeys,
              onChange: self.onSelectChange,
              onSelect: self.onSelect,
        };
        let option = null;
        if(self.state.agents.length>0){
            option = self.state.agents.map((d,i)=>{
                        return (<Option key={i} value={d.id}>{d.name}</Option>)
                    })
        }
        let Modal_content = null;
        if(self.state.input_show){
            Modal_content = (<Input type='number' id='rate' onChange={self.input_change} placeholder='请输入你抽成的百分比（占总金额的百分比，例如5%，写成0.05）' />)
        }else{
            Modal_content = (
                <Select onChange={self.fcChange} style={{width:'100%'}} placeholder='请选择你抽成的百分比，或点击自定义'>
                    <Option value={self.state.default_data.l1}>{self.state.default_data.l1}</Option>
                    <Option value={self.state.default_data.l2}>{self.state.default_data.l2}</Option>
                    <Option value={self.state.default_data.l3}>{self.state.default_data.l3}</Option>
                    <Option value='自定义'>自定义</Option>
                </Select>
                )
        }
        let alert = null;
        if(self.state.errormsg){
            alert = <Alert message={self.state.errormsg} type="error" />
        }
        return (
          <MyLayout>
            <Table
                loading={self.state.loading}
                rowSelection={rowSelection} 
                columns={columns} 
                dataSource={self.state.records} 
                onSearch={self.onTableChange} 
                pagination={self.state.pagination}
                footer={()=>'请在表格中对设备进行勾选，然后选择代理商后进行提交'}
            />
            <Select onChange={self.seChange} style={{width:'30%',marginRight:"1%"}} placeholder='请选择代理商' notFoundContent='请添加代理后进行操作'>
                {
                    option
                }
            </Select>
            <Button type='primary' onClick={self.group}>提交</Button>
            <Modal 
              width="450px"
              title="选择分成" 
              visible={this.state.visible}
              onOk={this.set_group}
              onCancel={this.handleCancel}
            >
                {Modal_content}
                {alert}
            </Modal>
            <Modal 
              width="300px"
              title="下级分成" 
              visible={this.state.visible_bo}
              onOk={this.handleOk_bo}
              onCancel={this.handleCancel_bo}
            >
                {self.state.arr_bo.map((q,i)=>{
                    return (
                        <p key={i} style={{textAlign:'center'}}><span>{q.agent}：</span><span>{q.fencheng*100+'%'}</span></p>
                        )
                })}

            </Modal>
          </MyLayout>
        );
    }
});


export default AdminDlist;
export { AdminDlist };