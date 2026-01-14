/**
 * GraphQL API Route Handler
 * ==========================
 * 
 * Proxy route for GraphQL requests to backend
 */

import { NextRequest, NextResponse } from 'next/server';

const GRAPHQL_ENDPOINT = process.env.GRAPHQL_ENDPOINT || 'http://localhost:8000/graphql';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const authHeader = request.headers.get('authorization');

    const response = await fetch(GRAPHQL_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader && { Authorization: authHeader }),
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    // Handle GraphQL errors
    if (data.errors) {
      // Check for authentication errors
      const authError = data.errors.find(
        (e: { extensions?: { code?: string } }) => 
          e.extensions?.code === 'UNAUTHENTICATED'
      );

      if (authError) {
        return NextResponse.json(
          { errors: data.errors },
          { status: 401 }
        );
      }
    }

    return NextResponse.json(data, {
      status: response.ok ? 200 : response.status,
    });
  } catch (error) {
    console.error('[GraphQL] Proxy error:', error);
    return NextResponse.json(
      {
        errors: [
          {
            message: 'Failed to connect to GraphQL server',
            extensions: { code: 'INTERNAL_SERVER_ERROR' },
          },
        ],
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  // Return GraphQL schema introspection endpoint info
  return NextResponse.json({
    endpoint: '/api/graphql',
    methods: ['POST'],
    documentation: '/api/graphql/playground',
  });
}

