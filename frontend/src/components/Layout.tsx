import type { ReactNode } from "react";

interface LayoutProps {
  sidebar: ReactNode;
  main: ReactNode;
  bottom: ReactNode;
}

export function Layout({ sidebar, main, bottom }: LayoutProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">{sidebar}</aside>
      <main className="main-panel">
        <section className="chat-section">{main}</section>
        <section className="workspace-section">{bottom}</section>
      </main>
    </div>
  );
}
