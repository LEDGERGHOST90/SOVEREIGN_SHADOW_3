
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const milestones = await prisma.agentMilestone.findMany({
      where: { userId: session.user.id },
      orderBy: { createdAt: 'desc' }
    });

    return NextResponse.json(milestones.map(m => ({
      id: m.id,
      title: m.title,
      description: m.description,
      category: m.category,
      achieved: m.achieved,
      achievedAt: m.achievedAt?.toISOString(),
      createdAt: m.createdAt.toISOString()
    })));
  } catch (error) {
    console.error("Milestones fetch error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { title, description, category } = await req.json();

    if (!title || !category) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 });
    }

    const milestone = await prisma.agentMilestone.create({
      data: {
        userId: session.user.id,
        title,
        description,
        category
      }
    });

    return NextResponse.json({
      id: milestone.id,
      title: milestone.title,
      description: milestone.description,
      category: milestone.category,
      achieved: milestone.achieved,
      createdAt: milestone.createdAt.toISOString()
    });
  } catch (error) {
    console.error("Milestone creation error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
