import React from 'react';

export const Slider = ({ value, onChange, min = 0, max = 100, step = 1 }) => {
  return (
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      style={{
        width: '100%',
        margin: '0.5rem 0',
      }}
    />
  );
};
