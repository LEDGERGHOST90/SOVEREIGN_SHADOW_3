
import React, { useState, useEffect, useRef } from 'react';
import { KnowledgeNode, KnowledgeEdge, LocalFile, Strategy } from '../types';
import { useStrategies } from '../context/StrategyContext';
import { Network, Share2, ZoomIn, ZoomOut, RefreshCw, Move } from 'lucide-react';

export const KnowledgeGraph: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { strategies } = useStrategies();
  
  const [nodes, setNodes] = useState<KnowledgeNode[]>([]);
  const [edges, setEdges] = useState<KnowledgeEdge[]>([]);
  const [scale, setScale] = useState(0.8); // Start slightly zoomed out
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // --- INITIALIZE GRAPH DATA ---
  useEffect(() => {
    // 1. Convert Strategies to Nodes
    const strategyNodes: KnowledgeNode[] = strategies.map(s => ({
      id: s.id,
      type: 'strategy',
      label: s.analysis.name,
      data: s,
      createdAt: s.createdAt,
      color: '#6366f1', // Indigo 500
      x: Math.random() * 800,
      y: Math.random() * 600,
      vx: 0, vy: 0,
      radius: 8 + (s.analysis.overallSentiment / 20) // Size based on sentiment
    }));

    // 2. Convert Local Files (from persistence) to Nodes
    const scanStr = localStorage.getItem('latestScan');
    let fileNodes: KnowledgeNode[] = [];
    if (scanStr) {
      try {
        const scan = JSON.parse(scanStr);
        // Only take top relevant files to avoid clutter
        fileNodes = (scan.files as LocalFile[])
           .slice(0, 60)
           .map((f, i) => ({
             id: f.path,
             type: 'file',
             label: f.name,
             data: f,
             createdAt: f.lastModified,
             color: f.category === 'Financial_Analytics' ? '#22c55e' : '#64748b', // Green or Slate
             x: Math.random() * 800,
             y: Math.random() * 600,
             vx: 0, vy: 0,
             radius: 4
           }));
      } catch (e) {}
    }

    // 3. Create Edges & Asset Nodes
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
        color: '#eab308', // Yellow 500
        x: Math.random() * 800,
        y: Math.random() * 600,
        vx: 0, vy: 0,
        radius: 12 // Assets are hubs
    }));

    // Create edges Strategy -> Asset
    strategyNodes.forEach(n => {
        (n.data as Strategy).analysis.assets.forEach(asset => {
             newEdges.push({ source: n.id, target: `asset-${asset}`, relationship: 'trades' });
        });
    });

    // Create edges File -> Category Hubs (Implicit)
    // Ideally we link files to modules, but for now we just have files and strategies.
    
    const allNodes = [...strategyNodes, ...fileNodes, ...assetNodes];
    setNodes(allNodes);
    setEdges(newEdges);

  }, [strategies]);

  // --- ADVANCED PHYSICS ENGINE ---
  useEffect(() => {
    let animationFrameId: number;

    const updatePhysics = () => {
        setNodes(prevNodes => {
            const newNodes = prevNodes.map(node => ({ ...node }));
            const width = containerRef.current?.clientWidth || 800;
            const height = containerRef.current?.clientHeight || 600;
            const center = { x: width / 2, y: height / 2 };

            // Physics Constants
            const REPULSION = 400;
            const SPRING_LENGTH = 120;
            const SPRING_STRENGTH = 0.02;
            const CENTER_GRAVITY = 0.01;
            const CLUSTER_STRENGTH = 0.03;
            const DAMPING = 0.85; // More damping = stable
            const MAX_VELOCITY = 8;

            // 1. Type-Based Clustering Centers
            // We define virtual centers for different node types to encourage grouping
            const clusters = {
                strategy: { x: center.x - 150, y: center.y - 100 },
                asset: { x: center.x, y: center.y }, // Assets in middle
                file: { x: center.x + 150, y: center.y + 100 },
                concept: { x: center.x - 150, y: center.y + 100 },
                module: { x: center.x + 150, y: center.y - 100 }
            };

            // 2. Repulsion (Coulomb's Law)
            for (let i = 0; i < newNodes.length; i++) {
                for (let j = i + 1; j < newNodes.length; j++) {
                    const n1 = newNodes[i];
                    const n2 = newNodes[j];
                    
                    let dx = (n1.x || 0) - (n2.x || 0);
                    let dy = (n1.y || 0) - (n2.y || 0);
                    let distSq = dx * dx + dy * dy;
                    
                    // Avoid division by zero / singular forces
                    if (distSq < 100) distSq = 100; 

                    const force = REPULSION * ((n1.radius || 5) + (n2.radius || 5)) / distSq;
                    
                    const dist = Math.sqrt(distSq);
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;

                    n1.vx = (n1.vx || 0) + fx;
                    n1.vy = (n1.vy || 0) + fy;
                    n2.vx = (n2.vx || 0) - fx;
                    n2.vy = (n2.vy || 0) - fy;
                }
            }

            // 3. Attraction (Hooke's Law for Edges)
            edges.forEach(edge => {
                const source = newNodes.find(n => n.id === edge.source);
                const target = newNodes.find(n => n.id === edge.target);
                if (source && target) {
                    let dx = (target.x || 0) - (source.x || 0);
                    let dy = (target.y || 0) - (source.y || 0);
                    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                    
                    // Spring force
                    const force = (dist - SPRING_LENGTH) * SPRING_STRENGTH;
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;

                    source.vx = (source.vx || 0) + fx;
                    source.vy = (source.vy || 0) + fy;
                    target.vx = (target.vx || 0) - fx;
                    target.vy = (target.vy || 0) - fy;
                }
            });

            // 4. Global Forces (Center Gravity + Type Clustering)
            newNodes.forEach(node => {
                // Pull to absolute center
                node.vx = (node.vx || 0) - ((node.x || 0) - center.x) * CENTER_GRAVITY;
                node.vy = (node.vy || 0) - ((node.y || 0) - center.y) * CENTER_GRAVITY;

                // Pull to Type Cluster Center
                const cluster = clusters[node.type as keyof typeof clusters];
                if (cluster) {
                     node.vx = (node.vx || 0) - ((node.x || 0) - cluster.x) * CLUSTER_STRENGTH;
                     node.vy = (node.vy || 0) - ((node.y || 0) - cluster.y) * CLUSTER_STRENGTH;
                }

                // Damping & Velocity Cap
                node.vx = Math.max(-MAX_VELOCITY, Math.min(MAX_VELOCITY, (node.vx || 0) * DAMPING));
                node.vy = Math.max(-MAX_VELOCITY, Math.min(MAX_VELOCITY, (node.vy || 0) * DAMPING));

                // Update Position
                node.x = (node.x || 0) + node.vx;
                node.y = (node.y || 0) + node.vy;
            });

            return newNodes;
        });
        
        animationFrameId = requestAnimationFrame(updatePhysics);
    };

    updatePhysics();
    return () => cancelAnimationFrame(animationFrameId);
  }, [edges]);

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

      // Hit testing for hover
      const rect = canvasRef.current?.getBoundingClientRect();
      if (!rect) return;
      const mouseX = (e.clientX - rect.left - rect.width/2 - offset.x) / scale + rect.width/2;
      const mouseY = (e.clientY - rect.top - rect.height/2 - offset.y) / scale + rect.height/2;

      const hit = nodes.find(n => {
          const dx = (n.x || 0) - mouseX;
          const dy = (n.y || 0) - mouseY;
          return Math.sqrt(dx*dx + dy*dy) < (n.radius || 5) + 5;
      });

      setHoveredNode(hit ? hit.id : null);
      // Update cursor
      if (containerRef.current) {
          containerRef.current.style.cursor = hit ? 'pointer' : isDragging ? 'grabbing' : 'grab';
      }
  };

  const handleMouseUp = () => {
      setIsDragging(false);
  };

  // --- RENDER LOOP ---
  useEffect(() => {
      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      if (!canvas || !ctx) return;

      // Resize to container
      canvas.width = containerRef.current?.clientWidth || 800;
      canvas.height = containerRef.current?.clientHeight || 600;

      const render = () => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          
          ctx.save();
          // Camera Transform
          ctx.translate(canvas.width/2 + offset.x, canvas.height/2 + offset.y);
          ctx.scale(scale, scale);
          ctx.translate(-canvas.width/2, -canvas.height/2);

          // Draw Edges
          edges.forEach(edge => {
              const source = nodes.find(n => n.id === edge.source);
              const target = nodes.find(n => n.id === edge.target);
              if (source && target) {
                  ctx.beginPath();
                  ctx.moveTo(source.x || 0, source.y || 0);
                  ctx.lineTo(target.x || 0, target.y || 0);
                  ctx.strokeStyle = 'rgba(148, 163, 184, 0.2)'; // Slate 400, very transparent
                  ctx.lineWidth = 1;
                  ctx.stroke();
              }
          });

          // Draw Nodes
          nodes.forEach(node => {
              const isHovered = hoveredNode === node.id;
              
              // Glow effect for active/important nodes
              if (isHovered || node.type === 'asset') {
                  ctx.shadowBlur = isHovered ? 20 : 10;
                  ctx.shadowColor = node.color || '#fff';
              } else {
                  ctx.shadowBlur = 0;
              }

              ctx.beginPath();
              const radius = (node.radius || 5) * (isHovered ? 1.2 : 1);
              ctx.arc(node.x || 0, node.y || 0, radius, 0, Math.PI * 2);
              ctx.fillStyle = node.color || '#fff';
              ctx.fill();

              // Labels
              // Always show labels for Assets & Strategies, others only on hover
              if (isHovered || node.type === 'asset' || node.type === 'strategy') {
                  ctx.shadowBlur = 0; // No glow for text
                  ctx.fillStyle = isHovered ? '#fff' : 'rgba(255,255,255,0.7)';
                  ctx.font = isHovered ? 'bold 12px Inter' : '10px Inter';
                  ctx.fillText(node.label, (node.x || 0) + radius + 4, (node.y || 0) + 4);
              }
          });

          ctx.restore();
          requestAnimationFrame(render);
      };
      
      render();
  }, [nodes, edges, scale, offset, hoveredNode]);


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
          <div className="flex gap-2">
             <div className="flex items-center gap-2 mr-4 text-xs text-slate-500 border-r border-slate-700 pr-4">
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-[#6366f1]"></div> Strategy</div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-[#eab308]"></div> Asset</div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-[#22c55e]"></div> File</div>
             </div>
             <button onClick={() => setScale(s => s * 1.1)} className="p-2 bg-slate-800 rounded hover:bg-slate-700 text-white" title="Zoom In"><ZoomIn size={18} /></button>
             <button onClick={() => setScale(s => s * 0.9)} className="p-2 bg-slate-800 rounded hover:bg-slate-700 text-white" title="Zoom Out"><ZoomOut size={18} /></button>
             <button onClick={() => { setOffset({x:0,y:0}); setScale(0.8); }} className="p-2 bg-slate-800 rounded hover:bg-slate-700 text-white" title="Reset View"><RefreshCw size={18} /></button>
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
          
          {/* Overlay Stats */}
          <div className="absolute bottom-4 left-4 pointer-events-none">
             <div className="text-[10px] text-slate-600 font-mono">
                PHYSICS ENGINE: ACTIVE<br/>
                NODES: {nodes.length}<br/>
                EDGES: {edges.length}<br/>
                SCALE: {scale.toFixed(2)}x
             </div>
          </div>

          {/* Tooltip for Hovered Node */}
          {hoveredNode && (
            <div className="absolute top-4 right-4 bg-slate-900/90 backdrop-blur p-3 rounded-lg border border-indigo-500/30 text-xs max-w-xs pointer-events-none animate-fade-in">
                 {(() => {
                     const n = nodes.find(node => node.id === hoveredNode);
                     if (!n) return null;
                     return (
                         <div>
                             <div className="font-bold text-white mb-1 text-sm">{n.label}</div>
                             <div className="text-slate-400 uppercase text-[10px] mb-2 tracking-wider">{n.type}</div>
                             {n.type === 'strategy' && (
                                 <div className="space-y-1">
                                     <div className="flex justify-between text-slate-300"><span>Risk:</span> <span className="text-white">{(n.data as Strategy).analysis.riskLevel}</span></div>
                                     <div className="flex justify-between text-slate-300"><span>Sentiment:</span> <span className="text-white">{(n.data as Strategy).analysis.overallSentiment}</span></div>
                                 </div>
                             )}
                             {n.type === 'file' && (
                                 <div className="text-slate-300 truncate">{(n.data as LocalFile).path}</div>
                             )}
                         </div>
                     )
                 })()}
            </div>
          )}
       </div>
    </div>
  );
};
