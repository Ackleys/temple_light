import React, {Component, cloneElement, ReactElement } from 'react';
import { Modal, Form, Input, Upload, InputNumber } from 'antd';
import { UploadImg, FormModal } from '@common/components';
import { OnCreated as FormOnCreated, OnUpdated as FormOnUpdated } from '@common/components/form_modal';
import api, { Duration, DurationForm } from '@api/temple';

import _ from 'lodash';

import { FormItemProps } from 'antd/lib/form';

export type DurationIds = {hallId: number, durationId?: number};
export type OnCreated = FormOnCreated<Duration>;
export type OnUpdated = FormOnUpdated<Duration>;

export default class extends FormModal<Duration, DurationForm, DurationIds> {
  get resTypeName() {
    return '灯';
  }

  get itemsMeta(): FormModal<Duration, DurationForm>['itemsMeta'] {
    return {
      name: {
        label: '时长名',
        children: <Input />,
      },
      rate: {
        label: '时长(天)',
        children: <InputNumber min={0} max={100} step={0.1} />,
      }
    }
  }

  onCreating = async (form: DurationForm, id: DurationIds) => {
    return await api.createDuration(form, id.hallId);
  }
  onUpdating = async (form: DurationForm, id: DurationIds) => {
    return await api.updateDuration(form, id.hallId, id.durationId!);
  }
}
