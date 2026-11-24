import { useState } from 'react';
import { getProfile, saveProfile } from '../lib/profile.js';
import Notice from '../components/Notice.jsx';
import { InfoIcon } from '../components/Icons.jsx';

const CROPS = ['Rice', 'Jute', 'Potato', 'Black gram', 'Apple', 'Pear', 'Grape'];

// The farmer's name, district, crops and language, saved in this browser only.
export default function Profile() {
  const [form, setForm] = useState(getProfile);
  const [saved, setSaved] = useState(false);
  const [failed, setFailed] = useState(false);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
    setSaved(false);
  }

  function toggleCrop(crop) {
    update('crops', form.crops.includes(crop) ? form.crops.filter((c) => c !== crop) : [...form.crops, crop]);
  }

  function onSubmit(event) {
    event.preventDefault();
    try {
      setForm(saveProfile(form));
      setSaved(true);
      setFailed(false);
    } catch {
      setFailed(true);
    }
  }

  return (
    <main className="page">
      <header className="page-head">
        <h1 className="page-title">Profile</h1>
        <p className="page-sub">Saved only on this device. SafeCrop does not send your name or district anywhere.</p>
      </header>

      <div className="profile-layout">
        <form className="card form" onSubmit={onSubmit}>
          <label className="field">
            <span className="field-label">Name</span>
            <input
              type="text"
              value={form.name}
              onChange={(e) => update('name', e.target.value)}
              maxLength={60}
              autoComplete="given-name"
              placeholder="Your name"
            />
          </label>

          <label className="field">
            <span className="field-label">District</span>
            <input
              type="text"
              value={form.district}
              onChange={(e) => update('district', e.target.value)}
              maxLength={60}
              placeholder="For example: Rangpur"
            />
          </label>

          <fieldset className="field">
            <legend className="field-label">Main crops</legend>
            <div className="chips">
              {CROPS.map((crop) => (
                <label key={crop} className="chip">
                  <input type="checkbox" checked={form.crops.includes(crop)} onChange={() => toggleCrop(crop)} />
                  <span>{crop}</span>
                </label>
              ))}
            </div>
            <input
              type="text"
              value={form.otherCrops}
              onChange={(e) => update('otherCrops', e.target.value)}
              maxLength={120}
              placeholder="Other crops (optional)"
              aria-label="Other crops"
            />
          </fieldset>

          <fieldset className="field">
            <legend className="field-label">Language for advice</legend>
            <div className="chips">
              {[
                ['en', 'English'],
                ['bn', 'বাংলা (Bangla)'],
              ].map(([value, label]) => (
                <label key={value} className="chip">
                  <input type="radio" name="lang" value={value} checked={form.lang === value} onChange={() => update('lang', value)} />
                  <span>{label}</span>
                </label>
              ))}
            </div>
            <p className="field-hint">
              The app's screens are in English. With Bangla, Gemini writes the advice in Bangla; the backup advice (when
              Gemini is not available) is in English.
            </p>
          </fieldset>

          <div className="btn-row">
            <button type="submit" className="btn btn-primary">
              Save
            </button>
          </div>
          <p className="sr-only" aria-live="polite">
            {saved ? 'Saved' : ''}
          </p>
          {saved && <Notice tone="good" title="Saved" />}
          {failed && (
            <Notice tone="error" title="Could not save" live>
              <p>This browser does not allow saving (private mode?).</p>
            </Notice>
          )}
        </form>

        <section className="card about" aria-labelledby="about-title">
          <h2 id="about-title" className="card-title">
            About SafeCrop
          </h2>
          <p>
            SafeCrop looks at a photo of one leaf. It first checks the photo (blur, grain, darkness, blockiness), then
            compares it with labelled pictures using a fine-tuned AI model (CLIP), and shows the 5 most similar pictures.
            Gemini then writes advice from facts we checked.
          </p>
          <h3 className="about-sub">What it can do</h3>
          <ul className="facts">
            <li>Recognise 8 problems: potato late blight, apple scab, rice stem borer, black gram yellow mosaic, pear leaf spot, grape leaf blight, jute mosaic and jute dieback.</li>
            <li>Say when a leaf looks healthy, when it may be a disease it doesn't know, and when the photo is too unclear.</li>
            <li>Warn you about a bad photo and tell you how to take a better one.</li>
          </ul>
          <h3 className="about-sub">What it cannot do</h3>
          <ul className="facts">
            <li>It does not know other diseases, and it has not been tested much on real phone photos yet.</li>
            <li>It does not give chemical names or doses.</li>
            <li>It is not a final diagnosis.</li>
          </ul>
          <p className="safety">
            <InfoIcon />
            <span>
              SafeCrop gives a best guess, not a final diagnosis. Ask your local agriculture officer before using any
              chemical. Krishi Call Centre: <a href="tel:16123">16123</a>.
            </span>
          </p>
          <p className="field-hint">
            Privacy: photos are checked and not stored on our server. History and this profile stay in this browser.
          </p>
          <p className="field-hint">SafeCrop, CSE299 Junior Design, North South University.</p>
        </section>
      </div>
    </main>
  );
}
