// A plain page with a title and one line of text. Used by pages that are not built yet.
export default function SimplePage({ title, sub, children }) {
  return (
    <main className="page">
      <header className="page-head">
        <h1 className="page-title">{title}</h1>
        {sub && <p className="page-sub">{sub}</p>}
      </header>
      {children}
    </main>
  );
}
