import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { ApiError, getAdvice } from '../api.js';
import { getCheck, saveAdvice } from '../lib/history.js';
import { getProfile } from '../lib/profile.js';
import { forgetPhoto, photoFor } from '../lib/session.js';
import { finalOf, formatDate, OUR_DECISIONS, seconds, shortTitle } from '../lib/words.js';
import Steps from '../components/Steps.jsx';
import Notice from '../components/Notice.jsx';
import ResultCard from '../components/ResultCard.jsx';
import Neighbours from '../components/Neighbours.jsx';
import AdviceBox from '../components/AdviceBox.jsx';
import { BookIcon, ClockIcon, InfoIcon, RetakeIcon } from '../components/Icons.jsx';
import { useTitle } from '../lib/useTitle.js';

const HELPLINE = '16123';

// One check: the photo warning, the answer, the 5 similar pictures and the advice.
// The result comes from History in this browser (saved by the Check page), so opening it again needs no server call.
// Advice is asked for right after a new check; an old check without advice shows a "Get advice" button instead.
export default function Result() {
  const { id } = useParams();
  // a new page state for every check (so nothing from the last check is left over)
  return <ResultView key={id} id={id} />;
}

function ResultView({ id }) {
  const location = useLocation();
  const [entry] = useState(() => getCheck(id));
  const [adviceState, setAdviceState] = useState(entry?.advice ? 'done' : 'idle');
  const [advice, setAdvice] = useState(entry?.advice || null);
  // the answer shown: CLIP's, or our second check's (Gemini) when it said no (26 Nov)
  const shown = entry ? finalOf(entry.check, advice) : null;
  useTitle(entry ? shortTitle({ ...entry, ...shown }) : 'Result not found');
  const [adviceError, setAdviceError] = useState(null);
  const asked = useRef(new Set());

  const askAdvice = useCallback(async () => {
    setAdviceState('working');
    setAdviceError(null);
    try {
      // send the same photo again (kept in memory only), so Gemini can give its second opinion
      const a = await getAdvice(id, { file: photoFor(id), lang: getProfile().lang });
      saveAdvice(id, a);
      forgetPhoto(id);
      setAdvice(a);
      setAdviceState('done');
    } catch (err) {
      setAdviceError(err instanceof ApiError ? err : new ApiError('server'));
      setAdviceState('failed');
    }
  }, [id]);

  const decision = entry?.check.result.decision;
  const fresh = Boolean(location.state && location.state.fresh);

  // a new check: ask for advice once (not for "retake", which has nothing to advise on)
  useEffect(() => {
    if (!entry || entry.advice || decision === 'retake' || !fresh || asked.current.has(id)) return;
    asked.current.add(id);
    askAdvice();
  }, [entry, decision, fresh, id, askAdvice]);

  if (!entry) {
    return (
      <main className="page">
        <header className="page-head">
          <h1 className="page-title">Result not found</h1>
          <p className="page-sub">This check is not saved on this device. It may have been deleted from History.</p>
        </header>
        <div className="btn-row narrow">
          <Link to="/check" className="btn btn-primary">
            <RetakeIcon /> Check a leaf
          </Link>
          <Link to="/history" className="btn btn-outline">
            <ClockIcon /> See history
          </Link>
        </div>
      </main>
    );
  }

  const { check } = entry;
  const { result, photo_check: pc, neighbours, timing_ms: t } = check;
  const retake = decision === 'retake';
  const fromGemini = shown.source === 'gemini';
  const ours =
    (OUR_DECISIONS.has(shown.decision) || shown.decision === 'second_check') && shown.disease_id !== 'other_unknown';

  const step3 = retake ? 'skipped' : adviceState === 'idle' ? 'waiting' : adviceState;
  const notes = [
    `Done · ${seconds(t.read + t.photo_check)}`,
    `Done · ${seconds(t.embed + t.search)}`,
    step3 === 'done' && advice?.timing_ms ? `Done · ${seconds(advice.timing_ms)}` : '',
  ];

  // the photo warning already says how to retake; don't repeat it as the tip
  const tip = result.tip && result.tip !== pc.message ? result.tip : null;

  const buttons = (
    <>
      <Link to="/check" className="btn btn-outline">
        <RetakeIcon /> Retake
      </Link>
      {ours && (
        <Link to={`/diseases/${shown.disease_id}`} className="btn btn-outline">
          <BookIcon /> Learn about this disease
        </Link>
      )}
      <Link to="/history" className="btn btn-outline">
        <ClockIcon /> See history
      </Link>
    </>
  );

  return (
    <main className="page">
      <header className="page-head">
        <h1 className="page-title">Result</h1>
        <p className="page-sub">Checked {formatDate(entry.date)}</p>
      </header>

      <div className="result-layout">
        <div className="result-main">
          <section className="card steps-card" aria-label="Progress">
            <Steps states={['done', 'done', step3]} notes={notes} row />
          </section>

          {pc.message && result.reason !== 'not_a_leaf' && (
            <Notice tone="warn" title="Check your photo">
              <p>{pc.message}</p>
              {pc.fix_applied === 'resample' && <p>SafeCrop smoothed the blocky photo before comparing it.</p>}
            </Notice>
          )}

          <ResultCard
            result={shown}
            clip={fromGemini ? result : null}
            thumb={entry.thumb}
            tipToShow={fromGemini ? null : tip}
          />

          {retake && (
            <div className="btn-row">
              <Link to="/check" className="btn btn-primary">
                <RetakeIcon /> Retake the photo
              </Link>
            </div>
          )}

          {!(retake && result.reason === 'not_a_leaf') && (
            <Neighbours
              neighbours={neighbours}
              note={
                fromGemini
                  ? 'The closest pictures in our library. Our second check did not agree with them.'
                  : retake || decision === 'not_sure'
                    ? 'These are the closest pictures, but they may not match your leaf.'
                    : 'Compare your leaf with these pictures.'
              }
            />
          )}
        </div>

        <div className="result-side">
          {!retake &&
            (adviceState === 'idle' ? (
              <section className="card">
                <h2 className="card-title">What to do</h2>
                <p className="card-note">Advice was not loaded for this check.</p>
                <button type="button" className="btn btn-outline btn-small" onClick={askAdvice}>
                  Get advice
                </button>
              </section>
            ) : (
              <AdviceBox
                state={adviceState}
                advice={advice}
                error={adviceError}
                onRetry={askAdvice}
                actions={
                  <Link to="/check" className="btn btn-outline btn-small">
                    <RetakeIcon /> Check again
                  </Link>
                }
              />
            ))}

          <div className="btn-row result-buttons">{buttons}</div>

          <p className="safety">
            <InfoIcon />
            <span>
              SafeCrop gives a best guess, not a final diagnosis. Ask your local agriculture officer before using any
              chemical. Krishi Call Centre: <a href={`tel:${HELPLINE}`}>{HELPLINE}</a>.
            </span>
          </p>
        </div>
      </div>
    </main>
  );
}
