import axios, { Data, Res } from './common';

type User = (God | Advertiser | Agent) & {
  common: {
    logo: URL;
    title: string;
  }
}

interface God {
  role: 1;
  god: {
    id: number;
    name: string;
    level: number;
  }
}

interface Agent {
  role: 2;
  agent: {
    id: number;
    name: string;
    phone: string;
    email: string;
    desc: string;
    address: string;
    remark: string;
  }
}

interface Advertiser {
  role: 3;
  advertiser: {
    id: number;
    name: string;
    phone: string;
    email: string;
    desc: string;
    address: string;
    remark: string;
  }
}

export default abstract class {
  static async login(data: {phone: string, pswd: string}): Promise<User> {
    return (await axios.post<Data<User>>('/auth/login', data)).data.data;
  }
}
