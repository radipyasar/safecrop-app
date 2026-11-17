import { NavLink } from 'react-router-dom';
import { BookIcon, CameraIcon, ClockIcon, HomeIcon, LeafMark, UserIcon } from './Icons.jsx';
import ServerStatus from './ServerStatus.jsx';

const LINKS = [
  { to: '/', label: 'Home', Icon: HomeIcon },
  { to: '/check', label: 'Check a leaf', Icon: CameraIcon },
  { to: '/diseases', label: 'Diseases', Icon: BookIcon },
  { to: '/history', label: 'History', Icon: ClockIcon },
  { to: '/profile', label: 'Profile', Icon: UserIcon },
];

// The menu on the left (laptops and bigger screens).
// NavLink adds aria-current="page" to the link of the page you are on; the CSS colours it green.
export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">
          <LeafMark />
        </span>
        <span className="brand-name">SafeCrop</span>
      </div>

      <nav aria-label="Main">
        <ul className="side-links">
          {LINKS.map(({ to, label, Icon }) => (
            <li key={to}>
              <NavLink to={to} end={to === '/'} className="side-link">
                <Icon className="side-link-icon" />
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="side-foot">
        <ServerStatus />
        <p>SafeCrop, CSE299 Junior Design, NSU.</p>
      </div>
    </aside>
  );
}
