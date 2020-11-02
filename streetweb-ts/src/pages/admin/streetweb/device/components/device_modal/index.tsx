import React from 'react';
import { Input } from 'antd';
import { toInteger } from 'lodash';
import FormModal, { OnCreated as FormOnCreated, OnUpdated as FormOnUpdated } from '@common/components/form_modal';
import api, { Device, DeviceForm } from '@api/device'

export type OnCreated = FormOnCreated<Device>;
export type OnUpdated = FormOnUpdated<Device>;

export default class extends FormModal<Device, DeviceForm> {
  get resTypeName() {
    return '设备';
  }

  get itemsMeta(): FormModal<Device, DeviceForm>['itemsMeta'] {
    return {
      imei: {
        label: 'imei',
        children: <Input />,
      },
      address: {
        label: '投放地址',
        children: <Input />,
      },
      template: {
        label: '发送模板',
        children: <Input />,
      },
      exp_resp: {
        label: '期望回复',
        children: <Input />,
      },
    };
  }

  onCreating = async (form: DeviceForm) => await api.createDevice(form);
  onUpdating = async (form: DeviceForm, id: number) => await api.updateDevice(id, form);
}
