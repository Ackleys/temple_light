import React, {Component} from 'react';
import { withRouter, RouteComponentProps } from 'react-router-dom';
import { Col, Row, Card, Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';

import api from '@api/auth';

import style from './style.module.less';

@withRouter
export default class extends Component<Partial<RouteComponentProps>, {
  loading: boolean,
}> {
  readonly state = {
    loading: false,
  }

  render() {
    const { history } = this.props;
    const { loading } = this.state;
    return (
      <>
        <Row 
          className={style.login}
          justify='space-around'
          align='middle'
        >
          <Col xs={20} sm={16} md={12} lg={10} xl={8} xxl={6} className={style.col}>
            <Card title='用户登录'>
              <Form onFinish={async ({user, password}) => {
                try {
                  this.setState({loading: true});
                  await api.login({
                    phone: user,
                    pswd: password,
                  });
                  history?.replace('/');
                } catch(e) {
                  message.error(e.response.data.msg);
                } finally {
                  this.setState({loading: false});
                }
                
              }}>
                <Form.Item
                  name='user'
                  rules={[{required: true, message: '请输入用户名'}]}
                >
                  <Input prefix={<UserOutlined />} placeholder='用户名'/>
                </Form.Item>
                <Form.Item
                  name='password'
                  rules={[{required: true, message: '请输入密码'}]}
                >
                  <Input.Password prefix={<LockOutlined />} placeholder='密码'/>
                </Form.Item>
                <Form.Item>
                  <Button type='primary' htmlType='submit' className={style.btn} loading={loading}>
                    登录
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </Col>
        </Row>
      </>
    )
  }
}