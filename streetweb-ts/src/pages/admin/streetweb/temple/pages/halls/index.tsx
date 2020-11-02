import React, {Component} from 'react';
import { RouteComponentProps, withRouter } from 'react-router-dom';

import { Col, Row, List, Avatar, Card, Typography, Popconfirm, message } from 'antd';

import produce from 'immer';

import PageHeader from './components/page_header';
import LightModal from './components/light_modal'
import DurationModal from './components/duration_modal';

import api, { Light, Hall, Duration } from '@api/temple';

import style from './style.module.less';

type State = {
  hall: Hall | null,
  lights: Light[],
  durations: Duration[],
}

@withRouter
export default class extends Component<Partial<RouteComponentProps<{id: string}>>, State> {

  readonly state: State = {
    hall: null,
    lights: [],
    durations: [],
  }

  async componentDidMount() {

    const { match } = this.props;
    const hallId = Number.parseInt(match!.params.id);

    let hall = await api.getHall(hallId);

    this.setState({
      hall,
      lights: await api.getLights(hallId),
      durations: await api.getDurations(hallId),
    })
  }

  render() {
    
    const { hall, lights, durations } = this.state;

    return (
      <>
        <Row gutter={[24, 24]}>
          <Col span={24}>
            <PageHeader 
              {...hall!} 
              onHallUpdated={hall => {
                this.setState({hall});
              }}
              onLightCreated={light => {
                this.setState(produce(draft => {
                  draft.lights.push(light);
                }))
              }}
              onDurationCreated={duration => {
                this.setState(produce(draft => {
                  draft.durations.push(duration);
                }))
              }}
            />
          </Col>
          <Col xs={24} lg={12}>
            <Card className={style.card}>
              <List
                header='灯列表'
                size='small'
                itemLayout='horizontal'
                dataSource={lights}
                pagination={{
                  pageSize: 20,
                  current: 1,
                }}
                renderItem={item => (
                  <List.Item
                    actions={[
                      (<LightModal 
                          type='update' 
                          default={item}
                          id={{hallId: hall!.id, lightId: item.id}}
                          onUpdated={light => {
                            this.setState(produce(draft => {
                              const idx = draft.lights.findIndex(li => li.id == light.id);
                              draft.lights[idx] = light;
                            }));
                          }}
                       >
                          <Typography.Link>
                            设置
                          </Typography.Link>
                      </LightModal>),
                      
                      <Popconfirm
                        title={`删除${item.name}`}
                        okType='danger'
                        okText='删除'
                        cancelText='取消'
                        placement='bottom'
                        onConfirm={async () => {
                          if(await api.deleteLight(hall!.id, item.id)) {
                            this.setState({
                              lights: lights.filter(li => li.id != item.id),
                            });
                            message.success(`${item.name}删除成功`);
                          } else {
                            message.error(`${item.name}删除失败`);
                          }
                        }}
                      >
                        <Typography.Link type='secondary'>
                          删除
                        </Typography.Link>
                      </Popconfirm>
                    ]}
                  >
                    <List.Item.Meta
                      avatar={
                        <Avatar src={item.imageUrl}/>
                      }
                      title={item.name}
                      description={`${item.price}元`}
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card className={style.card}>
              <List
                header='时长列表'
                size='small'
                itemLayout='horizontal'
                dataSource={durations}
                pagination={{
                  pageSize: 20,
                  current: 1,
                }}
                renderItem={item => (
                  <List.Item
                    actions={[
                      (<DurationModal 
                          type='update' 
                          default={item}
                          id={{hallId: hall!.id, durationId: item.id}}
                          onUpdated={duration => {
                            this.setState(produce(draft => {
                              const idx = draft.durations.findIndex(li => li.id == duration.id);
                              draft.durations[idx] = duration;
                            }));
                          }}
                       >
                          <Typography.Link>
                            设置
                          </Typography.Link>
                      </DurationModal>),
                      
                      <Popconfirm
                        title={`删除${item.name}`}
                        okType='danger'
                        okText='删除'
                        cancelText='取消'
                        placement='bottom'
                        onConfirm={async () => {
                          if(await api.deleteDuration(hall!.id, item.id)) {
                            this.setState({
                              durations: durations.filter(li => li.id != item.id),
                            });
                            message.success(`${item.name}删除成功`);
                          } else {
                            message.error(`${item.name}删除失败`);
                          }
                        }}
                      >
                        <Typography.Link type='secondary'>
                          删除
                        </Typography.Link>
                      </Popconfirm>
                    ]}
                  >
                    <List.Item.Meta
                      // avatar={
                      //   <Avatar src={item.imageUrl}/>
                      // }
                      title={item.name}
                      description={`${item.rate}天`}
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        </Row>
      </>
    )
  }
}