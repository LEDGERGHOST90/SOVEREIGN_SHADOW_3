
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import AgentConsole from "@/components/agent/agent-console";

export default async function AgentPage() {
  const session = await getServerSession(authOptions);

  if (!session) {
    redirect("/");
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agent Console</h1>
          <p className="text-muted-foreground">
            Your personal AI development companion with progress tracking and reflection capabilities
          </p>
        </div>
      </div>
      
      <AgentConsole />
    </div>
  );
}
