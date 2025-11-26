
'use client';

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  Vault,
  Zap,
  Map,
  BarChart3,
  Bot,
  User,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Crown,
  Building2,
  Receipt,
  Calculator,
  TrendingUp,
  Sparkles
} from "lucide-react";
import { signOut } from "next-auth/react";

const navigation = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    description: "Overview & System Status"
  },
  {
    name: "Vault Tracker",
    href: "/vault",
    icon: Vault,
    description: "Cold Storage & Security"
  },
  {
    name: "Oracle RWA Engine",
    href: "/rwa",
    icon: Crown,
    description: "Real-World Assets • Ellison-Inspired"
  },
  {
    name: "Advanced Trading",
    href: "/trading",
    icon: Zap,
    description: "AI-Powered Trade Execution"
  },
  {
    name: "Strategy Scout",
    href: "/strategy-scout",
    icon: Sparkles,
    description: "AI Strategy Analyzer • Gemini-Powered"
  },
  {
    name: "Enhanced Siphon",
    href: "/siphon",
    icon: Building2,
    description: "Hybrid AI Siphon Logic"
  },
  {
    name: "TRUE P&L + Tax",
    href: "/tax-timeline",
    icon: Receipt,
    description: "Real P&L Timeline with Tax Analysis"
  },
  {
    name: "Heatmap",
    href: "/heatmap",
    icon: Map,
    description: "Asset Allocation View"
  },
  {
    name: "Analytics",
    href: "/analytics",
    icon: BarChart3,
    description: "Performance & Risk"
  },
  {
    name: "AI Advisor",
    href: "/advisor",
    icon: Bot,
    description: "R2 + Shadow.AI"
  },
  {
    name: "Agent Console",
    href: "/agent",
    icon: User,
    description: "Personal Progress"
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
    description: "System Configuration"
  }
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  const handleSignOut = async () => {
    await signOut({ redirect: true, callbackUrl: "/" });
  };

  return (
    <div className={cn(
      "fixed left-0 top-0 z-50 h-screen transition-all duration-300",
      "bg-white/5 backdrop-blur-xl border-r border-white/10",
      collapsed ? "w-16" : "w-64"
    )}>
      <div className="flex h-full flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          {!collapsed && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-400 via-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                <Vault className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-sm font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-blue-500 to-purple-600">
                  Sovereign
                </h1>
                <p className="text-xs text-white/60">Legacy Loop</p>
              </div>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="h-8 w-8 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-white/70 hover:text-white transition-all duration-300"
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto py-4">
          <nav className="space-y-1 px-2">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "group flex items-center rounded-xl px-3 py-2 text-sm font-medium transition-all duration-300",
                    "hover:bg-white/10 hover:backdrop-blur-sm",
                    isActive
                      ? "bg-white/15 backdrop-blur-sm text-white border border-white/20 shadow-lg"
                      : "text-white/70 hover:text-white"
                  )}
                >
                  <item.icon className={cn(
                    "h-5 w-5 shrink-0",
                    collapsed ? "mr-0" : "mr-3",
                    isActive ? "text-white" : "text-white/70 group-hover:text-white"
                  )} />
                  {!collapsed && (
                    <div className="flex-1">
                      <div className="font-medium">{item.name}</div>
                      <div className="text-xs text-white/50">
                        {item.description}
                      </div>
                    </div>
                  )}
                  {collapsed && (
                    <div className="absolute left-16 z-50 ml-2 rounded-xl bg-white/10 backdrop-blur-xl border border-white/20 px-3 py-2 text-sm opacity-0 shadow-2xl group-hover:opacity-100 transition-all duration-300">
                      <div className="font-medium text-white">{item.name}</div>
                      <div className="text-xs text-white/60">
                        {item.description}
                      </div>
                    </div>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer */}
        <div className="border-t border-white/10 p-4">
          <Button
            variant="ghost"
            onClick={handleSignOut}
            className={cn(
              "w-full justify-start text-white/70 hover:text-red-400 hover:bg-red-500/10 transition-all duration-300 rounded-xl",
              collapsed && "px-2"
            )}
          >
            <LogOut className={cn("h-5 w-5", collapsed ? "mr-0" : "mr-3")} />
            {!collapsed && "Sign Out"}
          </Button>
        </div>
      </div>
    </div>
  );
}
