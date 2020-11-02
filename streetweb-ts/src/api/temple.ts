import axios, { Data } from './common';



export interface Temple {
  id: number;
  name: string;
  contactName: string;
  contactInfo: string;
  bannerImgUrl: string;
  createTime: string;
}

export interface TempleForm extends Pick<Temple, 'name' | 'contactName' | 'contactInfo' | 'bannerImgUrl'> {

}


export interface Hall {
  id: number;
  name: string;
  status: 'running' | 'stopped';
  relatedDeviceImei: number;
  daily: {
    flow: number,
    income: number,
  }
}

export interface HallForm extends Pick<Hall, 'name' | 'relatedDeviceImei'> {
  
}

export interface Light {
  id: number;
  name: string;
  price: number;
  imageUrl: string;
}

export interface LightForm extends Pick<Light, 'name' | 'price' | 'imageUrl'> {
  
}

export interface Duration {
  id: number;
  name: string;
  rate: number;
}

export interface DurationForm extends Pick<Duration, 'name' | 'rate'> {
  
}

export default abstract class {

  static async getTemple(): Promise<Temple> {
    let resp = await axios.get<Data<Temple>>(`/temple`);
    return resp.data.data;
  }

  static async createTemple(form: TempleForm): Promise<Temple> {
    let resp = await axios.post<Data<Temple>>(`/temple`, form);
    return resp.data.data;
  }

  static async updateTemple(form: TempleForm): Promise<Temple> {
    let resp = await axios.patch<Data<Temple>>(`/temple`, form);
    return resp.data.data;
  }

  static async getHalls(): Promise<Hall[]> {
    let resp = await axios.get<Data<Hall[]>>(`/temple/halls`);
    return resp.data.data;
  }

  static async getHall(hallId: number): Promise<Hall> {
    let resp = await axios.get<Data<Hall>>(`/temple/halls/${hallId}`);
    return resp.data.data;
  }

  static async createHall(form: HallForm): Promise<Hall> {
    let resp = await axios.post<Data<Hall>>(`/temple/halls`, form);
    return resp.data.data;
  }

  static async updateHall(hallId: number, form: HallForm): Promise<Hall> {
    let resp = await axios.patch<Data<Hall>>(`/temple/halls/${hallId}`, form);
    return resp.data.data;
  }

  static async deleteHall(hallId: number): Promise<boolean> {
    try {
      let resp = await axios.delete<Data>(`/temple/halls/${hallId}`);
      return resp.data.code === 0;
    } catch {
      return false;
    }
  }

  static async getLights(hallId: number): Promise<Light[]> {
    console.log('api ligts', {hallId});
    let resp = await axios.get<Data<Light[]>>(`/temple/halls/${hallId}/lights`);
    console.log('api lights', resp.data.data);
    return resp.data.data;
  }

  static async createLight(form: LightForm, hallId: number): Promise<Light> {
    let resp = await axios.post<Data<Light>>(`/temple/halls/${hallId}/lights`, form);
    return resp.data.data;
  }

  static async updateLight(form: LightForm, hallId: number, lightId: number): Promise<Light> {
    let resp = await axios.patch<Data<Light>>(`/temple/halls/${hallId}/lights/${lightId}`, form);
    return resp.data.data;
  }

  static async deleteLight(hallId: number, lightId: number): Promise<boolean> {
    try {
      let resp = await axios.delete<Data>(`/temple/halls/${hallId}/lights/${lightId}`);
      return resp.data.code === 0;
    } catch {
      return false;
    }
  }

  static async getDurations(hallId: number): Promise<Duration[]> {
    let resp = await axios.get<Data<Duration[]>>(`/temple/halls/${hallId}/durations`);
    return resp.data.data;
  }

  static async createDuration(form: DurationForm, hallId: number): Promise<Duration> {
    let resp = await axios.post<Data<Duration>>(`/temple/halls/${hallId}/durations`, form);
    return resp.data.data;
  }

  static async updateDuration(form: DurationForm, hallId: number, durationId: number): Promise<Duration> {
    let resp = await axios.patch<Data<Duration>>(`/temple/halls/${hallId}/durations/${durationId}`, form);
    return resp.data.data;
  }

  static async deleteDuration(hallId: number, durationId: number): Promise<boolean> {
    try {
      let resp = await axios.delete<Data>(`/temple/halls/${hallId}/durations/${durationId}`);
      return resp.data.code === 0;
    } catch {
      return false;
    }
  }

}
