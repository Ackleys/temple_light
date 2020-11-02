import React from 'react';
import { Input } from 'antd';
import { toInteger } from 'lodash';
import FormModal, { OnCreated as FormOnCreated, OnUpdated as FormOnUpdated } from '@common/components/form_modal';
import api, { Agent, AgentForm } from '@api/god'

export type OnCreated = FormOnCreated<Agent>;

export default class extends FormModal<Agent, AgentForm> {
  get resTypeName() {
    return '设备';
  }

  get itemsMeta(): FormModal<Agent, AgentForm>['itemsMeta'] {
    return {
      name: {
        label: '姓名',
        children: <Input />,
      },
      phone: {
        label: '电话',
        children: <Input />,
      },
      email: {
        label: 'email',
        children: <Input />,
      },
      address: {
        label: '地址',
        children: <Input />,
      },
      remark: {
        label: '备注',
        children: <Input />,
      },
    };
  }

  onCreating = async (form: AgentForm) => {
    const { id } = await api.createAgent(form);
    return {
      ...form,
      id,
    };
  }
}
