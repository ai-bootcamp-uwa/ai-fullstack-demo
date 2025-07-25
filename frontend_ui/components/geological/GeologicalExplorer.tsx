"use client";
import { Thread } from "@/components/assistant-ui/thread";
import { useGeologicalRuntime } from "@/lib/runtime";
import { AssistantRuntimeProvider } from "@assistant-ui/react";
import dynamic from "next/dynamic";
const GeologicalMap = dynamic(
  () => import("./GeologicalMap").then((mod) => mod.GeologicalMap),
  { ssr: false }
);

export const GeologicalExplorer = () => {
  const runtime = useGeologicalRuntime();
  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="h-screen flex">
        {/* Sidebar with chat */}
        <div className="w-80 bg-white border-r shadow-sm">
          {/* Header */}
          <div className="p-4 border-b bg-gradient-to-r from-blue-600 to-green-600 text-white">
            <h2 className="font-bold text-lg">Geological Assistant</h2>
            <p className="text-sm opacity-90">
              Ask about geological sites and explore WA data
            </p>
          </div>
          {/* Chat Interface */}
          <div className="flex-1 overflow-hidden h-[calc(100vh-120px)]">
            <Thread />
          </div>
        </div>
        {/* Map area */}
        <div className="flex-1 bg-gray-100">
          <GeologicalMap />
        </div>
      </div>
    </AssistantRuntimeProvider>
  );
};
