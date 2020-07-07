import {
  createHashHistory,
  createBrowserHistory,
} from 'history';

const history = process.env.NODE_ENV === 'production'
  ? createBrowserHistory()
  : createHashHistory();

export default history;
