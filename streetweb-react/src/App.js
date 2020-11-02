import React from 'react';
import './App.less';

import { Route, BrowserRouter } from 'react-router-dom';
import Layout from '@pages/common/layout';
import Admin, { Temple } from '@pages';

function App() {
  return (
    <BrowserRouter>
        <Layout>
          <Route path='/temple' component={Temple} />
        </Layout>
    </BrowserRouter>
  );
}

export default App;
