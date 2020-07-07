import React from 'react';
import {
  Link,
} from 'react-router-dom';

const About = () => (
  <div>
    <h1>About Us</h1>
    <p>This is the about page</p>
    <p>
      Please view our&nbsp;
      <Link to="/">Back Home</Link>
    </p>
  </div>
);

export default About;
