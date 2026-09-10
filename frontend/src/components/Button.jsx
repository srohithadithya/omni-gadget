import React from 'react';
import '../index.css';

const Button = ({ children, variant = 'primary', size = 'md', onClick, disabled, loading, iconLeft, iconRight, className = '' }) => {
  const baseClasses = `btn btn-${variant} btn-${size} ${className}`;
  return (
    <button
      className={baseClasses}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading && <span className="loader" />}
      {!loading && iconLeft && <span className="nav-icon">{iconLeft}</span>}
      {!loading && children}
      {!loading && iconRight && <span className="nav-icon">{iconRight}</span>}
    </button>
  );
};

export default Button;