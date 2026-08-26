export type DetectionState = 
  | 'NO_FRUIT'
  | 'UNSUPPORTED_FRUIT'
  | 'MULTIPLE_FRUITS'
  | 'SEARCHING'
  | 'DETECTED';

export const GUIDANCE_MESSAGES: Record<DetectionState, string> = {
  NO_FRUIT: 'Show one Apple or Banana clearly',
  UNSUPPORTED_FRUIT: 'This fruit is not supported in V1',
  MULTIPLE_FRUITS: 'Show only one fruit',
  SEARCHING: 'Searching for fruit...',
  DETECTED: 'Fruit detected, holding steady...'
};

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface DetectionResult {
  fruit_type: string;
  detection_confidence: number;
  bbox: BoundingBox;
}
