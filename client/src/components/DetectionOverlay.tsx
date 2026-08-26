import React from 'react';
import { type DetectionState, GUIDANCE_MESSAGES, type DetectionResult } from '../types/overlay';

interface DetectionOverlayProps {
  state: DetectionState;
  detections: DetectionResult[];
  videoWidth: number;
  videoHeight: number;
}

export const DetectionOverlay: React.FC<DetectionOverlayProps> = ({ state, detections, videoWidth, videoHeight }) => {
  let bannerStyle = { backgroundColor: 'rgba(0,0,0,0.7)', color: 'white' };
  
  if (state === 'DETECTED') {
    bannerStyle.backgroundColor = 'rgba(74, 222, 128, 0.9)'; // Green
    bannerStyle.color = '#000';
  } else if (state === 'UNSUPPORTED_FRUIT' || state === 'MULTIPLE_FRUITS') {
    bannerStyle.backgroundColor = 'rgba(239, 68, 68, 0.9)'; // Red
  }

  return (
    <div className="overlay-container" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
      
      {/* Guidance Banner */}
      <div 
        data-testid="guidance-banner"
        style={{
          position: 'absolute',
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          padding: '10px 20px',
          borderRadius: '24px',
          fontSize: '1rem',
          fontWeight: 'bold',
          textAlign: 'center',
          boxShadow: '0 4px 6px rgba(0,0,0,0.3)',
          zIndex: 10,
          ...bannerStyle
        }}
      >
        {GUIDANCE_MESSAGES[state]}
      </div>

      {/* SVG for Bounding Boxes */}
      <svg 
        style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 5 }}
        viewBox={videoWidth > 0 ? `0 0 ${videoWidth} ${videoHeight}` : "0 0 100 100"}
        preserveAspectRatio="none"
      >
        {detections.map((det, idx) => {
          let boxColor = '#4ade80';
          if (state === 'UNSUPPORTED_FRUIT' || state === 'MULTIPLE_FRUITS') {
            boxColor = '#ef4444';
          }

          const width = det.bbox.x2 - det.bbox.x1;
          const height = det.bbox.y2 - det.bbox.y1;

          return (
            <g key={idx}>
              <rect
                x={det.bbox.x1}
                y={det.bbox.y1}
                width={width}
                height={height}
                fill="none"
                stroke={boxColor}
                strokeWidth="4"
              />
              <rect
                x={det.bbox.x1}
                y={det.bbox.y1 - 30}
                width={Math.max(120, width * 0.5)}
                height="30"
                fill={boxColor}
              />
              <text
                x={det.bbox.x1 + 5}
                y={det.bbox.y1 - 10}
                fill="#000"
                fontSize="18"
                fontWeight="bold"
                fontFamily="sans-serif"
              >
                {det.fruit_type.toUpperCase()} {(det.detection_confidence * 100).toFixed(0)}%
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};
