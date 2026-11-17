import ScanCard from '../components/ScanCard.jsx';
import Leaf from '../components/Leaf.jsx';
import { InfoIcon } from '../components/Icons.jsx';
import { DISEASES } from '../data/sample.js';

export default function Home() {
  return (
    <main className="page">
      <Header />
      <div className="dashboard">
        <ScanCard />
        <Diseases />
        <aside className="note">
          <InfoIcon className="note-icon" />
          <p>
            SafeCrop gives a best guess from photos, not a final diagnosis. Before spraying, check with your local
            agriculture officer.
          </p>
        </aside>
      </div>
      <footer className="page-foot">
        SafeCrop, CSE299 Junior Design, North South University.
      </footer>
    </main>
  );
}

function Header() {
  const now = new Date();
  const hour = now.getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  const date = now.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });

  return (
    <header className="page-head">
      <h1 className="page-title">{greeting}</h1>
      <p className="page-sub">{date}. What would you like to check today?</p>
    </header>
  );
}

function Diseases() {
  return (
    <section className="card" aria-labelledby="dis-title">
      <div className="card-head">
        <h2 id="dis-title" className="card-title">Diseases SafeCrop knows</h2>
        <span className="count">{DISEASES.length}</span>
      </div>
      <ul className="diseases">
        {DISEASES.map((d) => (
          <li key={d.crop + d.name} className="disease">
            <span className="disease-thumb">
              <Leaf {...d.look} className="disease-leaf" label={`${d.crop} ${d.name.toLowerCase()}`} />
            </span>
            <span className="disease-text">
              <span className="disease-crop">{d.crop}</span>
              <span className="disease-name">{d.name}</span>
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
