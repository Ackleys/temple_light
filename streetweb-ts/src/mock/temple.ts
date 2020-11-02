import MockAdapter from 'axios-mock-adapter';
import { Temple, TempleForm } from '@api/temple';
import { merge } from 'lodash';

export default (mock: MockAdapter) => {
  // mock.onGet(/^\/temple$/).reply(() => {
  //   if(temple === null) {
  //     return [404, {
  //       code: 0,
  //     }];
  //   }
  //   return [200, {
  //     code: 0,
  //     data: temple,
  //   }]
  // });
  mock.onGet(/^\/temple$/).passThrough();
  // mock.onPost(/^\/temple$/).reply(({data, url}) => {
  //   const obj: TempleForm = JSON.parse(data!);
  //   if(temple !== null) {
  //     return [409, {
  //       code: 0,
  //     }];
  //   }
  //   temple = merge({
  //     id: 1,
  //     createTime: '2017-5-12',
  //   }, obj);
  //   return [200, {
  //     code: 0,
  //     data: temple,
  //   }];
  // });
  mock.onPost(/^\/temple$/).passThrough();
  // mock.onPatch(/^\/temple$/).reply(({data, url}) => {
  //   const obj: TempleForm = JSON.parse(data!);

  //   if(temple === null) {
  //     return [404, {
  //       code: 0,
  //     }];
  //   }
  //   temple = merge(temple, obj);
  //   return [200, {
  //     code: 0,
  //     data: temple,
  //   }];
  // });
  mock.onPatch(/^\/temple$/).passThrough();
};

//let temple: Temple | null = null;

let temple: Temple | null = {
  id: 1,
  name: 'xxx寺',
  contactName: '王某某',
  contactInfo: '18959338563',
  bannerImgUrl: '',
  createTime: '2017-6-21',
};
