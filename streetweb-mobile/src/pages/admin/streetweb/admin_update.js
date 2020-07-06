"use strict";

import React        from 'react';
import ReactDOM     from 'react-dom';
import { Form, Icon } from '@ant-design/compatible';
import {  Button, Menu, Modal,Input ,Upload,message } from 'antd';
import {MyLayout}     from '../common/layout.js';
const FormItem = Form.Item;
import {browserHistory} from 'react-router';
var AdminUpdate = require('create-react-class')({
  	getInitialState: function() {
		return{
			fileList0:[],
		}
	   
  	},
  	componentWillMount:function(){

  	},
 	componentDidMount:function(){
   
  	},
  	handleSubmit:function(e){
    	let self = this;
        e.preventDefault();
        this.props.form.validateFieldsAndScroll((err, values) => {
          if (!err) {
                console.log('Received values of form: ', values);
                let url = window.API_PREFIX+"/god/info/update";
                var callback = function(err,res){
                    if(err){
                        message.error(err.err.msg);
                    }else{
                        console.log(res.body);
                        message.success('修改成功！');
                    }
                };
                let myForm = new FormData();
                let data = {}
                for (let i in values){
                	if(values[i]!==undefined){
	                	if(i === '0'){
	                		myForm.append(i,values[i].fileList[0]);
	                		myForm.append('postfix',self.state.postfix);
	                	}else{
	                		data[i] = values[i];
	                	}
                	}
                }
                myForm.append('update',JSON.stringify(data));
                var xhr  = new XMLHttpRequest();
                xhr.open("POST", url,true); 
                xhr.send(myForm);
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
        })
    },
    customRequest0(info){
		console.log(info.file);
	    this.setState({fileList0:[info.file]});
    },
    file:function(rule,v,callback,source){
    	let self = this;
    	console.log(source);
    	if(source[rule.field]){
	    	if(source[rule.field].file.type==='image/jpeg'||source[rule.field].file.type==='image/png'){
    			if(source[rule.field].file.size/1024>20){
    				callback(false);
    			}else{
    				let arr = source[rule.field].file.name.split('.');
    				self.setState({postfix:arr[arr.length-1]});
    				callback();
    			}
	    	}else{
	    		callback(false);
	    	}
    	}else{
    		callback();
    	}
    },

    checkAgent:function(){
        if(localStorage.getItem("level")<4){
        	alert('您没有此权限，请申请为总代理。');
		}
	},
  	render: function (){
		let self = this;
    	const { getFieldDecorator, getFieldValue } = this.props.form;
		return (
	  		<MyLayout>
	   			<Form onSubmit={this.handleSubmit} className='agentsetting' >
		            <FormItem label='title' extra='网站标题，例如：xx后台管理系统'>
		              {getFieldDecorator('title', {
		                
		              })(
		                <Input placeholder="请输入网站标题" />
		              )}
		            </FormItem>
		            <FormItem label='网站logo' extra='请上传jpg或png格式的图片，大小不超过20KB'>
		              {getFieldDecorator('0', {
		                  	validateTrigger:'onChange',
			                rules: [{
			                  validator:self.file, message: '请正确上传后提交',
			                }]
		              })(
		                	<Upload name="file0" fileList={self.state.fileList0} customRequest={self.customRequest0}>
							    <Button>
							      	<Icon type="upload" /> 网站logo
							    </Button>
						  	</Upload>
		              )}
		            </FormItem>
		            <Button htmlType='submit'>提交</Button>
		        </Form>
	  		</MyLayout>
		);
  	}
});

AdminUpdate = Form.create()(AdminUpdate);
export default AdminUpdate;
export { AdminUpdate };