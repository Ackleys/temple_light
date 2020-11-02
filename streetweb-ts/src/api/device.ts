import axios, { Data, Res } from './common';

export interface Device {
  id: number;
  imei: string;
  signal: number; //信号强度
  address: string; //投放地点
  comm_state: CommState;
  template: string; //TODO: 模板字符串
  exp_resp: string;
}

export interface DeviceForm extends Pick<Device, 'imei' | 'address' | 'template' | 'exp_resp'> {

}

export enum CommState {
  Offline,
  Online,
}

export interface DeviceForm extends Pick<Device, 'imei' | 'address' | 'template'> {
  
}

export default abstract class {
  static async getDevices() {
    const resp = await axios.get<Data<Device[]>>('/v2/devices');
    return resp.data.data;
  }

  static async createDevice(form: DeviceForm) {
    const resp = await axios.post<Data<Device>>('/v2/devices', form);
    return resp.data.data;
  }

  static async updateDevice(id: number, form: DeviceForm) {
    const resp = await axios.patch<Data<Device>>(`/v2/devices/${id}`, form);
    return resp.data.data;
  }

  static async deleteDevice(id: number) {
    const resp = await axios.delete<Data<Res>>(`/v2/devices/${id}`);
    return resp.data;
  }
}