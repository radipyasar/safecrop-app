import { useParams } from 'react-router-dom';
import SimplePage from '../components/SimplePage.jsx';

// Day 5: the disease, how sure we are, the 5 closest photos and the advice.
export default function Result() {
  const { id } = useParams();
  return <SimplePage title="Result" sub={`Check number ${id}. (Coming on Day 5.)`} />;
}
