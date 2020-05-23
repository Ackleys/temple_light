"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';
import {  Button, Menu,  Icon, Table,Modal,Input,Alert,message,Select,Popconfirm} from 'antd';
import {MyLayout}     from '../common/layout.js';
import {List}      from './ad_list.js';
const Option = Select.Option;
const Search = Input.Search;
const AdDevice = React.createClass({
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
            visible:false,
            visible_bo:false,
            errormsg:'',
            add_option:[],
            add_id:0,
            adlist_show:false,
            coupons:[]
        };
    },
    componentWillMount:function(){
        this.address();
        this.type();
        this.get_ad(1,9999);
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
              self.dev_list(1,10);
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
    dev_list:function(page=1,psize=10){
        var self = this;
        var url  = window.API_PREFIX+"/advertiser/device/coupon/fetch?page="+page+'&psize='+psize+'&address_id='+self.state.add_id;
        var callback = function(err,res){
          if(err){
  
          }else{
                console.log(res.body); 
                let arr = []
                let pager = self.state.pagination;
                res.body.data.devices.forEach(function(q,i){
                    q.cat = self.cat_change(q.cat);
                    q.key = q.id;
                    
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
        console.log(selectedRowKeys);
       this.setState({ selectedRowKeys });
       this.setState({ imei:selectedRowKeys });
    },
    onSelect:function(record,select,selectedRows){
       
    }, 
    seChange:function(v){
        
        let re = this.state.records;
        let imei = this.state.imei;
        for (let i = 0;i<re.length;i++){
            for(let j = 0;j<imei.length;j++){
                if(re[i].id === imei[j]){
                    for(let q = 0;q<re[i].coupons.length;q++){
                        if(re[i].coupons[q] === v){
                            alert('设备'+re[i].imei+'已添加过该广告');
                            return false;
                        }
                    }
                }
            }
        }
        this.setState({coupon_id:v});
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
        }else if(!self.state.coupon_id){
             alert('请选择广告后再提交');
            return false;
        }else{
            self.set_group();
        }
    },
    set_group:function(){
        let url = window.API_PREFIX+'/advertiser/device/multi/add/coupon';
        var self = this;
        var callback = function(err,res){
            if(err){
                message.error(err.err.msg);
            }else{
               message.success('分配成功！');
               self.setState({selectedRowKeys:[],imei:[]});
               self.dev_list(1,10); 
            }
        };
        let data = {
            device_ids:self.state.imei,
            coupon_id:self.state.coupon_id,
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
    handleOk_bo:function(){
        this.setState({visible_bo:false,arr_bo:[]});
    },
    handleCancel_bo:function(){
        this.setState({visible_bo:false,arr_bo:[]});

    },
    handleCancel:function(){
        this.setState({visible:false,input_show:false,errormsg:'请注意您选择的分成为自己获得的分成比例',editmoney:false});
    },
    search:function(t,v){
        var self = this;
        var url  = window.API_PREFIX+'/device/search';
        var callback = function(err,res){
            if(err){
                message.error(err.err.msg);    
            }else{
                console.log(res.body);
                const pager = self.state.pagination;
                pager.total = 1;
                res.body.data.key = res.body.data.imei;
                self.setState({records:[res.body.data],loading:false,pagination:pager});   
            }
        };
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
        let data = {};
        data[t] = v;
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
    address:function(){
        let url = window.API_PREFIX+'/device/address/fetch';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                //console.log(res.body);             
                self.setState({add_option:res.body.data});
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
                    callback(JSON.parse(xhr.responseText),null);
                }
            }
        };
    },
    select:function(t){
        let self = this;
        this.setState({add_id:t},self.dev_list);
    },
    get_ad:function(page,psize){
        let url = window.API_PREFIX+'/advertiser/coupon/fetch?page='+page+'&psize='+psize;
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body.data);
                
                self.setState({coupons:res.body.data.coupons});
            }
        };
        let data={};
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
    render: function (){
        let self = this;
        let columns = [{
                    title: '自编号',
                    dataIndex: 'id',
                },{
                    title: 'IMEI(点击查看投放传单)',
                    dataIndex: 'imei',
                    onCellClick:(re)=>{self.setState({device_id:re.id,adlist_show:true})},
                    render:(t,re)=><a>{t}</a>
                },{
                    title: '设备类型',
                    dataIndex: 'cat',
                },{
                    title: '投放地址',
                    dataIndex: 'address',
                },{
                    title: '传单数量',
                    dataIndex: 'coupon',
                },{
                    title: '备注',
                    dataIndex: 'remark',
                }]
        const rowSelection = {
              selectedRowKeys:self.state.selectedRowKeys,
              onChange: self.onSelectChange,
              onSelect: self.onSelect,
        };
        let alert = null;
        let option = null;
        let content = null;
        if(self.state.errormsg){
            alert = <Alert message={self.state.errormsg} type="error" />
        }
        const add_option = self.state.add_option.map((q,i)=>{return <Option key={i} value={q.id+''}>{q.region+q.address}</Option>});
        option = self.state.coupons.map((q,i)=>{return <Option key={i} value={q.id}>{q.title}</Option>});
        if(!self.state.adlist_show){
            content  =  <div>
                            <div style = {{height:'8vh'}}>
                                <div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
                                {/*<Search placeholder="请输入imei"
                                    style={{ width: 200,marginLeft:20 }}
                                    onSearch={self.search.bind(self,'imei')} />
                                <Search placeholder="请输入设备自编号"
                                    style={{ width: 200,marginLeft:20 }}
                                    onSearch={self.search.bind(self,'device_id')} />*/}
                                <Select placeholder='请选择地址' notFoundContent='暂无地址' style={{width:200,marginLeft:20}} onSelect={self.select}>
                                            {add_option}
                                        </Select>
                            </div>
                            <Table
                                loading={self.state.loading}
                                rowSelection={rowSelection} 
                                columns={columns} 
                                dataSource={self.state.records} 
                                onChange={self.onTableChange} 
                                pagination={self.state.pagination}
                                footer={()=>'请在表格中对设备进行勾选，之后选择电子传单进行提交'}
                            />
                            <Select value={self.state.coupon_id} onChange={self.seChange} style={{width:'30%',marginRight:"1%"}} placeholder='请选择电子传单' notFoundContent='请添加电子传单后进行操作'>
                                {
                                    option
                                }
                            </Select>
                            <Button type='primary' onClick={self.group}>提交</Button>
                        </div>
        }else{
            content = <List device_id={self.state.device_id} show={(s)=>{self.setState({adlist_show:s})}} />
        }
        return (
          <MyLayout>
            {content}
            
          </MyLayout>
        );
    }
});


export default AdDevice;
export { AdDevice };