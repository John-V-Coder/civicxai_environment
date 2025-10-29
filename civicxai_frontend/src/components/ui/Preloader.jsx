import React from 'react';
import './Preloader.css';
import preloaderIcon from '../../assets/bite-piper.png';

const Preloader = () => {
  return (
    <div className="preloader">
      <img src={preloaderIcon} alt="Loading..." className="preloader-icon" />
    </div>
  );
};

export default Preloader;
