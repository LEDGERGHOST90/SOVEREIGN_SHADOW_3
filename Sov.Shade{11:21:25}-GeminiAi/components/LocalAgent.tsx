
import React, { useState, useRef, useEffect } from 'react';
import { FolderOpen, FileCode, Layers, Calendar, Loader2, Database, Shield, Home, Heart, Cpu, Wallet, FileText, RefreshCw } from 'lucide-react';
import { generateSovereignDailyReport } from '../services/geminiService';
import { LocalFile, ModuleAOutput, TimelineEntry, SovereignCategory } from '../types';
import { useStrategies } from '../context/StrategyContext';

export const LocalAgent: React.FC = () => {
  const { strategies } = useStrategies(); // Connect to Knowledge Graph
  const [files, setFiles] = useState<LocalFile[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [moduleAOutput, setModuleAOutput] = useState<ModuleAOutput | null>(null);
  const [dailyReport, setDailyReport] = useState<string | null>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- MODULE A: CLASSIFICATION LOGIC ---
  const classifyFile = (path: string, name: string): SovereignCategory => {
    const lowerPath = path.toLowerCase();
    
    if (lowerPath.includes('finance') || lowerPath.includes('trade') || lowerPath.includes('crypto') || lowerPath.includes('bot') || lowerPath.includes('sniper')) return 'Financial_Analytics';
    if (lowerPath.includes('nest') || lowerPath.includes('server') || lowerPath.includes('cloud') || lowerPath.includes('infra')) return 'NeverNest';
    if (lowerPath.includes('care') || lowerPath.includes('health') || lowerPath.includes('medical') || lowerPath.includes('va')) return 'VA_Caregiving';
    if (lowerPath.includes('home') || lowerPath.includes('house') || lowerPath.includes('iot') || lowerPath.includes('smart')) return 'Home_Management';
    if (lowerPath.includes('ai') || lowerPath.includes('llm') || lowerPath.includes('gpt') || lowerPath.includes('agent') || lowerPath.includes('model')) return 'AI_Innovation';
    
    return 'Uncategorized';
  };

  const getFileType = (name: string): LocalFile['type'] => {
    const ext = name.split('.').pop()?.toLowerCase();
    if (['ts', 'tsx', 'js', 'jsx', 'py', 'rs', 'go', 'html', 'css', 'json'].includes(ext || '')) return 'code';
    if (['md', 'txt', 'csv'].includes(ext || '')) return 'text';
    if (['jpg', 'png', 'svg', 'jpeg'].includes(ext || '')) return 'image';
    if (['mp4', 'mov', 'avi'].includes(ext || '')) return 'video';
    if (['mp3', 'wav'].includes(ext || '')) return 'audio';
    if (ext === 'pdf') return 'pdf';
    return 'unknown';
  };

  // --- MODULE A: SCANNER LOGIC ---
  const handleFolderSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    setIsScanning(true);
    
    const fileList = Array.from(e.target.files);
    const processedFiles: LocalFile[] = [];

    // Process in chunks to avoid UI freeze
    for (const file of fileList) {
      const path = file.webkitRelativePath || file.name;
      
      // Skip node_modules and .git for sanity
      if (path.includes('node_modules') || path.includes('.git')) continue;

      processedFiles.push({
        name: file.name,
        path: path,
        lastModified: file.lastModified,
        created: file.lastModified, // Browser limit: create time often unavailable, use modified
        size: file.size,
        type: getFileType(file.name),
        category: classifyFile(path, file.name),
        // content: await readFile(file) // Optional: Read content if needed for deep analysis
      });
    }

    // Sort by date desc
    processedFiles.sort((a, b) => b.lastModified - a.lastModified);
    setFiles(processedFiles);

    // Generate Module A Output JSON
    const output: ModuleAOutput = {
      scanned_at: new Date().toISOString(),
      root_folder: fileList[0]?.webkitRelativePath.split('/')[0] || 'unknown',
      files: processedFiles,
      timeline_view: generateTimeline(processedFiles)
    };
    
    setModuleAOutput(output);
    setIsScanning(false);
  };

  const generateTimeline = (files: LocalFile[]): TimelineEntry[] => {
    const groups: { [key: string]: LocalFile[] } = {};
    
    files.forEach(f => {
      const date = new Date(f.lastModified).toISOString().split('T')[0];
      if (!groups[date]) groups[date] = [];
      groups[date].push(f);
    });

    return Object.keys(groups)
      .sort((a, b) => new Date(b).getTime() - new Date(a).getTime())
      .map(date => ({
        date,
        // Simplified logic: In a real FS watcher, we'd diff against DB to find 'new' vs 'modified'
        // Here we treat all scan results as 'modified/active' for that day
        new_files: [], 
        modified_files: groups[date]
      }));
  };

  const handleGenerateDailyReport = async () => {
    if (!moduleAOutput) return;
    setIsGeneratingReport(true);
    try {
      const report = await generateSovereignDailyReport(moduleAOutput, strategies.slice(0, 5));
      setDailyReport(report);
    } catch (e) {
      console.error(e);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  // Icons for pillars
  const getPillarIcon = (cat: SovereignCategory) => {
    switch(cat) {
      case 'Financial_Analytics': return <Wallet className="text-green-400" />;
      case 'NeverNest': return <Shield className="text-blue-400" />;
      case 'VA_Caregiving': return <Heart className="text-pink-400" />;
      case 'Home_Management': return <Home className="text-orange-400" />;
      case 'AI_Innovation': return <Cpu className="text-purple-400" />;
      default: return <FolderOpen className="text-slate-400" />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12 animate-fade-in">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Database className="text-indigo-500" />
            SovereignShadow <span className="text-slate-500 text-lg font-normal">| Local Agent (Module A)</span>
          </h1>
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
            // @ts-ignore
            webkitdirectory=""
            directory=""
            multiple
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold flex items-center gap-2 shadow-lg shadow-indigo-500/20 transition-all"
          >
            {isScanning ? <Loader2 className="animate-spin" /> : <FolderOpen size={18} />}
            {isScanning ? 'Scanning...' : 'Scan Ecosystem Folder'}
          </button>
        </div>
      </div>

      {/* SCANNER OUTPUT UI */}
      {moduleAOutput && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* LEFT: PILLARS & TIMELINE */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* 5 PILLARS DASHBOARD */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {(['Financial_Analytics', 'NeverNest', 'VA_Caregiving', 'Home_Management', 'AI_Innovation', 'Uncategorized'] as SovereignCategory[]).map(cat => {
                const count = moduleAOutput.files.filter(f => f.category === cat).length;
                return (
                  <div key={cat} className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex items-center gap-3 hover:border-indigo-500/30 transition-colors">
                    <div className="p-2 bg-slate-800 rounded-lg">
                      {getPillarIcon(cat)}
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 uppercase font-bold tracking-wider">{cat.replace('_', ' ')}</div>
                      <div className="text-2xl font-bold text-white">{count}</div>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* TIMELINE VIEW */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center">
                <h3 className="font-bold text-white flex items-center gap-2">
                  <Calendar size={18} className="text-indigo-400" />
                  Timeline View
                </h3>
                <span className="text-xs text-slate-500 font-mono">JSON_OUTPUT_READY</span>
              </div>
              <div className="max-h-[500px] overflow-y-auto p-4 space-y-6">
                {moduleAOutput.timeline_view.map((entry, idx) => (
                  <div key={idx} className="relative pl-6 border-l border-slate-800">
                    <div className="absolute left-[-5px] top-0 w-2.5 h-2.5 rounded-full bg-indigo-600 border-2 border-slate-900"></div>
                    <h4 className="text-sm font-bold text-slate-300 mb-2">{entry.date}</h4>
                    <div className="space-y-2">
                      {entry.modified_files.slice(0, 6).map((f, fidx) => (
                        <div key={fidx} className="flex items-center justify-between text-xs p-2 bg-slate-800/50 rounded hover:bg-slate-800 transition-colors">
                          <div className="flex items-center gap-2 truncate">
                            <FileCode size={14} className="text-slate-500 flex-shrink-0" />
                            <span className="text-indigo-300 truncate max-w-[300px]">{f.path}</span>
                          </div>
                          <span className="text-slate-600 flex-shrink-0 ml-2">{f.category}</span>
                        </div>
                      ))}
                      {entry.modified_files.length > 6 && (
                        <div className="text-xs text-slate-500 pl-2 italic">
                          + {entry.modified_files.length - 6} more files...
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT: DAILY REPORT & ACTIONS */}
          <div className="space-y-6">
             
             {/* ACTIONS */}
             <div className="bg-slate-800 border border-indigo-500/20 p-4 rounded-xl">
               <h3 className="text-white font-bold mb-3 flex items-center gap-2">
                 <RefreshCw size={18} className="text-indigo-400" />
                 Module Actions
               </h3>
               <button 
                 onClick={handleGenerateDailyReport}
                 disabled={isGeneratingReport}
                 className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
               >
                 {isGeneratingReport ? <Loader2 className="animate-spin" /> : <FileText size={18} />}
                 Generate Daily Record
               </button>
             </div>

             {/* DAILY REPORT DISPLAY */}
             {dailyReport ? (
               <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 animate-fade-in">
                 <div className="flex justify-between items-center mb-4">
                   <h3 className="text-lg font-bold text-white">Daily Record</h3>
                   <span className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded">Generated</span>
                 </div>
                 <div className="prose prose-invert prose-sm max-w-none font-mono text-xs leading-relaxed text-slate-300 whitespace-pre-wrap">
                   {dailyReport}
                 </div>
                 <div className="mt-4 pt-4 border-t border-slate-800 flex justify-end">
                   <button className="text-xs text-indigo-400 hover:text-white flex items-center gap-1">
                     <Database size={12} /> Save to Log
                   </button>
                 </div>
               </div>
             ) : (
               <div className="bg-slate-900/50 border border-slate-800 border-dashed rounded-xl p-8 text-center text-slate-500 text-sm">
                 Scan a folder and click "Generate Daily Record" to see the Module C output.
               </div>
             )}

             {/* JSON RAW DATA PREVIEW */}
             <div className="bg-slate-950 p-4 rounded-xl border border-slate-900">
               <h4 className="text-xs font-bold text-slate-600 mb-2">RAW MODULE A OUTPUT (JSON)</h4>
               <pre className="text-[10px] text-green-400/70 font-mono overflow-hidden h-32 relative">
                 {JSON.stringify(moduleAOutput, null, 2)}
                 <div className="absolute bottom-0 left-0 w-full h-16 bg-gradient-to-t from-slate-950 to-transparent"></div>
               </pre>
             </div>

          </div>
        </div>
      )}
    </div>
  );
};
