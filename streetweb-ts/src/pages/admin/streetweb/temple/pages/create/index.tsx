import React, {Component} from 'react';
import { withRouter, RouteComponentProps } from 'react-router-dom';
import { Empty, Button } from 'antd';
import TempleModal from '@pages/temple/components/temple_modal';
import api from '@api/temple';

@withRouter
export default class extends Component<Partial<RouteComponentProps>> {
  async componentDidMount() {
    const { history } = this.props;
    try {
      await api.getTemple();
      history!.replace('/temple');
    } catch { }
  }

  render() {
    const { history } = this.props;

    return (
      <Empty
        description='尚未创建寺庙'
        style={{paddingTop: '40px'}}
      >
        <TempleModal
          onCreated={temple => {
            history!.replace('/temple');
          }}
        >
          <Button type='primary'>立即创建</Button>
        </TempleModal>
      </Empty>
    );
  }
}