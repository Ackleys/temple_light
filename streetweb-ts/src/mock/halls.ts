import MockAdapter from 'axios-mock-adapter';
import { Hall, HallForm } from '@api/temple';
import { maxBy, merge } from 'lodash';

export default (mock: MockAdapter) => {
  // mock.onGet(/^\/temple\/halls$/).reply(() => [200, {
  //   code: 0,
  //   data: halls,
  // }]);
  mock.onGet(/^\/temple\/halls$/).passThrough();

  // mock.onGet(/^\/temple\/halls\/\d+$/).reply(({url}) => {
  //   const hallId = Number.parseInt(url!.match(/^\/temple\/halls\/(\d+)$/)![1])
  //   return [200, {
  //     code: 0,
  //     data: halls.find(e => e.id === hallId),
  //   }];
  // });
  mock.onGet(/^\/temple\/halls\/\d+$/).passThrough();

  // mock.onPost(/^\/temple\/halls$/).reply(({data}: {data?: string}) => {
  //   let obj: HallForm = JSON.parse(data!);
  //   let hall: Hall = {
  //     id: (maxBy(halls, h => h.id)?.id ?? 1) + 1,
  //     ...obj!,
  //     status: 'running',
  //     daily: {
  //       flow: 0,
  //       income: 0,
  //     }
  //   }

  //   halls = [...halls, hall];

  //   return [200, {
  //     code: 0,
  //     data: hall,
  //   }];
  // });
  mock.onPost(/^\/temple\/halls$/).passThrough();

  // mock.onPatch(/^\/temple\/halls\/\d+$/).reply(({data, url}) => {
  //   const hallId = Number.parseInt(url!.match(/^\/temple\/halls\/(\d+)$/)![1])
  //   const obj: HallForm = JSON.parse(data!);
  //   if(!halls.find(h => h.id === hallId)) {
  //     return [404, {
  //       code: 1,
  //     }];
  //   }

  //   halls = merge(halls, [{...obj, id: hallId}]);
  //   return [200, {
  //     code: 0,
  //     data: halls.find(h => h.id === hallId),
  //   }];
  // });
  mock.onPatch(/^\/temple\/halls\/\d+$/).passThrough();

  // mock.onDelete(/^\/temple\/halls\/\d+$/).reply(({url}) => {
  //   const hallId = Number.parseInt(url!.match(/^\/temple\/halls\/(\d+)$/)![1])
  //   if(hallId == 2) {
  //     return [409, {
  //       code: 1,
  //     }];
  //   }

  //   halls = halls.filter(h => h.id != hallId);
  //   return [200, {
  //     code: 0,
  //   }];
  // });
  mock.onDelete(/^\/temple\/halls\/\d+$/).passThrough();
};

let halls: Hall[] = [
  {
    id: 1,
    name: '大雄宝殿',
    status: 'running',
    relatedDeviceImei: 210164927714504,
    daily: {
      flow: 233,
      income: 542.2,
    },
  }, {
    id: 2,
    name: '净土宝殿',
    status: 'stopped',
    relatedDeviceImei: 982425814284942,
    daily: {
      flow: 130,
      income: 242.5,
    },
  }, {
    id: 3,
    name: '极乐宝殿',
    status: 'running',
    relatedDeviceImei: 284032287774607,
    daily: {
      flow: 157,
      income: 175.3,
    },
  }, {
    id: 4,
    name: '弥陀宝殿',
    status: 'running',
    relatedDeviceImei: 890583483828231,
    daily: {
      flow: 95,
      income: 310.7,
    },
  }, 
];
