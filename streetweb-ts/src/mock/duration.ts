import MockAdapter from 'axios-mock-adapter';
import { Duration, DurationForm } from '@api/temple';
import { maxBy, merge } from 'lodash';

export default (mock: MockAdapter) => {
  // mock.onGet(/^\/temple\/halls\/\d+\/durations$/).reply(({url}) => {
  //   console.log('mock', 'get duration');
  //   const hallId = Number.parseInt(url!.match(/^\/temple\/halls\/(\d+)\/durations$/)![1]);
  //   return [200, {
  //     code: 0,
  //     data: durations[hallId],
  //   }];
  // });
  mock.onGet(/^\/temple\/halls\/\d+\/durations$/).passThrough();

  // mock.onPost(/^\/temple\/halls\/\d+\/durations$/).reply(({data, url}) => {
  //   let obj: DurationForm = JSON.parse(data!);
  //   const hallId = Number.parseInt(url!.match(/^\/temple\/halls\/(\d+)\/durations$/)![1]);
  //   const subDurations: Duration[] = durations[hallId] ?? [];
  //   let duration: Duration = {
  //     id: (maxBy(subDurations, li => li.id)?.id ?? 1) + 1,
  //     ...obj!,
  //   };

  //   durations[hallId] = [...durations[hallId], duration];

  //   return [200, {
  //     code: 0,
  //     data: duration,
  //   }];
  // });
  mock.onPost(/^\/temple\/halls\/\d+\/durations$/).passThrough();

  // mock.onPatch(/^\/temple\/halls\/\d+\/durations\/\d+$/).reply(({data, url}) => {
  //   const match = url!.match(/^\/temple\/halls\/(\d+)\/durations\/(\d+)$/);
  //   const hallId = Number.parseInt(match![1]);
  //   const durationId = Number.parseInt(match![2]);
  //   const subDurations = durations[hallId];
  //   const obj: Duration = JSON.parse(data!);

  //   if(!subDurations.find(li => li.id === durationId)) {
  //     return [404, {
  //       code: 1,
  //     }];
  //   }

  //   durations[hallId] = merge(subDurations, [{...obj, id: durationId}]);
  //   return [200, {
  //     code: 0,
  //     data: subDurations.find(li => li.id === durationId),
  //   }];
  // });
  mock.onPatch(/^\/temple\/halls\/\d+\/durations\/\d+$/).passThrough();
  

  // mock.onDelete(/^\/temple\/halls\/\d+\/durations\/\d+$/).reply(({url}) => {
  //   const match = url!.match(/^\/temple\/halls\/(\d+)\/durations\/(\d+)$/);
  //   const hallId = Number.parseInt(match![1]);
  //   const durationId = Number.parseInt(match![2]);

  //   durations[hallId] = durations[hallId].filter(li => li.id != durationId);
  //   return [200, {
  //     code: 0,
  //   }];
  // });
  mock.onDelete(/^\/temple\/halls\/\d+\/durations\/\d+$/).passThrough();
};

let durations: {[key: number]: Duration[]} = {
  1: [
    {
      id: 1,
      name: '一天',
      rate: 1,
    }, {
      id: 2,
      name: '三天',
      rate: 3,
    },{
      id: 3,
      name: '七天',
      rate: 7,
    },
  ],
  2: [
    {
      id: 4,
      name: '一天',
      rate: 1,
    }, {
      id: 5,
      name: '五天',
      rate: 5,
    }, {
      id: 6,
      name: '九天',
      rate: 9,
    }, 
  ],
  3: [],
  4: [
    {
      id: 7,
      name: '一天',
      rate: 1,
    },{
      id: 8,
      name: '七七四十九',
      rate: 47,
    }, {
      id: 9,
      name: '九九八十一',
      rate: 81,
    },
  ],
};


