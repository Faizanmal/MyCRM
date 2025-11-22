'use client';

// Authentication is temporarily disabled for development; this component
// intentionally bypasses auth checks. Remove these comments and re-enable
// the imports when restoring authentication behavior.

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  // TEMPORARY: Authentication disabled - always allow access
  // Authentication disabled: bypassing checks for now.

  console.log('TEMP: ProtectedRoute bypassed - authentication disabled');
  return <>{children}</>;
}
