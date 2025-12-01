import { Link } from "wouter";
import { AlertTriangle } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background text-foreground">
      <div className="glass-panel p-8 md:p-12 rounded-lg border-destructive/30 text-center max-w-md mx-4">
        <div className="flex justify-center mb-6">
          <div className="relative">
            <AlertTriangle className="h-16 w-16 text-destructive" />
            <div className="absolute inset-0 bg-destructive/20 blur-xl rounded-full animate-pulse" />
          </div>
        </div>
        
        <h1 className="text-4xl font-display font-bold mb-2 text-destructive">404</h1>
        <h2 className="text-xl font-mono mb-6 text-muted-foreground">SIGNAL_LOST</h2>
        
        <p className="text-muted-foreground mb-8">
          The requested sector could not be located in the sovereign grid.
        </p>

        <Link href="/" className="inline-flex items-center justify-center px-6 py-3 rounded-md bg-destructive/10 hover:bg-destructive/20 text-destructive border border-destructive/50 transition-colors font-medium">
          Return to Command
        </Link>
      </div>
    </div>
  );
}
