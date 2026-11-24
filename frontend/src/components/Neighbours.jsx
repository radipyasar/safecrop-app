import { fileUrl } from '../api.js';

// "Similar pictures from our library": the 5 closest database pictures (clean versions), so the farmer can compare
// by eye.
export default function Neighbours({ neighbours, note }) {
  if (!neighbours || neighbours.length === 0) return null;
  return (
    <section className="card" aria-labelledby="similar-title">
      <div className="card-head">
        <h2 id="similar-title" className="card-title">
          Similar pictures from our library
        </h2>
        <span className="count">{neighbours.length}</span>
      </div>
      {note && <p className="card-note">{note}</p>}
      <ul className="similar">
        {neighbours.map((n) => (
          <li key={n.thumb_url} className="similar-item">
            <img src={fileUrl(n.thumb_url)} alt={n.disease_name} loading="lazy" width="200" height="200" />
            <span className="similar-name">{n.disease_name}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
