"use client";
import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { api, BankAccount } from "@/lib/api";

export default function UploadPage() {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [selectedAccount, setSelectedAccount] = useState("");
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.accounts.list().then(setAccounts);
  }, []);

  const onDrop = useCallback((files: File[]) => {
    if (files[0]) setFile(files[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"] },
    maxFiles: 1,
  });

  async function handleUpload() {
    if (!file || !selectedAccount) return;
    setUploading(true);
    setError("");
    try {
      await api.uploads.upload(selectedAccount, `${month}-01`, file);
      setSuccess(true);
      setFile(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Statement</h1>
        <p className="text-gray-500">Upload a CSV from any bank. We handle the format automatically.</p>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Account</label>
          <select
            value={selectedAccount}
            onChange={(e) => setSelectedAccount(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="">Select account...</option>
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>
                {a.nickname} ({a.bank_name})
              </option>
            ))}
          </select>
          {accounts.length === 0 && (
            <p className="text-sm text-gray-400 mt-1">
              <a href="/dashboard/accounts" className="text-emerald-600">Add an account</a> first.
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Month</label>
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition ${
            isDragActive ? "border-emerald-500 bg-emerald-50" : "border-gray-300 hover:border-emerald-400"
          }`}
        >
          <input {...getInputProps()} />
          {file ? (
            <div>
              <p className="font-medium text-gray-900">{file.name}</p>
              <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          ) : (
            <div>
              <p className="text-gray-600">Drop your CSV here or click to browse</p>
              <p className="text-sm text-gray-400 mt-1">Supports Chase, BofA, Amex, Wells Fargo, and more</p>
            </div>
          )}
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}
        {success && (
          <div className="bg-emerald-50 text-emerald-800 rounded-lg p-4 text-sm">
            Uploaded! Your transactions are being processed. Go to <a href="/dashboard" className="font-medium underline">Overview</a> to run analysis.
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || !selectedAccount || uploading}
          className="w-full bg-emerald-600 text-white py-3 rounded-lg font-semibold hover:bg-emerald-700 transition disabled:opacity-40"
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </div>
    </div>
  );
}
