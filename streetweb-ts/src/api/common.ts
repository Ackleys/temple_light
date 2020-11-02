import axios from 'axios';

const axiosInstace = axios.create({
  baseURL: '/admin'
});

//TODO: for debug
(window as any).axios = axios;
(window as any).axiosInstance = axiosInstace;

export interface Data<TPayload = undefined> {
  code: number;
  data: TPayload;
}

export interface Res {
  code: number;
  msg: string;
}

export type V1ArrPayload<TName extends string, T>  = {
  count: number;
} & Record<TName, T[]>;

export default axiosInstace;