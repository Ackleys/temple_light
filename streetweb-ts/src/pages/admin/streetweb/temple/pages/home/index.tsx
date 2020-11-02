import React, {Component} from 'react';
import { withRouter, RouteComponentProps } from 'react-router-dom';

import urljoin from 'url-join';
import immer from 'immer';

import { Col, Row, List, message } from 'antd';

import HallCard from './components/hall_card';
import TemplePageHeader from './components/page_header';
import Modal from 'antd/lib/modal/Modal';

import api, {Hall, Temple} from '@api/temple';

type State = {
  temple: Temple | null,
  halls: Hall[],
};


@withRouter
export default class extends Component<Partial<RouteComponentProps>, State> {

  readonly state: State = {
    temple: null,
    halls: [],
  }

  async componentDidMount() {
    const { history, match } = this.props;

    try {
      this.setState({
        temple: await api.getTemple(),
        halls: await api.getHalls(),
      });
    } catch {
      history!.replace(urljoin(match!.url, 'create'));
    }
    
  }

  render() {
    const { history, match } = this.props;
    const { halls, temple } = this.state;

    return (
      <>
        <Row gutter={[24, 24]}>
          <Col span={24}>
            <TemplePageHeader 
              {...temple!}
              onHallCreated={hall => {
                this.setState(immer(draft => {
                  draft.halls.push(hall);
                }))
              }}
              onTempleUpdated={temple => {
                this.setState({temple});
              }}
            />
          </Col>
        </Row>
        <List
          grid={{
            gutter: 24,
            xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 5,
          }}
          dataSource={halls}
          renderItem={item => (
            <List.Item>
              <HallCard {...item} 
                onDelete={async () => {
                  if(await api.deleteHall(item.id)) {
                    this.setState({
                      halls: halls.filter(i => i !== item),
                    });
                    message.success(`${item.name}删除成功`);
                  } else {
                    message.error(`${item.name}删除失败`);
                  }
                }}
                onEdit={() => {
                  history!.push(urljoin(match!.path, 'halls', `${item.id}`));
                }}
              />
            </List.Item>
          )}
        />
      </>
    );
  }
};
