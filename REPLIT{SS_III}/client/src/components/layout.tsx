import { Link, useLocation } from "wouter";
import { 
  LayoutDashboard, 
  Brain, 
  Terminal, 
  Settings, 
  Bell, 
  Search, 
  User, 
  Menu,
  Shield
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Sheet, 
  SheetContent, 
} from "@/components/ui/sheet";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useState } from "react";
import { cn } from "@/lib/utils";

export default function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = [
    { href: "/", icon: LayoutDashboard, label: "Dashboard" },
    { href: "/intelligence", icon: Brain, label: "Synoptic Core" },
    { href: "/strategies", icon: Terminal, label: "Architect Forge" },
    { href: "/settings", icon: Settings, label: "Settings" },
  ];

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-sidebar border-r border-sidebar-border">
      <div className="h-16 flex items-center px-6 border-b border-sidebar-border">
        <Shield className="h-6 w-6 text-primary mr-2" />
        <span className="font-display font-bold text-lg tracking-wide text-sidebar-foreground">
          SOVEREIGN<span className="text-primary">.SHADOW</span>
        </span>
      </div>

      <div className="flex-1 py-6 px-3 space-y-1">
        {navItems.map((item) => (
          <Link key={item.href} href={item.href} className={cn(
            "flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors group relative overflow-hidden",
            location === item.href 
              ? "text-sidebar-primary-foreground bg-sidebar-primary/10 border border-sidebar-primary/20" 
              : "text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent"
          )}>
            {location === item.href && (
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary shadow-[0_0_10px_var(--primary)]" />
            )}
            <item.icon className={cn("h-5 w-5 mr-3", location === item.href ? "text-primary" : "text-sidebar-foreground/40 group-hover:text-sidebar-foreground")} />
            {item.label}
          </Link>
        ))}
      </div>

      <div className="p-4 border-t border-sidebar-border">
        <div className="flex items-center gap-3">
          <Avatar className="h-9 w-9 border border-sidebar-border">
            <AvatarImage src="https://github.com/shadcn.png" />
            <AvatarFallback>OP</AvatarFallback>
          </Avatar>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-sidebar-foreground">Operator.01</span>
            <span className="text-xs text-sidebar-foreground/50">Access Level 5</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-background text-foreground flex font-sans">
      {/* Desktop Sidebar */}
      <div className="hidden md:block w-64 shrink-0 h-screen sticky top-0">
        <SidebarContent />
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="p-0 w-64 border-r-sidebar-border bg-sidebar text-sidebar-foreground">
          <SidebarContent />
        </SheetContent>
      </Sheet>

      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-16 flex items-center justify-between px-4 md:px-8 border-b border-border bg-background/50 backdrop-blur-sm sticky top-0 z-10">
          <div className="flex items-center gap-4 md:hidden">
            <Button variant="ghost" size="icon" className="-ml-2" onClick={() => setSidebarOpen(true)}>
              <Menu className="h-5 w-5" />
            </Button>
            <span className="font-display font-bold text-lg">SS3</span>
          </div>

          <div className="hidden md:flex items-center text-sm text-muted-foreground">
            <span className="mr-2 text-green-500">●</span> System Nominal
            <span className="mx-4 text-border">|</span>
            <span className="font-mono">Latency: 12ms</span>
          </div>

          <div className="flex items-center gap-4">
            <div className="relative hidden sm:block w-64">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search assets, signals..." 
                className="pl-9 bg-secondary/5 border-secondary/10 focus-visible:ring-secondary text-xs h-9" 
              />
            </div>
            <Button variant="ghost" size="icon" className="relative text-muted-foreground hover:text-foreground">
              <Bell className="h-5 w-5" />
              <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-primary animate-pulse" />
            </Button>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-4 md:p-8 overflow-y-auto scrollbar-hide">
          <div className="max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
