import { useState, useEffect, useRef } from 'react';
import { DetectionOverlay } from '../components/DetectionOverlay';
import { type DetectionState, type DetectionResult } from '../types/overlay';

type CameraState = 'initializing' | 'granted' | 'denied' | 'error' | 'unsupported';

export function CameraScreen() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [cameraState, setCameraState] = useState<CameraState>('initializing');
  const [errorMessage, setErrorMessage] = useState<string>('');
  
  const [detectionState] = useState<DetectionState>('NO_FRUIT');
  const [detections] = useState<DetectionResult[]>([]);
  const [videoDimensions, setVideoDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    let stream: MediaStream | null = null;

    const initCamera = async () => {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setCameraState('unsupported');
        setErrorMessage('Camera API is not supported in this browser.');
        return;
      }

      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' }
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setCameraState('granted');
      } catch (err: any) {
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
          setCameraState('denied');
          setErrorMessage('Camera access was denied. Please grant permissions to use the app.');
        } else {
          setCameraState('error');
          setErrorMessage(err.message || 'An unknown error occurred while accessing the camera.');
        }
      }
    };

    initCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const handleVideoPlay = () => {
    if (videoRef.current) {
      setVideoDimensions({
        width: videoRef.current.videoWidth,
        height: videoRef.current.videoHeight
      });
    }
  };

  return (
    <div className="camera-container">
      {cameraState === 'initializing' && (
        <div className="status-message">
          <p>Initializing camera...</p>
        </div>
      )}
      
      {(cameraState === 'unsupported' || cameraState === 'denied' || cameraState === 'error') && (
        <div className="status-message error">
          <p>{errorMessage}</p>
        </div>
      )}

      {cameraState === 'granted' && (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            onPlay={handleVideoPlay}
            className="video-preview"
          />
          <div className="overlay">
            <div className="target-box" style={{ opacity: detectionState === 'NO_FRUIT' ? 1 : 0.2 }}>
            </div>
            <DetectionOverlay 
              state={detectionState} 
              detections={detections} 
              videoWidth={videoDimensions.width}
              videoHeight={videoDimensions.height}
            />
          </div>
        </>
      )}
    </div>
  );
}
