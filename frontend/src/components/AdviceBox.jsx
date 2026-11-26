import { FALLBACK_WORDS } from '../lib/words.js';
import Notice from './Notice.jsx';
import { ChatIcon } from './Icons.jsx';

// The advice: fills in when /api/advice answers. state: working | done | failed
export default function AdviceBox({ state, advice, error, onRetry, actions }) {
  return (
    <section className="card advice" aria-labelledby="advice-title" aria-busy={state === 'working'}>
      <div className="card-head">
        <h2 id="advice-title" className="card-title">
          <ChatIcon className="title-icon" /> What to do
        </h2>
      </div>

      {state === 'working' && (
        <div className="advice-loading" role="status">
          <p className="advice-wait">Writing advice from our checked facts…</p>
          <span className="skeleton" />
          <span className="skeleton" />
          <span className="skeleton short" />
        </div>
      )}

      {state === 'failed' && (
        <Notice
          tone="error"
          title={error?.kind === 'not_found' ? 'Advice is not available for this check' : 'Advice could not load'}
          live
          actions={
            error?.kind === 'not_found'
              ? actions
              : onRetry && (
                  <button type="button" className="btn btn-outline btn-small" onClick={onRetry}>
                    Try again
                  </button>
                )
          }
        >
          <p>
            {error?.kind === 'not_found'
              ? 'SafeCrop no longer remembers this check (the server may have restarted). Check the photo again to get advice.'
              : error?.message}
          </p>
        </Notice>
      )}

      {state === 'done' && advice && (
        <div className="advice-body">
          {advice.agrees === 'no' &&
            (advice.final && advice.final.source === 'gemini' ? (
              <Notice tone="warn" title="Our two checks disagree">
                <p>
                  The picture comparison and our second check gave different answers. The answer shown comes from the
                  second check. If you are not sure, ask your local agriculture officer.
                </p>
              </Notice>
            ) : (
              // a check saved before 26 Nov (no `final`): today's notice
              <Notice tone="warn" title="Second opinion">
                <p>Our second check is not sure about this answer. Retake the photo or ask an expert.</p>
              </Notice>
            ))}
          <p className="advice-summary" lang={advice.lang}>
            {advice.summary}
          </p>
          {advice.steps?.length > 0 && (
            <ol className="advice-steps" lang={advice.lang}>
              {advice.steps.map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ol>
          )}
          {advice.see_expert_when && (
            <p className="advice-expert" lang={advice.lang}>
              <strong>Call an expert when:</strong> {advice.see_expert_when}
            </p>
          )}
          {advice.safety_note && (
            <p className="advice-safety" lang={advice.lang}>
              {advice.safety_note}
            </p>
          )}
          <p className="advice-source">
            {advice.source === 'gemini'
              ? 'Written by Gemini (an AI helper) from SafeCrop’s checked facts.'
              : `From SafeCrop’s checked facts (${FALLBACK_WORDS[advice.fallback_reason] || 'the AI helper was not available'}).`}
          </p>
        </div>
      )}
    </section>
  );
}
