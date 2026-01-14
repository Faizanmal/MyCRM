/**
 * Health Check API Route
 * =======================
 * 
 * System health monitoring endpoint
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  uptime: number;
  components: ComponentHealth[];
  metrics: SystemMetrics;
}

interface ComponentHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  latency_ms: number;
  message?: string;
  last_check: string;
}

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_connections: number;
  requests_per_second: number;
}

export async function GET(request: NextRequest) {
  const detailed = request.nextUrl.searchParams.get('detailed') === 'true';

  try {
    // Fetch health from backend
    const backendResponse = await fetch(`${BACKEND_URL}/api/health/`, {
      cache: 'no-store',
    });

    const backendHealth = backendResponse.ok
      ? await backendResponse.json()
      : { status: 'unhealthy', message: 'Backend unavailable' };

    // Check Redis
    const redisHealth = await checkRedis();

    // Check database via backend
    const dbHealth = backendHealth.database || {
      status: backendResponse.ok ? 'healthy' : 'unknown',
      latency_ms: 0,
    };

    // Compile health status
    const health: HealthStatus = {
      status: determineOverallStatus([
        backendHealth.status,
        redisHealth.status,
        dbHealth.status,
      ]),
      timestamp: new Date().toISOString(),
      version: process.env.APP_VERSION || '1.0.0',
      uptime: process.uptime(),
      components: [
        {
          name: 'frontend',
          status: 'healthy',
          latency_ms: 0,
          last_check: new Date().toISOString(),
        },
        {
          name: 'backend',
          status: backendResponse.ok ? 'healthy' : 'unhealthy',
          latency_ms: backendHealth.latency_ms || 0,
          message: backendHealth.message,
          last_check: new Date().toISOString(),
        },
        {
          name: 'database',
          status: dbHealth.status || 'unknown',
          latency_ms: dbHealth.latency_ms || 0,
          last_check: new Date().toISOString(),
        },
        {
          name: 'cache',
          ...redisHealth,
          last_check: new Date().toISOString(),
        },
      ],
      metrics: detailed
        ? {
            cpu_usage: backendHealth.metrics?.cpu_usage || 0,
            memory_usage: backendHealth.metrics?.memory_usage || 0,
            disk_usage: backendHealth.metrics?.disk_usage || 0,
            active_connections: backendHealth.metrics?.active_connections || 0,
            requests_per_second: backendHealth.metrics?.requests_per_second || 0,
          }
        : {
            cpu_usage: 0,
            memory_usage: 0,
            disk_usage: 0,
            active_connections: 0,
            requests_per_second: 0,
          },
    };

    const statusCode =
      health.status === 'healthy' ? 200 : health.status === 'degraded' ? 200 : 503;

    return NextResponse.json(health, { status: statusCode });
  } catch (error) {
    console.error('[Health] Check failed:', error);
    return NextResponse.json(
      {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: 'Health check failed',
        components: [],
        metrics: {},
      },
      { status: 503 }
    );
  }
}

async function checkRedis(): Promise<{
  status: 'healthy' | 'degraded' | 'unhealthy';
  latency_ms: number;
  message?: string;
}> {
  try {
    const start = Date.now();
    const response = await fetch(`${BACKEND_URL}/api/health/redis/`, {
      cache: 'no-store',
    });
    const latency = Date.now() - start;

    if (response.ok) {
      return { status: 'healthy', latency_ms: latency };
    } else {
      return { status: 'degraded', latency_ms: latency, message: 'Redis responding slowly' };
    }
  } catch {
    return { status: 'unhealthy', latency_ms: 0, message: 'Redis unavailable' };
  }
}

function determineOverallStatus(
  statuses: (string | undefined)[]
): 'healthy' | 'degraded' | 'unhealthy' {
  const hasUnhealthy = statuses.some((s) => s === 'unhealthy');
  const hasDegraded = statuses.some((s) => s === 'degraded');

  if (hasUnhealthy) return 'unhealthy';
  if (hasDegraded) return 'degraded';
  return 'healthy';
}

