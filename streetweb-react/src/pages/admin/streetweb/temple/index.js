import React, {Component} from 'react';
import p from 'immer';

import { Empty, Button, Modal, Form, Input, Upload } from 'antd';


import CreateTemple from './components/create_temple'

import './style.less';


export default class extends Component {
  
  constructor(props) {
    super(props);
    this.state = {
      state: 'before-create',
    }
  }


  handleForm = async () => {
    if(this.form === undefined)
      return;

    try {
      const value = await this.form.validateFields()
      console.log(value)
    } catch(e) {
      console.log('err', e);
    }
  }

  componentDidMount() {
    
  }

  render() {
    return (
      <>
        <Empty
          description='尚未创建寺庙'
          style={{paddingTop: '40px'}}
        >
          <Button type='primary' onClick={() => this.createTemple.setVisible(true)}>立即创建</Button>
        </Empty>
        

        
        <CreateTemple ref={ref => this.createTemple = ref} />

      </>
    );
  }
};