"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';
import {  Button, Menu,  Icon, Table,Modal,Input,Alert,message,Select,Form} from 'antd';
import {MyLayout}     from '../common/layout.js';
const Option = Select.Option;
const FormItem = Form.Item;
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
var Level1Dlist = require('create-react-class')({
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
            errormsg:null,
            loading_b:false,
            agent_list:[],
            value:'',
            to_agent:0,
            id:'device_id',
            imei_data:[],//模糊查询的imei
        };
    },
    componentWillMount:function(){
        this.equ_list(1,10);
    },
    handleSubmit:function(e){
        let self = this;
        e.preventDefault();
        this.props.form.validateFieldsAndScroll((err, values) => {
            if (!err) {
                console.log('Received values of form: ', values);
                let data = {};
                for (let i in values) {
                    if(values[i]){
                        data[i] = values[i];
                    }
                    if(i === 'device_id'){
                        data[i] = values[i]-0;
                    }
                }
                self.get_device(data);  
            }
        })
    },
    get_device:function(data){
        let self = this;
        let url = window.API_PREFIX+'/god/unknow_device/search';
        var callback = function(err,res){
            if(err){
                message.error(err.err.msg);
            }else{
                console.log(res.body);
                const pager = self.state.pagination;
                pager.total = 1;
                res.body.data.key=res.body.data.imei;
                self.setState({records:[res.body.data],pagination:pager});
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
                        callback({err:JSON.parse(xhr.responseText)},null);
                }
            }
        };
    },
    handleChange:function(value,num){
        const { setFieldsValue } = this.props.form;
        if(value === 'imei'){
            setFieldsValue({'imei':num});
            this.fruzzy_seach_imei(num);
        }
    },
    fruzzy_seach_imei:function(num){
        let self = this;
        let url = window.API_PREFIX+'/god/device/fuzzy_query/imei';
        var callback = function(err,res){
              if(err){

              }else{
                console.log(res.body);
                let data={};
                data['imei_data'] = res.body.data;
                self.setState(data);
              }
        };
        let data={};
        data.imei= num;
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
    fruzzy_seach_name:function(n){
      let self = this;
      let url = window.API_PREFIX+'/god/fuzzy_agent/name';
      var callback = function(err,res){
            if(err){
  
            }else{
              console.log(res.body);
              let data={};
              data['agent_list'] = res.body.data.names;
              self.setState(data);
            }
        };
        let data={};
        data.name= n;
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
    equ_list:function(page,psize){
        var self = this;
        var url  = window.API_PREFIX+"/god/unknow_device/fetch?page="+page+'&psize='+psize;
        var callback = function(err,res){
          if(err){
  
          }else{
                console.log(res.body);
                let arr = []
                let pager = self.state.pagination;
                res.body.data.devices.forEach(function(q,i){
                    q.key = q.imei;
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
    typeChange:function(v){
        this.setState({id:v});
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
       this.setState({ selectedRowKeys,imei: selectedRowKeys});
    },
    onSelect:function(record,select,selectedRows){
        /*if(select){
            if(record.operator_level===0){
                alert('您选择了已经分配的设备，请注意！')
            }
            this.state.imei.push(record.imei);
        }else{
            this.state.imei.remove(record.imei);
        }*/
    }, 
    seChange:function(v){
        //this.setState({agent_id:v});
        console.log(v)
        this.setState({value:v});
        this.fruzzy_seach_name(v);
    },
    seSelect:function(v,o){
        this.setState({value:o.props.children,to_agent:v-0});
    },
    group:function(){
        let self = this;
        if(self.state.imei.length<=0){
            alert('请选择设备后再提交');
            return false;
        }else if(!self.state.to_agent){
             alert('请选择代理商后再提交');
            return false;
        }else{
            //弹出弹窗填写占总金额的分成比例,
            self.setState({loading_b:true},function(){self.set_group()});
            
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

        let url = window.API_PREFIX+'/god/multi/first_distribution';
        var self = this;
        self.setState({errormsg:null});
        var callback = function(err,res){
            if(err){
                self.setState({errormsg:err.err.msg});
            }else{
               message.success('分组成功！');
               self.setState({loading_b:false,selectedRowKeys:[],imei:[]});
               self.equ_list();
            }
        };
        let data = {
            imeis:self.state.imei,
            to_agent:self.state.to_agent,
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
    render: function (){
        let self = this;
        const columns = [{
                    title: '自编号',
                    dataIndex: 'id',
                },{
                    title: 'IMEI',
                    dataIndex: 'imei',
                }];
        const rowSelection = {
              selectedRowKeys:self.state.selectedRowKeys,
              onChange: self.onSelectChange,
              onSelect: self.onSelect,
        };
        let option = null;
        
        option = self.state.agent_list.map((d,i)=>{
                    return (<Option key={i} value={d.id}>{d.name}</Option>)
                })
        
        const { getFieldDecorator, getFieldValue } = this.props.form;
        const imei_options = this.state.imei_data.map((d,i) => <Option key={i} value={d}>{d}</Option>);
        let alert = null;
        let input = <Select
                        combobox={true}
                        placeholder='IMEI(可模糊搜索)'
                        notFoundContent=""
                        defaultActiveFirstOption={false}
                        showArrow={false}
                        filterOption={false}
                        onChange={this.handleChange.bind(self,'imei')}
                        style={{width:'25%',marginRight:10,float:'left'}}
                    >
                        {imei_options}
                    </Select>
                    
        if(self.state.errormsg){
            alert = (<Alert type = 'error' message={self.state.errormsg} />)
        }
        if(self.state.id === 'device_id'){
            input = <Input style={{width:'25%',marginRight:10,float:'left'}} placeholder='请输入自编号' />
                    
        }
        return (
            <MyLayout>
                <div className='home_head'>
                    <Form onSubmit={this.handleSubmit}>
                        <FormItem className='formitem' >
                            <Select defaultValue='device_id' style = {{width:100,float:'left'}} onChange={self.typeChange}>
                                <Option value='device_id'>自编号</Option>
                                <Option value='imei'>imei</Option>
                            </Select>
                            {getFieldDecorator(self.state.id,  {
                            })(
                                input
                            )}
                            <Button type="primary" style={{marginRight:'5%'}} htmlType='submit'>查询</Button>
                        </FormItem>
                        {alert}
                    </Form>
                </div>
                <Table
                    loading={self.state.loading}
                    rowSelection={rowSelection} 
                    columns={columns} 
                    dataSource={self.state.records} 
                    onChange={self.onTableChange} 
                    pagination={self.state.pagination}
                    footer={()=>'请在表格中对设备进行勾选，然后选择代理商后进行提交'}
                />
                <Select onSearch={self.seChange}
                    onSelect={self.seSelect} 
                    value={this.state.value}
                    combobox={true}
                    style={{width:'30%',marginRight:"1%"}} 
                    placeholder='请输入代理商的名字（可模糊搜索）'
                    defaultActiveFirstOption={false}
                    showArrow={false}
                    filterOption={false} 
                    notFoundContent=''>
                    {
                        option
                    }
                </Select>
                <Button type='primary' onClick={self.group} loading={self.state.loading_b}>提交</Button>
                {alert}
            </MyLayout>
        );
    }
});
Level1Dlist = Form.create()(Level1Dlist);

export default Level1Dlist;
export { Level1Dlist };