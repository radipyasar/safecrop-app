import { describe } from '../lib/words.js';
import { LeafMark } from './Icons.jsx';

// The answer: the farmer's photo, the disease (or a special result), how sure, and the next best guess.
export default function ResultCard({ result, thumb, tipToShow }) {
  const d = describe(result);
  return (
    <section className="card verdict" data-decision={result.decision} aria-labelledby="verdict-title">
      <div className="verdict-photo">
        {thumb ? <img src={thumb} alt="Your photo" /> : <LeafMark className="verdict-photo-none" />}
      </div>
      <div className="verdict-body">
        {d.kicker && <p className="verdict-kicker">{d.kicker}</p>}
        <h2 id="verdict-title" className="verdict-title">
          {d.title}
        </h2>
        <p>
          <span className="badge" data-tone={d.tone}>
            {d.badge}
          </span>
        </p>
        {d.lines.map((line) => (
          <p key={line} className="verdict-line">
            {line}
          </p>
        ))}
        {tipToShow && <p className="verdict-tip">{tipToShow}</p>}
      </div>
    </section>
  );
}
