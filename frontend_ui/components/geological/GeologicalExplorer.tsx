"use client";
import dynamic from "next/dynamic";
const GeologicalMap = dynamic(
  () => import("./GeologicalMap").then((mod) => mod.GeologicalMap),
  { ssr: false }
);

export const GeologicalExplorer = () => {
  return (
    <div className="h-screen flex">
      {/* Sidebar (static content for now) */}
      <div className="w-80 bg-white border-r shadow-sm p-4">
        <h2 className="font-bold text-lg mb-2">Sidebar (Static)</h2>
        <p>This will be the chat/sidebar area.</p>
      </div>
      {/* Map area (placeholder) */}
      <div className="flex-1 bg-gray-100">
        <GeologicalMap />
      </div>
    </div>
  );
};
