import React from 'react';
import './App.less';

import { Switch, Route, BrowserRouter } from 'react-router-dom';
import Layout from '@common/layout';
import { Temple, Device, Login, Agent } from '@pages';

function App() {
  return (
    <BrowserRouter>
        <Switch>
          <Route path='/login' component={Login} />
          <Route>
            <Layout>
              <Switch>
                <Route path='/temple' component={Temple} />
                <Route path='/device' component={Device} />
                <Route path='/agent' component={Agent} />
              </Switch>
            </Layout>
          </Route>
        </Switch>
        
    </BrowserRouter>
  );
}

export default App;
