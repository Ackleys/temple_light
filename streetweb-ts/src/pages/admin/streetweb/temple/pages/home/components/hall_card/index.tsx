import React, {Component, cloneElement} from 'react';

import { Button, Card, Col, Row, Tooltip, Popconfirm, Statistic, Space, Typography, Popover, Badge } from 'antd';
import { EditOutlined, DeleteOutlined, QrcodeOutlined, SyncOutlined, BlockOutlined } from '@ant-design/icons';

import style from './style.module.less';
import PopQRCode from './components/pop_qrcode';
import { withRouter, RouteComponentProps } from 'react-router-dom';

import { Hall } from '@api/temple';

import urljoin from 'url-join';
import { BadgeProps } from 'antd/lib/badge';

import Action from '@common/components/action';

interface Props extends Partial<RouteComponentProps>, Hall {
  onDelete?: () => void;
  onEdit?: () => void;
}

@withRouter
export default class extends Component<Props> {
  render() {
    const { name, status, relatedDeviceImei, onDelete, onEdit, daily: {flow, income} } = this.props;
    const badgeProps = {
      running: {
        status: 'processing',
        text: '运行中',
      },
      stopped: {
        status: 'warning',
        text: '已停止',
      },
    }[status] as BadgeProps;


    return (
      <Card
        className={style.card}
        title={name}
        size='small'
        extra={
          <>
            <Popconfirm
              title={`删除${name}?`}
              okType='danger'
              okText='删除'
              cancelText='取消'
              placement='bottom'
              onConfirm={onDelete}
            >
              <Action tip='删除' icon={<DeleteOutlined />}/>
            </Popconfirm>
            <PopQRCode imei={relatedDeviceImei}>
              <Action tip='二维码' icon={<QrcodeOutlined />}/>
            </PopQRCode>
            
            <Action onClick={onEdit} tip='编辑' icon={<BlockOutlined />}/>
          </>
        }
      >
        <Row justify='space-around'>
          <Col span={6}>
            <Statistic title='客流量' value={flow} />
          </Col>
          <Col span={6}>
            <Statistic title='日收益' value={income} />
          </Col>
        </Row>

        <Row 
          justify='space-between'
          className={style.hallState}
        >
          <Col>
            <Typography.Text type="secondary">
              <Badge {...badgeProps} />
            </Typography.Text>
          </Col>
          <Col>
            <Typography.Text type="secondary">
              {relatedDeviceImei}
            </Typography.Text>
          </Col>
        </Row>
      </Card>
    );
  }
}
