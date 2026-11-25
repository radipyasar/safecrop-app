import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { setPendingPhoto } from '../lib/session.js';
import { LeafShape } from './Leaf.jsx';
import { CameraIcon, UploadIcon } from './Icons.jsx';

// The main job of the home page: upload (or take) a photo of a sick leaf.
// A photo dropped on the drop area opens the Check page with that photo ready.
export default function ScanCard() {
  const navigate = useNavigate();
  const [dragging, setDragging] = useState(false);

  function onDrop(event) {
    event.preventDefault();
    setDragging(false);
    const file = event.dataTransfer.files && event.dataTransfer.files[0];
    if (!file) return;
    setPendingPhoto(file);
    navigate('/check');
  }

  return (
    <section className="scan" aria-labelledby="scan-title">
      <div className="scan-copy">
        <h2 id="scan-title" className="scan-title">Check a sick leaf</h2>
        <p className="scan-text">
          Upload a clear photo of one leaf. SafeCrop checks the photo first, then compares it with labelled photos of
          8 diseases.
        </p>
        <div className="scan-actions">
          <Link to="/check" className="btn btn-primary">
            <UploadIcon /> Upload a photo
          </Link>
          <Link to="/check" className="btn btn-on-dark camera-only">
            <CameraIcon /> Use camera
          </Link>
        </div>
        <ol className="scan-steps" aria-label="What happens next">
          <li>
            <span className="scan-step-num">1</span>Photo check
          </li>
          <li>
            <span className="scan-step-num">2</span>Compare
          </li>
          <li>
            <span className="scan-step-num">3</span>Get advice
          </li>
        </ol>
      </div>

      <div
        className="dropzone"
        data-dragging={dragging || undefined}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        <LeafInFocus />
        <p className="dropzone-title">Drop a leaf photo here</p>
        <p className="dropzone-hint">JPEG, PNG, WebP or HEIC. One leaf, filling the frame.</p>
      </div>
    </section>
  );
}

// One tilted leaf with the camera's focus box on a spot.
function LeafInFocus() {
  const cx = 110;
  const cy = 86;
  const angle = -24;
  const scale = 1;
  const spots = [
    [58, 50, 4.2],
    [40, 72, 3.4],
    [62, 88, 5.2],
    [46, 104, 3],
  ];

  // where a point on the leaf ends up after the leaf is moved, tilted and scaled
  const place = ([x, y]) => {
    const a = (angle * Math.PI) / 180;
    const dx = (x - 50) * scale;
    const dy = (y - 70) * scale;
    return [cx + dx * Math.cos(a) - dy * Math.sin(a), cy + dx * Math.sin(a) + dy * Math.cos(a)];
  };
  const [fx, fy] = place(spots[2]);

  return (
    <svg className="dropzone-art" viewBox="0 0 220 172" role="img" aria-label="A leaf with brown spots" focusable="false">
      <g transform={`translate(${cx} ${cy}) rotate(${angle}) scale(${scale}) translate(-50 -70)`}>
        <LeafShape tone="hero" spots={spots} />
      </g>
      <rect x={fx - 16} y={fy - 16} width="32" height="32" rx="5" fill="none" stroke="#f3c94f" strokeWidth="2" />
    </svg>
  );
}
