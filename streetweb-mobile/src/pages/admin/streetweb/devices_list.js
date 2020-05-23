"use strict";

import React        from 'react';
import {browserHistory } from 'react-router';
import {SearchBar, ListView, List, Badge} from 'antd-mobile';
import * as ReactDOM from "react-dom";

const Item = List.Item;
const Brief = Item.Brief;


const dataSource = new ListView.DataSource({
    rowHasChanged: (row1, row2) => row1 !== row2,
});


const DevicesList = React.createClass({
    getInitialState: function() {
        return {
            dataSource,
            type:[],
            records:[],
            "pagination": {
                "showSizeChanger":true,
                //defaultPageSize: 10,
                //defaultCurrent : 1,
                "current"        : 1,
                "pageSize"       : 10,
                "pageSizeOptions": ['10', '25', '50', '100']
            },
            selectedRowKeys:[],
            loading:true,
            show:false,
            visible:false,
            btn:'查看地图',
            url:'',
            package:'',
            title:'',
            agent_id:'',
            level:2,
            imei:[],//批量选择保存的imei
            edit_show:false,//批量编辑界面显示
            height: document.documentElement.clientHeight * 3 / 4,
        };
    },

    componentWillMount:function(){
        this.get_msg();
        this.type();
    },

    //如何修改呢, 我们到底继续显示就可以了, 不用显示页面
    componentDidMount: function() {
        //在这里调用dataSource的方法
        //dataSource: this.state.dataSource.cloneWithRows(this.rData),
        const hei = document.documentElement.clientHeight - ReactDOM.findDOMNode(this.lv).parentNode.offsetTop;
        this.setState({
            height: hei,
        });
    },


    // 获取agent_id 和 agent_name
    get_msg:function(){
        let url = window.API_PREFIX+'/agent/cur';
        var self = this;
        var callback = function(err,res){
            if(err){

            }else{
                console.log(res.body);
                self.setState({agent_id:res.body.data.id,agent_name:res.body.data.name});
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
        console.log(window.API_PREFIX);

        //获取设备类型id-类型名字典
        var url = window.API_PREFIX+"/device/cat";

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

                //type: [{num: xx, value: xx}]
                self.setState({type:arr});

                //TODO: 先暂时显示第一页
                self.equ_list(1,10);
                return;
                //NOTE: 和页面相关的代码

                if(sessionStorage.getItem('psize')){
                    let pager = self.state.pagination;
                    pager.current = sessionStorage.getItem('page')-0;
                    pager.pageSize = sessionStorage.getItem('psize')-0;
                    self.setState({pagination:pager});
                    self.equ_list(sessionStorage.getItem('page'),sessionStorage.getItem('psize'));
                    sessionStorage.removeItem('page');
                    sessionStorage.removeItem('psize')
                }else{
                    self.equ_list(1,10);
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

    cat_change:function(t){
        let a = '';
        this.state.type.map(q=>{
            if(q.num === t+''){
                a = q.value;
            }
        });
        if(t>1){
            a = '倒计时';
        }
        return a;
    },

    equ_list:function(page,psize,map){
        var self = this;
        var url  = window.API_PREFIX+'/device/fetch?page='+page+'&psize='+psize;
        var callback = function(err,res){
            if(err){
                message.error(err.err.msg);
                self.setState({loading:false});
            }else{
                console.log(res.body);
                let num = 0;
                let arr = [];
                res.body.data.devices.forEach(function(q,i){
                    q.cats = self.cat_change(q.cat);  //q.cats 类型字符串
                    q.key = q.imei;                   //q.key imei码

                    if(!q.address) {
                        q.address = "未知地点";
                    }

                    if(q.map_display){
                        arr.push(num);
                    }
                    if(q.use_state){
                        q.use_state = '使用中';
                    }else if(!q.use_state){
                        q.use_state = '空闲';
                    }
                    if(q.comm_state === 1){
                        q.comm_state = '在线';
                    }else {
                        q.comm_state = '关机';
                    }
                    if(q.signal<=10){
                        if(q.signal<=0){
                            q.signal = '无信号 '+q.signal;
                        }else{
                            q.signal = '弱 '+q.signal;
                        }
                    }else if(q.signal<=14){
                        q.signal = '中 '+q.signal;
                    }else{
                        q.signal = '强 '+q.signal;
                    }
                    num++;
                });
                if(map){
                    let arrs = [];
                    let content = '';
                    let opt = {
                        width : 0,     // 信息窗口宽度
                        height: 0,     // 信息窗口高度
                        title : "信息窗口" , // 信息窗口标题
                        enableMessage:true//设置允许信息窗发送短息
                    };
                    res.body.data.devices.map((d,i)=>{
                        let pointArr = [];
                        if(d.lng==0){
                            return false;
                        }
                        pointArr.push(new BMap.Point(d.lng-0,d.lat-0));
                        let marker = new BMap.Marker(GpsToBaiduPoints(pointArr)[0]);
                        arrs.push(GpsToBaiduPoints(pointArr)[0]);
                        map.addOverlay(marker);
                        marker.addEventListener("click", function(e){
                            content = 	"IMEI："+d.imei+"<br />"
                                +"信号："+d.signal+"<br />"
                                +"状态："+d.comm_state+"<br />"
                                +"运营商："+d.operator+"<br />";
                            let p = e.target;
                            let po = new BMap.Point(p.getPosition().lng, p.getPosition().lat);
                            let infoWindow = new BMap.InfoWindow(content,opt);  // 创建信息窗口对象
                            map.openInfoWindow(infoWindow,po); //开启信息窗口
                        });
                        if(i === res.body.data.devices.length-1){
                            map.setViewport(arrs);
                        }
                    })
                }else{
                    const pager = self.state.pagination;
                    pager.total = res.body.data.count;
                    self.setState({
                        records:res.body.data.devices,  //NOTE: records数组就是设备数组
                        dataSource: self.state.dataSource.cloneWithRows(res.body.data.devices),  //TODO: 这边需要注意一下
                        //selectedRowKeys:arr,
                        loading:false,
                        pagination:pager
                    });
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


    render: function () {
        return (
            <div>
                <SearchBar placeholder="请输入imei进行查询" maxLength={8} />
                <ListView
                    ref={el => this.lv = el /*用于获取组件高度*/}
                    dataSource={this.state.dataSource}
                    style={{height: this.state.height, overflow: 'auto'}}
                    renderHeader={() => <span>设备列表(显示为：设备类型+设备ID)</span>}
                    renderFooter={() => <div style={{padding: '30px', 'text-align': 'center'}}>暂无数据</div>}
                    renderRow={(rowData, sectionID, rowID) => (
                        <Item key={rowID} arrow="horizontal" extra={<Badge text={rowData.comm_state}/>}>
                            {rowData.cats + rowData.id} <Brief>{rowData.operator} | {rowData.address}</Brief>
                        </Item>
                    )} />
            </div>
        )
    }
});

export default DevicesList;
export { DevicesList };
