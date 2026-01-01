
import React, { useState, useEffect, useRef } from 'react';
import { KnowledgeNode, KnowledgeEdge, LocalFile, Strategy } from '../types';
import { useStrategies } from '../context/StrategyContext';
import { Network, Share2, ZoomIn, ZoomOut, RefreshCw, Move, Layers, Map } from 'lucide-react';

export const KnowledgeGraph: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { strategies } = useStrategies();
  
  const [mode, setMode] = useState<'live' | 'blueprint'>('blueprint'); // Default to blueprint for architectural review
  const [nodes, setNodes] = useState<KnowledgeNode[]>([]);
  const [edges, setEdges] = useState<KnowledgeEdge[]>([]);
  const [scale, setScale] = useState(0.7); 
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // --- BLUEPRINT DATA (TARGET ARCHITECTURE) ---
  const generateBlueprint = () => {
      const blueprintNodes: KnowledgeNode[] = [
          { id: 'root', type: 'module', label: 'sovereign_shadow (Root)', data: {}, x: 0, y: 0, color: '#fff', radius: 20 },
          
          // CORE LOGIC
          { id: 'core', type: 'module', label: 'core/', data: {}, x: -150, y: -100, color: '#6366f1', radius: 15 },
          { id: 'risk', type: 'concept', label: 'risk_engine', data: {}, x: -250, y: -150, color: '#818cf8', radius: 8 },
          { id: 'agents', type: 'concept', label: 'agents (Unified)', data: {}, x: -250, y: -50, color: '#818cf8', radius: 8 },
          { id: 'regime', type: 'concept', label: 'market_regime', data: {}, x: -150, y: -200, color: '#818cf8', radius: 8 },
          
          // INTERFACE
          { id: 'neural_hub', type: 'module', label: 'neural_hub (FastAPI)', data: {}, x: 150, y: -100, color: '#10b981', radius: 15 },
          { id: 'dashboard', type: 'file', label: 'dashboard (Vite)', data: {}, x: 250, y: -150, color: '#34d399', radius: 8 },
          { id: 'api', type: 'file', label: 'api_routes', data: {}, x: 250, y: -50, color: '#34d399', radius: 8 },

          // SYSTEMS
          { id: 'systems', type: 'module', label: 'systems/', data: {}, x: 0, y: 150, color: '#f59e0b', radius: 15 },
          { id: 'aave', type: 'asset', label: 'aave_protocol', data: {}, x: -80, y: 220, color: '#fbbf24', radius: 10 },
          { id: 'meme', type: 'asset', label: 'meme_scanner', data: {}, x: 80, y: 220, color: '#fbbf24', radius: 10 },

          // DATA
          { id: 'data', type: 'module', label: 'data/', data: {}, x: 200, y: 100, color: '#ec4899', radius: 12 },
          { id: 'brain', type: 'file', label: 'brain_state.json', data: {}, x: 280, y: 100, color: '#f472b6', radius: 8 },
          
          // CONFIG
          { id: 'config', type: 'module', label: 'config/', data: {}, x: -200, y: 100, color: '#94a3b8', radius: 10 },
      ];

      const blueprintEdges: KnowledgeEdge[] = [
          { source: 'root', target: 'core', relationship: 'contains' },
          { source: 'root', target: 'neural_hub', relationship: 'contains' },
          { source: 'root', target: 'systems', relationship: 'contains' },
          { source: 'root', target: 'data', relationship: 'contains' },
          { source: 'root', target: 'config', relationship: 'contains' },

          { source: 'core', target: 'risk', relationship: 'includes' },
          { source: 'core', target: 'agents', relationship: 'includes' },
          { source: 'core', target: 'regime', relationship: 'includes' },

          { source: 'neural_hub', target: 'dashboard', relationship: 'serves' },
          { source: 'neural_hub', target: 'api', relationship: 'routes' },
          { source: 'neural_hub', target: 'core', relationship: 'imports' }, // Key dependency

          { source: 'systems', target: 'aave', relationship: 'protocol' },
          { source: 'systems', target: 'meme', relationship: 'protocol' },
          { source: 'systems', target: 'core', relationship: 'uses' },

          { source: 'data', target: 'brain', relationship: 'persists' },
      ];

      return { nodes: blueprintNodes, edges: blueprintEdges };
  };

  // --- INITIALIZE GRAPH DATA ---
  useEffect(() => {
    if (mode === 'blueprint') {
        const bp = generateBlueprint();
        setNodes(bp.nodes);
        setEdges(bp.edges);
        return;
    }

    // LIVE MODE LOGIC (Existing)
    const strategyNodes: KnowledgeNode[] = strategies.map(s => ({
      id: s.id,
      type: 'strategy',
      label: s.analysis.name,
      data: s,
      createdAt: s.createdAt,
      color: '#6366f1',
      x: Math.random() * 800 - 400,
      y: Math.random() * 600 - 300,
      vx: 0, vy: 0,
      radius: 8 + (s.analysis.overallSentiment / 20)
    }));

    const scanStr = localStorage.getItem('latestScan');
    let fileNodes: KnowledgeNode[] = [];
    if (scanStr) {
      try {
        const scan = JSON.parse(scanStr);
        fileNodes = (scan.files as LocalFile[])
           .slice(0, 60)
           .map((f, i) => ({
             id: f.path,
             type: 'file',
             label: f.name,
             data: f,
             createdAt: f.lastModified,
             color: f.category === 'Financial_Analytics' ? '#22c55e' : '#64748b',
             x: Math.random() * 800 - 400,
             y: Math.random() * 600 - 300,
             vx: 0, vy: 0,
             radius: 4
           }));
      } catch (e) {}
    }

    const newEdges: KnowledgeEdge[] = [];
    const assets = new Set<string>();
    
    strategyNodes.forEach(n => {
        (n.data as Strategy).analysis.assets.forEach(asset => assets.add(asset));
    });

    const assetNodes: KnowledgeNode[] = Array.from(assets).map(asset => ({
        id: `asset-${asset}`,
        type: 'asset',
        label: asset,
        data: {},
        createdAt: Date.now(),
        color: '#eab308',
        x: Math.random() * 800 - 400,
        y: Math.random() * 600 - 300,
        vx: 0, vy: 0,
        radius: 12
    }));

    strategyNodes.forEach(n => {
        (n.data as Strategy).analysis.assets.forEach(asset => {
             newEdges.push({ source: n.id, target: `asset-${asset}`, relationship: 'trades' });
        });
    });
    
    setNodes([...strategyNodes, ...fileNodes, ...assetNodes]);
    setEdges(newEdges);

  }, [strategies, mode]);

  // --- PHYSICS ENGINE ---
  useEffect(() => {
    let animationFrameId: number;

    const updatePhysics = () => {
        setNodes(prevNodes => {
            const newNodes = prevNodes.map(node => ({ ...node }));
            // Center is (0,0) in our canvas transform
            
            // Physics Constants
            const REPULSION = 600;
            const SPRING_LENGTH = mode === 'blueprint' ? 150 : 100;
            const SPRING_STRENGTH = 0.04;
            const CENTER_GRAVITY = 0.01;
            const DAMPING = 0.85;

            // Repulsion
            for (let i = 0; i < newNodes.length; i++) {
                for (let j = i + 1; j < newNodes.length; j++) {
                    const n1 = newNodes[i];
                    const n2 = newNodes[j];
                    let dx = (n1.x || 0) - (n2.x || 0);
                    let dy = (n1.y || 0) - (n2.y || 0);
                    let distSq = dx * dx + dy * dy;
                    if (distSq < 100) distSq = 100; 
                    const force = REPULSION * ((n1.radius || 5) + (n2.radius || 5)) / distSq;
                    const dist = Math.sqrt(distSq);
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    n1.vx = (n1.vx || 0) + fx; n1.vy = (n1.vy || 0) + fy;
                    n2.vx = (n2.vx || 0) - fx; n2.vy = (n2.vy || 0) - fy;
                }
            }

            // Attraction
            edges.forEach(edge => {
                const source = newNodes.find(n => n.id === edge.source);
                const target = newNodes.find(n => n.id === edge.target);
                if (source && target) {
                    let dx = (target.x || 0) - (source.x || 0);
                    let dy = (target.y || 0) - (source.y || 0);
                    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                    const force = (dist - SPRING_LENGTH) * SPRING_STRENGTH;
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    source.vx = (source.vx || 0) + fx; source.vy = (source.vy || 0) + fy;
                    target.vx = (target.vx || 0) - fx; target.vy = (target.vy || 0) - fy;
                }
            });

            // Center Gravity
            newNodes.forEach(node => {
                node.vx = (node.vx || 0) - ((node.x || 0)) * CENTER_GRAVITY;
                node.vy = (node.vy || 0) - ((node.y || 0)) * CENTER_GRAVITY;
                node.vx = Math.max(-10, Math.min(10, (node.vx || 0) * DAMPING));
                node.vy = Math.max(-10, Math.min(10, (node.vy || 0) * DAMPING));
                node.x = (node.x || 0) + node.vx;
                node.y = (node.y || 0) + node.vy;
            });

            return newNodes;
        });
        
        animationFrameId = requestAnimationFrame(updatePhysics);
    };

    updatePhysics();
    return () => cancelAnimationFrame(animationFrameId);
  }, [edges, mode]);

  // --- INTERACTION HANDLERS ---
  const handleMouseDown = (e: React.MouseEvent) => {
      setIsDragging(true);
      setDragStart({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
      if (isDragging) {
          const dx = e.clientX - dragStart.x;
          const dy = e.clientY - dragStart.y;
          setOffset(prev => ({ x: prev.x + dx, y: prev.y + dy }));
          setDragStart({ x: e.clientX, y: e.clientY });
          return;
      }
      const rect = canvasRef.current?.getBoundingClientRect();
      if (!rect) return;
      const mouseX = (e.clientX - rect.left - rect.width/2 - offset.x) / scale;
      const mouseY = (e.clientY - rect.top - rect.height/2 - offset.y) / scale;

      const hit = nodes.find(n => {
          const dx = (n.x || 0) - mouseX;
          const dy = (n.y || 0) - mouseY;
          return Math.sqrt(dx*dx + dy*dy) < (n.radius || 5) + 5;
      });
      setHoveredNode(hit ? hit.id : null);
      if (containerRef.current) containerRef.current.style.cursor = hit ? 'pointer' : isDragging ? 'grabbing' : 'grab';
  };

  const handleMouseUp = () => setIsDragging(false);

  // --- RENDER LOOP ---
  useEffect(() => {
      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      if (!canvas || !ctx) return;

      canvas.width = containerRef.current?.clientWidth || 800;
      canvas.height = containerRef.current?.clientHeight || 600;

      const render = () => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.save();
          ctx.translate(canvas.width/2 + offset.x, canvas.height/2 + offset.y);
          ctx.scale(scale, scale);

          // Edges
          edges.forEach(edge => {
              const source = nodes.find(n => n.id === edge.source);
              const target = nodes.find(n => n.id === edge.target);
              if (source && target) {
                  ctx.beginPath();
                  ctx.moveTo(source.x || 0, source.y || 0);
                  ctx.lineTo(target.x || 0, target.y || 0);
                  ctx.strokeStyle = mode === 'blueprint' ? 'rgba(99, 102, 241, 0.4)' : 'rgba(148, 163, 184, 0.2)';
                  ctx.lineWidth = mode === 'blueprint' ? 2 : 1;
                  ctx.stroke();
              }
          });

          // Nodes
          nodes.forEach(node => {
              const isHovered = hoveredNode === node.id;
              ctx.shadowBlur = isHovered ? 20 : 0;
              ctx.shadowColor = node.color || '#fff';
              ctx.beginPath();
              ctx.arc(node.x || 0, node.y || 0, (node.radius || 5) * (isHovered ? 1.2 : 1), 0, Math.PI * 2);
              ctx.fillStyle = node.color || '#fff';
              ctx.fill();

              // Labels
              if (isHovered || node.type === 'module' || node.type === 'concept' || scale > 1.2) {
                  ctx.fillStyle = '#fff';
                  ctx.font = isHovered ? 'bold 12px Inter' : '10px Inter';
                  ctx.fillText(node.label, (node.x || 0) + (node.radius || 5) + 4, (node.y || 0) + 4);
              }
          });

          ctx.restore();
          requestAnimationFrame(render);
      };
      
      render();
  }, [nodes, edges, scale, offset, hoveredNode, mode]);

  return (
    <div className="h-[calc(100vh-100px)] flex flex-col animate-fade-in">
       <div className="flex justify-between items-center mb-4 px-2">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <Network className="text-indigo-500" />
                Module D <span className="text-slate-500 text-lg font-normal">| Knowledge Graph</span>
            </h1>
            <p className="text-slate-400 text-sm mt-1">Interactive Force-Directed Neural Network</p>
          </div>
          <div className="flex items-center gap-4">
             {/* MODE SWITCHER */}
             <div className="bg-slate-900 p-1 rounded-lg border border-slate-800 flex">
                <button 
                    onClick={() => setMode('live')}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center gap-2 ${mode === 'live' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                >
                    <RefreshCw size={14} /> Live State
                </button>
                <button 
                    onClick={() => setMode('blueprint')}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center gap-2 ${mode === 'blueprint' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                >
                    <Map size={14} /> Target Blueprint
                </button>
             </div>

             <div className="flex gap-2">
                <button onClick={() => setScale(s => s * 1.1)} className="p-2 bg-slate-800 rounded hover:bg-slate-700 text-white"><ZoomIn size={18} /></button>
                <button onClick={() => setScale(s => s * 0.9)} className="p-2 bg-slate-800 rounded hover:bg-slate-700 text-white"><ZoomOut size={18} /></button>
                <button onClick={() => { setOffset({x:0,y:0}); setScale(0.8); }} className="p-2 bg-slate-800 rounded hover:bg-slate-700 text-white"><Move size={18} /></button>
             </div>
          </div>
       </div>

       <div 
            ref={containerRef} 
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl overflow-hidden relative shadow-inner shadow-black/50"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
       >
          <canvas ref={canvasRef} className="block w-full h-full" />
          
          <div className="absolute bottom-4 left-4 pointer-events-none">
             <div className="text-[10px] text-slate-600 font-mono">
                GRAPH MODE: {mode.toUpperCase()}<br/>
                NODES: {nodes.length}<br/>
                EDGES: {edges.length}<br/>
                SCALE: {scale.toFixed(2)}x
             </div>
          </div>

          {mode === 'blueprint' && (
              <div className="absolute top-4 left-4 pointer-events-none bg-purple-900/20 border border-purple-500/30 p-4 rounded-lg backdrop-blur-sm max-w-sm">
                  <h3 className="text-purple-300 font-bold text-sm mb-2">Target Architecture Plan</h3>
                  <ul className="text-xs text-slate-300 space-y-1 list-disc pl-4">
                      <li><span className="text-white font-bold">core/</span> becomes the unified logic center.</li>
                      <li><span className="text-white font-bold">neural_hub</span> is the SINGLE interface (FastAPI + Vite).</li>
                      <li><span className="text-white font-bold">AAVE_system</span> renamed to <span className="font-mono text-yellow-400">aave_protocol</span>.</li>
                      <li><span className="text-white font-bold">web_api</span> (Flask) is deprecated/removed.</li>
                  </ul>
              </div>
          )}
       </div>
    </div>
  );
};
