import MockAdapter from 'axios-mock-adapter';
import { Light, LightForm } from '@api/temple';
import { maxBy, merge } from 'lodash';

export default (mock: MockAdapter) => {
  // mock.onGet(/^\/temple\/halls\/\d+\/lights$/).reply(({url}) => {
  //   const hallId = Number.parseInt(url!.match(/^\/temple\/halls\/(\d+)\/lights$/)![1]);
  //   return [200, {
  //     code: 0,
  //     data: lights[hallId],
  //   }];
  // });
  mock.onGet(/^\/temple\/halls\/\d+\/lights$/).passThrough()

  // mock.onPost(/^\/temple\/halls\/\d+\/lights$/).reply(({data, url}) => {
  //   let obj: LightForm = JSON.parse(data!);
  //   const hallId = Number.parseInt(url!.match(/^\/temple\/halls\/(\d+)\/lights$/)![1]);
  //   const subLights: Light[] = lights[hallId] ?? [];
  //   let light: Light = {
  //     id: (maxBy(subLights, li => li.id)?.id ?? 1) + 1,
  //     ...obj!,
  //   };

  //   lights[hallId] = [...lights[hallId], light];

  //   return [200, {
  //     code: 0,
  //     data: light,
  //   }];
  // });
  mock.onPost(/^\/temple\/halls\/\d+\/lights$/).passThrough();

  // mock.onPatch(/^\/temple\/halls\/\d+\/lights\/\d+$/).reply(({data, url}) => {
  //   const match = url!.match(/^\/temple\/halls\/(\d+)\/lights\/(\d+)$/);
  //   const hallId = Number.parseInt(match![1]);
  //   const lightId = Number.parseInt(match![2]);
  //   const subLights = lights[hallId];
  //   const obj: Light = JSON.parse(data!);

  //   if(!subLights.find(li => li.id === lightId)) {
  //     return [404, {
  //       code: 1,
  //     }];
  //   }

  //   lights[hallId] = merge(subLights, [{...obj, id: lightId}]);
  //   return [200, {
  //     code: 0,
  //     data: subLights.find(li => li.id === lightId),
  //   }];
  // });
  mock.onPatch(/^\/temple\/halls\/\d+\/lights\/\d+$/).passThrough();

  // mock.onDelete(/^\/temple\/halls\/\d+\/lights\/\d+$/).reply(({url}) => {
  //   const match = url!.match(/^\/temple\/halls\/(\d+)\/lights\/(\d+)$/);
  //   const hallId = Number.parseInt(match![1]);
  //   const lightId = Number.parseInt(match![2]);

  //   lights[hallId] = lights[hallId].filter(li => li.id != lightId);
  //   return [200, {
  //     code: 0,
  //   }];
  // });
  mock.onDelete(/^\/temple\/halls\/\d+\/lights\/\d+$/).passThrough();
};

let lights: {[key: number]: Light[]} = {
  1: [
    {
      id: 1,
      name: '亲情灯',
      price: 0.2,
      imageUrl: '/img/v2/55022972.png',
    }, {
      id: 2,
      name: '事业灯',
      price: 0.3,
      imageUrl: '/img/v2/55022972.png',
    },{
      id: 3,
      name: '爱情灯',
      price: 0.25,
      imageUrl: '/img/v2/55022972.png',
    },
  ],
  2: [
    {
      id: 4,
      name: '友谊灯',
      price: 0.14,
      imageUrl: '/img/v2/55022972.png',
    }, {
      id: 5,
      name: '学业灯',
      price: 0.28,
      imageUrl: '/img/v2/55022972.png',
    }, {
      id: 6,
      name: '生活灯',
      price: 0.31,
      imageUrl: '/img/v2/55022972.png',
    }, {
      id: 7,
      name: '富贵灯',
      price: 0.57,
      imageUrl: '/img/v2/55022972.png',
    },
  ],
  3: [
    {
      id: 8,
      name: '运势灯',
      price: 0.14,
      imageUrl: '/img/v2/55022972.png',
    }, {
      id: 9,
      name: '环保灯',
      price: 0.28,
      imageUrl: '/img/v2/55022972.png',
    },
  ],
  4: [],
};
