import { Link } from 'react-router-dom';
import { fileUrl, getDiseases } from '../api.js';
import { useLoad } from '../lib/useLoad.js';
import { cap } from '../lib/words.js';
import Notice from '../components/Notice.jsx';
import { ChevronIcon } from '../components/Icons.jsx';

// The 8 problems SafeCrop knows, from GET /api/diseases, grouped by crop.
export default function Diseases() {
  const { data, error, loading, retry } = useLoad('diseases', getDiseases);

  const groups = [];
  for (const d of data || []) {
    let g = groups.find((x) => x.crop === d.crop);
    if (!g) groups.push((g = { crop: d.crop, items: [] }));
    g.items.push(d);
  }

  return (
    <main className="page">
      <header className="page-head">
        <h1 className="page-title">Diseases</h1>
        <p className="page-sub">The 8 problems SafeCrop knows: 7 diseases and 1 insect pest. Tap one to learn more.</p>
      </header>

      {loading && <DiseaseSkeleton />}

      {error && (
        <Notice
          tone="error"
          title="Could not load the diseases"
          live
          actions={
            <button type="button" className="btn btn-outline btn-small" onClick={retry}>
              Try again
            </button>
          }
        >
          <p>{error.message}</p>
        </Notice>
      )}

      <div className="crop-groups">
        {groups.map((g) => (
          <section key={g.crop} aria-labelledby={`crop-${g.crop}`}>
            <h2 id={`crop-${g.crop}`} className="crop-title">
              {cap(g.crop)}
            </h2>
            <ul className="disease-cards">
              {g.items.map((d) => (
                <li key={d.id}>
                  <DiseaseCard d={d} />
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </main>
  );
}

export function DiseaseCard({ d }) {
  return (
    <Link to={`/diseases/${d.id}`} className="dcard">
      <span className="dcard-photo">
        {d.thumb_url && <img src={fileUrl(d.thumb_url)} alt="" loading="lazy" width="200" height="200" />}
      </span>
      <span className="dcard-body">
        <span className="dcard-name">
          {d.name_en}
          {d.kind === 'pest' && <span className="tag">Insect pest</span>}
        </span>
        <span className="dcard-bn" lang="bn">
          {d.name_bn}
        </span>
        <span className="dcard-short">{d.short}</span>
      </span>
      <ChevronIcon className="dcard-chevron" />
    </Link>
  );
}

function DiseaseSkeleton() {
  return (
    <ul className="disease-cards" aria-label="Loading">
      {[0, 1, 2, 3].map((i) => (
        <li key={i} className="dcard dcard-loading">
          <span className="dcard-photo" />
          <span className="dcard-body">
            <span className="skeleton" />
            <span className="skeleton short" />
          </span>
        </li>
      ))}
    </ul>
  );
}
