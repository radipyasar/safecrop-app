import { Link, useParams } from 'react-router-dom';
import SimplePage from '../components/SimplePage.jsx';

// Day 6: facts about one disease, from GET /api/diseases/{id}.
export default function DiseaseDetail() {
  const { id } = useParams();
  return (
    <SimplePage title="Disease" sub={`Disease "${id}". (Coming on Day 6.)`}>
      <Link to="/diseases">Back to all diseases</Link>
    </SimplePage>
  );
}
