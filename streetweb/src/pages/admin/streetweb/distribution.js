"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';
import {  Button, Menu,  Icon, Table,Modal,Input,Alert,message,Select,Popconfirm} from 'antd';
import {MyLayout}     from '../common/layout.js';
const Option = Select.Option;
const Search = Input.Search;
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
function accAdd(arg1,arg2){
    var r1,r2,m;
    try{r1=arg1.toString().split(".")[1].length}catch(e){r1=0}
    try{r2=arg2.toString().split(".")[1].length}catch(e){r2=0}
    m=Math.pow(10,Math.max(r1,r2))
    return (arg1*m+arg2*m)/m
}
function accSub(arg1,arg2){ 
return accAdd(arg1,-arg2); 
} 
const Distribution = React.createClass({
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
            salesmen:[],
            agent_id:'',
            visible:false,
            visible_bo:false,
            arr_bo:[],
            rate:0,
            input_show:false,
            //level:'',
            errormsg:'百分比要写成小数形式，例如5%填写为0.05，和要为1',
            editmoney:false,
            slevel:0,
            btn_loading:false,
            self:0,
            sl1:0,
            sl2:0,
            sl3:0,
            key:0,
        };
    },
    componentWillMount:function(){
        //this.get_msg();
        this.type();
        this.get_agent();
        //this.getData();
    },
    get_agent:function(page,psize){
    let self = this;
    const pager = this.state.pagination;
    let url = window.API_PREFIX+'/agent/sub_salesman/fetch';
    var callback = function(err,res){
          if(err){
                //console.log(err);
          }else{
                //console.log(res.body);
                self.setState({salesmen:res.body.data.salesmen});
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
    equ_list:function(page=1,psize=10){
        var self = this;
        var url  = window.API_PREFIX+"/device/salesman/fetch?page="+page+'&psize='+psize;
        var callback = function(err,res){
          if(err){
  
          }else{
                //console.log(res.body);
                let num = 0;
                let arr = []
                let pager = self.state.pagination;
                res.body.data.devices.forEach(function(q,i){
                    q.cat = self.cat_change(q.cat);
                    q.key = q.imei;
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
        console.log(selectedRowKeys);
       this.setState({ selectedRowKeys });
       this.setState({ imei:selectedRowKeys });
    },
    onSelect:function(record,select,selectedRows){
        if(select){
            //this.state.imei.push(record.imei);
        }else{
            //this.state.imei.remove(record.imei);
        }
    }, 
    fruzzy_seach_name:function(n){
        let self = this;
        let url = window.API_PREFIX+'/agent/search?page=1&psize=999999';
        var callback = function(err,res){
            if(err){
  
            }else{
              console.log(res.body);
              let data={};
              data['agents'] = res.body.data.agents;
              self.setState(data);
            }
        };
        let data={};
        data.name= n;
        data.salesman = 0;
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
    seChange:function(v){
         console.log(v)
        this.setState({value:v});
        this.fruzzy_seach_name(v);
    },
    seSelect:function(v,o){
        this.setState({value:o.props.children,agent_id:v});
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
            if(self.state.slevel===0){

                self.setState({sl1:0,sl2:0,sl3:0,self:0,visible:true});
            }else{
                self.setState({sl1:0,sl2:0,sl3:0,self:1},()=>{
                    self.set_group();
                });
            }
            
        }
    },
    editmoney:function(){
        let self = this;
        let url = window.API_PREFIX+'/device/update';
        var callback = function(err,res){
            if(err){
                self.setState({errormsg:err.err.msg,btn_loading:false});
            }else{
               message.success('修改成功！');
               self.setState({visible:false,editmoney:false,btn_loading:false});
               self.equ_list();
            }
        };
        let data = {
            imeis:[self.state.self_imei],
            //num:1,
            update:{ 
                self:parseFloat(self.state.self),
                sl1:parseFloat(self.state.sl1),
                sl2:parseFloat(self.state.sl2),
                sl3:parseFloat(self.state.sl3)
            } 
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
    myself:function(imei){
        this.setState({visible:true,editmoney:true,self_imei:imei});
    },
    set_group:function(){
        let self = this;
        if(isNaN(self.state.self)){
            self.setState({errormsg:'请填入正确的自己的比例'});
            return false;
        }else if(isNaN(self.state.sl1)){
            self.setState({errormsg:'请填入正确的一级业务员的比例'});
            return false;
        }else if(isNaN(self.state.sl2)){
            self.setState({errormsg:'请填入正确的二级业务员的比例'});
            return false;
        }else if(isNaN(self.state.sl3)){
            self.setState({errormsg:'请填入正确的三级业务员的比例'});
            return false;
        }
        if(self.state.slevel===0){
            let arr = [self.state.self,self.state.sl1,self.state.sl2,self.state.sl3];
            if(arr.reduce(accAdd)!==1){
                self.setState({errormsg:'比例之和不为1,请重新输入'});
                return false;
            }
        }
        self.setState({btn_loading:true});
        if(self.state.editmoney){
            self.editmoney();
        }else{   
            let url = window.API_PREFIX+'/device/salesman/multi/distribution';
            let callback = function(err,res){
                if(err){
                    if(self.state.slevel){
                        message.error(err.err.msg);
                    }
                    self.setState({errormsg:err.err.msg});
                }else{
                   message.success('分组成功！');
                   self.setState({input_show:false,visible:false,selectedRowKeys:[],imei:[],btn_loading:false,key:Math.random(),self:'',sl1:'',sl2:'',sl3:''});
                   self.equ_list();
                }
            };
            let data = {
                imeis:self.state.imei,
                to_agent:self.state.agent_id,
                self:self.state.self,
                sl1:self.state.sl1,
                sl2:self.state.sl2,
                sl3:self.state.sl3,
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
        }
    },
    input_change:function(e){
        console.log(e.target.value);
        if(e.target.value<1&&e.target.value>=0){
            if(e.target.id === 'self'){
                this.setState({self:parseFloat(e.target.value),errormsg:null});
            }else if(e.target.id === 'rate1'){
                this.setState({sl1:parseFloat(e.target.value),errormsg:null});
            }else if(e.target.id === 'rate2'){
                this.setState({sl2:parseFloat(e.target.value),errormsg:null});
            }else if(e.target.id === 'rate3'){
                this.setState({sl3:parseFloat(e.target.value),errormsg:null});
            }
        }else{
            this.setState({errormsg:'请输入小于1大于等于零的数字'});

        }
    },
    update:function(data){
        let url = window.API_PREFIX+'/device/update';
        let self = this;
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
        this.setState({visible:false,errormsg:'请注意您选择的分成为自己获得的分成比例',editmoney:false,btn_loading:false,key:Math.random()});
    },
    getlevel:function(l){
        this.setState({slevel:l});
    },
    recycle:function(re){
        let url = window.API_PREFIX+'/device/recycle';
        let self = this;
        var callback = function(err,res){
            if(err){
                message.success(err.err.msg);
            }else{
               message.success('收回成功！');
               self.equ_list();
            }
        };
                
        var xhr  = new XMLHttpRequest();
        xhr.open("PATCH", url);
        xhr.setRequestHeader("Content-Type", "application/json;charset=utf-8") ; 
        xhr.send(JSON.stringify({imei:re.imei}));
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
    render: function (){
        let self = this;
        let columns = [{
                    title: '业务员',
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
                    title: '上级分成 | 我的分成 | 下级分成',
                    dataIndex: ' ',
                    render:(text,re) => {
                        let top=[0,0];
                        let mid=0;
                        let bot=[0,0];
                        let data=[];
                        re.self = accSub(1,[re.sl3,re.sl2,re.sl1].reduce(accAdd));
                        /*if(re.operator_level === 4){
                            data = [{agent:'省级代理','fencheng':re.l3},{agent:'市县代理','fencheng':re.l2},{agent:'运营商','fencheng':re.l1}];
                        }else if(re.operator_level === 3){
                            data = [{agent:'市县代理','fencheng':re.l2},{agent:'运营商','fencheng':re.l1}];
                        }else if(re.operator_level === 2){
                            data = [{agent:'运营商','fencheng':re.l1}];
                        }else{
                            data = [{agent:'该运营商已经是最后一级','fencheng':''}];
                        }*/
                        if(self.state.slevel === 0){
                            mid = re.self;
                            bot = [re.sl3,re.sl2,re.sl1];
                            data = [{agent:'一级业务员','fencheng':re.sl1},{agent:'二级业务员','fencheng':re.sl2},{agent:'三级业务员','fencheng':re.sl3}];
                        }else if(self.state.slevel === 1){
                            top = [re.self,0] 
                            mid = re.sl1;
                            bot = [re.sl2,re.sl3];
                            data = [{agent:'二级业务员','fencheng':re.sl2},{agent:'三级业务员','fencheng':re.sl3}];
                            
                        }else if(self.state.slevel === 2){
                            top = [re.self,re.sl1]
                            mid = re.sl2;
                            bot = [re.sl3,0];
                            data = [{agent:'三级业务员','fencheng':re.sl3}];
                            
                        }else{
                            data = [{agent:'该业务员已经是最后一级','fencheng':''}];
                        }
                        return(
                            <span>
                                <a href="#" style={{color: '#666'}}>{(top.reduce(function(prev, curr,){
                                                          return prev + curr;
                                                      })*100).toFixed(2)+'%'}
                                </a>
                                <span className="ant-divider" />
                                <a href="#" style={{color: '#666'}} >{mid*100+'%'}</a>
                                <span className="ant-divider" />
                                <a href="#" onClick={this.bottom_agent.bind(self,data)}>{(bot.reduce(function(prev, curr,){
                                                          return prev + curr;
                                                      })*100).toFixed(2)+'%'}
                                </a>
                            </span>
                        )},
                }];
        if(self.state.slevel === 0){
            columns.push({
                    title: '修改分成',
                    dataIndex: 'back',
                    render:(text,re)=>{
                        return  <Button onClick={()=>{
                            if(!re.operator){
                                alert('请分出设备后在进行修改');
                                return false;
                            }
                            self.setState({sl1:re.sl1,sl2:re.sl2,sl3:re.sl3,self:accSub(1,[re.sl3,re.sl2,re.sl1].reduce(accAdd))});
                            self.myself(re.imei);
                        }}>修改</Button>
                                
                    }
                })
        }
        const rowSelection = {
              selectedRowKeys:self.state.selectedRowKeys,
              onChange: self.onSelectChange,
              onSelect: self.onSelect,
        };
        let option = null;
        if(self.state.salesmen.length>0){
            option = self.state.salesmen.map((d,i)=>{
                        return (<Option key={i} value={d.key}>{d.title}</Option>)
                    })
        }        
        let alerts = null;
        if(self.state.errormsg){
            alerts = <Alert message={self.state.errormsg} type="error" />
        }
        return (
          <MyLayout slevel={(l)=>{self.getlevel(l)}}>
            <div style = {{height:'8vh'}}>
                <div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
                <Search placeholder="请输入imei"
                    style={{ width: 200,marginLeft:20 }}
                    onSearch={self.search.bind(self,'imei')} />
                <Search placeholder="请输入设备自编号"
                    style={{ width: 200,marginLeft:20 }}
                    onSearch={self.search.bind(self,'device_id')} />
            </div>
            <Table
                loading={self.state.loading}
                rowSelection={rowSelection} 
                columns={columns} 
                dataSource={self.state.records} 
                onChange={self.onTableChange} 
                pagination={self.state.pagination}
                footer={()=>'请在表格中对设备进行勾选，然后选择业务员后进行提交'}
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
            <Button type='primary' onClick={self.group}>提交</Button>
            <Modal 
              width="450px"
              title="分成设置（占总金额的百分比，例如5%，写成0.05）" 
              visible={this.state.visible}
              onOk={this.set_group}
              onCancel={this.handleCancel}
              key={self.state.key}
              footer={[<Button type = 'primary' key="back" size="large" onClick={this.handleCancel}>取消</Button>,
                        <Button type = 'primary' key="submit" size="large" onClick={this.set_group} loading={self.state.btn_loading}>提交</Button>
              ]}
            >
                <Input defaultValue={self.state.self} addonBefore={'我的分成'} type='number' id='self' onChange={self.input_change} placeholder='请输入你抽成的百分比，填写格式为小数' />
                <Input defaultValue={self.state.sl1} addonBefore={'一级分成'} type='number' id='rate1' onChange={self.input_change} placeholder='请输入一级业务员抽成的百分比，填写格式为小数' />
                <Input defaultValue={self.state.sl2} addonBefore={'二级分成'} type='number' id='rate2' onChange={self.input_change} placeholder='请输入二级业务员抽成的百分比，填写格式为小数' />
                <Input defaultValue={self.state.sl3} addonBefore={'三级分成'} type='number' id='rate3' onChange={self.input_change} placeholder='请输入三级业务员抽成的百分比，填写格式为小数' />
                {alerts}
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


export default Distribution;
export { Distribution };