
'use client';

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { motion } from "framer-motion";
import { 
  MessageCircle, 
  Activity, 
  Target, 
  Settings as SettingsIcon,
  CheckCircle,
  AlertTriangle,
  Clock
} from "lucide-react";
import { toast } from "sonner";

interface Milestone {
  id: number;
  title: string;
  commit?: string;
  timestamp: Date;
}

interface Reflection {
  id: number;
  milestoneId: number;
  text: string;
  timestamp: Date;
}

interface Highlight {
  id: number;
  filePath: string;
  snippetRef: string;
  tag: 'review' | 'polish' | 'risk';
  created_at: Date;
}

interface AgentSettings {
  reviewInterval: string;
  strictMode: boolean;
}

export default function AgentConsole() {
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [reflections, setReflections] = useState<Reflection[]>([]);
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [settings, setSettings] = useState<AgentSettings>({ reviewInterval: "2h", strictMode: false });
  const [newReflection, setNewReflection] = useState("");
  const [selectedMilestone, setSelectedMilestone] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [progressResponse, highlightsResponse, settingsResponse] = await Promise.all([
        fetch("/api/agent/progress-log"),
        fetch("/api/agent/highlights"),
        fetch("/api/agent/settings")
      ]);

      if (progressResponse.ok) {
        const progressData = await progressResponse.json();
        setMilestones(progressData.milestones || []);
        setReflections(progressData.reflections || []);
      }

      if (highlightsResponse.ok) {
        const highlightsData = await highlightsResponse.json();
        setHighlights(highlightsData.highlights || []);
      }

      if (settingsResponse.ok) {
        const settingsData = await settingsResponse.json();
        setSettings(settingsData);
      }
    } catch (error) {
      console.error('Failed to load agent data:', error);
    }
  };

  const submitReflection = async () => {
    if (!selectedMilestone || !newReflection.trim()) return;

    try {
      const response = await fetch("/api/agent/reflection", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          milestoneId: selectedMilestone, 
          text: newReflection.trim() 
        })
      });

      if (response.ok) {
        const data = await response.json();
        setReflections([...reflections, data.reflection]);
        setNewReflection("");
        setSelectedMilestone(null);
        toast.success("Reflection saved successfully");
      }
    } catch (error) {
      toast.error("Failed to save reflection");
    }
  };

  const getTagColor = (tag: string) => {
    switch (tag) {
      case 'review': return 'bg-green-500';
      case 'polish': return 'bg-yellow-500';
      case 'risk': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getTagIcon = (tag: string) => {
    switch (tag) {
      case 'review': return <CheckCircle className="w-3 h-3" />;
      case 'polish': return <Clock className="w-3 h-3" />;
      case 'risk': return <AlertTriangle className="w-3 h-3" />;
      default: return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Agent Console Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Card className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 border-purple-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <MessageCircle className="w-5 h-5" />
              Personal Agent Console
            </CardTitle>
            <CardDescription className="text-gray-300">
              AI-powered development companion with progress tracking and reflection capabilities
            </CardDescription>
          </CardHeader>
        </Card>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Progress Timeline */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <Card className="h-[400px]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Progress Timeline
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 overflow-y-auto max-h-[300px]">
              {milestones.map((milestone) => {
                const milestoneReflections = reflections.filter(r => r.milestoneId === milestone.id);
                return (
                  <div key={milestone.id} className="border-b border-gray-200 pb-3 last:border-b-0">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-sm">{milestone.title}</h4>
                      <Badge variant="secondary" className="text-xs">
                        {milestone.commit || "manual"}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">
                      {new Date(milestone.timestamp).toLocaleString()}
                    </p>
                    
                    {/* Show existing reflections */}
                    {milestoneReflections.map(reflection => (
                      <div key={reflection.id} className="bg-muted/50 p-2 rounded text-xs mb-2">
                        <p className="text-muted-foreground italic">
                          "{reflection.text}"
                        </p>
                        <span className="text-xs text-muted-foreground">
                          {new Date(reflection.timestamp).toLocaleString()}
                        </span>
                      </div>
                    ))}
                    
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-xs"
                      onClick={() => setSelectedMilestone(milestone.id)}
                    >
                      Add Reflection
                    </Button>
                  </div>
                );
              })}
              
              {milestones.length === 0 && (
                <p className="text-muted-foreground text-center py-8">
                  No milestones tracked yet
                </p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Highlight Review */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <Card className="h-[400px]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Highlight Review
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 overflow-y-auto max-h-[300px]">
              {highlights.map((highlight) => (
                <div key={highlight.id} className="flex items-center gap-3 p-2 rounded hover:bg-muted/50 transition-colors">
                  <div className={`w-3 h-3 rounded-full flex items-center justify-center ${getTagColor(highlight.tag)}`}>
                    {getTagIcon(highlight.tag)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {highlight.filePath}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {highlight.tag} - {highlight.snippetRef}
                    </p>
                  </div>
                </div>
              ))}
              
              {highlights.length === 0 && (
                <p className="text-muted-foreground text-center py-8">
                  No highlights to review
                </p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Reflection Input */}
        {selectedMilestone && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="lg:col-span-2"
          >
            <Card>
              <CardHeader>
                <CardTitle>Add Reflection</CardTitle>
                <CardDescription>
                  Milestone: {milestones.find(m => m.id === selectedMilestone)?.title}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Add your reflection on this milestone..."
                  value={newReflection}
                  onChange={(e) => setNewReflection(e.target.value)}
                  rows={3}
                />
                <div className="flex gap-2">
                  <Button onClick={submitReflection} disabled={!newReflection.trim()}>
                    Save Reflection
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setSelectedMilestone(null);
                      setNewReflection("");
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Agent Settings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="lg:col-span-2"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <SettingsIcon className="w-5 h-5" />
                Agent Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Review Interval</label>
                <select 
                  className="w-full p-2 border rounded-md bg-background"
                  value={settings.reviewInterval}
                  onChange={(e) => setSettings({...settings, reviewInterval: e.target.value})}
                >
                  <option value="1h">Every Hour</option>
                  <option value="2h">Every 2 Hours</option>
                  <option value="4h">Every 4 Hours</option>
                  <option value="daily">Daily</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={settings.strictMode}
                    onChange={(e) => setSettings({...settings, strictMode: e.target.checked})}
                  />
                  Strict Mode
                </label>
                <p className="text-xs text-muted-foreground">
                  Enable enhanced code review and validation
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
