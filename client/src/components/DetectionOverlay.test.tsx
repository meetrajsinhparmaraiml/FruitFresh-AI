import { render, screen } from '@testing-library/react';
import { DetectionOverlay } from './DetectionOverlay';
import '@testing-library/jest-dom';
import { describe, it, expect } from 'vitest';

describe('DetectionOverlay', () => {
  it('renders NO_FRUIT state correctly', () => {
    render(<DetectionOverlay state="NO_FRUIT" detections={[]} videoWidth={640} videoHeight={480} />);
    expect(screen.getByTestId('guidance-banner')).toHaveTextContent('Show one Apple or Banana clearly');
  });

  it('renders UNSUPPORTED_FRUIT state correctly', () => {
    render(<DetectionOverlay state="UNSUPPORTED_FRUIT" detections={[{ fruit_type: 'orange', detection_confidence: 0.9, bbox: { x1: 0, y1: 0, x2: 10, y2: 10 } }]} videoWidth={640} videoHeight={480} />);
    expect(screen.getByTestId('guidance-banner')).toHaveTextContent('This fruit is not supported in V1');
  });

  it('renders MULTIPLE_FRUITS state correctly', () => {
    render(<DetectionOverlay state="MULTIPLE_FRUITS" detections={[]} videoWidth={640} videoHeight={480} />);
    expect(screen.getByTestId('guidance-banner')).toHaveTextContent('Show only one fruit');
  });
  
  it('renders DETECTED state correctly', () => {
    render(<DetectionOverlay state="DETECTED" detections={[{ fruit_type: 'apple', detection_confidence: 0.95, bbox: { x1: 0, y1: 0, x2: 10, y2: 10 } }]} videoWidth={640} videoHeight={480} />);
    expect(screen.getByTestId('guidance-banner')).toHaveTextContent('Fruit detected, holding steady...');
  });
});
