import { CameraScreen } from './screens/CameraScreen';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>FruitFresh AI V2</h1>
        <p className="subtitle">Supported Fruits: Apple & Banana</p>
      </header>
      
      <main className="app-main">
        <CameraScreen />
      </main>

      <footer className="app-footer">
        <div className="disclaimer">
          <strong>Disclaimer:</strong> This system estimates visible external condition only. 
          It does NOT assess internal rot, pathogens, pesticide safety, nutrition, or guaranteed shelf life.
        </div>
      </footer>
    </div>
  );
}

export default App;
