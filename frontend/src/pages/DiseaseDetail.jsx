import { Link, useParams } from 'react-router-dom';
import { fileUrl, getDisease } from '../api.js';
import { useLoad } from '../lib/useLoad.js';
import { cap } from '../lib/words.js';
import Notice from '../components/Notice.jsx';
import { CameraIcon, InfoIcon, LinkIcon } from '../components/Icons.jsx';

// Facts about one disease, from GET /api/diseases/{id}: checked facts with their sources.
export default function DiseaseDetail() {
  const { id } = useParams();
  const { data: d, error, loading, retry } = useLoad('disease:' + id, () => getDisease(id));

  return (
    <main className="page">
      <p className="back">
        <Link to="/diseases">← All diseases</Link>
      </p>

      {loading && (
        <div className="card detail-loading" aria-label="Loading">
          <span className="skeleton" />
          <span className="skeleton" />
          <span className="skeleton short" />
        </div>
      )}

      {error && (
        <>
          <header className="page-head">
            <h1 className="page-title">{error.kind === 'not_found' ? 'Disease not found' : 'Could not load this page'}</h1>
          </header>
          <Notice
            tone="error"
            live
            actions={
              error.kind !== 'not_found' && (
                <button type="button" className="btn btn-outline btn-small" onClick={retry}>
                  Try again
                </button>
              )
            }
          >
            <p>{error.message}</p>
          </Notice>
        </>
      )}

      {d && (
        <>
          <header className="page-head">
            <p className="verdict-kicker">
              {cap(d.crop)} · {d.kind === 'pest' ? 'Insect pest' : 'Disease'}
            </p>
            <h1 className="page-title">{d.name_en}</h1>
            <p className="detail-bn" lang="bn">
              {d.name_bn}
            </p>
            <p className="detail-short">{d.short}</p>
          </header>

          <div className="detail-layout">
            <div className="detail-main">
              {d.photos.length > 0 && (
                <section className="card" aria-labelledby="photos-title">
                  <h2 id="photos-title" className="card-title">
                    Example pictures
                  </h2>
                  <ul className="similar detail-photos">
                    {d.photos.slice(0, 4).map((p) => (
                      <li key={p} className="similar-item">
                        <img src={fileUrl(p)} alt={`${d.name_en}, example`} loading="lazy" width="200" height="200" />
                      </li>
                    ))}
                  </ul>
                  {d.photo_credit && <p className="credit">Photos: {d.photo_credit}</p>}
                </section>
              )}
              <FactList title="Signs to look for" items={d.signs} />
              <FactList title="What to do now" items={d.do_now} ordered />
              <FactList title="How to prevent it" items={d.prevention} />
            </div>

            <div className="detail-side">
              <section className="card">
                <h2 className="card-title">When to call an expert</h2>
                <p className="fact-text">{d.see_expert_when}</p>
                <p className="fact-text">
                  Krishi Call Centre: <a href={`tel:${d.helpline}`}>{d.helpline}</a>, or your Upazila Agriculture Office.
                </p>
              </section>
              <section className="card">
                <h2 className="card-title">What causes it</h2>
                <p className="fact-text">{d.cause}</p>
              </section>
              {d.looks_like.length > 0 && <FactList title="Can be confused with" items={d.looks_like} />}
              <section className="card">
                <h2 className="card-title">Sources</h2>
                <ul className="sources">
                  {d.sources.map((s) => (
                    <li key={s.url}>
                      <a href={s.url} target="_blank" rel="noopener noreferrer">
                        {s.title} <LinkIcon className="ext-icon" />
                        <span className="sr-only">(opens in a new tab)</span>
                      </a>
                    </li>
                  ))}
                </ul>
              </section>
              <p className="safety">
                <InfoIcon />
                <span>
                  SafeCrop never gives chemical names or doses. Ask your local agriculture officer which product and
                  dose to use.
                </span>
              </p>
              <Link to="/check" className="btn btn-primary">
                <CameraIcon /> Check a leaf
              </Link>
            </div>
          </div>
        </>
      )}
    </main>
  );
}

function FactList({ title, items, ordered = false }) {
  if (!items || items.length === 0) return null;
  const List = ordered ? 'ol' : 'ul';
  return (
    <section className="card">
      <h2 className="card-title">{title}</h2>
      <List className={ordered ? 'facts facts-ordered' : 'facts'}>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </List>
    </section>
  );
}
