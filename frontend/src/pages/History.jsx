import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { clearHistory, deleteCheck, MAX_CHECKS, onHistoryChange, readHistory } from '../lib/history.js';
import { describe, formatDate, shortTitle } from '../lib/words.js';
import { CameraIcon, ChevronIcon, LeafMark, TrashIcon } from '../components/Icons.jsx';
import { useTitle } from '../lib/useTitle.js';

// Past checks saved in this browser, newest first. Opening one shows the saved result (no server call).
export default function History() {
  useTitle('History');
  const [list, setList] = useState(readHistory);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => onHistoryChange(setList), []);

  return (
    <main className="page">
      <header className="page-head head-row">
        <div>
          <h1 className="page-title">History</h1>
          <p className="page-sub">
            Your past checks, saved only on this device (the newest {MAX_CHECKS} are kept).
          </p>
        </div>
        {list.length > 0 && !confirming && (
          <button type="button" className="btn btn-outline btn-small" onClick={() => setConfirming(true)}>
            <TrashIcon /> Clear all
          </button>
        )}
      </header>

      {confirming && (
        <div className="confirm" role="alertdialog" aria-labelledby="confirm-title">
          <p id="confirm-title" className="confirm-title">
            Delete all {list.length} saved {list.length === 1 ? 'check' : 'checks'}?
          </p>
          <p className="confirm-text">This can't be undone.</p>
          <div className="btn-row">
            <button
              type="button"
              className="btn btn-danger btn-small"
              onClick={() => {
                clearHistory();
                setConfirming(false);
              }}
            >
              Yes, delete all
            </button>
            <button type="button" className="btn btn-outline btn-small" onClick={() => setConfirming(false)} autoFocus>
              Cancel
            </button>
          </div>
        </div>
      )}

      {list.length === 0 ? (
        <section className="card empty">
          <LeafMark className="empty-icon" />
          <p className="empty-title">No checks yet. Check your first leaf.</p>
          <Link to="/check" className="btn btn-primary">
            <CameraIcon /> Check a leaf
          </Link>
        </section>
      ) : (
        <ul className="history">
          {list.map((c) => (
            <li key={c.id} className="hrow">
              <Link to={`/result/${c.id}`} className="hrow-link">
                <span className="hrow-thumb">{c.thumb ? <img src={c.thumb} alt="" /> : <LeafMark />}</span>
                <span className="hrow-text">
                  <span className="hrow-title">{shortTitle(c)}</span>
                  <span className="hrow-meta">
                    <span className="badge badge-small" data-tone={describe(c.check.result).tone}>
                      {c.confidence_words}
                    </span>
                    <span>{formatDate(c.date)}</span>
                  </span>
                </span>
                <ChevronIcon className="hrow-chevron" />
              </Link>
              <button
                type="button"
                className="icon-btn"
                onClick={() => deleteCheck(c.id)}
                aria-label={`Delete the check from ${formatDate(c.date)} (${shortTitle(c)})`}
              >
                <TrashIcon />
              </button>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
