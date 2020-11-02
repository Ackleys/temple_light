import React, {Component} from 'react';
import { Route, Switch, RouteComponentProps, withRouter } from 'react-router-dom';

import urljoin from 'url-join';

import Home from './pages/home';
import Create from './pages/create';
import Halls from './pages/halls';

const routes: {
  path: string,
  component: typeof Component,
}[] = [
  {
    path: '/create',
    component: Create,
  }, {
    path: '/halls/:id',
    component: Halls,
  }, {
    path: '/',
    component: Home,
  },
]

@withRouter
export default class extends Component<Partial<RouteComponentProps>> {

  render() {
    const { match } = this.props;
    return (
      <>
        <Switch>
          {routes.map(({path, component}) => 
            <Route path={urljoin(match!.url, path)} component={component}/>
          )}
        </Switch>
      </>
    );
  }
};