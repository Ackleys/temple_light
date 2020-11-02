import React, {Component} from 'react';
import { withRouter, RouteComponentProps } from 'react-router-dom';

import { Button, PageHeader, Descriptions, Typography } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import LightModal, { OnCreated as OnLightCreated } from '../light_modal';
import DurationModal, { OnCreated as OnDurationCreated } from '../duration_modal';
import HallModal, { OnUpdated } from '@pages/temple/components/hall_modal';

import templeStyle from '@pages/temple/style.module.less';

import { Hall } from '@api/temple';

type Props = Partial<RouteComponentProps> & Hall & {
  onHallUpdated?: OnUpdated;
  onLightCreated?: OnLightCreated;
  onDurationCreated?: OnDurationCreated;
}

@withRouter
export default class extends Component<Props> {
  render() {
    const { history, onHallUpdated, onLightCreated, onDurationCreated, name, relatedDeviceImei, id } = this.props;

    return (
      <PageHeader
        className={templeStyle.pageHeader}
        title={name}
        extra={[
          <LightModal
            id={{hallId: id}}
            onCreated={onLightCreated}
          >
            <Button 
              icon={<PlusOutlined/>}
            >
              添加灯
            </Button>
          </LightModal>,
          <DurationModal
            id={{hallId: id}}
            onCreated={onDurationCreated}
          >
            <Button
              icon={<PlusOutlined/>}
            >
              添加时长
            </Button>
          </DurationModal>,
          <HallModal
            type='update'
            default={{name, relatedDeviceImei}}
            id={id}
            onUpdated={onHallUpdated}
          >
            <Button 
              icon={<EditOutlined/>}
              type='primary'
            >
              编辑设置
            </Button>
          </HallModal>
        ]}
        onBack={() => history!.goBack()}
      >
        <Descriptions size="small" column={3}>
          {/* <Descriptions.Item label="联系人">王某某</Descriptions.Item>
          <Descriptions.Item label="联系方式">136xxxxxxxx</Descriptions.Item>
          <Descriptions.Item label="创建时间">2017-5-12</Descriptions.Item> */}
        </Descriptions>
      </PageHeader>
    );
  }
};