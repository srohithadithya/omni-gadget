import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App component', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />);
    expect(container).toBeInTheDocument();
  });
});
