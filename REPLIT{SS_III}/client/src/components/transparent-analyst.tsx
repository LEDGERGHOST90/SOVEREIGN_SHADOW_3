import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, ShieldCheck, CheckCircle, AlertCircle, Search } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

interface TransparentAnalystProps {
  recommendation: string;
  steps: string[];
  className?: string;
}

export function TransparentAnalyst({ recommendation, steps, className }: TransparentAnalystProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={cn("rounded-lg border border-primary/20 bg-primary/5 overflow-hidden", className)}>
      {/* Header / Recommendation Block */}
      <div className="p-4 border-b border-primary/10">
        <div className="flex items-center gap-2 mb-2">
          <ShieldCheck className="h-4 w-4 text-primary" />
          <span className="text-xs font-bold text-primary tracking-wider uppercase">Transparent Analyst</span>
        </div>
        <p className="text-sm font-medium text-foreground leading-relaxed">
          {recommendation}
        </p>
      </div>

      {/* Collapsible Process Block */}
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div className="bg-muted/30 px-4 py-2 flex items-center justify-between">
          <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-mono">Execution Audit Trail</span>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm" className="h-6 w-6 p-0 hover:bg-white/5">
              {isOpen ? (
                <ChevronUp className="h-3 w-3 text-muted-foreground" />
              ) : (
                <ChevronDown className="h-3 w-3 text-muted-foreground" />
              )}
            </Button>
          </CollapsibleTrigger>
        </div>
        
        <CollapsibleContent>
          <div className="p-4 bg-black/20 space-y-3 border-t border-white/5">
            {steps.map((step, index) => (
              <div key={index} className="flex gap-3 text-xs font-mono text-muted-foreground">
                <span className="text-primary/50 shrink-0">{(index + 1).toString().padStart(2, '0')}</span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}
