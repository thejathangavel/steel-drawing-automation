import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Box, Typography, Button } from '@mui/material';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error, errorInfo: null };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Uncaught error:", error, errorInfo);
        this.setState({ errorInfo });
    }

    public render() {
        if (this.state.hasError) {
            return (
                <Box sx={{ p: 4, bgcolor: '#fef2f2', color: '#991b1b', height: '100vh' }}>
                    <Typography variant="h4" gutterBottom>Something went wrong.</Typography>
                    <Typography variant="body1" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap', mb: 2 }}>
                        {this.state.error?.toString()}
                    </Typography>
                    {this.state.errorInfo && (
                        <Box component="pre" sx={{ p: 2, bgcolor: 'rgba(0,0,0,0.05)', overflow: 'auto', fontSize: '0.8rem' }}>
                            {this.state.errorInfo.componentStack}
                        </Box>
                    )}
                    <Button variant="contained" color="error" onClick={() => window.location.reload()}>
                        Reload Page
                    </Button>
                </Box>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
