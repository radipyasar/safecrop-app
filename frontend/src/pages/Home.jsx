import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import ScanCard from '../components/ScanCard.jsx';
import Notice from '../components/Notice.jsx';
import { InfoIcon, LeafMark } from '../components/Icons.jsx';
import { fileUrl, getDiseases } from '../api.js';
import { onHistoryChange, readHistory } from '../lib/history.js';
import { getProfile } from '../lib/profile.js';
import { useLoad } from '../lib/useLoad.js';
import { cap, describe, shortTitle } from '../lib/words.js';

const RECENT = 4;

export default function Home() {
  return (
    <main className="page">
      <Header />
      <div className="dashboard">
        <ScanCard />
        <RecentChecks />
        <Diseases />
        <aside className="note">
          <InfoIcon className="note-icon" />
          <p>
            SafeCrop gives a best guess, not a final diagnosis. Ask your local agriculture officer before using any
            chemical.
          </p>
        </aside>
      </div>
      <footer className="page-foot">SafeCrop, CSE299 Junior Design, North South University.</footer>
    </main>
  );
}

function Header() {
  const now = new Date();
  const hour = now.getHours();
  const greeting = hour < 5 ? 'Good evening' : hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  const name = getProfile().name;
  const date = now.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });

  return (
    <header className="page-head">
      <h1 className="page-title">
        {greeting}
        {name ? `, ${name}` : ''}
      </h1>
      <p className="page-sub">{date}. What would you like to check today?</p>
    </header>
  );
}

// The newest checks from History (hidden when there are none).
function RecentChecks() {
  const [list, setList] = useState(readHistory);
  useEffect(() => onHistoryChange(setList), []);
  if (list.length === 0) return null;

  return (
    <section className="card" aria-labelledby="recent-title">
      <div className="card-head">
        <h2 id="recent-title" className="card-title">
          Recent checks
        </h2>
        <Link to="/history" className="card-link">
          See all ({list.length})
        </Link>
      </div>
      <ul className="recent">
        {list.slice(0, RECENT).map((c) => (
          <li key={c.id}>
            <Link to={`/result/${c.id}`} className="recent-item">
              <span className="recent-thumb">{c.thumb ? <img src={c.thumb} alt="" /> : <LeafMark />}</span>
              <span className="recent-text">
                <span className="recent-title">{shortTitle(c)}</span>
                <span className="badge badge-small" data-tone={describe(c.check.result).tone}>
                  {c.confidence_words}
                </span>
                <span className="recent-date">
                  {new Date(c.date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                </span>
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}

// The 8 diseases from the back end; each card opens its page.
function Diseases() {
  const { data, error, loading, retry } = useLoad('diseases', getDiseases);

  return (
    <section className="card" aria-labelledby="dis-title">
      <div className="card-head">
        <h2 id="dis-title" className="card-title">
          Diseases SafeCrop knows
        </h2>
        <Link to="/diseases" className="card-link">
          See all
        </Link>
      </div>
      {error && (
        <Notice
          tone="error"
          title="Could not load the diseases"
          actions={
            <button type="button" className="btn btn-outline btn-small" onClick={retry}>
              Try again
            </button>
          }
        >
          <p>{error.message}</p>
        </Notice>
      )}
      <ul className="diseases">
        {loading &&
          Array.from({ length: 8 }, (_, i) => (
            <li key={i} className="disease" aria-hidden="true">
              <span className="disease-thumb" />
              <span className="disease-text">
                <span className="skeleton" />
              </span>
            </li>
          ))}
        {(data || []).map((d) => (
          <li key={d.id}>
            <Link to={`/diseases/${d.id}`} className="disease">
              <span className="disease-thumb">
                {d.thumb_url && <img src={fileUrl(d.thumb_url)} alt="" loading="lazy" width="200" height="200" />}
              </span>
              <span className="disease-text">
                <span className="disease-crop">{cap(d.crop)}</span>
                <span className="disease-name">{diseaseShortName(d)}</span>
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}

// "Potato late blight" on potato → "Late blight" (the crop is shown above it)
function diseaseShortName(d) {
  const crop = d.crop.toLowerCase();
  const name = d.name_en;
  return name.toLowerCase().startsWith(crop + ' ') ? cap(name.slice(crop.length + 1)) : name;
}
