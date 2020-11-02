import React, {Component} from 'react';
import { PageHeader, DeviceTable } from './components';

import { Col, Row, message } from 'antd';

import api, { Device } from '@api/device';
import produce from 'immer';


export default class extends Component<{}, {
  devices: Device[],
  loading: boolean,
}> {

  readonly state = {
    devices: [],
    loading: true,
  }

  async componentDidMount() {
    const devices = await api.getDevices();
    this.setState({
      devices, 
      loading: false,
    });
  }

  render() {
    const { devices, loading } = this.state;
    return (
      <>
        <Row gutter={[24, 24]}>
          <Col span={24}>
            <PageHeader
              OnDeviceCreated={device => {
                this.setState(produce(draft => {
                  draft.devices.push(device);
                }))
              }}
            />
          </Col>
          <Col span={24}>
            <DeviceTable 
              devices={devices} 
              loading={loading} 
              onUpdate={device => {
                this.setState(produce(draft => {
                  const i = draft.devices.findIndex(d => d.id == device.id);
                  draft.devices[i] = device;
                }))
              }}
              onDelete={async device => {
                await api.deleteDevice(device.id);
                this.setState({
                  devices: devices.filter(({id}) => id != device.id),
                }, () => {
                  message.success('删除成功');
                })
              }}
            />
          </Col>
        </Row>
          
      </>
    )
  }
}