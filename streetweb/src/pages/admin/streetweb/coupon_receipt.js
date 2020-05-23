"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import {  Button, Icon, Modal,Input,Table,Upload,Alert,Popconfirm,message,Switch} from 'antd';
import {MyLayout}     from '../common/layout.js';
const Search = Input.Search;
const CouponReceipt = React.createClass({
    getInitialState: function() {
        return{
            records:[],
            data:{},
            loading:false,
            errormsg:null,
            src:'',
            code:'',
            visible:false,
            condition:true
        }
    },
    componentWillMount:function(){
        
    },
    componentDidMount:function(){
   
    },       
    use_coupon:function(){
        let url = window.API_PREFIX+'/advertiser/coupon_receipt/use';
        var self = this;
        self.setState({loading:true,visible:false});
        var callback = function(err,res){
            if(err){
                self.setState({loading:false});
            }else{
                console.log(res.body); 
                self.setState({loading:false});          
                self.search(self.state.code); 
            }
        };
        let data = {
            code:self.state.code
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
    time:function (now) {
        let y = now.getFullYear();
        let m = now.getMonth() + 1;
        let d = now.getDate();
        return y + "-" + (m < 10 ? "0" + m : m) + "-" + (d < 10 ? "0" + d : d) + " " + now.toTimeString().substr(0, 8);
    },
    search:function(v){
        var self = this;
        var url  = window.API_PREFIX+'/advertiser/coupon_receipt/search';
        var callback = function(err,res){
            if(err){
                message.error(err.err.msg);    
            }else{
                console.log(res.body);
                res.body.data.key = 1;
                res.body.data.code = v;
                res.body.data.time = self.time(new Date(res.body.data.time*1000));
                if(res.body.data.used){
                    self.setState({condition:false});
                }else{
                     self.setState({condition:true});
                }
                self.setState({records:[res.body.data],code:v});   
            }
        };
        var xhr  = new XMLHttpRequest();
        xhr.open("POST", url);
        let data = {code:v};
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
    handleVisibleChange:function (visible)  {
    console.log(this.state.condition);
    console.log(visible);
    if (this.state.condition) {
        this.setState({ visible });
    } else {
      this.setState({ visible:false }); // show the popconfirm
    }
  },
    render: function (){
        let self = this;
        let errormsg = null;
        let columns = [ {
                            title: '传单券码',
                            dataIndex: 'code',
                            
                        },{
                            title: '使用时间',
                            dataIndex: 'time',
                            render:(t,re)=>{
                                if(!re.used){
                                    return '未使用'
                                }else{
                                    return t;
                                }
                            }
                        }, {
                            title: '使用传单',
                            dataIndex: 'used',
                            render:(t,re) => {
                                let dis = '';
                                let word = '';
                                if(t){
                                    dis = true;
                                    word = '已使用';
                                }else{
                                    dis = false;
                                    word = '未使用';
                                }
                                return  <Popconfirm 
                                            title="确定使用该传单吗" 
                                            onConfirm={self.use_coupon} 
                                            visible={this.state.visible}
                                            onVisibleChange={this.handleVisibleChange}
                                            onCancel={()=>{this.setState({visible:false})}}
                                            okText="是" 
                                            cancelText="否">
                                            <Button type='primary' loading={self.state.loading} disabled={dis}>{word}</Button>
                                        </Popconfirm>
                            }
                        }
                        ];
        if ( self.state.errormsg ) {
            errormsg = <Alert message={this.state.errormsg} type="error" />;
        }
        return (
            <MyLayout>
                <div style = {{height:'8vh'}}>
                    <div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
                    <Search placeholder="请输入传单右下角编号"
                        style={{ width: 200,marginLeft:20 }}
                        onSearch={self.search} />
                </div>
                <Table
                    columns={columns} 
                    dataSource={self.state.records} 
                />
            </MyLayout>
        );
    }
});
export default CouponReceipt;
export { CouponReceipt };