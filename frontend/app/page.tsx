"use client";

import ChatInterface from "../components/ChatInterface";

export const dynamic = "force-dynamic";

export default function Home() {
  return (
    <main className="h-full">
      <ChatInterface />
    </main>
  );
}
