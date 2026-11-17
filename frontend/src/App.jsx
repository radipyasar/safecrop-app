import { Route, Routes } from 'react-router-dom';
import Sidebar from './components/Sidebar.jsx';
import BottomNav from './components/BottomNav.jsx';
import { LeafMark } from './components/Icons.jsx';
import Home from './pages/Home.jsx';
import Check from './pages/Check.jsx';
import Result from './pages/Result.jsx';
import Diseases from './pages/Diseases.jsx';
import DiseaseDetail from './pages/DiseaseDetail.jsx';
import History from './pages/History.jsx';
import Profile from './pages/Profile.jsx';
import NotFound from './pages/NotFound.jsx';

// Laptop and desktop: menu on the left, the page fills the rest of the screen.
// Phone: a small top bar, one column, and a bar at the bottom.
export default function App() {
  return (
    <div className="app">
      <Sidebar />
      <div className="app-main">
        <header className="mobile-bar">
          <div className="brand">
            <span className="brand-mark">
              <LeafMark />
            </span>
            <span className="brand-name">SafeCrop</span>
          </div>
        </header>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/check" element={<Check />} />
          <Route path="/result/:id" element={<Result />} />
          <Route path="/diseases" element={<Diseases />} />
          <Route path="/diseases/:id" element={<DiseaseDetail />} />
          <Route path="/history" element={<History />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
      <BottomNav />
    </div>
  );
}
