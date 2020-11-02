import React from 'react';
import { Input } from 'antd';
import api, { Temple, TempleForm } from '@api/temple';
import { UploadImg, FormModal } from '@common/components';
import { OnCreated as FormOnCreated, OnUpdated as FormOnUpdated } from '@common/components/form_modal';

export type OnCreated = FormOnCreated<Temple>;
export type OnUpdated = FormOnUpdated<Temple>;

export default class extends FormModal<Temple, TempleForm, undefined> {
  get resTypeName() {
    return '寺庙';
  }

  get itemsMeta(): FormModal<Temple, TempleForm>['itemsMeta'] {
    return {
      name: {
        label: '寺庙名',
        children: <Input />,
      },
      contactName: {
        label: '联系人',
        children: <Input />,
      },
      contactInfo: {
        label: '联系电话',
        rules: [
          {
            pattern: /^1[3456789]\d{9}$/,
            message: '电话格式无效',
          }
        ],
        children: <Input />,
      },
      bannerImgUrl: {
        label: '横幅图片',
        children: (
          <UploadImg />
        ),
      }
    }
  }

  onCreating = async (form: TempleForm) => await api.createTemple(form);
  onUpdating = async (form: TempleForm, id: undefined) => {
    return await api.updateTemple(form);
  }
}
