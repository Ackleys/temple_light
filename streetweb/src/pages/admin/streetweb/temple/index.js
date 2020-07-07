import React, {Component, Fragment} from 'react';
import Layout from '@common/layout';
import p from 'immer';

import { Empty, Button, Modal, Form, Input, Upload } from 'antd';
import { PlusOutlined } from '@ant-design/icons'

export default class extends Component {
  
  constructor(props) {
    super(props);
    this.state = {
      visible: false,
    };
    
  }

  showModal = () => {
    this.setState({
      visible: true,
    });
  }

  closeModal = () => {
    this.setState({
      visible: false,
    });
  }

  handleForm = async () => {
    if(this.form === undefined)
      return;

    try {
      const value = await this.form.validateFields()
      console.log(value)
    } catch(e) {
      console.log('err', e);
    }
  }

  onFinish = () => {

  }

  render() {
    const {visible} = this.state;

    return (
      <Layout>
        <Empty
          description='您尚未创建寺庙'
          style={{paddingTop: '40px'}}
        >
          <Button type='primary' onClick={this.showModal}>立即创建</Button>
        </Empty>
        {/* 
          您还未创建寺庙 -> 立即创建
          弹出模态框, 填写寺庙信息
        */}

        <Modal
          title='创建寺庙'
          visible={visible}
          onOk={this.handleForm}
          onCancel={this.closeModal}
          okText='创建'
          cancelText='取消'
        >
          <Form
            ref={form => this.form = form}
            onFinish={this.onFinish}
            labelCol={{span: 6}}
            wrapperCol={{span: 18}}
          >
            <Form.Item
              label='寺庙名称'
              name='temple_name'
              rules={[
                {
                  required: true,
                  message: '请输入寺庙名称',
                }
              ]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              label='联系人'
              name='contact_name'
            >
              <Input />
            </Form.Item>
            <Form.Item
              label='联系方式'
              name='contact_info'
            >
              <Input />
            </Form.Item>

            <Form.Item
              label='主图'
              name='picture'
              valuePropName='fileList'
            >
              <Upload
                listType='picture-card'
                showUploadList={false}
                accept='image/*'
                beforeUpload={() => false}
                style={{width: '100%'}}
              >
                <div>
                  <PlusOutlined />
                  <div className='ant-upload-text'>上传</div>
                </div>
              </Upload>

            </Form.Item>

          </Form>

        </Modal>

      </Layout>
    );
  }
};