import type { PaletteMode } from '@mui/material';
import { alpha } from '@mui/material/styles';

export const getDesignTokens = (mode: PaletteMode) => ({
    palette: {
        mode,
        ...(mode === 'dark' ? {
            // Dark Mode Colors
            primary: {
                main: '#3b82f6',
                light: '#60a5fa',
                dark: '#2563eb',
                contrastText: '#ffffff',
            },
            secondary: {
                main: '#64748b',
                light: '#94a3b8',
                dark: '#475569',
                contrastText: '#ffffff',
            },
            background: {
                default: '#0f172a',
                paper: '#1e293b',
            },
            text: {
                primary: '#f8fafc',
                secondary: '#94a3b8',
            },
        } : {
            // Light Mode Colors
            primary: {
                main: '#2563eb',
                light: '#60a5fa',
                dark: '#1e40af',
                contrastText: '#ffffff',
            },
            secondary: {
                main: '#475569',
                light: '#64748b',
                dark: '#334155',
                contrastText: '#f8fafc',
            },
            background: {
                default: '#f8fafc',
                paper: '#ffffff',
            },
            text: {
                primary: '#0f172a',
                secondary: '#475569',
            },
        }),
    },
    typography: {
        fontFamily: '"Plus Jakarta Sans", "Inter", "Roboto", "Helvetica", "Arial", sans-serif',
        h1: { fontWeight: 800, letterSpacing: '-0.025em' },
        h2: { fontWeight: 700, letterSpacing: '-0.025em' },
        h3: { fontWeight: 700, letterSpacing: '-0.025em' },
        h4: { fontWeight: 700, letterSpacing: '-0.025em' },
        h5: { fontWeight: 600, letterSpacing: '-0.02em' },
        h6: { fontWeight: 600, letterSpacing: '-0.02em' },
        button: {
            textTransform: 'none' as const,
            fontWeight: 600,
            borderRadius: 8,
        },
    },
    components: {
        MuiCssBaseline: {
            styleOverrides: {
                body: {
                    scrollbarColor: mode === 'dark' ? "#334155 #0f172a" : "#cbd5e1 #f1f5f9",
                    "&::-webkit-scrollbar, & *::-webkit-scrollbar": {
                        backgroundColor: mode === 'dark' ? "#0f172a" : "#f1f5f9",
                        width: 8,
                    },
                    "&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb": {
                        borderRadius: 8,
                        backgroundColor: mode === 'dark' ? "#334155" : "#cbd5e1",
                        minHeight: 24,
                        border: `2px solid ${mode === 'dark' ? "#0f172a" : "#f1f5f9"}`,
                    },
                    "&::-webkit-scrollbar-thumb:focus, & *::-webkit-scrollbar-thumb:focus": {
                        backgroundColor: mode === 'dark' ? "#475569" : "#94a3b8",
                    },
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: 10,
                    boxShadow: 'none',
                    padding: '10px 24px',
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': {
                        transform: 'translateY(-1px)',
                        boxShadow: '0 4px 12px rgba(59, 130, 246, 0.25)',
                    },
                },
                contained: {
                    backgroundImage: 'linear-gradient(to bottom right, #3b82f6, #2563eb)',
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    backgroundImage: 'none',
                    transition: 'box-shadow 0.3s ease-in-out, background-color 0.3s ease',
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    borderRadius: 16,
                    border: `1px solid ${mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'}`,
                    backgroundColor: mode === 'dark' ? alpha('#1e293b', 0.6) : alpha('#ffffff', 0.8),
                    backdropFilter: 'blur(12px)',
                },
            },
        },
        MuiChip: {
            styleOverrides: {
                root: {
                    fontWeight: 600,
                    borderRadius: 8,
                },
            },
        },
    },
});
