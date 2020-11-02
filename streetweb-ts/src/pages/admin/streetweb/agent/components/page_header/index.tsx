import React, {Component} from 'react';
import { withRouter, RouteComponentProps } from 'react-router-dom';
import { Button, PageHeader, Descriptions } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import templeStyle from '@pages/temple/style.module.less';

import AgentModal, { OnCreated as OnAgentCreated } from '../agent_modal';

type Props = Partial<RouteComponentProps> & {
  onAgentCreated?: OnAgentCreated;
}

export default class extends Component<Props> {
  render() {
    const { onAgentCreated } = this.props;

    return (
      <PageHeader
        className={templeStyle.pageHeader}
        title='设备管理'
        extra={[
          <AgentModal
            type='create'
            onCreated={onAgentCreated}
          >
            <Button 
              icon={<PlusOutlined/>}
              type='primary'
            >
              添加代理
            </Button>
          </AgentModal>,
        ]}
      >
        <Descriptions size="small" column={3}>
        </Descriptions>
      </PageHeader>
    );
  }
};