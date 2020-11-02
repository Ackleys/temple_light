import axios, { Data, Res, V1ArrPayload } from './common';

export interface Agent {
  id: number;
  name: string;
  phone: string;
  address: string;
  remark: string;
}

export interface AgentForm extends Pick<Agent, 'name' | 'phone' | 'address' | 'remark'> {
  email: string;
}

export default abstract class {
  static async getAgents(): Promise<V1ArrPayload<'agents', Agent>> {
    return (await axios.get('/god/agent/fetch')).data.data;
  }

  static async createAgent(form: AgentForm): Promise<{id: number}> {
    return (await axios.put('/god/agent/add', form)).data.data;
  }

}
