import React, {Component} from 'react';
import { PageHeader, AgentTable } from './components';
import { Col, Row, message } from 'antd';
import api, { Agent } from '@api/god';
import produce from 'immer';

export default class extends Component<{}, {
  agents: Agent[],
  loading: boolean,
}> {

  readonly state = {
    agents: [],
    loading: true,
  }

  async componentDidMount() {
    const agents = (await api.getAgents()).agents;
    this.setState({
      agents, 
      loading: false,
    });
  }

  render() {
    const { agents, loading } = this.state;
    return (
      <>
        <Row gutter={[24, 24]}>
          <Col span={24}>
            <PageHeader
              onAgentCreated={agent => {
                this.setState(produce(draft => {
                  draft.agents.push(agent);
                }))
              }}
            />
          </Col>
          <Col span={24}>
            <AgentTable 
              agents={agents} 
              loading={loading} 
            />
          </Col>
        </Row>
          
      </>
    )
  }
}