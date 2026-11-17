import { NavLink } from 'react-router-dom';
import { BookIcon, CameraIcon, ClockIcon, HomeIcon, UserIcon } from './Icons.jsx';

// The bar at the bottom of the app. The camera button in the middle is the quickest way to check a leaf.
export default function BottomNav() {
  return (
    <nav className="bottom-nav" aria-label="Main">
      <NavItem to="/" Icon={HomeIcon} label="Home" />
      <NavItem to="/diseases" Icon={BookIcon} label="Diseases" />
      <NavLink to="/check" className="nav-item nav-check">
        <span className="nav-check-circle">
          <CameraIcon />
        </span>
        <span className="nav-label">Check</span>
      </NavLink>
      <NavItem to="/history" Icon={ClockIcon} label="History" />
      <NavItem to="/profile" Icon={UserIcon} label="Profile" />
    </nav>
  );
}

function NavItem({ to, Icon, label }) {
  return (
    <NavLink to={to} end={to === '/'} className="nav-item">
      <Icon className="nav-icon" />
      <span className="nav-label">{label}</span>
    </NavLink>
  );
}
