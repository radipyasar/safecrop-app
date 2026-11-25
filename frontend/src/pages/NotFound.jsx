import { Link } from 'react-router-dom';
import SimplePage from '../components/SimplePage.jsx';
import { useTitle } from '../lib/useTitle.js';

// Shown for any address that is not one of our pages.
export default function NotFound() {
  useTitle('Page not found');
  return (
    <SimplePage title="Page not found" sub="This address is not a SafeCrop page.">
      <Link to="/">Go to the home page</Link>
    </SimplePage>
  );
}
