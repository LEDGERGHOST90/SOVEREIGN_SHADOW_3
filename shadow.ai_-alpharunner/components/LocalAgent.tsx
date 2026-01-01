
import React, { useState, useRef, useMemo, useEffect } from 'react';
import { FolderOpen, FileCode, Layers, Calendar, Loader2, Database, Shield, Home, Heart, Cpu, Wallet, RefreshCw, ChevronRight, ChevronDown, Download, Eye, EyeOff, Code, BrainCircuit, Sparkles, AlertCircle, History, FileText, X, Microscope, Network, ClipboardCheck, AlertTriangle, Terminal, HardDrive } from 'lucide-react';
// Fix: Removed analyzeProjectFiles as it is not exported from geminiService
import { generateSovereignDailyReport, analyzeFolderStructure, generateTriEraAnalysis, generateModuleBSummary } from '../services/geminiService';
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
  const [viewMode, setViewMode] = useState<'timeline' | 'tree' | 'refactor'>('tree');
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
        case 'Legacy_Loop': return 'bg-amber-900/20 text-amber-400 border-amber-500/30';
        case 'Sovereign_Shadow': return 'bg-blue-900/20 text-blue-400 border-blue-500/30';
        case 'Gemini_Current': return 'bg-indigo-900/20 text-indigo-400 border-indigo-500/30';
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
      <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-slate-800/60 pb-6 mb-8">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic flex items-center gap-3">
            <HardDrive className="text-cyan-400" size={32} />
            Local <span className="text-slate-500 not-italic text-2xl">| Agent Scanner</span>
          </h1>
          <p className="text-slate-400 font-mono-tech text-xs mt-2 max-w-2xl border-l-2 border-cyan-500/30 pl-3">
             Recursive Indexing. Ecosystem Mapping. Era Classification.
          </p>
        </div>
        
        <div className="flex flex-col gap-3 items-end">
           {/* SCAN OPTIONS */}
           <div className="flex items-center gap-2 text-[10px] font-mono font-bold uppercase text-slate-400 bg-black p-2 rounded-lg border border-slate-800">
              <label className="flex items-center gap-1.5 cursor-pointer hover:text-white transition-colors">
                 <input type="checkbox" checked={readContent} onChange={e => setReadContent(e.target.checked)} className="rounded bg-slate-900 border-slate-700 text-cyan-500" />
                 <span>Read Content</span>
              </label>
              <div className="h-3 w-[1px] bg-slate-700 mx-1"></div>
              <span>Max:</span>
              <input 
                type="number" 
                value={maxFileSizeKB} 
                onChange={e => setMaxFileSizeKB(Number(e.target.value))} 
                className="w-10 bg-slate-900 border border-slate-700 rounded px-1 text-center text-white" 
                min={1} max={500}
              />
              <span>KB</span>
           </div>

           {/* ERA SELECTOR */}
           <div className="flex bg-black p-1 rounded-lg border border-slate-800">
              {(['Legacy_Loop', 'Sovereign_Shadow', 'Gemini_Current'] as Era[]).map(era => (
                  <button
                    key={era}
                    onClick={() => setActiveEra(era)}
                    className={`px-3 py-1.5 rounded text-[9px] font-black uppercase tracking-widest transition-all ${
                        activeEra === era 
                        ? 'bg-indigo-600 text-white shadow-lg' 
                        : 'text-slate-500 hover:text-white hover:bg-slate-900'
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
                    className="px-6 py-3 bg-cyan-600 hover:bg-cyan-500 text-black clip-corner font-black text-xs uppercase tracking-widest flex items-center gap-2 shadow-[0_0_20px_rgba(8,145,178,0.3)] transition-all"
                >
                    {isScanning ? <Loader2 className="animate-spin" size={14} /> : <FolderOpen size={14} />}
                    {isScanning ? 'INDEXING...' : `SCAN TO ${activeEra.split('_')[0].toUpperCase()}`}
                </button>
           </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-950/20 border border-red-500/30 p-4 rounded-xl flex items-center gap-3 text-red-400 font-mono text-xs animate-pulse">
          <AlertCircle size={16} />
          <span>ERROR: {error}</span>
        </div>
      )}

      {/* SCANNER OUTPUT UI */}
      {moduleAOutput ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* LEFT: DATA VISUALIZATION */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* ERA STATUS BAR */}
            <div className="grid grid-cols-3 gap-4">
                {(['Legacy_Loop', 'Sovereign_Shadow', 'Gemini_Current'] as Era[]).map(era => {
                    const count = files.filter(f => f.era === era).length;
                    return (
                        <div key={era} className={`p-3 rounded-xl border ${count > 0 ? 'bg-black border-slate-800' : 'bg-black/50 border-slate-900 opacity-50'}`}>
                            <div className="text-[9px] text-slate-500 uppercase font-black mb-1">{era.replace('_', ' ')}</div>
                            <div className="flex items-end gap-2">
                                <span className={`text-2xl font-black ${count > 0 ? 'text-white' : 'text-slate-700'}`}>{count}</span>
                                <span className="text-[10px] text-slate-600 mb-1 font-mono uppercase">items</span>
                            </div>
                        </div>
                    )
                })}
            </div>
            
            {/* FILTER STATS */}
            {ignoredCount > 0 && (
                <div className="bg-slate-900/50 border border-slate-800 p-2 rounded-lg text-[10px] font-mono text-slate-500 flex items-center gap-2">
                    <EyeOff size={12} />
                    <span>{ignoredCount} SYSTEM FILES EXCLUDED (NOISE REDUCTION)</span>
                </div>
            )}

            {/* MAIN CONTENT VIEW */}
            <div className="bg-black border border-slate-800 rounded-xl overflow-hidden min-h-[500px] flex flex-col shadow-2xl relative">
               <div className="absolute inset-0 bg-scanline opacity-5 pointer-events-none"></div>
               {/* TOOLBAR */}
               <div className="flex items-center justify-between bg-slate-900/80 p-3 border-b border-slate-800 backdrop-blur-sm relative z-10">
                    <div className="flex gap-1">
                        <button 
                            onClick={() => setViewMode('tree')}
                            className={`px-3 py-1.5 rounded text-[10px] font-black uppercase tracking-wider flex items-center gap-2 ${viewMode === 'tree' ? 'bg-black text-cyan-400 border border-cyan-900' : 'text-slate-500 hover:text-white'}`}
                        >
                            <Layers size={12} /> Tree
                        </button>
                        <button 
                            onClick={() => setViewMode('timeline')}
                            className={`px-3 py-1.5 rounded text-[10px] font-black uppercase tracking-wider flex items-center gap-2 ${viewMode === 'timeline' ? 'bg-black text-purple-400 border border-purple-900' : 'text-slate-500 hover:text-white'}`}
                        >
                            <Calendar size={12} /> Timeline
                        </button>
                        <button 
                            onClick={() => setViewMode('refactor')}
                            className={`px-3 py-1.5 rounded text-[10px] font-black uppercase tracking-wider flex items-center gap-2 ${viewMode === 'refactor' ? 'bg-black text-red-400 border border-red-900' : 'text-slate-500 hover:text-white'}`}
                        >
                            <ClipboardCheck size={12} /> Optimization
                        </button>
                    </div>
                    <div className="text-[10px] font-mono text-slate-500">
                        TOTAL: {files.length} NODES
                    </div>
               </div>

               <div className="flex-1 overflow-y-auto p-4 custom-scrollbar relative z-10">
                  {viewMode === 'timeline' && (
                    <div className="space-y-6">
                        {moduleAOutput.timeline_view.map((entry, idx) => {
                             const intensity = Math.min(100, entry.modified_files.length * 10);
                             return (
                                <div key={idx} className="relative pl-6 border-l border-slate-800">
                                    <div className="absolute left-[-5px] top-0 w-2.5 h-2.5 rounded-full bg-indigo-600 border-2 border-slate-900"></div>
                                    <div className="flex items-center gap-3 mb-2">
                                        <h4 className="text-xs font-bold text-slate-300 font-mono">{entry.date}</h4>
                                        <div className="h-1 rounded-full bg-indigo-900/30 w-24 overflow-hidden">
                                            <div className="h-full bg-indigo-500" style={{ width: `${intensity}%` }}></div>
                                        </div>
                                        <span className="text-[9px] text-slate-600 font-bold uppercase">{entry.modified_files.length} commits</span>
                                    </div>
                                    <div className="space-y-1">
                                    {entry.modified_files.slice(0, 6).map((f, fidx) => (
                                        <div key={fidx} onClick={() => handleFileSelect(f)} className="cursor-pointer flex items-center justify-between text-xs p-2 bg-slate-900/50 rounded border border-transparent hover:border-indigo-500/30 transition-colors group">
                                            <div className="flex items-center gap-2 truncate">
                                                <FileCode size={12} className="text-slate-600 flex-shrink-0" />
                                                <span className="text-slate-400 group-hover:text-white truncate max-w-[250px] font-mono text-[10px]">{f.name}</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <span className={`px-1.5 rounded text-[9px] font-bold border ${getEraColor(f.era)}`}>
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
                  )}

                  {viewMode === 'tree' && (
                    <div>
                         {fileTree && fileTree.children.map((node, i) => (
                            <RecursiveFileNode key={i} node={node} level={0} onSelect={handleFileSelect} />
                        ))}
                    </div>
                  )}

                  {viewMode === 'refactor' && (
                      <div className="space-y-4">
                          <div className="bg-red-950/20 border border-red-500/30 p-4 rounded-xl">
                              <h3 className="text-red-400 font-black text-xs uppercase tracking-widest flex items-center gap-2 mb-3"><AlertTriangle size={14} /> Critical Clean-Up</h3>
                              <ul className="text-xs text-slate-300 space-y-2 list-disc pl-4 leading-relaxed font-mono">
                                  <li><span className="text-white font-bold">Consolidate Web Frameworks:</span> You have Flask (web_api), FastAPI (neural_hub), and Next.js (app). <br/><span className="text-green-400">Recommendation:</span> Keep neural_hub (FastAPI) as the single backend. Kill web_api.</li>
                                  <li><span className="text-white font-bold">Standardize Naming:</span> Rename <code>AAVE_system</code> to <code>aave_protocol</code>. Rename <code>SS_III</code> to <code>sovereign_shadow</code>.</li>
                                  <li><span className="text-white font-bold">Flatten Scripts:</span> 69 files in <code>scripts/</code> is unmaintainable. Group them into <code>scripts/trading</code>, <code>scripts/maintenance</code>, etc.</li>
                              </ul>
                          </div>
                          
                          <div className="bg-indigo-950/20 border border-indigo-500/30 p-4 rounded-xl">
                              <h3 className="text-indigo-400 font-black text-xs uppercase tracking-widest flex items-center gap-2 mb-3"><Layers size={14} /> Structural Merges</h3>
                              <ul className="text-xs text-slate-300 space-y-2 list-disc pl-4 leading-relaxed font-mono">
                                  <li>Merge <code>agents/</code> into <code>core/agents/</code>. Don't split logic.</li>
                                  <li>Merge <code>shadow_sdk/</code> into <code>core/sdk/</code>.</li>
                                  <li>Move useful contents of <code>modules/</code> into <code>core/</code> and delete the folder.</li>
                              </ul>
                          </div>

                          <div className="p-4 rounded-lg border border-slate-800 bg-slate-900/50 text-center">
                              <p className="text-slate-500 text-[10px] font-mono">
                                  View the <strong>Knowledge Graph (Blueprint Mode)</strong> to see the visualized target architecture.
                              </p>
                          </div>
                      </div>
                  )}
               </div>
            </div>
          </div>

          {/* RIGHT: ACTIONS & INSPECTOR */}
          <div className="space-y-6">
             {/* ACTIONS PANEL */}
             <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-xl shadow-lg">
               <h3 className="text-white font-black text-xs uppercase tracking-widest mb-4 flex items-center gap-2">
                 <RefreshCw size={14} className="text-cyan-400" />
                 Processing Modules
               </h3>
               <div className="space-y-3">
                    <button 
                        onClick={handleAnalyzeStructure}
                        disabled={isAnalyzingStructure}
                        className="w-full py-3 bg-black hover:bg-slate-900 text-slate-300 border border-slate-800 rounded-lg transition-colors flex items-center justify-center gap-2 text-[10px] font-bold uppercase tracking-wider"
                    >
                        {isAnalyzingStructure ? <Loader2 className="animate-spin" size={12}/> : <BrainCircuit size={12} />}
                        Analyze Structure
                    </button>

                    <button 
                        onClick={handleTriEraAnalysis}
                        disabled={isAnalyzingEvolution || files.length === 0}
                        className={`w-full py-3 rounded-lg transition-colors flex items-center justify-center gap-2 text-[10px] font-bold uppercase tracking-wider ${
                            files.length > 0 
                            ? 'bg-gradient-to-r from-purple-900/50 to-indigo-900/50 border border-purple-500/30 text-white hover:border-purple-400'
                            : 'bg-black text-slate-600 border border-slate-800 cursor-not-allowed'
                        }`}
                    >
                        {isAnalyzingEvolution ? <Loader2 className="animate-spin" size={12}/> : <History size={12} />}
                        Evolution Scan
                    </button>
                    
                    <button 
                        onClick={handleGenerateDailyReport}
                        disabled={isGeneratingReport}
                        className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors flex items-center justify-center gap-2 text-[10px] font-black uppercase tracking-widest shadow-lg shadow-indigo-600/20"
                    >
                        {isGeneratingReport ? <Loader2 className="animate-spin" size={12}/> : <FileText size={12} />}
                        Log Daily Record
                    </button>

                    <button onClick={handleExportJson} className="w-full py-2 bg-transparent hover:bg-slate-800 text-slate-500 hover:text-white rounded flex items-center justify-center gap-2 text-[10px] font-mono">
                        <Download size={12} /> EXPORT_JSON
                    </button>
               </div>
             </div>

             {/* FILE INSPECTOR (MODULE B INTEGRATED) */}
             {selectedFile ? (
                 <div className="bg-black border border-slate-800 rounded-xl p-4 animate-fade-in flex flex-col h-[600px] shadow-2xl relative overflow-hidden">
                    <div className="absolute inset-0 bg-scanline opacity-5 pointer-events-none"></div>
                    <div className="flex justify-between items-start mb-4 relative z-10">
                        <div>
                            <h4 className="text-white font-mono font-bold text-xs truncate max-w-[200px] text-cyan-400">{selectedFile.name}</h4>
                            <div className="text-[10px] text-slate-600 truncate max-w-[200px] font-mono mt-0.5">{selectedFile.path}</div>
                        </div>
                        <button onClick={() => setSelectedFile(null)} className="text-slate-600 hover:text-red-400 transition-colors"><X size={16} /></button>
                    </div>
                    
                    <div className="flex gap-2 mb-4 relative z-10">
                        <span className={`text-[9px] px-1.5 py-0.5 rounded border font-bold uppercase ${getEraColor(selectedFile.era)}`}>
                            {selectedFile.era?.replace('_', ' ')}
                        </span>
                        <span className="text-[9px] px-1.5 py-0.5 bg-slate-900 text-slate-400 rounded border border-slate-800 font-mono">
                            {(selectedFile.size / 1024).toFixed(1)} KB
                        </span>
                    </div>

                    {/* FILE CONTENT PREVIEW */}
                    <div className="bg-slate-900/50 rounded border border-slate-800 p-3 overflow-auto custom-scrollbar font-mono text-[10px] text-slate-400 mb-4 h-32 relative z-10 leading-relaxed">
                        {selectedFile.content ? selectedFile.content.substring(0, 2000) + (selectedFile.content.length > 2000 ? '...' : '') : '// Binary or Empty File'}
                    </div>
                    
                    {/* MODULE B: SUMMARIZER OUTPUT */}
                    {fileSummary ? (
                        <div className="flex-1 overflow-y-auto space-y-4 border-t border-slate-800 pt-4 relative z-10 custom-scrollbar">
                            <div className="bg-indigo-950/20 border border-indigo-500/20 p-3 rounded-lg">
                                <h5 className="text-[10px] font-black text-indigo-400 mb-2 uppercase">Core Logic</h5>
                                <p className="text-[11px] text-slate-300 leading-relaxed">{fileSummary.meaningSummary}</p>
                            </div>
                            
                            <div>
                                <h5 className="text-[10px] font-black text-white mb-2 flex items-center gap-1 uppercase"><Code size={12} /> Components</h5>
                                <div className="flex flex-wrap gap-1.5">
                                    {fileSummary.keyFunctions.map((fn, i) => (
                                        <span key={i} className="px-1.5 py-0.5 bg-slate-900 text-slate-400 text-[10px] font-mono border border-slate-800 rounded">{fn}</span>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <h5 className="text-[10px] font-black text-red-400 mb-2 flex items-center gap-1 uppercase"><Shield size={12} /> Risk Factors</h5>
                                <ul className="space-y-1">
                                    {fileSummary.risks.map((risk, i) => (
                                        <li key={i} className="text-[10px] text-red-300/80 pl-2 border-l border-red-900/50">{risk}</li>
                                    ))}
                                </ul>
                            </div>

                            <div>
                                <h5 className="text-[10px] font-black text-green-400 mb-2 flex items-center gap-1 uppercase"><Network size={12} /> Graph Links</h5>
                                <div className="text-[10px] text-slate-500 font-mono">
                                    {fileSummary.connections.moduleA && <div>- SCANNER: {fileSummary.connections.moduleA}</div>}
                                    {fileSummary.connections.moduleD && <div>- GRAPH: {fileSummary.connections.moduleD}</div>}
                                </div>
                            </div>
                        </div>
                    ) : (
                         <button 
                            onClick={handleAnalyzeFile}
                            disabled={isAnalyzingFile}
                            className="w-full py-3 bg-slate-900 hover:bg-slate-800 text-cyan-400 border border-slate-800 hover:border-cyan-500/50 rounded-lg text-[10px] font-bold uppercase tracking-widest flex items-center justify-center gap-2 mt-auto relative z-10 transition-all"
                         >
                            {isAnalyzingFile ? <Loader2 className="animate-spin" size={14}/> : <Microscope size={14} />}
                            Deep Scan (Module B)
                         </button>
                    )}
                 </div>
             ) : (
                 <div className="bg-black/40 border border-slate-800 border-dashed rounded-xl p-8 text-center text-slate-600 text-xs font-mono h-[200px] flex items-center justify-center">
                    // AWAITING FILE SELECTION...
                 </div>
             )}

             {/* TRI-ERA ANALYSIS DISPLAY */}
             {triEraAnalysis && (
                <div className="bg-slate-950/80 border border-purple-500/30 rounded-xl p-5 animate-fade-in shadow-lg shadow-purple-900/10">
                    <div className="flex items-center gap-2 mb-3">
                        <History size={16} className="text-purple-400" />
                        <h3 className="font-black text-white text-xs uppercase tracking-widest">Evolution Analysis</h3>
                    </div>
                    <p className="text-[11px] text-slate-400 mb-4 leading-relaxed border-l-2 border-purple-500/20 pl-2">
                        {triEraAnalysis.evolutionSummary}
                    </p>
                    <div className="space-y-2">
                        <div className="p-2 bg-black rounded border border-slate-800">
                            <div className="text-[9px] text-slate-600 uppercase font-black mb-1">Legacy (GPT-5)</div>
                            <div className="text-[10px] text-slate-400 leading-tight">{triEraAnalysis.legacyStrengths}</div>
                        </div>
                         <div className="p-2 bg-black rounded border border-slate-800">
                            <div className="text-[9px] text-slate-600 uppercase font-black mb-1">Sovereign (Claude)</div>
                            <div className="text-[10px] text-slate-400 leading-tight">{triEraAnalysis.sovereignInnovations}</div>
                        </div>
                         <div className="p-2 bg-indigo-950/30 rounded border border-indigo-500/30">
                            <div className="text-[9px] text-indigo-400 uppercase font-black mb-1">Gemini Potential</div>
                            <div className="text-[10px] text-indigo-200 leading-tight">{triEraAnalysis.geminiPotential}</div>
                        </div>
                    </div>
                </div>
             )}
          </div>
        </div>
      ) : (
          <div className="flex flex-col items-center justify-center py-24 bg-black/40 border border-slate-800 border-dashed rounded-xl text-slate-600">
              <FolderOpen size={64} className="mb-6 opacity-30 text-indigo-500" />
              <h3 className="text-xl font-black text-white mb-2 uppercase tracking-tight">System Offline</h3>
              <p className="text-xs max-w-md text-center mb-8 font-mono">
                  Select a local directory to initialize the File System Agent.
              </p>
              <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-black text-xs uppercase tracking-widest flex items-center gap-2 shadow-[0_0_30px_rgba(79,70,229,0.3)] transition-all"
                >
                    <FolderOpen size={16} />
                    Mount Local Drive
                </button>
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
        return 'text-slate-600';
    };

    return (
        <div className="select-none font-mono text-[11px]">
            <div 
                className={`flex items-center gap-2 py-1 px-2 hover:bg-slate-900 rounded cursor-pointer border border-transparent hover:border-slate-800 transition-colors ${level === 0 ? 'mb-1' : ''}`}
                style={{ paddingLeft: `${level * 16 + 8}px` }}
                onClick={() => isFolder ? setIsOpen(!isOpen) : (node.fileData && onSelect(node.fileData))}
            >
                <span className="text-slate-600">
                    {isFolder ? (
                        hasChildren ? (isOpen ? <ChevronDown size={12} /> : <ChevronRight size={12} />) : <FolderOpen size={12} />
                    ) : (
                        <FileCode size={12} className={getCategoryColor(node.category)} />
                    )}
                </span>
                <span className={`${isFolder ? 'text-slate-300 font-bold' : 'text-slate-500 hover:text-cyan-400'} truncate`}>
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
