import React from 'react';
import {
  HashRouter,
  Router as BaseRouter,
  Switch,
  Route,
} from 'react-router-dom';

import history from './history';

import Home from './Home';
import About from './About';

const Router = process.env.NODE_ENV === 'production' ? BaseRouter : HashRouter;

const App = () => (
  <Router history={history}>
    <Switch>
      <Route path="/about">
        <About />
      </Route>
      <Route path="/">
        <Home />
      </Route>
    </Switch>
  </Router>
);

export default App;
