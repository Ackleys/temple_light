import React, {Component, ReactElement } from 'react';

import clsx from 'clsx';

import { Typography, Popover } from 'antd';

import style from './style.module.less';
import QRCode from 'qrcode.react';

type Props = {
  children: ReactElement,
  imei: number,
}

class QRCodeContainer extends React.Component<Omit<Props, 'children'> & {url: string}, {}> {
  componentDidMount() {
    this.update();
  }

  componentDidUpdate() {
    this.update();
  }

  update() {
    const { imei } = this.props;
    const text = `${imei}`;

    const canvas: HTMLCanvasElement | null = document.querySelector(`canvas.${style.qrcodeContainer}.i${imei}`);
    const ctx = canvas?.getContext('2d');
    if(ctx && canvas) {
      ctx.save();
      ctx.resetTransform();
      ctx.translate(canvas.width, canvas.height);

      ctx.font = '15px Verdana';
      ctx.textBaseline = 'bottom';
      ctx.textAlign = 'end';
      
      const {width, actualBoundingBoxRight: right, actualBoundingBoxAscent: ascent, actualBoundingBoxDescent: descent} = ctx.measureText(text);
      ctx.fillStyle = 'white';
      ctx.fillRect(0, 0, -width + right, -ascent + descent);

      ctx.fillStyle = 'black';
      ctx.fillText(text, 0, 0);
      ctx.restore();
    }
  }

  render() {
    const { url, imei } = this.props;
    return (
      <QRCode 
        value={url} 
        size={200}
        level='H'
        className={clsx([style.qrcodeContainer], `i${imei}`)}
      />
    )
  }
}


export default class extends Component<Props, {}> {
  render() {
    const { imei } = this.props;
    const url = `http://m.fzstack.com/${imei}`
    return (
      <Popover
        trigger='click'
        placement='bottom'
        content={(
          <>
            <div className={style.qrcodeBox}>
              <QRCodeContainer imei={imei} url={url}/>
              <Typography.Text 
                type="secondary" 
                className={style.text}
                ellipsis
                copyable={{
                  text: url,
                  tooltips: (['复制', '复制成功']),
                }}
              >
                {url}
              </Typography.Text>
            </div>
          </>
        )}
      >
        {this.props.children}
      </Popover>
    )
  }
}