import React, {Component, cloneElement, ReactElement } from 'react';
import { Modal, Form, Input, Upload, InputNumber } from 'antd';
import { UploadImg, FormModal } from '@common/components';
import { OnCreated as FormOnCreated, OnUpdated as FormOnUpdated } from '@common/components/form_modal';
import api, { Light, LightForm } from '@api/temple';

import _ from 'lodash';

import { FormItemProps } from 'antd/lib/form';

export type LightIds = {hallId: number, lightId?: number};
export type OnCreated = FormOnCreated<Light>;
export type OnUpdated = FormOnUpdated<Light>;

export default class extends FormModal<Light, LightForm, LightIds> {
  get resTypeName() {
    return '灯';
  }

  get itemsMeta(): FormModal<Light, LightForm>['itemsMeta'] {
    return {
      name: {
        label: '灯名',
        children: <Input />,
      },
      price: {
        label: '单价',
        children: <InputNumber min={0} max={100} step={0.01} />,
      },
      imageUrl: {
        label: '图片',
        children: <UploadImg expanded={false}/>
      }
    }
  }

  onCreating = async (form: LightForm, id: LightIds) => {
    return await api.createLight(form, id.hallId);
  }
  onUpdating = async (form: LightForm, id: LightIds) => {
    return await api.updateLight(form, id.hallId, id.lightId!);
  }
}
