'use client';

import React, { useState, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  FolderOpen,
  Loader2,
  Database,
  FileText,
  Calendar
} from 'lucide-react';

export function LocalAgent() {
  const [isScanning, setIsScanning] = useState(false);
  const [fileCount, setFileCount] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFolderSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;

    setIsScanning(true);
    const fileList = Array.from(e.target.files);

    // Filter out node_modules and .git
    const filteredFiles = fileList.filter(
      (file) =>
        !file.webkitRelativePath.includes('node_modules') &&
        !file.webkitRelativePath.includes('.git')
    );

    setFileCount(filteredFiles.length);

    // TODO: Send to backend for analysis
    setTimeout(() => {
      setIsScanning(false);
    }, 2000);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <Database className="text-indigo-500" />
            SovereignShadow Local Agent
          </h2>
          <p className="text-slate-400 mt-2 max-w-2xl">
            Ingest local files, classify into pillars, and generate daily reports.
            Your files never leave your machine except for transient AI analysis.
          </p>
        </div>
        <div className="flex gap-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFolderSelect}
            className="hidden"
            {...({ webkitdirectory: '', directory: '' } as any)}
            multiple
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            className="bg-indigo-600 hover:bg-indigo-700"
          >
            {isScanning ? (
              <Loader2 className="animate-spin mr-2" size={18} />
            ) : (
              <FolderOpen size={18} className="mr-2" />
            )}
            {isScanning ? 'Scanning...' : 'Scan Ecosystem Folder'}
          </Button>
        </div>
      </div>

      {fileCount > 0 && (
        <Card className="bg-slate-900/50 border-white/10 p-8">
          <div className="text-center">
            <div className="text-6xl font-bold text-indigo-400 mb-2">
              {fileCount}
            </div>
            <div className="text-slate-400">Files Scanned</div>
            <p className="text-slate-500 text-sm mt-4">
              File analysis and classification coming soon...
            </p>
          </div>
        </Card>
      )}

      {fileCount === 0 && (
        <Card className="bg-slate-900/50 border-white/10 border-dashed p-12 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-800 mb-6 text-slate-400">
            <FolderOpen size={32} />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">
            No folder selected
          </h3>
          <p className="text-slate-400 max-w-md mx-auto">
            Click "Scan Ecosystem Folder" to analyze your local codebase and
            generate insights.
          </p>
        </Card>
      )}
    </div>
  );
}
