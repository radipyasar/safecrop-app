import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApiError, checkPhoto } from '../api.js';
import { saveCheck } from '../lib/history.js';
import { formatBytes, looksLikePhoto, makeThumbnail, MAX_UPLOAD_BYTES, preparePhoto } from '../lib/image.js';
import { rememberPhoto, takePendingPhoto } from '../lib/session.js';
import Steps from '../components/Steps.jsx';
import Notice from '../components/Notice.jsx';
import { CameraIcon, GalleryIcon, InfoIcon, UploadIcon } from '../components/Icons.jsx';

const TIPS = [
  'One leaf, filling most of the photo',
  'Good light, but not harsh direct sun',
  'Hold the phone steady and tap the leaf to focus',
  'Use the original photo, not one sent through a chat app',
];

// Error kinds where trying the same photo again can help (the others need a different file).
const RETRY_KINDS = new Set(['offline', 'unreachable', 'starting', 'server', 'bad_answer']);

// Upload or take a photo, see it, then send it to the back end.
export default function Check() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [previewFailed, setPreviewFailed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [dragging, setDragging] = useState(false);
  const busyRef = useRef(false);
  const uploadInput = useRef(null);
  const cameraInput = useRef(null);

  // a photo dropped on the home page
  useEffect(() => {
    const dropped = takePendingPhoto();
    if (dropped) choose(dropped);
  }, []);

  // show the chosen photo; free the memory when it changes
  useEffect(() => {
    if (!file) return undefined;
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setPreviewFailed(false);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function choose(chosen) {
    if (!chosen || busyRef.current) return;
    setError(null);
    if (!looksLikePhoto(chosen)) {
      setFile(null);
      setError(new ApiError('not_photo', 'This file is not a photo. Choose a JPEG, PNG, WebP or HEIC photo of a leaf.'));
      return;
    }
    if (chosen.size === 0) {
      setFile(null);
      setError(new ApiError('empty', 'The file is empty. Choose a photo of a leaf.'));
      return;
    }
    setFile(chosen);
  }

  function onInput(event) {
    choose(event.target.files && event.target.files[0]);
    event.target.value = ''; // so choosing the same file again still works
  }

  function onDrop(event) {
    event.preventDefault();
    setDragging(false);
    choose(event.dataTransfer.files && event.dataTransfer.files[0]);
  }

  async function runCheck() {
    if (!file || busyRef.current) return; // never send twice
    busyRef.current = true;
    setBusy(true);
    setError(null);
    try {
      const prepared = await preparePhoto(file);
      if (prepared.file.size > MAX_UPLOAD_BYTES) {
        throw new ApiError('too_big', `The photo is too big (${formatBytes(prepared.file.size)}). The limit is 10 MB.`);
      }
      const [check, thumb] = await Promise.all([checkPhoto(prepared.file), makeThumbnail(prepared.file)]);
      saveCheck(check, thumb);
      rememberPhoto(check.check_id, prepared.file);
      navigate(`/result/${check.check_id}`, { state: { fresh: true } });
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError('server'));
      busyRef.current = false;
      setBusy(false);
    }
  }

  function chooseAnother() {
    setFile(null);
    setError(null);
  }

  const failed = error && file;
  const stepStates = busy ? ['working', 'working', 'waiting'] : failed ? ['failed', 'failed', 'waiting'] : [];

  return (
    <main className="page">
      <header className="page-head">
        <h1 className="page-title">Check a leaf</h1>
        <p className="page-sub">Upload or take a photo of one sick leaf. SafeCrop checks the photo, then compares it with labelled photos.</p>
      </header>

      <div className="check-layout">
        <section
          className="card check-card"
          data-dragging={dragging || undefined}
          aria-label="Your photo"
          onDragOver={(e) => {
            e.preventDefault();
            if (!busy) setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
        >
          <input ref={uploadInput} type="file" accept="image/*,.heic,.heif" hidden onChange={onInput} />
          <input ref={cameraInput} type="file" accept="image/*" capture="environment" hidden onChange={onInput} />

          {!file ? (
            <div className="drop">
              <GalleryIcon className="drop-icon" />
              <p className="drop-title">Add a photo of one leaf</p>
              <p className="drop-hint">
                <span className="drag-only">Drop it here or choose one. </span>JPEG, PNG, WebP or HEIC, up to 10 MB.
              </p>
              <div className="btn-row">
                <button type="button" className="btn btn-primary" onClick={() => uploadInput.current.click()}>
                  <UploadIcon /> Upload a photo
                </button>
                <button type="button" className="btn btn-outline" onClick={() => cameraInput.current.click()}>
                  <CameraIcon /> Use camera
                </button>
              </div>
            </div>
          ) : (
            <div className="chosen">
              <div className="preview">
                {previewFailed ? (
                  <p className="preview-none">
                    This browser can't show a preview of this photo (iPhone HEIC photos often look like this). It can
                    still be checked.
                  </p>
                ) : (
                  previewUrl && <img src={previewUrl} alt="The photo you chose" onError={() => setPreviewFailed(true)} />
                )}
              </div>
              <p className="chosen-name">
                {file.name || 'Photo'} · {formatBytes(file.size)}
              </p>
              <div className="btn-row">
                <button type="button" className="btn btn-primary" onClick={runCheck} disabled={busy} aria-busy={busy}>
                  {busy ? <span className="spinner spinner-light" aria-hidden="true" /> : <CameraIcon />}
                  {busy ? 'Checking…' : 'Check this leaf'}
                </button>
                <button type="button" className="btn btn-outline" onClick={chooseAnother} disabled={busy}>
                  Choose another
                </button>
              </div>
            </div>
          )}

          {error && (
            <Notice tone="error" title={TITLES[error.kind] || 'Something went wrong'} live>
              <p>{error.message}</p>
              {file && RETRY_KINDS.has(error.kind) && <p>Press “Check this leaf” to try again.</p>}
            </Notice>
          )}
        </section>

        <aside className="check-side">
          <section className="card">
            <h2 className="card-title">What happens</h2>
            <Steps states={stepStates} />
            <p className="sr-only" aria-live="polite">
              {busy ? 'Checking the photo and comparing it with our library.' : ''}
            </p>
          </section>
          <section className="card">
            <h2 className="card-title">For a good photo</h2>
            <ul className="tips">
              {TIPS.map((t) => (
                <li key={t}>{t}</li>
              ))}
            </ul>
          </section>
          <p className="privacy">
            <InfoIcon /> Your photo is checked and not stored on our server. A small copy is kept only on this device,
            in History.
          </p>
        </aside>
      </div>
    </main>
  );
}

const TITLES = {
  offline: 'No internet',
  unreachable: "Can't reach SafeCrop",
  starting: 'SafeCrop is starting',
  empty: 'Empty file',
  too_big: 'Photo too big',
  not_photo: 'Not a photo',
  server: 'Server error',
  bad_answer: 'Server error',
};
