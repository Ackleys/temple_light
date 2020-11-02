import React, {Component} from 'react';
import commonStyle from '@common/style.module.less';
import { Card, Table, Typography, Popconfirm, Button } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import api, { Device, CommState } from '@api/device';
import Badge, { BadgeProps } from 'antd/lib/badge';
import Tag, { TagProps } from 'antd/lib/tag';
import { CloseCircleOutlined, FrownOutlined, MehOutlined, SmileOutlined } from '@ant-design/icons';
import Action from '@common/components/action';

import DeviceModal, { OnUpdated } from '../device_modal';

export default class extends Component<{
  devices: Device[],
  loading: boolean,
  onUpdate?: OnUpdated,
  onDelete?: (device: Device) => void,
}> {

  render() {
    const { devices, loading } = this.props;
    return (
      <Card className={commonStyle.card}>
        <Table dataSource={devices} columns={this.columns} loading={loading} />
      </Card>
    )
  }

  get columns(): {dataIndex?: keyof Device, [x: string]: any}[] {
    const { onUpdate, onDelete } = this.props;
    return [{
      title: 'imei',
      dataIndex: 'imei',
      render: (imei: number, record: Device) => {
        return (
          <DeviceModal
            type='update'
            id={record.id}
            default={record}
            onUpdated={onUpdate}
          >
            <Typography.Link 
            onClick={() => {
              console.log(record);
            }}
            type='secondary'
          >
            {imei}
          </Typography.Link>
          </DeviceModal>
        )
      }
    },{
      title: '通信状态',
      dataIndex: 'comm_state',
      render: (state: CommState) => {
        const badgeProps: BadgeProps = {
          [CommState.Online]: {
            status: 'processing' as const,
            text: '在线',
          },
          [CommState.Offline]: {
            status: 'warning' as const,
            text: '离线',
          },
        }[state];
        return <Badge {...badgeProps}/>
      },
    }, {
      title: '信号强度',
      dataIndex: 'signal',
      render: (signal: number, record: Device) => {
        enum Signal {
          NoSignal = 0,
          Weak = 10,
          Midium = 14,
          Strong = 32,
        }
        if(record.comm_state === CommState.Offline) {
          signal = 0;
        }
        let signalEnum: Signal = Signal[Object.keys(Signal)
          .filter(k => typeof Signal[k as any] === 'number')
          .find(k => (Signal[k as any] as any) >= signal) as any] as any;
        const tagProps: TagProps = {
          [Signal.NoSignal]: {
            color: 'red',
            children: '无',
            icon: <CloseCircleOutlined />,
          },
          [Signal.Weak]: {
            color: 'gold',
            children: '弱',
            icon: <FrownOutlined />,
          },
          [Signal.Midium]: {
            color: 'lime',
            children: '中',
            icon: <MehOutlined />,
          },
          [Signal.Strong]: {
            color: 'green',
            children: '强',
            icon: <SmileOutlined />,
          },
        }[signalEnum];
        tagProps.children += ` (${signal})`;
        return <Tag {...tagProps} />
      },
    }, {
      title: '投放地点',
      dataIndex: 'address',
    }, {
      title: '操作',
      key: 'delete',
      render: (_: any, record: Device) => {
        return (
          <Popconfirm
            title={`删除${name}?`}
            okType='danger'
            okText='删除'
            cancelText='取消'
            placement='bottom'
            onConfirm={() => {
              onDelete?.(record);
            }}
          >
            <Action tip='删除' icon={<DeleteOutlined />}/>
          </Popconfirm>
        )
      }
    }
  ]}

  
}

