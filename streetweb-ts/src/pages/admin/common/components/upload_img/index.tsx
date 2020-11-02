import React, { Component } from 'react';
import { Upload } from 'antd';
import { PlusOutlined } from '@ant-design/icons'
import style from './style.module.less';
import clsx from 'clsx';

export default class extends Component<{
  onChange?: (...p: any) => any;
  value?: string;
  expanded?: boolean;
}> {

  static defaultProps = {
    expanded: true,
  }

  render() {
    const { onChange, value, expanded } = this.props;
    return (
      <Upload
        className={clsx({[style.upload]: expanded})}
        listType='picture-card'
        showUploadList={false}
        accept='image/*'
        beforeUpload={() => false}
        style={{width: '100%'}}
        onChange={(info) => {
          const reader = new FileReader();
          reader.readAsDataURL(info.file as any);
          reader.onload = () => {
            onChange?.(reader.result);
          };
        }}
      >
        <div>
          {value ? (
            <img 
              src={value!}
              width='100%'
            />
          ) : (
            <>
              <PlusOutlined />
              <div className='ant-upload-text'>上传</div>
            </>
          )}
        </div>
      </Upload>
    )
  }
}
