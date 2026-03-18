"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, Report } from "@/lib/api";
import ReactMarkdown from "react-markdown";

export default function ReportDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<Report | null>(null);

  useEffect(() => {
    if (id) api.reports.get(id).then(setReport);
  }, [id]);

  if (!report) return <div className="text-center py-20 text-gray-400">Loading report...</div>;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-2xl shadow-sm p-8">
        <article className="prose prose-emerald max-w-none">
          <ReactMarkdown>{report.content_md}</ReactMarkdown>
        </article>
      </div>
    </div>
  );
}
