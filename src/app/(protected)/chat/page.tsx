"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";
import type { ChatMessage } from "@/types";

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "أهلاً يا حبيبي! أنا أم محمد، جدتك من حي السيدة زينب 🧓\n\nاسألني عن أي حاجة - وصفات أكل، علاجات شعبية، أمثال، أو أي حاجة عايز تعرفها.\n\nزي ما بيقولوا: اللي يسأل ما يتوهش! 😄",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    // Placeholder response - will be connected to OpenAI API
    setTimeout(() => {
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "يا حبيبي، لسه بنجهز الشات ده. بس إن شاء الله قريب هتقدر تسألني عن أي حاجة وأنا هرد عليك زي الجدة بالظبط! ربنا يكرمك 🧓❤️",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="max-w-2xl mx-auto h-[calc(100vh-10rem)]">
      <div className="text-center mb-4">
        <h1 className="text-2xl font-bold text-primary">🧓 اسأل الجدة</h1>
        <p className="text-sm text-muted-foreground">
          اللي يسأل ما يتوهش!
        </p>
      </div>

      <Card className="flex flex-col h-[calc(100%-4rem)] border-border/50">
        {/* Messages */}
        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          <div className="space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.role === "user" ? "justify-start" : "justify-end"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground"
                  }`}
                >
                  {msg.role === "assistant" && (
                    <span className="text-lg ml-1">🧓</span>
                  )}
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-end">
                <div className="bg-secondary rounded-2xl px-4 py-3">
                  <span className="text-lg">🧓</span>
                  <span className="text-sm text-muted-foreground mr-2">
                    الجدة بتفكر...
                  </span>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Input */}
        <div className="p-4 border-t border-border flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="اسأل الجدة... مثلاً: إيه علاج البرد؟"
            className="flex-1"
            disabled={loading}
          />
          <Button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="bg-primary hover:bg-primary/90"
          >
            ابعت
          </Button>
        </div>
      </Card>
    </div>
  );
}
