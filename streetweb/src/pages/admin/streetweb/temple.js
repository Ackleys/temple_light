import React, {Component} from 'react';
import Layout from '@common/layout';
import produce from 'immer';

import { Empty, Button } from 'antd';

export default class extends Component {
  
  constructor(props) {
    super(props);
    this.state = {

    };
    
  }

  render() {
    return (
      <>
        <div>
          test
        </div>
        <Empty
          description='您尚未创建寺庙'
        >
          <Button type='primary'>立即创建</Button>
        </Empty>
        {/* 
          您还未创建寺庙 -> 立即创建
          弹出模态框, 填写寺庙信息
        */}
      </>
    );
  }
};