
import React, { useState, useRef, useMemo, useEffect } from 'react';
import { FolderOpen, FileCode, Layers, Calendar, Loader2, Database, Shield, Home, Heart, Cpu, Wallet, RefreshCw, ChevronRight, ChevronDown, Download, Eye, EyeOff, Code, BrainCircuit, Sparkles, AlertCircle, History, FileText, X, Microscope, Network } from 'lucide-react';
import { generateSovereignDailyReport, analyzeFolderStructure, generateTriEraAnalysis, analyzeProjectFiles, generateModuleBSummary } from '../services/geminiService';
import { LocalFile, ModuleAOutput, TimelineEntry, SovereignCategory, StructureAnalysis, Era, TriEraAnalysis, FileSummary } from '../types';
import { useStrategies } from '../context/StrategyContext';

// --- MODULE A1: EXCLUSION FILTERS ---
const IGNORED_PATHS = [
  'node_modules', 
  '.git', 
  '.DS_Store', 
  'dist', 
  'build', 
  'coverage', 
  '.vscode', 
  '.idea', 
  '__pycache__',
  'Thumbs.db',
  '.next',
  'out',
  'target', // Java/Rust
  'vendor', // PHP/Ruby
  'bin', 
  'obj'
];

const IGNORED_EXTENSIONS = [
  'exe', 'dll', 'so', 'dylib', 'bin', 'iso', 'img', 'dmg', 'zip', 'tar', 'gz', '7z', 'rar', 'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'
];

const shouldIgnore = (path: string) => {
  const parts = path.split('/');
  // Check against ignored directories
  if (parts.some(part => IGNORED_PATHS.includes(part))) return true;
  
  // Check extensions
  const ext = path.split('.').pop()?.toLowerCase();
  if (ext && IGNORED_EXTENSIONS.includes(ext)) return true;
  
  return false;
};

// --- MODULE A2: RECURSIVE TREE TYPES ---
interface FileTreeNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children: FileTreeNode[];
  fileData?: LocalFile;
  category?: SovereignCategory;
}

