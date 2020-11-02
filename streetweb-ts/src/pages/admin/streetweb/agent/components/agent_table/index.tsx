import React, {Component} from 'react';
import commonStyle from '@common/style.module.less';
import { Card, Table } from 'antd';
import { Agent } from '@api/god';

export default class extends Component<{
  agents: Agent[],
  loading: boolean,
}> {
  render() {
    const { agents, loading } = this.props;
    return (
      <Card className={commonStyle.card}>
        <Table dataSource={agents} columns={this.columns} loading={loading} />
      </Card>
    )
  }

  get columns(): {dataIndex: keyof Agent, [x: string]: any}[] {
    return [
      {
        title: '名称',
        dataIndex: 'name',
      }, {
        title: '电话',
        dataIndex: 'phone',
      }, {
        title: '地址',
        dataIndex: 'address',
      }, {
        title: '备注',
        dataIndex: 'remark',
      }
    ]
  }
}

