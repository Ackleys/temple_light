import React from 'react';
import { Input } from 'antd';
import { toInteger } from 'lodash';
import FormModal, { OnCreated as FormOnCreated, OnUpdated as FormOnUpdated } from '@common/components/form_modal';
import api, { Hall, HallForm } from '@api/temple'

export type OnCreated = FormOnCreated<Hall>;
export type OnUpdated = FormOnUpdated<Hall>;

export default class extends FormModal<Hall, HallForm> {
  get resTypeName() {
    return '殿';
  }

  get itemsMeta(): FormModal<Hall, HallForm>['itemsMeta'] {
    return {
      name: {
        label: '殿名',
        children: <Input />,
      },
      relatedDeviceImei: {
        label: '关联设备imei',
        getValueFromEvent: e => toInteger(e.target.value),
        rules: [{
          type: 'integer',
          min: 100000000000000,
          max: 999999999999999,
          message: 'imei格式错误',
        }],
        children: <Input />,
      }
    };
  }

  onCreating = async (form: HallForm) => await api.createHall(form);
  onUpdating = async (form: HallForm, id: number) => await api.updateHall(id, form);
}
