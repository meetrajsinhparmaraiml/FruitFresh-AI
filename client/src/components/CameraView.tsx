import { useState, useEffect, useRef } from 'react';

type CameraState = 'initializing' | 'granted' | 'denied' | 'error' | 'unsupported';

export function CameraView() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [cameraState, setCameraState] = useState<CameraState>('initializing');
  const [errorMessage, setErrorMessage] = useState<string>('');

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
      // Cleanly stop tracks on component unmount
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="camera-container">
      {cameraState === 'initializing' && (
        <div className="status-message">
          <p>Initializing camera...</p>
        </div>
      )}
      
      {cameraState === 'unsupported' && (
        <div className="status-message error">
          <p>{errorMessage}</p>
        </div>
      )}

      {cameraState === 'denied' && (
        <div className="status-message error">
          <p>{errorMessage}</p>
        </div>
      )}

      {cameraState === 'error' && (
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
            className="video-preview"
          />
          <div className="overlay">
            <div className="target-box">
              <span className="target-label">Show one Apple or Banana clearly</span>
            </div>
            <div className="readiness-indicator">
              <span className="dot ready"></span> Camera Ready
            </div>
          </div>
        </>
      )}
    </div>
  );
}
