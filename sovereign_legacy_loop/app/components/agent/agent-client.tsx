
'use client';

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  User, 
  Target, 
  MessageSquare, 
  AlertCircle,
  CheckCircle,
  Clock,
  Plus,
  Settings,
  Lightbulb,
  TrendingUp,
  Shield
} from "lucide-react";
import { AgentMilestone, AgentReflection, AgentHighlight } from "@/lib/types";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";

export default function AgentClient() {
  const [milestones, setMilestones] = useState<AgentMilestone[]>([]);
  const [reflections, setReflections] = useState<AgentReflection[]>([]);
  const [highlights, setHighlights] = useState<AgentHighlight[]>([]);
  const [loading, setLoading] = useState(true);

  // New milestone form
  const [newMilestone, setNewMilestone] = useState({
    title: '',
    description: '',
    category: 'wealth'
  });

  // New reflection form
  const [newReflection, setNewReflection] = useState({
    content: '',
    mood: 'confident',
    tags: ''
  });

  const fetchAgentData = async () => {
    try {
      const [milestonesRes, reflectionsRes, highlightsRes] = await Promise.all([
        fetch('/api/agent/milestones'),
        fetch('/api/agent/reflections'),
        fetch('/api/agent/highlights')
      ]);

      if (milestonesRes.ok) {
        const data = await milestonesRes.json();
        setMilestones(data);
      }

      if (reflectionsRes.ok) {
        const data = await reflectionsRes.json();
        setReflections(data);
      }

      if (highlightsRes.ok) {
        const data = await highlightsRes.json();
        setHighlights(data);
      }
    } catch (error) {
      toast.error("Failed to fetch agent data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgentData();
  }, []);

  const handleCreateMilestone = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMilestone.title) return;

    try {
      const response = await fetch('/api/agent/milestones', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newMilestone)
      });

      if (response.ok) {
        const milestone = await response.json();
        setMilestones(prev => [milestone, ...prev]);
        setNewMilestone({ title: '', description: '', category: 'wealth' });
        toast.success("Milestone created successfully");
      } else {
        throw new Error('Failed to create milestone');
      }
    } catch (error) {
      toast.error("Failed to create milestone");
    }
  };

  const handleCreateReflection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newReflection.content) return;

    try {
      const tags = newReflection.tags.split(',').map(tag => tag.trim()).filter(Boolean);
      
      const response = await fetch('/api/agent/reflections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: newReflection.content,
          mood: newReflection.mood,
          tags
        })
      });

      if (response.ok) {
        const reflection = await response.json();
        setReflections(prev => [reflection, ...prev]);
        setNewReflection({ content: '', mood: 'confident', tags: '' });
        toast.success("Reflection added successfully");
      } else {
        throw new Error('Failed to create reflection');
      }
    } catch (error) {
      toast.error("Failed to create reflection");
    }
  };

  const getMilestoneIcon = (category: string) => {
    switch (category) {
      case 'wealth': return <TrendingUp className="h-4 w-4" />;
      case 'security': return <Shield className="h-4 w-4" />;
      case 'trading': return <Target className="h-4 w-4" />;
      default: return <Target className="h-4 w-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'HIGH': return 'destructive';
      case 'MEDIUM': return 'secondary';
      case 'LOW': return 'default';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-gold bg-clip-text text-transparent">
            Personal Agent Console
          </h1>
          <p className="text-muted-foreground">
            Track progress, reflect on growth, and review system highlights
          </p>
        </div>
        <Button variant="outline" size="sm" className="gap-2">
          <Settings className="h-4 w-4" />
          Agent Settings
        </Button>
      </div>

      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium">Total Milestones</span>
            </div>
            <div className="text-2xl font-bold mt-1">{milestones.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-400" />
              <span className="text-sm font-medium">Achieved</span>
            </div>
            <div className="text-2xl font-bold mt-1 text-green-400">
              {milestones.filter(m => m.achieved).length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-blue-400" />
              <span className="text-sm font-medium">Reflections</span>
            </div>
            <div className="text-2xl font-bold mt-1 text-blue-400">
              {reflections.length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-orange-400" />
              <span className="text-sm font-medium">Open Highlights</span>
            </div>
            <div className="text-2xl font-bold mt-1 text-orange-400">
              {highlights.filter(h => h.status === 'OPEN').length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="milestones" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="milestones" className="gap-2">
            <Target className="h-4 w-4" />
            Milestones
          </TabsTrigger>
          <TabsTrigger value="reflections" className="gap-2">
            <MessageSquare className="h-4 w-4" />
            Reflections
          </TabsTrigger>
          <TabsTrigger value="highlights" className="gap-2">
            <AlertCircle className="h-4 w-4" />
            Highlights
          </TabsTrigger>
        </TabsList>

        <TabsContent value="milestones" className="space-y-6">
          {/* Create Milestone */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Create New Milestone
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateMilestone} className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Title</label>
                    <Input
                      value={newMilestone.title}
                      onChange={(e) => setNewMilestone(prev => ({ ...prev, title: e.target.value }))}
                      placeholder="e.g., Reach $10K portfolio value"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Category</label>
                    <select 
                      value={newMilestone.category}
                      onChange={(e) => setNewMilestone(prev => ({ ...prev, category: e.target.value }))}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="wealth">Wealth</option>
                      <option value="trading">Trading</option>
                      <option value="security">Security</option>
                      <option value="learning">Learning</option>
                    </select>
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Description</label>
                  <Textarea
                    value={newMilestone.description}
                    onChange={(e) => setNewMilestone(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe this milestone and why it's important..."
                  />
                </div>
                <Button type="submit" className="gap-2">
                  <Plus className="h-4 w-4" />
                  Create Milestone
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Milestones List */}
          <Card>
            <CardHeader>
              <CardTitle>Progress Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                <div className="space-y-4">
                  <AnimatePresence>
                    {milestones.map((milestone) => (
                      <motion.div
                        key={milestone.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className={`p-4 rounded-lg border ${
                          milestone.achieved 
                            ? 'bg-green-500/10 border-green-500/20' 
                            : 'bg-muted/30 border-border'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            <div className={`p-2 rounded-full ${
                              milestone.achieved 
                                ? 'bg-green-500/20 text-green-400' 
                                : 'bg-muted text-muted-foreground'
                            }`}>
                              {milestone.achieved ? <CheckCircle className="h-4 w-4" /> : getMilestoneIcon(milestone.category)}
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium">{milestone.title}</h4>
                              {milestone.description && (
                                <p className="text-sm text-muted-foreground mt-1">
                                  {milestone.description}
                                </p>
                              )}
                              <div className="flex items-center gap-2 mt-2">
                                <Badge variant="outline" className="text-xs">
                                  {milestone.category}
                                </Badge>
                                <span className="text-xs text-muted-foreground">
                                  {new Date(milestone.createdAt).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reflections" className="space-y-6">
          {/* Create Reflection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5" />
                New Reflection
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateReflection} className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Mood</label>
                    <select 
                      value={newReflection.mood}
                      onChange={(e) => setNewReflection(prev => ({ ...prev, mood: e.target.value }))}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="confident">Confident</option>
                      <option value="cautious">Cautious</option>
                      <option value="excited">Excited</option>
                      <option value="focused">Focused</option>
                      <option value="analytical">Analytical</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Tags</label>
                    <Input
                      value={newReflection.tags}
                      onChange={(e) => setNewReflection(prev => ({ ...prev, tags: e.target.value }))}
                      placeholder="trading, strategy, market-analysis (comma-separated)"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Reflection</label>
                  <Textarea
                    value={newReflection.content}
                    onChange={(e) => setNewReflection(prev => ({ ...prev, content: e.target.value }))}
                    placeholder="Share your thoughts on recent trades, market conditions, or lessons learned..."
                    rows={4}
                  />
                </div>
                <Button type="submit" className="gap-2">
                  <MessageSquare className="h-4 w-4" />
                  Add Reflection
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Reflections List */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Reflections</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                <div className="space-y-4">
                  {reflections.map((reflection) => (
                    <div key={reflection.id} className="p-4 rounded-lg bg-muted/30 border">
                      <div className="flex items-start justify-between mb-3">
                        <Badge variant="outline">{reflection.mood}</Badge>
                        <span className="text-xs text-muted-foreground">
                          {new Date(reflection.createdAt).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm leading-relaxed mb-3">
                        {reflection.content}
                      </p>
                      {reflection.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {reflection.tags.map((tag, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="highlights" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                System Highlights & Issues
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {highlights.length > 0 ? highlights.map((highlight) => (
                  <div key={highlight.id} className="p-4 rounded-lg border">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant={getSeverityColor(highlight.severity) as any}>
                            {highlight.severity}
                          </Badge>
                          <span className="text-sm font-medium">{highlight.component}</span>
                          <Badge variant={highlight.status === 'OPEN' ? 'destructive' : 'default'}>
                            {highlight.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {highlight.issue}
                        </p>
                        <span className="text-xs text-muted-foreground">
                          {new Date(highlight.createdAt).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                )) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>No system highlights at this time</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
