import { CheckIcon } from './Icons.jsx';

// The 3 steps of a check. Each step's state comes from a real call:
//   "Photo check" and "Compare" while /api/check runs, "Get advice" while /api/advice runs.
// state: waiting | working | done | failed | skipped
export const STEP_LABELS = ['Photo check', 'Compare', 'Get advice'];

export default function Steps({ states, notes = [], row = false }) {
  return (
    <ol className={'steps' + (row ? ' steps-row' : '')} aria-label="Progress">
      {STEP_LABELS.map((label, i) => {
        const state = states[i] || 'waiting';
        return (
          <li key={label} className="step" data-state={state}>
            <span className="step-dot" aria-hidden="true">
              {state === 'done' ? <CheckIcon /> : state === 'working' ? <span className="spinner" /> : i + 1}
            </span>
            <span className="step-text">
              <span className="step-label">{label}</span>
              <span className="step-note">{notes[i] || WORDS[state]}</span>
            </span>
          </li>
        );
      })}
    </ol>
  );
}

const WORDS = { waiting: 'Waiting', working: 'Working…', done: 'Done', failed: 'Stopped', skipped: 'Not needed' };
