import React, {Component, cloneElement} from 'react';
import { Button, Tooltip } from 'antd';

import style from './style.module.less';

export default class extends Component<{
  tip: string;
  icon: any; 
  onClick?: (e: any) => void;
}> {
  render() {
    const { tip, icon, onClick } = this.props;
    return (
      <Tooltip 
      title={tip}
    >
      <Button
        type='text'
        size='small'
        shape='circle'
        onClick={onClick}
        icon={
          cloneElement(icon, {
            className: style.actionIcon
          })
        }
      />
    </Tooltip>
    )
  }
}