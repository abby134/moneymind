"use client";
import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface CsvDropzoneProps {
  file: File | null;
  onFile: (file: File) => void;
}

export function CsvDropzone({ file, onFile }: CsvDropzoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles[0]) onFile(acceptedFiles[0]);
    },
    [onFile]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"] },
    maxFiles: 1,
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition ${
        isDragActive
          ? "border-emerald-500 bg-emerald-50"
          : "border-gray-300 hover:border-emerald-400"
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
          <p className="text-sm text-gray-400 mt-1">
            Supports Chase, BofA, Amex, Wells Fargo, and more
          </p>
        </div>
      )}
    </div>
  );
}