export const LocalAgent: React.FC = () => {
  const { strategies } = useStrategies(); 
  
  // State
  const [files, setFiles] = useState<LocalFile[]>([]); // Cumulative files
  const [activeEra, setActiveEra] = useState<Era>('Gemini_Current');
  const [isScanning, setIsScanning] = useState(false);
  
  // Outputs
  const [moduleAOutput, setModuleAOutput] = useState<ModuleAOutput | null>(null);
  const [dailyReport, setDailyReport] = useState<string | null>(null);
  const [structureAnalysis, setStructureAnalysis] = useState<StructureAnalysis | null>(null);
  const [triEraAnalysis, setTriEraAnalysis] = useState<TriEraAnalysis | null>(null);
  
  // Module B State
  const [fileSummary, setFileSummary] = useState<FileSummary | null>(null);
  const [isAnalyzingFile, setIsAnalyzingFile] = useState(false);

  // Loading States
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [isAnalyzingStructure, setIsAnalyzingStructure] = useState(false);
  const [isAnalyzingEvolution, setIsAnalyzingEvolution] = useState(false);
  
  // UI State
  const [viewMode, setViewMode] = useState<'timeline' | 'tree'>('tree');
  const [showRawJson, setShowRawJson] = useState(false);
  const [ignoredCount, setIgnoredCount] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<LocalFile | null>(null);
  
  // Scan Options
  const [readContent, setReadContent] = useState(true);
  const [maxFileSizeKB, setMaxFileSizeKB] = useState(50); // Default 50KB limit for content reading

  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- PERSISTENCE EFFECT ---
  useEffect(() => {
    const storedScan = localStorage.getItem('latestScan');
    if (storedScan) {
        try {
            const parsed = JSON.parse(storedScan);
            setModuleAOutput(parsed);
            setFiles(parsed.files || []);
        } catch (e) {
            console.error("Failed to load stored scan", e);
        }
    }
  }, []);

  useEffect(() => {
    if (moduleAOutput) {
        localStorage.setItem('latestScan', JSON.stringify(moduleAOutput));
    }
  }, [moduleAOutput]);


  // --- HELPER: CONTENT READER ---
  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      // Only read text files < maxFileSizeKB to prevent crashes
      if (file.size > maxFileSizeKB * 1024 || (!file.type.startsWith('text') && !file.name.match(/\.(js|ts|tsx|py|json|md|txt|css|html|java|c|cpp|rs|go|yaml|yml|xml|env)$/))) {
        resolve(""); 
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string || "");
      reader.onerror = () => resolve("");
      reader.readAsText(file);
    });
  };

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
    if (['ts', 'tsx', 'js', 'jsx', 'py', 'rs', 'go', 'html', 'css', 'json', 'java', 'c', 'cpp'].includes(ext || '')) return 'code';
    if (['md', 'txt', 'csv', 'log', 'xml', 'yaml', 'yml'].includes(ext || '')) return 'text';
    if (['jpg', 'png', 'svg', 'jpeg', 'gif', 'webp'].includes(ext || '')) return 'image';
    if (['mp4', 'mov', 'avi', 'mkv'].includes(ext || '')) return 'video';
    if (['mp3', 'wav', 'ogg'].includes(ext || '')) return 'audio';
    if (ext === 'pdf') return 'pdf';
    return 'unknown';
  };

  // --- MODULE A: SCANNER LOGIC ---
  const handleFolderSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    setIsScanning(true);
    setError(null);
    setIgnoredCount(0);
    
    const fileList = Array.from(e.target.files) as Array<File & { webkitRelativePath?: string }>;
    const newFiles: LocalFile[] = [];
    let ignored = 0;

    // Limit batch size to prevent browser freeze for reading content
    // But we still list all files
    const MAX_FILES_TO_READ = 200; 
    let readCount = 0;

    for (const file of fileList) {
      const path = file.webkitRelativePath || file.name;
      
      if (shouldIgnore(path)) {
        ignored++;
        continue;
      }

      // Read content if enabled and within limits
      let content = "";
      if (readContent && readCount < MAX_FILES_TO_READ) {
        content = await readFileContent(file);
        if (content) readCount++;
      }

      newFiles.push({
        name: file.name,
        path: path,
        lastModified: file.lastModified,
        created: file.lastModified, 
        size: file.size,
        type: getFileType(file.name),
        category: classifyFile(path, file.name),
        era: activeEra, // Tag with current selected Era
        content: content
      });
    }

    setIgnoredCount(prev => prev + ignored);

    // Merge with existing files (Cumulative Scan)
    setFiles(prev => {
      const combined = [...prev, ...newFiles];
      // Remove duplicates based on path + era
      const unique = combined.filter((v, i, a) => a.findIndex(t => t.path === v.path && t.era === v.era) === i);
      return unique.sort((a, b) => b.lastModified - a.lastModified);
    });

    // Update Module A Output 
    const combinedFiles = [...files, ...newFiles].filter((v, i, a) => a.findIndex(t => t.path === v.path && t.era === v.era) === i);

    const output: ModuleAOutput = {
      scanned_at: new Date().toISOString(),
      root_folder: fileList[0]?.webkitRelativePath?.split('/')[0] || 'Multiple Sources',
      files: combinedFiles, 
      timeline_view: generateTimeline(combinedFiles)
    };
    
    setModuleAOutput(output);
    setIsScanning(false);
    
    // Reset input
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const generateTimeline = (fileList: LocalFile[]): TimelineEntry[] => {
    const groups: { [key: string]: LocalFile[] } = {};
    
    fileList.forEach(f => {
      const date = new Date(f.lastModified).toISOString().split('T')[0];
      if (!groups[date]) groups[date] = [];
      groups[date].push(f);
    });

    return Object.keys(groups)
      .sort((a, b) => new Date(b).getTime() - new Date(a).getTime())
      .map(date => ({
        date,
        new_files: [], 
        modified_files: groups[date]
      }));
  };

  // --- MODULE A2: BUILD TREE LOGIC ---
  const buildFileTree = (fileList: LocalFile[]): FileTreeNode => {
    const root: FileTreeNode = { name: 'root', path: '', type: 'folder', children: [] };

    fileList.forEach(file => {
      const parts = file.path.split('/');
      let currentLevel = root;

      parts.forEach((part, index) => {
        const isFile = index === parts.length - 1;
        const existingNode = currentLevel.children.find(child => child.name === part);

        if (existingNode) {
          currentLevel = existingNode;
        } else {
          const newNode: FileTreeNode = {
            name: part,
            path: parts.slice(0, index + 1).join('/'),
            type: isFile ? 'file' : 'folder',
            children: [],
            fileData: isFile ? file : undefined,
            category: isFile ? file.category : undefined
          };
          currentLevel.children.push(newNode);
          currentLevel = newNode;
        }
      });
    });

    const sortNodes = (node: FileTreeNode) => {
        node.children.sort((a, b) => {
            if (a.type === b.type) return a.name.localeCompare(b.name);
            return a.type === 'folder' ? -1 : 1;
        });
        node.children.forEach(sortNodes);
    };
    sortNodes(root);

    return root;
  };

  const fileTree = useMemo(() => moduleAOutput ? buildFileTree(moduleAOutput.files) : null, [moduleAOutput]);

  // --- ACTIONS ---
  const handleGenerateDailyReport = async () => {
    if (!moduleAOutput) return;
    setIsGeneratingReport(true);
    setError(null);
    try {
      const report = await generateSovereignDailyReport(moduleAOutput, strategies.slice(0, 5));
      setDailyReport(report);
    } catch (e: any) {
      setError(e.message || "Failed to generate report.");
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const handleAnalyzeStructure = async () => {
    if (!moduleAOutput) return;
    setIsAnalyzingStructure(true);
    setError(null);
    try {
      const filePaths = moduleAOutput.files.map(f => f.path);
      const result = await analyzeFolderStructure(filePaths);
      setStructureAnalysis(result);
    } catch (e: any) {
      setError(e.message || "Failed to analyze structure.");
    } finally {
      setIsAnalyzingStructure(false);
    }
  };

  const handleTriEraAnalysis = async () => {
    if (!moduleAOutput || files.length === 0) return;
    setIsAnalyzingEvolution(true);
    setError(null);
    try {
        const result = await generateTriEraAnalysis(files);
        setTriEraAnalysis(result);
    } catch (e: any) {
        setError(e.message || "Failed to analyze evolution.");
    } finally {
        setIsAnalyzingEvolution(false);
    }
  };

  const handleAnalyzeFile = async () => {
    if (!selectedFile) return;
    setIsAnalyzingFile(true);
    setError(null);
    try {
        const summary = await generateModuleBSummary(selectedFile);
        setFileSummary(summary);
    } catch (e: any) {
        setError(e.message || "Failed to analyze file.");
    } finally {
        setIsAnalyzingFile(false);
    }
  };

  const handleExportJson = () => {
    if (!moduleAOutput) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(moduleAOutput, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `sovereign_scan_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

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

  const getEraColor = (era?: Era) => {
    switch(era) {
        case 'Legacy_Loop': return 'bg-amber-900/30 text-amber-400 border-amber-500/30';
        case 'Sovereign_Shadow': return 'bg-blue-900/30 text-blue-400 border-blue-500/30';
        case 'Gemini_Current': return 'bg-indigo-900/30 text-indigo-400 border-indigo-500/30';
        default: return 'bg-slate-800 text-slate-400';
    }
  };

  // Clear summary when selecting a new file
  const handleFileSelect = (file: LocalFile) => {
      setSelectedFile(file);
      setFileSummary(null);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12 animate-fade-in">
      {/* HEADER & ERA SELECTOR */}
      <div className="flex flex-col md:flex-row justify-between items-start gap-4">
        <div>
          <div className="flex items-center gap-3 mb-1">
              <div className="bg-green-900/30 text-green-400 px-2 py-0.5 text-xs rounded border border-green-900/50 flex items-center gap-1">
                  <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                  CORE ALIGNMENT: ACTIVE
              </div>
          </div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Database className="text-indigo-500" />
            SovereignShadow <span className="text-slate-500 text-lg font-normal">| Local Agent</span>
          </h1>
          <p className="text-slate-400 mt-2 max-w-2xl">
            Ingest files, map the ecosystem, and trace evolution across Eras.
          </p>
        </div>
        
        <div className="flex flex-col gap-3 items-end">
           {/* SCAN OPTIONS */}
           <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900 p-2 rounded-lg border border-slate-800">
              <label className="flex items-center gap-1 cursor-pointer">
                 <input type="checkbox" checked={readContent} onChange={e => setReadContent(e.target.checked)} className="rounded bg-slate-800 border-slate-700" />
                 <span>Read Content</span>
              </label>
              <div className="h-4 w-[1px] bg-slate-700 mx-1"></div>
              <span>Max Size:</span>
              <input 
                type="number" 
                value={maxFileSizeKB} 
                onChange={e => setMaxFileSizeKB(Number(e.target.value))} 
                className="w-12 bg-slate-800 border border-slate-700 rounded px-1 text-center" 
                min={1} max={500}
              />
              <span>KB</span>
           </div>

           {/* ERA SELECTOR */}
           <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-800">
              {(['Legacy_Loop', 'Sovereign_Shadow', 'Gemini_Current'] as Era[]).map(era => (
                  <button
                    key={era}
                    onClick={() => setActiveEra(era)}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                        activeEra === era 
                        ? 'bg-indigo-600 text-white shadow' 
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    {era.replace('_', ' ')}
                  </button>
              ))}
           </div>
           
           <div className="flex gap-2">
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
                    className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold flex items-center gap-2 shadow-lg shadow-indigo-500/20 transition-all"
                >
                    {isScanning ? <Loader2 className="animate-spin" /> : <FolderOpen size={18} />}
                    {isScanning ? 'Scanning...' : `Scan to ${activeEra.split('_')[0]}`}
                </button>
           </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-900/50 p-4 rounded-xl flex items-center gap-3 text-red-300 animate-pulse">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* SCANNER OUTPUT UI */}
      {moduleAOutput && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* LEFT: DATA VISUALIZATION */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* ERA STATUS BAR */}
            <div className="grid grid-cols-3 gap-4">
                {(['Legacy_Loop', 'Sovereign_Shadow', 'Gemini_Current'] as Era[]).map(era => {
                    const count = files.filter(f => f.era === era).length;
                    return (
                        <div key={era} className={`p-3 rounded-lg border ${count > 0 ? 'bg-slate-900 border-slate-700' : 'bg-slate-900/50 border-slate-800 opacity-50'}`}>
                            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">{era.replace('_', ' ')}</div>
                            <div className="flex items-end gap-2">
                                <span className={`text-xl font-bold ${count > 0 ? 'text-white' : 'text-slate-600'}`}>{count}</span>
                                <span className="text-xs text-slate-600 mb-1">files</span>
                            </div>
                        </div>
                    )
                })}
            </div>
            
            {/* FILTER STATS */}
            {ignoredCount > 0 && (
                <div className="bg-slate-900/50 border border-slate-800 p-2 rounded-lg text-xs text-slate-500 flex items-center gap-2">
                    <EyeOff size={14} />
                    <span>{ignoredCount} system/binary files excluded from scan to reduce noise.</span>
                </div>
            )}

            {/* MAIN CONTENT VIEW (Timeline or Tree) */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden min-h-[500px] flex flex-col">
               {/* TOOLBAR */}
               <div className="flex items-center justify-between bg-slate-900/50 p-3 border-b border-slate-800">
                    <div className="flex gap-1">
                        <button 
                            onClick={() => setViewMode('tree')}
                            className={`px-3 py-1.5 rounded text-xs font-medium flex items-center gap-2 ${viewMode === 'tree' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white'}`}
                        >
                            <Layers size={14} /> Tree
                        </button>
                        <button 
                            onClick={() => setViewMode('timeline')}
                            className={`px-3 py-1.5 rounded text-xs font-medium flex items-center gap-2 ${viewMode === 'timeline' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white'}`}
                        >
                            <Calendar size={14} /> Timeline
                        </button>
                    </div>
                    <div className="text-xs text-slate-500">
                        {files.length} Total Files
                    </div>
               </div>

               <div className="flex-1 overflow-y-auto p-4">
                  {viewMode === 'timeline' ? (
                    <div className="space-y-6">
                        {moduleAOutput.timeline_view.map((entry, idx) => {
                             const intensity = Math.min(100, entry.modified_files.length * 10);
                             return (
                                <div key={idx} className="relative pl-6 border-l border-slate-800">
                                    <div className="absolute left-[-5px] top-0 w-2.5 h-2.5 rounded-full bg-indigo-600 border-2 border-slate-900"></div>
                                    <div className="flex items-center gap-3 mb-2">
                                        <h4 className="text-sm font-bold text-slate-300">{entry.date}</h4>
                                        <div className="h-1.5 rounded-full bg-indigo-900/50 w-24 overflow-hidden">
                                            <div className="h-full bg-indigo-500" style={{ width: `${intensity}%` }}></div>
                                        </div>
                                        <span className="text-xs text-slate-600">{entry.modified_files.length} items</span>
                                    </div>
                                    <div className="space-y-1">
                                    {entry.modified_files.slice(0, 6).map((f, fidx) => (
                                        <div key={fidx} onClick={() => handleFileSelect(f)} className="cursor-pointer flex items-center justify-between text-xs p-2 bg-slate-800/30 rounded hover:bg-slate-800 transition-colors group">
                                            <div className="flex items-center gap-2 truncate">
                                                <FileCode size={12} className="text-slate-500 flex-shrink-0" />
                                                <span className="text-slate-400 group-hover:text-white truncate max-w-[250px]">{f.name}</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <span className={`px-1.5 rounded text-[9px] border ${getEraColor(f.era)}`}>
                                                    {f.era?.split('_')[0]}
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                    </div>
                                </div>
                             );
                        })}
                    </div>
                  ) : (
                    <div>
                         {fileTree && fileTree.children.map((node, i) => (
                            <RecursiveFileNode key={i} node={node} level={0} onSelect={handleFileSelect} />
                        ))}
                    </div>
                  )}
               </div>
            </div>
          </div>

          {/* RIGHT: ACTIONS & INSPECTOR */}
          <div className="space-y-6">
             
             {/* ACTIONS PANEL */}
             <div className="bg-slate-800 border border-indigo-500/20 p-4 rounded-xl shadow-lg shadow-indigo-900/10">
               <h3 className="text-white font-bold mb-3 flex items-center gap-2">
                 <RefreshCw size={18} className="text-indigo-400" />
                 Analysis Modules
               </h3>
               <div className="space-y-2">
                    <button 
                        onClick={handleAnalyzeStructure}
                        disabled={isAnalyzingStructure}
                        className="w-full py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2 text-xs"
                    >
                        {isAnalyzingStructure ? <Loader2 className="animate-spin" size={14}/> : <BrainCircuit size={14} />}
                        Structure (AI)
                    </button>

                    <button 
                        onClick={handleTriEraAnalysis}
                        disabled={isAnalyzingEvolution || files.length === 0}
                        className={`w-full py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 text-xs ${
                            files.length > 0 
                            ? 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white'
                            : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                        }`}
                    >
                        {isAnalyzingEvolution ? <Loader2 className="animate-spin" size={14}/> : <History size={14} />}
                        Tri-Era Evolution
                    </button>
                    
                    <button 
                        onClick={handleGenerateDailyReport}
                        disabled={isGeneratingReport}
                        className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2 text-xs"
                    >
                        {isGeneratingReport ? <Loader2 className="animate-spin" size={14}/> : <FileText size={14} />}
                        Daily Record
                    </button>

                    <button onClick={handleExportJson} className="w-full py-2 bg-slate-900 hover:bg-slate-950 text-slate-400 hover:text-white rounded border border-slate-800 flex items-center justify-center gap-2 text-xs">
                        <Download size={14} /> JSON
                    </button>
               </div>
             </div>

             {/* FILE INSPECTOR (MODULE B INTEGRATED) */}
             {selectedFile ? (
                 <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 animate-fade-in flex flex-col h-[600px]">
                    <div className="flex justify-between items-start mb-2">
                        <div>
                            <h4 className="text-white font-bold text-sm truncate max-w-[200px]">{selectedFile.name}</h4>
                            <div className="text-[10px] text-slate-500 truncate max-w-[200px]">{selectedFile.path}</div>
                        </div>
                        <button onClick={() => setSelectedFile(null)} className="text-slate-500 hover:text-white"><X size={16} /></button>
                    </div>
                    
                    <div className="flex gap-2 mb-3">
                        <span className={`text-[10px] px-1.5 py-0.5 rounded border ${getEraColor(selectedFile.era)}`}>
                            {selectedFile.era?.replace('_', ' ')}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 bg-slate-800 text-slate-400 rounded border border-slate-700">
                            {(selectedFile.size / 1024).toFixed(1)} KB
                        </span>
                    </div>

                    {/* FILE CONTENT PREVIEW */}
                    <div className="bg-black/30 rounded border border-slate-800 p-2 overflow-auto custom-scrollbar font-mono text-[10px] text-slate-300 mb-3 h-32">
                        {selectedFile.content ? selectedFile.content.substring(0, 2000) + (selectedFile.content.length > 2000 ? '...' : '') : '(No text content or binary file)'}
                    </div>
                    
                    {/* MODULE B: SUMMARIZER OUTPUT */}
                    {fileSummary ? (
                        <div className="flex-1 overflow-y-auto space-y-3 border-t border-slate-800 pt-3">
                            <div className="bg-indigo-900/10 border border-indigo-900/30 p-2 rounded">
                                <h5 className="text-xs font-bold text-indigo-300 mb-1">Core Meaning</h5>
                                <p className="text-[11px] text-slate-300 leading-relaxed">{fileSummary.meaningSummary}</p>
                            </div>
                            
                            <div>
                                <h5 className="text-xs font-bold text-white mb-1 flex items-center gap-1"><Code size={12} /> Key Components</h5>
                                <div className="flex flex-wrap gap-1">
                                    {fileSummary.keyFunctions.map((fn, i) => (
                                        <span key={i} className="px-1.5 py-0.5 bg-slate-800 text-slate-400 text-[10px] rounded">{fn}</span>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <h5 className="text-xs font-bold text-red-300 mb-1 flex items-center gap-1"><Shield size={12} /> Risks</h5>
                                <ul className="list-disc pl-3 space-y-1">
                                    {fileSummary.risks.map((risk, i) => (
                                        <li key={i} className="text-[10px] text-red-200/80">{risk}</li>
                                    ))}
                                </ul>
                            </div>

                            <div>
                                <h5 className="text-xs font-bold text-green-300 mb-1 flex items-center gap-1"><Network size={12} /> Connections</h5>
                                <div className="text-[10px] text-slate-400">
                                    {fileSummary.connections.moduleA && <div>• Scanner: {fileSummary.connections.moduleA}</div>}
                                    {fileSummary.connections.moduleD && <div>• Graph: {fileSummary.connections.moduleD}</div>}
                                </div>
                            </div>
                        </div>
                    ) : (
                         <button 
                            onClick={handleAnalyzeFile}
                            disabled={isAnalyzingFile}
                            className="w-full py-3 bg-indigo-900/30 hover:bg-indigo-900/50 text-indigo-300 border border-indigo-900/50 rounded text-xs flex items-center justify-center gap-2 mt-auto"
                         >
                            {isAnalyzingFile ? <Loader2 className="animate-spin" size={14}/> : <Microscope size={14} />}
                            Analyze This File (Module B)
                         </button>
                    )}
                 </div>
             ) : (
                 <div className="bg-slate-900/50 border border-slate-800 border-dashed rounded-xl p-8 text-center text-slate-600 text-xs">
                    Select a file to inspect contents.
                 </div>
             )}

             {/* TRI-ERA ANALYSIS DISPLAY */}
             {triEraAnalysis && (
                <div className="bg-slate-900 border border-purple-500/30 rounded-xl p-5 animate-fade-in shadow-lg shadow-purple-900/10">
                    <div className="flex items-center gap-2 mb-3">
                        <History size={18} className="text-purple-400" />
                        <h3 className="font-bold text-white text-sm">Evolution Analysis</h3>
                    </div>
                    <p className="text-xs text-slate-300 mb-4 leading-relaxed">
                        {triEraAnalysis.evolutionSummary}
                    </p>
                    <div className="space-y-2">
                        <div className="p-2 bg-slate-800/50 rounded border border-slate-800">
                            <div className="text-[10px] text-slate-500 uppercase font-bold">Legacy (GPT-5)</div>
                            <div className="text-xs text-slate-300">{triEraAnalysis.legacyStrengths}</div>
                        </div>
                         <div className="p-2 bg-slate-800/50 rounded border border-slate-800">
                            <div className="text-[10px] text-slate-500 uppercase font-bold">Sovereign (Claude)</div>
                            <div className="text-xs text-slate-300">{triEraAnalysis.sovereignInnovations}</div>
                        </div>
                         <div className="p-2 bg-indigo-900/20 rounded border border-indigo-900/40">
                            <div className="text-[10px] text-indigo-400 uppercase font-bold">Gemini Potential</div>
                            <div className="text-xs text-indigo-200">{triEraAnalysis.geminiPotential}</div>
                        </div>
                    </div>
                </div>
             )}

          </div>
        </div>
      )}
    </div>
  );
};

// --- RECURSIVE NODE COMPONENT ---
const RecursiveFileNode: React.FC<{ node: FileTreeNode; level: number; onSelect: (file: LocalFile) => void }> = ({ node, level, onSelect }) => {
    const [isOpen, setIsOpen] = useState(level < 2); 
    const hasChildren = node.children && node.children.length > 0;
    const isFolder = node.type === 'folder';

    const getCategoryColor = (cat?: SovereignCategory) => {
        if (!cat) return '';
        if (cat === 'Financial_Analytics') return 'text-green-400';
        if (cat === 'NeverNest') return 'text-blue-400';
        return 'text-slate-500';
    };

    return (
        <div className="select-none">
            <div 
                className={`flex items-center gap-2 py-1 px-2 hover:bg-slate-800 rounded cursor-pointer ${level === 0 ? 'mb-1' : ''}`}
                style={{ paddingLeft: `${level * 16 + 8}px` }}
                onClick={() => isFolder ? setIsOpen(!isOpen) : (node.fileData && onSelect(node.fileData))}
            >
                <span className="text-slate-500">
                    {isFolder ? (
                        hasChildren ? (isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />) : <FolderOpen size={14} />
                    ) : (
                        <FileCode size={14} className={getCategoryColor(node.category)} />
                    )}
                </span>
                <span className={`${isFolder ? 'text-slate-200 font-medium' : 'text-slate-400 text-xs'} truncate`}>
                    {node.name}
                </span>
            </div>
            {isOpen && hasChildren && (
                <div>
                    {node.children.map((child, i) => (
                        <RecursiveFileNode key={i} node={child} level={level + 1} onSelect={onSelect} />
                    ))}
                </div>
            )}
        </div>
    );
};
