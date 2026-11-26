// Plain words for results, used by the Result page, History and Home.

export const OUR_DECISIONS = new Set(['sure', 'likely', 'not_sure']); // disease_id is one of our 8 diseases

export function cap(text) {
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : '';
}

function lower(text) {
  return text ? text.charAt(0).toLowerCase() + text.slice(1) : '';
}

const isOther = (id) => typeof id === 'string' && id.startsWith('other_');
const isHealthy = (id) => typeof id === 'string' && id.startsWith('healthy');

// A one-line title for a check (History list, recent checks on Home).
export function shortTitle(entry) {
  switch (entry.decision) {
    case 'retake':
      return "Couldn't read the photo";
    case 'healthy':
      return entry.disease_name || 'Looks healthy';
    case 'not_in_list':
      return 'Not in our list';
    case 'not_sure':
      return entry.disease_id === 'other_unknown' ? 'Not sure' : entry.disease_name || 'Not sure';
    default:
      return entry.disease_name || 'Unknown';
  }
}

// The answer the farmer sees: CLIP's result, or our second check's (Gemini's) answer when it said no (26 Nov).
export function finalOf(check, advice) {
  const f = advice && advice.final;
  return f && f.source === 'gemini' ? f : check.result;
}

// The card words for a saved History entry (uses the final answer).
export function describeEntry(entry) {
  return describe(finalOf(entry.check, entry.advice), entry.check.result);
}

// Everything the result card says, from the /api/check `result`, or from the advice's `final` answer when our
// second check (Gemini) said no; then `clip` is CLIP's result, shown as "closest match in our library".
//   tone: good | warn | bad | neutral (colour of the confidence badge)
export function describe(result, clip = null) {
  if (result.source === 'gemini') return describeSecondCheck(result, clip);
  const { decision, reason, disease_id, disease_name, crop, vote_share, runner_up } = result;
  const votePct = Math.round((vote_share || 0) * 100);
  const pest = disease_id === 'rice_stem_borer' ? 'Rice stem borer is an insect pest, not a disease.' : '';

  if (decision === 'sure' || decision === 'likely') {
    const showRunner = decision === 'likely' && runner_up && runner_up.vote_share >= 0.1;
    return {
      kicker: cap(crop),
      title: disease_name,
      badge: result.confidence_words,
      tone: decision === 'sure' ? 'good' : 'warn',
      lines: [
        `${votePct}% of the vote from the 5 most similar pictures in our library.`,
        showRunner ? `Next best guess: ${runnerName(runner_up)}.` : '',
        pest,
      ].filter(Boolean),
    };
  }

  if (decision === 'not_sure') {
    let first;
    if (reason === 'healthy_or_other_unclear' && runner_up) {
      first = isHealthy(runner_up.disease_id)
        ? `This could be a ${lower(runner_up.disease_name)}, or ${lower(disease_name)}.`
        : `This could be ${lower(runner_up.disease_name)} (a disease SafeCrop doesn't cover), or ${lower(disease_name)}.`;
    } else {
      first = `The closest match is ${lower(disease_name)}` + (runner_up ? `, but it could also be ${runnerName(runner_up)}.` : '.');
    }
    return {
      kicker: cap(crop),
      title: 'Not sure',
      badge: 'Not sure',
      tone: 'warn',
      lines: [first, 'Retake a clearer photo, or show the leaf to your local agriculture officer.', pest].filter(Boolean),
    };
  }

  if (decision === 'healthy') {
    return {
      kicker: cap(crop),
      title: 'Looks healthy',
      badge: 'Looks healthy',
      tone: 'good',
      lines: [
        `This looks like a ${lower(disease_name)}. SafeCrop found no sign of the 8 diseases it knows.`,
        'Keep watching the plant, and check again if spots, yellowing or holes appear.',
      ],
    };
  }

  if (decision === 'not_in_list') {
    return {
      kicker: cap(crop),
      title: "May be a disease SafeCrop doesn't know yet",
      badge: 'Not in our list',
      tone: 'neutral',
      lines: [
        `It looks most like ${lower(disease_name)}, which is not one of the 8 diseases SafeCrop covers.`,
        'Ask your local agriculture officer to look at the leaf.',
      ],
    };
  }

  // retake
  return {
    kicker: '',
    title: reason === 'not_a_leaf' ? "We can't read this photo" : 'This photo is too unclear',
    badge: "Can't read this photo",
    tone: 'bad',
    lines: [
      reason === 'not_a_leaf'
        ? 'SafeCrop can only check photos of leaves.'
        : 'The photo is too unclear for a safe answer, so SafeCrop is not guessing.',
    ],
  };
}

// Our second check (Gemini) said no to CLIP's answer: its answer is the main one (decision rule of 26 Nov).
function describeSecondCheck(final, clip) {
  const closest = clip && clip.disease_name ? `Closest match in our library: ${lower(clip.disease_name)}.` : '';
  const expert = 'Ask an expert: show the leaf to your local agriculture officer.';

  if (final.decision === 'second_check') {
    return {
      kicker: cap(final.crop),
      title: `SafeCrop's answer: ${final.disease_name}`,
      badge: 'From our second check',
      tone: 'warn',
      lines: [
        closest,
        'Our second check looked at your photo and did not agree with the closest match.',
        final.disease_id === 'rice_stem_borer' ? 'Rice stem borer is an insect pest, not a disease.' : '',
      ].filter(Boolean),
    };
  }
  if (final.decision === 'not_in_list') {
    return {
      kicker: '',
      title: "May be a problem SafeCrop doesn't know yet",
      badge: 'Not in our list',
      tone: 'neutral',
      lines: [`Our second check sees: ${lower(final.disease_name)}.`, closest, expert].filter(Boolean),
    };
  }
  // not_sure, other_unknown: Gemini said no but can't name it
  return {
    kicker: '',
    title: 'Not sure',
    badge: 'Not sure',
    tone: 'warn',
    lines: [
      "Our second check does not agree with the closest match, and can't say what this is.",
      closest,
      'Retake a clearer photo, or show the leaf to your local agriculture officer.',
    ].filter(Boolean),
  };
}

function runnerName(guess) {
  const name = lower(guess.disease_name);
  return isOther(guess.disease_id) ? `${name} (not one of our 8)` : name;
}

// Why the fallback advice was used, in plain words.
export const FALLBACK_WORDS = {
  no_key: 'the AI helper is switched off',
  quota: "the AI helper's daily limit is used up",
  timeout: 'the AI helper was too slow',
  error: 'the AI helper had a problem',
  client_error: 'the AI helper had a problem',
  unsafe: 'the AI answer did not pass our safety check',
  retake: 'the photo needs a retake',
};

export function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export function seconds(ms) {
  return ms >= 1000 ? (ms / 1000).toFixed(1) + ' s' : Math.round(ms) + ' ms';
}
