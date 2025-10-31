
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

    const reflections = await prisma.agentReflection.findMany({
      where: { userId: session.user.id },
      orderBy: { createdAt: 'desc' },
      take: 20
    });

    return NextResponse.json(reflections.map(r => ({
      id: r.id,
      content: r.content,
      mood: r.mood,
      tags: r.tags,
      createdAt: r.createdAt.toISOString()
    })));
  } catch (error) {
    console.error("Reflections fetch error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { content, mood, tags } = await req.json();

    if (!content) {
      return NextResponse.json({ error: "Content is required" }, { status: 400 });
    }

    const reflection = await prisma.agentReflection.create({
      data: {
        userId: session.user.id,
        content,
        mood: mood || null,
        tags: tags || []
      }
    });

    return NextResponse.json({
      id: reflection.id,
      content: reflection.content,
      mood: reflection.mood,
      tags: reflection.tags,
      createdAt: reflection.createdAt.toISOString()
    });
  } catch (error) {
    console.error("Reflection creation error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
