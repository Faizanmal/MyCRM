'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
    onError?: (error: Error, errorInfo: ErrorInfo) => void;
    showDetails?: boolean;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

/**
 * Error Boundary Component
 * 
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI.
 * 
 * Features:
 * - Customizable fallback UI
 * - Error reporting callback
 * - Development mode error details
 * - Recovery options (retry, go home)
 */
export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        };
    }

    static getDerivedStateFromError(error: Error): Partial<State> {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
        // Log error to console
        console.error('ErrorBoundary caught an error:', error, errorInfo);

        // Update state with error info
        this.setState({ errorInfo });

        // Call custom error handler if provided
        if (this.props.onError) {
            this.props.onError(error, errorInfo);
        }

        // Report to error tracking service (Sentry, etc.)
        this.reportError(error, errorInfo);
    }

    private reportError(error: Error, errorInfo: ErrorInfo): void {
        // Send to Sentry or other error tracking service
        if (typeof window !== 'undefined' && (window as unknown as { Sentry?: { captureException: (error: Error, context: object) => void } }).Sentry) {
            (window as unknown as { Sentry: { captureException: (error: Error, context: object) => void } }).Sentry.captureException(error, {
                extra: {
                    componentStack: errorInfo.componentStack,
                },
            });
        }

        // Also log to backend if needed
        this.logErrorToBackend(error, errorInfo);
    }

    private async logErrorToBackend(error: Error, errorInfo: ErrorInfo): Promise<void> {
        try {
            await fetch('/api/errors/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: error.message,
                    stack: error.stack,
                    componentStack: errorInfo.componentStack,
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    timestamp: new Date().toISOString(),
                }),
            });
        } catch {
            // Silently fail - don't cause another error
            console.warn('Failed to log error to backend');
        }
    }

    private handleRetry = (): void => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
        });
    };

    private handleGoHome = (): void => {
        window.location.href = '/';
    };

    private handleReportBug = (): void => {
        const subject = encodeURIComponent(`Bug Report: ${this.state.error?.message || 'Unknown Error'}`);
        const body = encodeURIComponent(`
Error: ${this.state.error?.message || 'Unknown'}

Stack Trace:
${this.state.error?.stack || 'Not available'}

Component Stack:
${this.state.errorInfo?.componentStack || 'Not available'}

URL: ${window.location.href}
Time: ${new Date().toISOString()}
    `);
        window.open(`mailto:support@mycrm.com?subject=${subject}&body=${body}`);
    };

    render(): ReactNode {
        if (this.state.hasError) {
            // Custom fallback provided
            if (this.props.fallback) {
                return this.props.fallback;
            }

            // Default error UI
            return (
                <div className="min-h-[400px] flex items-center justify-center p-6">
                    <Card className="max-w-lg w-full shadow-lg">
                        <CardHeader className="text-center">
                            <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-red-100 flex items-center justify-center">
                                <AlertTriangle className="h-8 w-8 text-red-600" />
                            </div>
                            <CardTitle className="text-xl font-semibold text-gray-900">
                                Something went wrong
                            </CardTitle>
                            <CardDescription className="text-gray-600">
                                We encountered an unexpected error. Please try again or contact support if the problem persists.
                            </CardDescription>
                        </CardHeader>

                        <CardContent>
                            {/* Show error details in development */}
                            {(this.props.showDetails || process.env.NODE_ENV === 'development') && this.state.error && (
                                <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                                    <h4 className="text-sm font-medium text-gray-700 mb-2">Error Details</h4>
                                    <p className="text-sm text-red-600 font-mono break-all">
                                        {this.state.error.message}
                                    </p>
                                    {this.state.error.stack && (
                                        <details className="mt-2">
                                            <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                                                View Stack Trace
                                            </summary>
                                            <pre className="mt-2 text-xs text-gray-600 overflow-auto max-h-40 p-2 bg-gray-100 rounded">
                                                {this.state.error.stack}
                                            </pre>
                                        </details>
                                    )}
                                </div>
                            )}
                        </CardContent>

                        <CardFooter className="flex flex-col sm:flex-row gap-3 justify-center">
                            <Button onClick={this.handleRetry} className="w-full sm:w-auto">
                                <RefreshCw className="h-4 w-4 mr-2" />
                                Try Again
                            </Button>
                            <Button variant="outline" onClick={this.handleGoHome} className="w-full sm:w-auto">
                                <Home className="h-4 w-4 mr-2" />
                                Go to Home
                            </Button>
                            <Button variant="ghost" onClick={this.handleReportBug} className="w-full sm:w-auto">
                                <Bug className="h-4 w-4 mr-2" />
                                Report Bug
                            </Button>
                        </CardFooter>
                    </Card>
                </div>
            );
        }

        return this.props.children;
    }
}

/**
 * Hook-based error boundary wrapper for functional components
 */
export function withErrorBoundary<P extends object>(
    WrappedComponent: React.ComponentType<P>,
    errorBoundaryProps?: Omit<Props, 'children'>
): React.FC<P> {
    const WithErrorBoundary: React.FC<P> = (props) => (
        <ErrorBoundary {...errorBoundaryProps}>
            <WrappedComponent {...props} />
        </ErrorBoundary>
    );

    WithErrorBoundary.displayName = `withErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

    return WithErrorBoundary;
}

/**
 * Simple error fallback component for use with ErrorBoundary
 */
export function ErrorFallback({
    error,
    resetError
}: {
    error?: Error;
    resetError?: () => void;
}): React.JSX.Element {
    return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-red-700">
                <AlertTriangle className="h-5 w-5" />
                <span className="font-medium">Error</span>
            </div>
            {error && (
                <p className="mt-2 text-sm text-red-600">{error.message}</p>
            )}
            {resetError && (
                <Button
                    size="sm"
                    variant="outline"
                    onClick={resetError}
                    className="mt-3"
                >
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Retry
                </Button>
            )}
        </div>
    );
}

export default ErrorBoundary;
