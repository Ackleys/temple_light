import axios from '@api/common';
import MockAdapter from 'axios-mock-adapter';

import templeMock from './temple';
import hallsMock from './halls';
import LightsMock from './lights';
import DurationsMock from './duration';

const mock = new MockAdapter(axios);
[templeMock, hallsMock, LightsMock, DurationsMock].forEach(f => f(mock));
