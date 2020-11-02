import React, {Component} from 'react';
import { withRouter, RouteComponentProps } from 'react-router-dom';

import { Button, PageHeader, Descriptions, Typography } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';

import templeStyle from '@pages/temple/style.module.less';
import TempleModal, { OnUpdated as OnTempleUpdated } from '@pages/temple/components/temple_modal';
import HallModal, { OnCreated as onHallCreated } from '@pages/temple/components/hall_modal';

import { Temple } from '@api/temple';

type Props = Partial<RouteComponentProps> & Temple & {
  onHallCreated?: onHallCreated;
  onTempleUpdated?: OnTempleUpdated;
};

@withRouter
export default class extends Component<Props> {
  render() {
    const { onHallCreated, onTempleUpdated, name, contactName, contactInfo, createTime, bannerImgUrl } = this.props;
    return (
      <PageHeader
        className={templeStyle.pageHeader}
        title={name}
        extra={[
          <HallModal
            onCreated={onHallCreated}
          >
            <Button 
              icon={<PlusOutlined/>}
            >
              添加大殿
            </Button>
          </HallModal>,
          <TempleModal 
            type='update' 
            default={{name, contactName, contactInfo, bannerImgUrl}}
            onUpdated={onTempleUpdated}
          >
            <Button 
              icon={<EditOutlined/>}
              type='primary'
            >
              编辑设置
            </Button>
          </TempleModal>,
        ]}
        
      >
        <Descriptions size="small" column={3}>
        <Descriptions.Item label="联系人">{contactName}</Descriptions.Item>
        <Descriptions.Item label="联系方式">{contactInfo}</Descriptions.Item>
        <Descriptions.Item label="创建时间">{createTime}</Descriptions.Item>
        </Descriptions>
      </PageHeader>
    );
  }
};