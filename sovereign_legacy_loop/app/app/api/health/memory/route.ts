export async function GET() {
  const m = process.memoryUsage()
  const formatBytes = (bytes: number) => (bytes / 1024 / 1024).toFixed(2) + ' MB'
  
  console.log('[MEMORY]', {
    rss: formatBytes(m.rss),
    heapUsed: formatBytes(m.heapUsed),
    heapTotal: formatBytes(m.heapTotal),
    external: formatBytes(m.external)
  })
  
  return Response.json({
    pid: process.pid,
    uptime: process.uptime(),
    memory: {
      rss: m.rss,
      heapUsed: m.heapUsed,
      heapTotal: m.heapTotal,
      external: m.external,
      arrayBuffers: m.arrayBuffers
    },
    formatted: {
      rss: formatBytes(m.rss),
      heapUsed: formatBytes(m.heapUsed),
      heapTotal: formatBytes(m.heapTotal),
      external: formatBytes(m.external)
    }
  })
}

