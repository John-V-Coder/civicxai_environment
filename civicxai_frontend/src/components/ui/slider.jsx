import React from 'react';

export const Slider = ({ 
  value, 
  onChange, 
  onValueChange, 
  min = 0, 
  max = 100, 
  step = 1,
  className = '',
  ...props 
}) => {
  const handleChange = (e) => {
    const newValue = Number(e.target.value);
    
    // Support both onChange and onValueChange (shadcn/ui API)
    if (onValueChange && typeof onValueChange === 'function') {
      onValueChange([newValue]); // shadcn/ui expects array
    }
    if (onChange && typeof onChange === 'function') {
      onChange(newValue);
    }
  };

  // Handle array values from shadcn/ui API
  const currentValue = Array.isArray(value) ? value[0] : value;

  return (
    <input
      type="range"
      min={min}
      max={max}
      step={step}
      value={currentValue || min}
      onChange={handleChange}
      className={`w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600 ${className}`}
      {...props}
    />
  );
};
