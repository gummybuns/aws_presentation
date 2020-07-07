import React from 'react';
import {
  Link,
} from 'react-router-dom';

const Home = () => (
  <div>
    <h1>Hello World</h1>
    <p>Welcome to our website. I hope you like it.</p>
    <p>
      Please view our&nbsp;
      <Link to="/about">About Page</Link>
    </p>
  </div>
);

export default Home;
