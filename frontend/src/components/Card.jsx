import React from 'react';
import './index.css';

const Card = ({
  children,
  className = '',
  elevated = false,
  interactive = false,
  onClick,
  ...rest
}) => {
  const baseClasses = `
    card
    ${elevated ? 'card-elevated' : ''}
    ${interactive ? 'card-interactive' : ''}
    ${className}
  `;

  return (
    <div
      className={baseClasses.trim()}
      onClick={onClick}
      {...rest}
    >
      {children}
    </div>
  );
};

export default Card;