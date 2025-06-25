"use client";

import { useEffect, useState } from "react";
import { Chat } from "@/components/Chat";
import type { Message } from "@/lib/types";
import { callChatAPI } from "@/lib/api";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: Date.now().toString() + Math.random().toString(),
      content: "How can I help you today?",
      role: "assistant",
      agent: "default",
      timestamp: new Date(),
    },
  ]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  useEffect(() => {
    if (!isChatOpen || conversationId) return;
    (async () => {
      const data = await callChatAPI("", conversationId ?? "");
      setConversationId(data.conversation_id);
      const initialEvents = (data.events || []).map((e: any) => ({
        ...e,
        timestamp: e.timestamp ?? Date.now(),
      }));
      if (Array.isArray(data.messages) && data.messages.length > 0) {
        setMessages((prev) => [
          ...prev,
          ...data.messages.map((m: any) => ({
            id: Date.now().toString() + Math.random().toString(),
            content: m.content,
            role: "assistant",
            agent: m.agent,
            timestamp: new Date(),
          })),
        ]);
      }
    })();
  }, [isChatOpen, conversationId]);

  const handleSendMessage = async (content: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      content,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    const data = await callChatAPI(content, conversationId ?? "");

    if (!conversationId) setConversationId(data.conversation_id);

    if (data.messages) {
      const responses: Message[] = data.messages.map((m: any) => ({
        id: Date.now().toString() + Math.random().toString(),
        content: m.content,
        role: "assistant",
        agent: m.agent,
        timestamp: new Date(),
      }));
      setMessages((prev) => [...prev, ...responses]);
    }

    setIsLoading(false);
  };

  return (
    <main className="relative min-h-screen bg-gradient-to-br from-gray-50 to-gray-200 p-6">
      {/* Chat Icon */}
      {!isChatOpen && (
        <button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-6 right-6 z-50 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-r from-gray-900 to-black text-white shadow-lg hover:from-black hover:to-gray-800 transition-all duration-300 ease-in-out transform hover:scale-105"
          aria-label="Open chat"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            fill="none"
            viewBox="0 0 24 24"
            className="stroke-current"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z"
            />
          </svg>
        </button>
      )}

      {/* Chat Window */}
      {isChatOpen && (
        <div className="fixed bottom-6 right-6 z-40 w-full max-w-[95%] sm:max-w-[480px] h-[85vh] sm:h-[640px] bg-white rounded-2xl shadow-2xl border border-gray-100 flex flex-col overflow-hidden transition-all duration-300 ease-in-out">
          {/* Header */}
          <div className="flex items-center justify-between px-3 py-2 bg-gradient-to-b from-black to-gray-600 text-white rounded-t-2xl">
            <h4 className="text-base font-medium tracking-tight">Customer Assistant</h4>
            <button
              onClick={() => setIsChatOpen(false)}
              className="flex h-7 w-7 items-center justify-center rounded-full text-white hover:bg-white/30 transition-colors duration-200"
              aria-label="Close chat"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                fill="none"
                viewBox="0 0 24 24"
                className="stroke-current"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
          {/* Chat Content */}
          <div className="flex-1 overflow-auto bg-gray-50/50">
            <Chat
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </div>
        </div>
      )}
    </main>
  );
}