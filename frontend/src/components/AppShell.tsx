import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/chat", label: "Knowledge Chat", mark: "AI" },
  { to: "/documents", label: "Documents", mark: "DOC" },
  { to: "/sync", label: "Notion Sync", mark: "SYNC" },
  { to: "/settings", label: "Settings", mark: "SET" },
];

export function AppShell() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">N</span>
          <div>
            <strong>Knowledge Finder</strong>
            <span>Notion RAG workspace</span>
          </div>
        </div>
        <nav className="main-nav" aria-label="Main navigation">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to}>
              <span className="nav-mark">{link.mark}</span>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot">
          <span className="status-dot" />
          Local workspace
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
