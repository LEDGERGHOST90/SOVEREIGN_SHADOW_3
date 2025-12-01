import Layout from "@/components/layout";
import { SynopticCore } from "@/components/synoptic-core";
import { OracleInterface } from "@/components/oracle-interface";
import { ArchitectForge } from "@/components/architect-forge";
import { GatekeeperMonitor } from "@/components/gatekeeper-monitor";

export default function Dashboard() {
  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground glow-text">Command Center</h1>
            <p className="text-muted-foreground mt-1">Welcome back, Operator. Global market sentiment is <span className="text-primary">Bullish</span>.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="col-span-1 flex flex-col gap-6">
             <SynopticCore />
             <ArchitectForge />
             <GatekeeperMonitor />
          </div>
          
          {/* Right Column - Large Chart/Chat */}
          <div className="col-span-1 md:col-span-2 h-full min-h-[800px]">
            <OracleInterface />
          </div>
        </div>
      </div>
    </Layout>
  );
}
