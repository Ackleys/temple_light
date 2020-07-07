"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';
import QRCode       from 'qrcode.react';
import { Button, Menu, Table, Input, Modal, Alert, Tabs } from 'antd';
import {MyLayout}     from '../common/layout.js';
const InputGroup = Input.Group;
const TabPane = Tabs.TabPane;
const WithDraw = require('create-react-class')({
    getInitialState: function() {
        return {
          	records:[],
            "pagination": {
                "showSizeChanger":true,
                //defaultPageSize: 10,
                //defaultCurrent : 1,
                "current"        : 1,
                "pageSize"       : 10,
                "pageSizeOptions": ['10', '25', '50', '100']
            },
            data:{level:0,joinuped:{wechat:0}},
            visible: false,
            fee_visible:false,
            fee:0,
            balance:0,
            withdrawable_balance:0,
            remark:'',
            pswd:'',
            loading:true,
            btn_loading:false,
            title:'',
            key:0,
            url:'',
            nickname:'',
            errormsg:null,
            ewm_alert:'',
            timer:null,
            timer_l:null,
            realmoney:'',
            moneyfee:'',
            withdraw_data:{
                withdraw_fee:0
            },
            tabs:1,
            records2:[],
            "pagination2": {
                "showSizeChanger":true,
                //defaultPageSize: 10,
                //defaultCurrent : 1,
                "current"        : 1,
                "pageSize"       : 10,
                "pageSizeOptions": ['10', '25', '50', '100']
            },
            records3:[],
            "pagination3": {
                "showSizeChanger":true,
                //defaultPageSize: 10,
                //defaultCurrent : 1,
                "current"        : 1,
                "pageSize"       : 10,
                "pageSizeOptions": ['10', '25', '50', '100','500','10000']
            },

        };
    },
    componentWillMount: function() {
        this.wallet();
        this.qrcode_url();
        this.wallet_list(1,10);
        this.wallet_receipt(1,10);
        this.wechat_withdraw_all(1,10);
    },
    componentDidMount:function(){
       
    },
    componentWillUnmount:function(){
        clearInterval(this.state.timer);
        clearInterval(this.state.timer_l);
    },
    getData:function(id){
        var self = this;
        var url = window.API_PREFIX+"/agent/setting/fetch";
        var callback = function(err,res){
          if(err){

          }else{
              console.log(res.body);
              res.body.data.min_withdraw = res.body.data.min_withdraw/100;
              self.setState({withdraw_data:res.body.data}); 
          }
        };
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify({target_agent_id:id}));
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
    wallet:function(){
        let self = this;
        let url = window.API_PREFIX+'/economic/wallet/fetch';
        var callback = function(err,res){
            if(err){
               console.log(err);
            }else{
                console.log(res.body);
                self.setState({
                    balance:res.body.data.balance,
                    withdrawable_balance:res.body.data.withdrawable_balance,
                    nickname:res.body.data.nickname,
                    total_fee_sum:res.body.data.total_fee_sum,
                    receipt_sum:res.body.data.receipt_sum
                });
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
    qrcode_url:function(){
        let self = this;
        let url = window.API_PREFIX+'/economic/bindwechat_url/fetch';
        var callback = function(err,res){
            if(err){
               console.log(err);
            }else{
                console.log(res.body);
                self.setState({url:res.body.data.url});
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
    wallet_list:function(page,psize){
        let self = this;
        let url = window.API_PREFIX+'/economic/wechat_withdraw/fetch?page='+page+'&psize='+psize;
        var callback = function(err,res){
            if(err){
               console.log(err);
              self.setState({loading:false});
    
            }else{
                console.log(res.body);
                const pager = self.state.pagination;
                pager.total =  res.body.data.count;
                res.body.data.pays.forEach((q,i)=>{
                  q.key = i;
                  q.fee = q.fee/100;
                  q.time = self.getdate(new Date(q.time*1000));
                })
                self.setState({pagination:pager,loading:false,records:res.body.data.pays});
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
    wallet_receipt:function(page,psize){
        let self = this;
        let url = window.API_PREFIX+'/economic/wallet_receipt/fetch?page='+page+'&psize='+psize;
        var callback = function(err,res){
            if(err){
               console.log(err);
              self.setState({loading:false});
    
            }else{
                console.log(res.body);
                const pager = self.state.pagination2;
                pager.total =  res.body.data.count;
                res.body.data.wallet_receipts.forEach((q,i)=>{
                    q.key = i;
                    q.receipt = q.receipt/100;
                    q.withdrawable_receipt = q.withdrawable_receipt/100;
                    if(q.trade_type%2){
                        q.income = 0;
                    }else{
                        q.income = 1;
                    }
                    q.trade_type = self.trade_type(q.trade_type);
                    q.time = self.getdate(new Date(q.time*1000));
                })
                self.setState({pagination2:pager,loading:false,records2:res.body.data.wallet_receipts});
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
    wechat_withdraw_all:function(page,psize){
        let self = this;
        let url = window.API_PREFIX+'/economic/top_agent/wechat_withdraw/fetch?page='+page+'&psize='+psize;
        var callback = function(err,res){
            if(err){
                console.log(err);
                self.setState({loading:false});
            }else{
                console.log(res.body);
                const pager = self.state.pagination3;
                pager.total =  res.body.count;
                res.body.pays.forEach((q,i)=>{
                    q.key = i;
                    q.total_fee = q.total_fee/100;
                    q.wechat_fee = q.wechat_fee/100;
                    q.total_fee_sum = q.total_fee_sum/100;
                    q.receipt_sum = q.receipt_sum/100;
                    q.withdrawable_balance = q.withdrawable_balance/100;
                    q.balance = q.balance/100;
                    q.wechat_fee_rate = (q.wechat_fee_rate*100).toFixed(2)+'%';
                    q.fee = q.fee/100;
                    if(q.status == 1){
                        q.status='成功';
                    }else{
                        q.status='失败';
                    }
                    q.time = self.getdate(new Date(q.time*1000));
                })
                self.setState({pagination3:pager,loading:false,records3:res.body.pays});
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
    trade_type:function(t){
        return {1:'代理提成收入',2:'代理微信取现',3:'用户充值',4:'用户消费',5:'转账转入',6:'转账转出',7:'用户退款',8:'代理提成退款'}[t];
    },
    getdate:function (now) {
        let y = now.getFullYear();
        let m = now.getMonth() + 1;
        let d = now.getDate();
        return y + "-" + (m < 10 ? "0" + m : m) + "-" + (d < 10 ? "0" + d : d) + " " + now.toTimeString().substr(0, 8);
    },
    withdraw:function(){
        let self = this;
        if(!self.state.fee){
            self.setState({errormsg:'请填写完毕后提交'});
            return false;
        }
        if(!self.state.remark){
            self.setState({errormsg:'请填写完毕后提交'});
            return false;
        }
        if(!self.state.pswd){
            self.setState({errormsg:'请填写完毕后提交'});
            return false;
        }
        let url = window.API_PREFIX+'/economic/wechat_withdraw';
        self.setState({btn_loading:true});
        var callback = function(err,res){
            if(err){
                console.log(err);
                self.setState({errormsg:err.err.msg,btn_loading:false});
    
            }else{
                console.log(res.body);
                const pager = self.state.pagination;
                const pager2 = self.state.pagination2;
                self.setState({errormsg:null,fee_visible:false,key:Math.random(),btn_loading:false,realmoney:'',moneyfee:''});
                self.wallet();
                self.wallet_list(pager.current,pager.pageSize);
                self.wallet_receipt(pager2.current,pager2.pageSize);
            }
        };
        let data = {
          fee:self.state.fee,
          desc:'微信取现',
          remark:self.state.remark,
          pswd:self.state.pswd
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
    bindwechat:function(){
        let self = this;
        let url = window.API_PREFIX+'/economic/bindwechat/query';
        var callback = function(err,res){
            if(err){
                console.log(err);
            }else{
                console.log(res.body);
                if(res.body.data.status){
                  self.wallet();
                  self.setState({ewm_alert:'绑定成功'});
                  clearInterval(self.state.timer_l);
                }
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
        const pager = this.state.pagination;
        pager.current = pagination.current;
        pager.pageSize = pagination.pageSize;
        this.setState({
            pagination: pager,
        });
        this.wallet_list(pager.current,pager.pageSize);
    },
    onTableChange2:function(pagination, filters, sorter) {
        const pager = this.state.pagination2;
        pager.current = pagination.current;
        pager.pageSize = pagination.pageSize;
        this.setState({
            pagination2: pager,
        });
        this.wallet_receipt(pager.current,pager.pageSize);
    },
     onTableChange3:function(pagination, filters, sorter) {
        const pager = this.state.pagination3;
        pager.current = pagination.current;
        pager.pageSize = pagination.pageSize;
        this.setState({
            pagination3: pager,
        });
        this.wechat_withdraw_all(pager.current,pager.pageSize);
    },
    show_ewm:function(){
        let self = this;
        this.qrcode_url();
        this.state.timer = setInterval(function(){
            self.setState({ewm_alert:'二维码已过期，请返回重新获取'},function(){
                clearInterval(self.state.timer);
                clearInterval(self.state.timer_l);
            });
        },60000);
        this.state.timer_l = setInterval(function(){
            self.bindwechat();
        },1000);
        this.setState({visible:true}); 
    },
    fee_show:function(){
        this.setState({key:Math.random(),fee_visible:true}); 
    },
    handleCancel:function(){
        let self = this;
        clearInterval(self.state.timer);
        clearInterval(self.state.timer_l);
        this.setState({visible:false,ewm_alert:''});
    },
    fee_handleCancel:function(){
        this.setState({fee_visible:false,key:Math.random(),fee:0,remark:'',errormsg:null,realmoney:'',moneyfee:''});
    },
    inputChange:function(e){
        let self = this;
        let dom = e.target;
        if(dom.id === "fee"){
            let realmoney = parseInt(dom.value*100*(1-self.state.withdraw_data.withdraw_fee))/100;
            let moneyfee = (dom.value-realmoney).toFixed(2);
            self.setState({fee:dom.value*100,realmoney:realmoney,moneyfee:moneyfee});
        }else if(dom.id === "remark"){
            self.setState({remark:dom.value});
        }else if(dom.id === "pswd"){
            self.setState({pswd:dom.value});
        }
    },
    tabChange:function(v){
        console.log(v);
        this.setState({tabs:v});
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
                        template = "<html><head><meta charset=\"UTF-8\"></head><body><table style=\"mso-number-format:'\@';\">{table}</table></body></html>",  
                        base64 = function(s) { return window.btoa(unescape(encodeURIComponent(s))) },  
                        format = function(s, c) {  
                            return s.replace(/{(\w+)}/g,  
                                    function(m, p) { return c[p]; }); }  
                return function(table, name) {  
                    table = $('div[aria-hidden="false"]').find('table')[0];
                    $('.order').attr('style',"mso-number-format:'\@';");
                    var ctx = {worksheet: name || 'Worksheet', table: table.innerHTML}  
                    window.location.href = uri + base64(format(template, ctx))  
                }  
            })() 
            tableToExcel();
        }
    },
    render: function (){
        let self = this;
        let alert = null;
        let tabpane = null;
        const columns = [ {
                  title: '时间',
                  dataIndex: 'time',
              }, {
                  title: '微信昵称',
                  dataIndex: 'to_nickname',
              },{
                  title: '金额（元）',
                  dataIndex: 'fee',
              },{
                  title: '备注',
                  dataIndex: 'remark',
              }];
        const columns2 = [ {
                  title: '时间',
                  dataIndex: 'time',
              }/*,{
                  title: '订单号',
                  dataIndex: 'order_no',
              }*/,{
                  title: '交易类型',
                  dataIndex: 'trade_type',
              },{
                  title: '金额（元）',
                  dataIndex: 'receipt',
              },{
                  title: '可提现金额（元）',
                  dataIndex: 'withdrawable_receipt',
              },{
                  title: '备注',
                  dataIndex: 'remark',
              }];
        const columns3 = [{
                    title:'时间',
                    dataIndex:'time',
                },{
                    title:'企业付款单号',
                    dataIndex:'payment_no',
                    className:'order'
                }/*,{
                    title:'微信昵称',
                    dataIndex:'to_nickname',
                }*/,{
                    title:'总代理名称',
                    dataIndex:'name',
                },{
                    title:'提现金额（元）',
                    dataIndex:'total_fee',
                },{
                    title:'手续费（元）',
                    dataIndex:'wechat_fee',
                },{
                    title:'手续费率',
                    dataIndex:'wechat_fee_rate',
                },{
                    title:'应到账金额（元）',
                    dataIndex:'fee',
                },{
                    title:'提现状态',
                    dataIndex:'status',
                },{
                    title:'累积提现金额（元）',
                    dataIndex:'total_fee_sum',
                },{
                    title:'可提现金额（元）',
                    dataIndex:'withdrawable_balance',
                },{
                    title:'账户结余（元）',
                    dataIndex:'balance',
                },{
                    title:'累计收益（元）',
                    dataIndex:'receipt_sum',
                }] 
        if(self.state.errormsg){
            alert = <Alert message={self.state.errormsg} type='error'/>
        }
        if(self.state.data.level === 4&&self.state.data.joinuped.wechat){
            tabpane = <TabPane tab="平台提现记录" key="3">
                        <Button type='primary' style={{margin:10}} onClick={self.method1}>导出</Button>
                        <Table
                            loading={self.state.loading}
                            columns={columns3} 
                            dataSource={self.state.records3} 
                            onChange={self.onTableChange3} 
                            pagination={self.state.pagination3}
                        />
                    </TabPane>
        }
        return (
            <MyLayout id={(id)=>{this.getData(id)}} data={(d)=>{this.setState({data:d})}}>
                <div className='withdraw_head'>
                    <div className='head_box' style={{border:0,float:'none'}}>
                        <span>账 户&ensp;结 余</span>
                        <b>￥{self.state.balance/100}</b>   
                    </div>
                    <div className='head_box'>
                        <span>可提现金额</span>
                        <b>￥{self.state.withdrawable_balance/100}</b>
                        <Button onClick={self.fee_show}>提现</Button>
                    </div>
                </div>
                <div className='wechat'>
                    <span className='wechat_name'>当前微信号：{self.state.nickname}</span>
                    <Button style={{verticalAlign:'bottom'}} onClick={self.show_ewm}>绑定/修改微信</Button>
                </div>
                <Tabs
                    defaultActiveKey="1"
                    tabPosition={'left'}
                    onChange={self.tabChange}
                >
                    <TabPane tab="个人收益明细" key="1">
                        <p className='withdraw_title'>累计收益：￥ {self.state.receipt_sum/100}</p>
                        <Table
                            loading={self.state.loading}
                            columns={columns2} 
                            dataSource={self.state.records2} 
                            onChange={self.onTableChange2} 
                            pagination={self.state.pagination2}
                        />
                    </TabPane>
                    <TabPane tab="个人提现记录" key="2">
                        <p className='withdraw_title'>累积提现金额：￥ {self.state.total_fee_sum/100}</p>
                        <Table
                            loading={self.state.loading}
                            columns={columns} 
                            dataSource={self.state.records} 
                            onChange={self.onTableChange} 
                            pagination={self.state.pagination}
                        />
                    </TabPane>
                    {tabpane}
                </Tabs>
                
                <Modal 
                    width="400px"
                    title='扫码添加/修改微信号'
                    visible={self.state.visible}
                    onCancel={self.handleCancel}
                    footer={[<Button key="back" type="primary" size="large" onClick={self.handleCancel}>返回</Button>]}
                >
                    <div style={{textAlign:'center'}}>
                        <QRCode level='H' size={256} value = {this.state.url}/>
                        <p>{self.state.ewm_alert}</p>
                    </div>
                </Modal>
                <Modal 
                    width="400px"
                    title={'提现(提现手续费为'+(self.state.withdraw_data.withdraw_fee*100).toFixed(1)+'%，不足一分按一分扣除)'}
                    visible={self.state.fee_visible}
                    onCancel={self.fee_handleCancel}
                    key={self.state.key}
                    footer={[<Button key="back" type="primary" size="large" loading={self.state.btn_loading} onClick={self.withdraw}>提现</Button>]}
                >
                    <div style={{marginBottom:10}}><Input id='fee' placeholder='请输入提现金额' onChange={self.inputChange}/></div>
                    <div style={{marginBottom:10}}><Input style={{color:'#000'}} disabled addonBefore={'到账金额'}  value={self.state.realmoney} /></div>
                    <div style={{marginBottom:10}}><Input style={{color:'#000'}} disabled addonBefore={'手续费'} value={self.state.moneyfee} /></div>
                    <div style={{marginBottom:10}}><Input id='remark' placeholder='请输入备注' onChange={self.inputChange}/></div>
                    <div style={{marginBottom:10}}><Input id='pswd' type='password' placeholder='请输入登录密码' onChange={self.inputChange}/></div>
                    {alert}
                </Modal>
            </MyLayout>
        );
    }
});


export default WithDraw;
export { WithDraw };