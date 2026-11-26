import { fileUrl } from '../api.js';
import { LeafMark } from './Icons.jsx';

// "Similar pictures from our library": the 5 closest database pictures (clean versions), so the farmer can compare
// by eye. A fingerprint saved by our second check has no picture (we never keep photos): it shows a leaf mark and
// Gemini's words.
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
        {neighbours.map((n, i) => (
          <li key={n.thumb_url || `added-${i}`} className="similar-item">
            {n.thumb_url ? (
              <img src={fileUrl(n.thumb_url)} alt={n.disease_name} loading="lazy" width="200" height="200" />
            ) : (
              <span className="similar-none" title="Saved by our second check: no photo is kept">
                <LeafMark />
              </span>
            )}
            <span className="similar-name">{n.disease_name}</span>
            {n.added && <span className="similar-note">Saved by our second check</span>}
          </li>
        ))}
      </ul>
    </section>
  );
}
