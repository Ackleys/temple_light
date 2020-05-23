"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {  Button, Menu,  Icon, Table,Input,Modal,Select,message,Alert,Tabs} from 'antd';
import {Link}       from 'react-router';
import {MyLayout}     from '../common/layout.js';
const Option = Select.Option;
const TabPane = Tabs.TabPane;
const columns = [ {
                title: '自编号',
                dataIndex: 'id',
            }, {
                title: '设备IMEI',
                dataIndex: 'imei',
            },{
                title: '设备类型',
                dataIndex: 'cat',
            }];

const AddEquipment = React.createClass({
  getInitialState: function() {
    return {
    	type:{},
      visible:false,
      msg:['',''],
      option:[],
      records:[],
      num:'1',
      cat:0,
      errormsg:null,
      "pagination": {
          "showSizeChanger":true,
          //defaultPageSize: 10,
          //defaultCurrent : 1,
          "current"        : 1,
          "pageSize"       : 10,
          "pageSizeOptions": ['10', '25', '50', '100']
      },
    };
  },
  componentWillMount: function() {
    this.type();
  },
  type:function(){
    
      var self = this;
      var url  = window.API_PREFIX+"/device/cat";
      var callback = function(err,res){
        if(err){

        }else{
          console.log(res.body);
          let arr = [];
          for(let i in res.body.data){
            let data={
              num:i,
              value:res.body.data[i]
            };
            arr.push(data);
          }
          console.log(arr);
          self.setState({option:arr});
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
  help:function(){
    this.setState({visible:true,msg:["1，批量添加只能是连续的IMEI号 "," 2，类型必须一致，稍后可以在编辑设备一栏修改"]})
  },
  handleOk:function(){
     this.setState({visible:false,msg:['','']})
  },
  handleCancel:function(){
    this.setState({visible:false,msg:['','']})
  },
  handleChange:function(e){
    let exp = /^[0-9]+$/
    if(e.target.id === 'imei'){
      this.setState({imei:e.target.value});
    }else if(e.target.id === 'num'){
      if(exp.test(e.target.value-0)){
        this.setState({num:e.target.value-0,errormsg:null});
      }else{
        this.setState({errormsg:'请输入正确的数字'});
      }
    }
  },
  selectChange:function(e){
    this.setState({cat:e});
  },
  onTableChange:function(pagination, filters, sorter) {
      //console.log('params', pagination, filters, sorter);
      const pager = this.state.pagination;
      pager.current = pagination.current;
      pager.pageSize = pagination.pageSize;
      this.setState({
        pagination: pager,
      });
  },
  cat_change:function(t){
    let a = '';
    this.state.option.map(q=>{
      if(q.num === t+''){
        a = q.value;
      }
    })
    return a;
  },
  add:function(){
      var self = this;
      var url  = window.API_PREFIX+"/device/add";
      self.setState({errormsg:''});
      var callback = function(err,res){
        if(err){
          self.setState({errormsg:err.err.msg});
        }else{
          console.log(res.body);
            res.body.data.cat = self.cat_change(res.body.data.cat);
            res.body.data.key = Math.random();
          let arr = self.state.records;
          console.log(arr);
          arr.push(res.body.data);
          console.log(arr);
          self.setState({records:arr});
          message.info('添加成功');
        }
      };
      if(self.state.imei.length !== 15){
        self.setState({errormsg:'请输入正确的imei'});
        return false;
      }
      var data={
        imei:self.state.imei,
        cat:self.state.cat-0
      }
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
  tabChange:function(){
    this.setState({alert:null});
  },
  render: function (){
    let self = this;
    let alert = null;
    const option = self.state.option.map((q,i)=>{return (<Option key={i} value={q.num}>{q.value}</Option>)})
    if(self.state.errormsg){
       alert = <Alert message={self.state.errormsg} type="error" />
    }
    return (
      <MyLayout>
        <div className='add_equ'>
          <p>添加设备<Icon type="info-circle" onClick={this.help} /></p>
          <Tabs defaultActiveKey="1" size="small" onChange={self.tabChange}>
            <TabPane tab="IMEI添加" key="1">
              <Input style={{width:'100%',marginTop:10}} placeholder='请输入IMEI' id='imei' onChange={this.handleChange} />
              {/*<Input style={{width:'100%',marginTop:10}} placeholder='请输入数量' id='num' onChange={this.handleChange} />*/}
              {alert}
              <Select onChange={self.selectChange} placeholder='请选择设备类型' style={{width:'100%',marginTop:10}} >
                {option}
              </Select>
              <Button type='primary' style={{width:'100%',marginTop:10}} onClick={self.add}>添加</Button>
            </TabPane>
            {/*<TabPane tab="箱袋号添加" key="2">
              <Input style={{width:'100%',marginTop:10}} placeholder='请输入箱袋号' id='xd_num' onChange={this.handleChange} />
              <Input style={{width:'100%',marginTop:10}} placeholder='请输入数量' id='num' onChange={this.handleChange} />
              {alert}
              <Select onChange={self.selectChange} placeholder='请选择设备类型' style={{width:'100%',marginTop:10}} >
                {option}
              </Select>
              <Button type='primary' style={{width:'100%',marginTop:10}} onClick={self.add}>添加</Button>
            </TabPane>*/}
          </Tabs>
        </div>

        <Table columns={columns}                      
              dataSource={this.state.records} 
              onChange={self.onTableChange} 
              pagination={self.state.pagination}
              style={{'marginTop':20,float:'left',width:'79%'}}
        /> 


        <Modal 
          width="300px"
          title="提示" 
          visible={this.state.visible}
          onOk={this.handleOk}
          onCancel={this.handleCancel}
        >
         <p>{self.state.msg[0]}</p>
         <p>{self.state.msg[1]}</p>
        </Modal>
      </MyLayout>
    );
  }
});


export default AddEquipment;
export { AddEquipment };