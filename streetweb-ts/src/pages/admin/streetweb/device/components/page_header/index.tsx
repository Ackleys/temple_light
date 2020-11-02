import React, {Component} from 'react';
import { withRouter, RouteComponentProps } from 'react-router-dom';
import { Button, PageHeader, Descriptions } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import templeStyle from '@pages/temple/style.module.less';

import DeviceModal, { OnCreated as OnDeviceCreated } from '../device_modal';
import { Device } from '@api/device';

type Props = Partial<RouteComponentProps> & {
  OnDeviceCreated?: OnDeviceCreated;
}

export default class extends Component<Props> {
  render() {
    const { OnDeviceCreated } = this.props;

    return (
      <PageHeader
        className={templeStyle.pageHeader}
        title='设备管理'
        extra={[
          <DeviceModal
            type='create'
            onCreated={OnDeviceCreated}
          >
            <Button 
              icon={<PlusOutlined/>}
              type='primary'
            >
              添加设备
            </Button>
          </DeviceModal>,
        ]}
      >
        <Descriptions size="small" column={3}>
        </Descriptions>
      </PageHeader>
    );
  }
};