"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';
import moment       from 'moment';
import { Form, Icon } from '@ant-design/compatible';
import {  Button, Menu,  Table, Input,Alert,Tabs,DatePicker,Select,message } from 'antd';
import {MyLayout}     from '../common/layout.js';
const { MonthPicker, RangePicker } = DatePicker;
const FormItem = Form.Item;
const Option = Select.Option;
const dateFormat = 'YYYY-MM-DD HH:mm:ss';
const columns = [ {
                title: '自编号',
                dataIndex: 'id',
            }, {
                title: '设备',
                dataIndex: 'imei',
            },{
                title: '营业额（元）',
                dataIndex: 'income',
            },{
                title: '线上营业额（元）',
                dataIndex: 'online_income',
            },{
                title: '投币收益（元）（仅供参考）',
                dataIndex: 'offline_income',
            },{
                title: '投币个数',
                dataIndex: 'offline_coin',
            },/*{
                title: '线下退币',
                dataIndex: 'tuibi',
            }*/, {
                title: '设备状态',
                dataIndex: 'status',
            }, {
                title: '投放地点',
                dataIndex: 'address',
            }, {
                title: '运营商',
                dataIndex: 'operator', 
            }];


var TurnOver = require('create-react-class')({
  getInitialState: function() {
     return{
        "records":[],
        address_data:[],
        imei_data:[],
        num_data:[],
        'value':'',
        address:'',
        imei:'',
        "pagination": {
            "showSizeChanger":true,
            //defaultPageSize: 10,
            //defaultCurrent : 1,
            "current"        : 1,
            "pageSize"       : 10,
            "pageSizeOptions": ['10', '25', '50', '100','10000']
        },
        errormsg:null,
        idtmr:null,
     }
  },
  componentWillMount:function(){
    let data = {};
    let self = this;
    data.end = parseInt(new Date().getTime()/1000);
        data.start = data.end-60*60*24;
    this.setState({data:data},function(){self.order_list(1,10)});
    
  },
  handleSubmit:function(e){
    let self = this;
      e.preventDefault();
      this.props.form.validateFieldsAndScroll((err, values) => {
        if (!err) {
            console.log('Received values of form: ', values);
            let data = {};
            for (let i in values) {
              if(i === 'time'){
                if(values.time !== undefined&&values.time !== []){
                  data.start = parseInt(new Date(values.time[0].format()).getTime()/1000) ;
                  data.end = parseInt(new Date(values.time[1].format()).getTime()/1000) ;
                }else{
                  data.end = parseInt(new Date().getTime()/1000);
                  data.start = data.end-60*60*24;
                }
              }else{
                if(values[i]){
                  data[i] = values[i];
                }
              }
            }
            self.setState({data:data},function(){self.order_list(1,10);});
            
          }
      })
  },
  handleChange:function(value,num){
    const { setFieldsValue } = this.props.form;
    if(value === 'address'){
      setFieldsValue({'address':num});
      
        this.fruzzy_seach_add(num);
      
    }else if(value === 'imei'){
      setFieldsValue({'imei':num});
      
        this.fruzzy_seach_imei(num);
      
    }else if(value === 'number'){
      setFieldsValue({'number':num});
    }
  },
  fruzzy_seach_add:function(num){
    let self = this;
    let url = window.API_PREFIX+'/device/address/fuzzy_query/address';
    var callback = function(err,res){
          if(err){

          }else{
            console.log(res.body);
            let data={};
            data['address_data'] = res.body.data;
            self.setState(data);
          }
      };
      let data={};
      data.address = num;
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
  fruzzy_seach_imei:function(num){
    let self = this;
    let url = window.API_PREFIX+'/device/fuzzy_query/imei';
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
   onTableChange:function(pagination, filters, sorter) {
        //console.log('params', pagination, filters, sorter);
        const pager = this.state.pagination;
        pager.current = pagination.current;
        pager.pageSize = pagination.pageSize;
        this.setState({
          pagination: pager,
        });
        this.order_list(pagination.current,pagination.pageSize);
    },
  handleReset:function ()  {
      this.props.form.resetFields();
  },
  order_list:function(page,psize){
    let self = this;
    const pager = this.state.pagination;
    let url = window.API_PREFIX+'/economic/income/query?page='+page+'&psize='+psize;
    var callback = function(err,res){
          if(err){
            self.setState({errormsg:err.msg});
          }else{
              console.log(res.body);
              self.setState({errormsg:null});
              pager.total = res.body.data.count;
              if(res.body.data.incomes.length === 0){
                message.info('暂无数据');
                self.setState({records:res.body.data.incomes});
                return false;
              }
              res.body.data.incomes.forEach((d,i)=>{
                d.key = i;
                d.status = self.status(d.status);
                d.income = d.income/100;
                d.online_income = d.online_income/100;
                d.offline_income = d.offline_income/100;
              })
              self.setState({pagination:pager,records:res.body.data.incomes});
          }
      };
      var xhr  = new XMLHttpRequest();
      xhr.open("POST", url);
      xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
      xhr.send(JSON.stringify(self.state.data));
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
  status:function(n){
    if(n === 1){
      return '在线';
    }else{
      return '关机';
    }

  },
  getExplorer:function(){
    var explorer = window.navigator.userAgent ;
    //ie 
    if (explorer.indexOf("MSIE") >= 0) {
        return 'ie';
    }
    else if(explorer.indexOf("Edge") >= 0){
        return 'Edge';
    }
    //firefox 
    else if (explorer.indexOf("Firefox") >= 0) {
        return 'Firefox';
    }
    //Chrome
    else if(explorer.indexOf("Chrome") >= 0){
        return 'Chrome';
    }
    //Opera
    else if(explorer.indexOf("Opera") >= 0){
        return 'Opera';
    }
    //Safari
    else if(explorer.indexOf("Safari") >= 0){
        return 'Safari';
    }
  },
  method1:function(){
    let self = this;
    
    if(self.getExplorer()=='ie'||self.getExplorer()=='Edge'){
      var curTbl = document.getElementsByTagName('table')[0];
      var oXL;
      try{  
        oXL = new ActiveXObject("Excel.Application"); //创建AX对象excel  
      }catch(e){  
        alert("无法启动Excel!\n\n如果您确信您的电脑中已经安装了Excel，"+"那么请调整IE的安全级别。\n\n具体操作：\n\n"+"工具 → Internet选项 → 安全 → 自定义级别 → 对没有标记为安全的ActiveX进行初始化和脚本运行 → 启用");  
        return false;  
      } 

      //创建AX对象excel 
      var oWB = oXL.Workbooks.Add();
      //获取workbook对象 
      var xlsheet = oWB.Worksheets(1);
      //激活当前sheet 
      var sel = document.body.createTextRange();
      sel.moveToElementText(curTbl);
      //把表格中的内容移到TextRange中 
      sel.select;
      //全选TextRange中内容 
      sel.execCommand("Copy");
      //复制TextRange中内容  
      xlsheet.Paste();
      //粘贴到活动的EXCEL中       
      oXL.Visible = true;
      //设置excel可见属性

      try {
          var fname = oXL.Application.GetSaveAsFilename("Excel.xls", "Excel Spreadsheets (*.xls), *.xls");
      } catch (e) {
          print("Nested catch caught " + e);
      } finally {
          oWB.SaveAs(fname);

          oWB.Close(savechanges = false);
          //xls.visible = false;
          oXL.Quit();
          oXL = null;
          //结束excel进程，退出完成
          //window.setInterval("Cleanup();",1);
          self.state.idTmr = window.setInterval(function(){self.Cleanup()}, 1);
      }
    }else{
        var tableToExcel = (function() {  
            var uri = 'data:application/vnd.ms-excel;base64,',  
                    template = '<html><head><meta charset="UTF-8"></head><body><table>{table}</table></body></html>',  
                    base64 = function(s) { return window.btoa(unescape(encodeURIComponent(s))) },  
                    format = function(s, c) {  
                        return s.replace(/{(\w+)}/g,  
                                function(m, p) { return c[p]; }) }  
            return function(table, name) {  
               table = document.getElementsByTagName('table')[0];  
                var ctx = {worksheet: name || 'Worksheet', table: table.innerHTML}  
                window.location.href = uri + base64(format(template, ctx))  
            }  
        })() 
        tableToExcel();
    }
  },
  Cleanup:function(){
    let self = this;
    window.clearInterval(self.state.idTmr); 
  },

  render:function(){
    let self = this;
    const { getFieldDecorator, getFieldValue } = this.props.form;
    const add_options = this.state.address_data.map(d => <Option key={d}>{d}</Option>);
    const imei_options = this.state.imei_data.map(d => <Option key={d}>{d}</Option>);
    //const num_options = this.state.num_data.map(d => <Option key={d.text}>{d.text}</Option>);
    let alert = null;
    if(self.state.errormsg){
      alert = (<Alert type = 'error' message={self.state.errormsg} />)
    }
    return(
      <MyLayout>
        <div className='home_head'>
                <Form onSubmit={this.handleSubmit}>
                  <FormItem className='formitem'>
                {getFieldDecorator('time',  {
                  initialValue:[moment(new Date(parseInt(new Date().getTime())-86400000),dateFormat),moment(new Date(parseInt(new Date().getTime())),dateFormat)]
                  //new Date(data.format()).getTime();获取时间戳
                })(
                      <RangePicker showTime format="YYYY-MM-DD HH:mm:ss" style={{width:'50%',marginRight:10,float:'left'}}/>
                  )}
                   <Button type="primary" className='right' style={{visibility:'hidden'}}>隐藏</Button>
                <Button type="primary" className='right' style={{marginRight:'5%'}} htmlType='submit'>查询</Button>
                </FormItem>
                <FormItem className='formitem' >
                  {getFieldDecorator('address',  {

                })(
                      <Select
                      combobox={true}
                      placeholder='地址(可模糊搜索)'
                      notFoundContent=""
                      defaultActiveFirstOption={false}
                      showArrow={false}
                      filterOption={false}
                      onChange={this.handleChange.bind(self,'address')}
                      style={{width:'25%',marginRight:10,float:'left'}}
                    >
                      {add_options}
                    </Select>
                  )}
                  {getFieldDecorator('imei',  {
                    
                })(
                      <Select
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
              )}
                  {/*getFieldDecorator('number',  {
                    
                })(
                    <Select
                      combobox={true}
                      placeholder='编号(可模糊搜索)'
                      notFoundContent=""
                      defaultActiveFirstOption={false}
                      showArrow={false}
                      filterOption={false}
                      onChange={this.handleChange.bind(self,'number')}
                      style={{width:'25%',marginRight:10,float:'left'}}
                    >
                      {num_options}
                    </Select>
                  )*/}
                  <Button type="primary" className='right' onClick={self.handleReset}>清除</Button>
                  <Button type="primary" className='right' onClick={self.method1} style={{marginRight:'5%'}}>导出</Button>
                </FormItem>
                {alert}
              </Form>
            </div>
            <Table columns={columns}                      
                dataSource={this.state.records} 
                onChange={self.onTableChange} 
                pagination={self.state.pagination}
                style={{'marginTop':20}}
            /> 
      </MyLayout>
    )
  }
});

TurnOver = Form.create()(TurnOver);
export default TurnOver;
export { TurnOver };