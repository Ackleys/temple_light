"use strict";;
import React        from 'react';
import ReactDOM     from 'react-dom';
import {Link}       from 'react-router';
import QRCode       from 'qrcode.react';
import { SettingOutlined } from '@ant-design/icons';
import { Button, Menu, Table, Input, Alert, Modal, message } from 'antd';
import {MyLayout}     from '../common/layout.js';
import { browserHistory} from 'react-router';
const Search = Input.Search;
String.prototype.times = function(n) { return (new Array(n+1)).join(this);};
const MyEquipments = require('create-react-class')({

	getInitialState: function() {
		return {
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
			slevel:1,
		};
	},
	componentWillMount:function(){
		this.get_msg();
		this.type();
		
	},
	type:function(){
		var self = this;
		console.log(window.API_PREFIX);
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
	equ_list:function(page,psize,map){
		var self = this;
		var url  = window.API_PREFIX+'/device/salesman/fetch?page='+page+'&psize='+psize;
		var callback = function(err,res){
			if(err){
				message.error(err.err.msg);
				self.setState({loading:false});
			}else{
					console.log(res.body);
					let num = 0;
					let arr = []
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
						/*if(q.comm_state === 1){
	                        q.comm_state = '在线';
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
	                    }else {
	                        q.comm_state = '关机';
	                        q.signal = '无信号 '+q.signal;
	                    }*/
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
					})
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
							let translateCallback = function (data){
							    if(data.status === 0) {
							        let marker = new BMap.Marker(data.points[0]);
							        arrs.push(data.points[0]);
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
							        })
							    }
						        if(i === res.body.data.devices.length-1){
						        	map.setViewport(arrs);
						        }
						    }
							let convertor = new BMap.Convertor();
					        let pointArr = [];
					        pointArr.push(new BMap.Point(d.lng-0,d.lat-0));
					        convertor.translate(pointArr, 1, 5, translateCallback);
						})  
					}else{
						const pager = self.state.pagination;
						pager.total = res.body.data.count;
						self.setState({records:res.body.data.devices,selectedRowKeys:arr,loading:false,pagination:pager});
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
		console.log('selectedRowKeys changed: ', selectedRowKeys);
		console.log('selectedRows changed: ', selectedRows);
		this.setState({ selectedRowKeys });
	},
	onSelect:function(record,select,selectedRows){
		if(select){
			this.update(record.imei,1);
		}else{
			this.update(record.imei,0);

		}
		console.log(record);
		console.log(select);
	},
	update:function(imei,map){
		let url = window.API_PREFIX+'/device/update';
		var self = this;
		
		var callback = function(err,res){
			if(err){
				self.setState({errormsg:err.msg});
			}else{
				 self.equ_list();
			}
		};
		
		let update = {
			map_display:map
		}
		
		let data={
			start_imei:imei,
			num:1,
			update:update,
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
	show_fn:function(){
		let self = this;
		self.setState({show:!self.state.show},function(){
			if(self.state.show){
				self.setState({btn:'查看列表'});
				let map = new BMap.Map("maps");
				map.centerAndZoom(new BMap.Point(116.404, 39.915), 12); 
				map.addControl(new BMap.MapTypeControl());
				let top_left_control = new BMap.ScaleControl({anchor: BMAP_ANCHOR_TOP_LEFT});// 左上角，添加比例尺
				let top_left_navigation = new BMap.NavigationControl();  //左上角，添加默认缩放平移控件
				map.addControl(top_left_control);        
				map.addControl(top_left_navigation);     
				let geolocation = new BMap.Geolocation();
				if(self.state.records.length === 0){
					geolocation.getCurrentPosition(function(r){
						if(this.getStatus() == BMAP_STATUS_SUCCESS){
							map.panTo(r.point);
							console.log('您的位置：'+r.point.lng+','+r.point.lat);
						}
						else {
						}        
					},{enableHighAccuracy: true})
				}
				map.addEventListener("tilesloaded", function() {  
						map.enableScrollWheelZoom();
				}) //启用滚轮放大缩小，默认禁用
				self.setState({mp:map})
				self.equ_list(1,9999,map);
			}else{
				self.setState({btn:'查看地图'});
			}
		 
		});
		
	},
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
	show_ewm:function(re){
		let self = this;
		console.log(re.imei);
		let url ;
		let id ;
		if(re.salesman_agent_id){
			id = re.salesman_agent_id;
		}else{
			id = re.owner_agent_id;
		}
		if(re.cat === '倒计时'){
			if(re.nopay){
				url = window.QRcode_url+'chair_nopay/'+id+'/?imei='+re.imei+'&v=2.0';
			}else{
				url = window.QRcode_url+'chair/'+id+'/?imei='+re.imei+'&v=2.0';
			}
		}else if(re.cat === '投币器'){
			url = window.QRcode_url+'doll/'+id+'/?imei='+re.imei+'&v=2.0';
		}
		console.log(url)
		this.setState({visible:true,url:url,title:'二维码'},function(){
			let id = re.id+'';
			let num = 5-id.length
			if(num>0){
				id = '0'.times(num)+id;
			}
			let a = document.getElementsByTagName('canvas');
			let bb = a[0].getContext('2d');
			bb.fillStyle = '#fff';    
			bb.fillRect(156,236,100,30);
			bb.fillStyle = '#000';
			bb.font = '18px Adobe Ming Std';  
			bb.fillText(id,176,253); 
		});
	 
	},
	show_tc:function(re){
		let url = window.API_PREFIX+'/device/product/fetch';
		var self = this;
		var callback = function(err,res){
				if(err){

				}else{
						console.log(res.body);           
						self.setState({package:res.body.data,visible:true,title:'套餐'});
				}
		};
		let data = {
				device_id:re.id-0
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
		this.setState({visible:false,url:'',package:''});
	},
	handleCancel:function(){
		this.setState({visible:false,url:'',package:''});
	},
	modal_body:function(){
		let modal_body = null;
		if(this.state.url){
			modal_body = (<div style={{textAlign:'center'}}>
							<QRCode level='L' size={256} value = {this.state.url}/>
							<p>右键保存二维码即可</p>
						</div>);
		}else if(this.state.package){
			if(this.state.package.length === 0){
				modal_body='该设备暂无套餐';
			}else{
				modal_body = this.state.package.map((q,i)=>{
					let a;
					if(q.cat === 0 ){
						a = q.price/100+'元'+q.value/60+'分钟';
					}else{
						a = q.price/100+'元'+q.value+'个脉冲 ';
					}
					return (
						
							<p key={i} style={{textAlign:'center'}}>{i+1+'、'+a}</p>

						)
				})
			}
		}
		console.log(modal_body)
		return modal_body;
	},
	edit_equ:function(re){
		console.log(re);
		sessionStorage.setItem('re',JSON.stringify(re));
		/*sessionStorage.setItem('key',2);
		sessionStorage.setItem('subkey','2_1');*/
		browserHistory.push(window.URL_PREFIX+'/editequipment');
		return false;
	},
	alledit:function(){
		/*sessionStorage.setItem('key',2);
		sessionStorage.setItem('subkey','2_1');*/
		browserHistory.push(window.URL_PREFIX+'/editequipment');
	},
	search:function(t,v){
		var self = this;
        var url  = window.API_PREFIX+'/device/search';
        var callback = function(err,res){
            if(err){
                message.error(err.err.msg);
                
            }else{
                console.log(res.body);
				let num = 0;
				let arr = []
				let q = res.body.data;
				q.cat = self.cat_change(q.cat);
				q.key = 0;
				if(q.map_display){
					arr.push(num);
				}
				if(q.use_state){
					q.use_state = '使用中';
				}else if(!q.use_state){
					q.use_state = '空闲';
				}
				/*if(q.comm_state === 1){
                    q.comm_state = '在线';
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
                }else {
                    q.comm_state = '关机';
                    q.signal = '无信号 '+q.signal;
                }*/
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
				if(self.state.show){
					let maps = self.state.mp;
					let arrs = [];
					let content = ''; 
					let opt = {
				        width : 0,     // 信息窗口宽度
				        height: 0,     // 信息窗口高度
				        title : "信息窗口" , // 信息窗口标题
				        enableMessage:true//设置允许信息窗发送短息
				    };
					
					let translateCallback = function (data){
					    if(data.status === 0) {
					        let marker = new BMap.Marker(data.points[0]);
					        arrs.push(data.points[0]);
					        maps.addOverlay(marker);
					        
					        marker.addEventListener("click", function(e){
						        content = 	"IMEI："+q.imei+"<br />"
	                      					+"信号："+q.signal+"<br />"
	                      					+"状态："+q.comm_state+"<br />"
	                      					+"运营商："+q.operator+"<br />";
	                      		let p = e.target;
	                      		let po = new BMap.Point(p.getPosition().lng, p.getPosition().lat); 
					            let infoWindow = new BMap.InfoWindow(content,opt);  // 创建信息窗口对象 
					            maps.openInfoWindow(infoWindow,po); //开启信息窗口
					        })
					    }				        
				        maps.setViewport(arrs);   
				    }
					let convertor = new BMap.Convertor();
			        let pointArr = [];
			        pointArr.push(new BMap.Point(q.lng-0,q.lat-0));
			        convertor.translate(pointArr, 1, 5, translateCallback);
				    
				}else{
					const pager = self.state.pagination;
					pager.total = 1;
					self.setState({records:[q],selectedRowKeys:arr,loading:false,pagination:pager});
				}
               
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
	render:function(){
		let self = this;
		let content = null;
		/*let modal_body = null;
		if(this.state.url){
				modal_body = (<QRCode level='H' size={256} value = {this.state.url}/>);
			}*/
		const columns = [ {
							title: '自编号',
							dataIndex: 'id',
						}, {
							title: 'IMEI(点击查看设备套餐)',
							dataIndex: 'imei',
							render:(text,re) => <a onClick={self.show_tc.bind(self,re)}>{text}</a>,
						},{
							title: '设备类型',
							dataIndex: 'cat',
						},{
							title: '生成二维码',
							dataIndex: 'qrcode',
							render:(text,re) => <Button onClick={self.show_ewm.bind(self,re)}>生成二维码</Button>,
						},{
							title: '信号强度(强度值)',
							dataIndex: 'signal',
						},{
							title: '投放地点',
							dataIndex: 'address',
						},{
							title:'通信状态',
							dataIndex:'comm_state',
						},{
							title: '业务员',
							dataIndex: 'operator',
						},{
							title: '备注',
							dataIndex: 'remark',
						}, {
							title: '编辑',
							dataIndex: 'edit',
							render:(text,re) => <a onClick={self.edit_equ.bind(self,re)}><SettingOutlined /></a>,
						}];
		const rowSelection = {
					selectedRowKeys:self.state.selectedRowKeys,
					onChange: self.onSelectChange,
					onSelect: self.onSelect,
			 
		};
		if(self.state.slevel){
			columns.pop();
			if(self.state.slevel === 3){
				columns.push({
					title: '上级分成 | 我的分成',
							dataIndex: 'sl1',
							render:(text,re) => <span>
					                                <span href="#" style={{color: '#666'}}>{(1-re.sl3)*100}%</span>
					                                <span className="ant-divider" />
					                                <span href="#" style={{color: '#666'}}>{re.sl3*100}%</span> 
					                            </span>
				})
			}
		}
		if(self.state.show){
			content=(<div id = 'maps' style={{height:'80vh'}}></div>)
		}else{
			content = (
					<Table
						loading={self.state.loading}
						rowSelection={rowSelection} 
						columns={columns} 
						dataSource={self.state.records} 
						onChange={self.onTableChange} 
						pagination={self.state.pagination}
					/>
				)
		}
		return(
			<MyLayout slevel={(sl)=>{this.setState({slevel:sl})}}>
				<div style = {{height:'8vh'}}>
					<div style={{height:'100%',verticalAlign:'middle',display:'inline-block'}}></div>
					<Button onClick = {self.show_fn}>{self.state.btn}</Button>
					{/*<Button onClick = {self.alledit}>批量编辑</Button>*/}
					<Search placeholder="请输入imei"
					    style={{ width: 200,marginLeft:20 }}
					    onSearch={self.search.bind(self,'imei')} />
					<Search placeholder="请输入设备自编号"
					    style={{ width: 200,marginLeft:20 }}
					    onSearch={self.search.bind(self,'device_id')} />
				</div>
				{content}
				<Modal 
							width="300px"
							title={this.state.title} 
							visible={this.state.visible}
							onOk={this.handleOk}
							onCancel={this.handleCancel}
					>
							{self.modal_body()}
						</Modal>
			</MyLayout>
		)
	}
})
export default MyEquipments;
export { MyEquipments };