import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Alert, InputAdornment } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import PersonOutlineIcon from '@mui/icons-material/PersonOutline';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

import steelBg from '../assets/steel-structure.png';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const [activeSlide, setActiveSlide] = useState(0);

    const slides = [
        {
            title: "SteelFlow",
            subtitle: "Advanced Steel Drawing Workflow Automation & Management"
        },
        {
            title: "Automated Extraction",
            subtitle: "Intelligent parsing of PDF and DXF drawings for seamless data integration."
        },
        {
            title: "Project Insights",
            subtitle: "Real-time dashboards and analytics to track your project's progress."
        }
    ];

    React.useEffect(() => {
        const interval = setInterval(() => {
            setActiveSlide((prev) => (prev + 1) % slides.length);
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Simple mock validation for demo
        if (username === 'admin' && password === 'admin') {
            login('mock-jwt-token', username);
            navigate('/dashboard');
        } else {
            setError('Invalid credentials. Try admin / admin');
        }
    };

    return (
        <Box sx={{
            minHeight: '100vh',
            display: 'flex',
            bgcolor: 'background.default',
        }}>
            {/* Left Side - Visual/Branding */}
            <Box sx={{
                flex: 1.2,
                display: { xs: 'none', md: 'flex' },
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                p: 8,
                position: 'relative',
                overflow: 'hidden',
                backgroundImage: `url(${steelBg})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 58, 138, 0.9) 100%)',
                    zIndex: 1
                }
            }}>

                <Box sx={{ position: 'relative', zIndex: 2, maxWidth: 520, width: '100%' }}>

                    <Box sx={{ minHeight: 200 }}>
                        {slides.map((slide, index) => (
                            <Box
                                key={index}
                                sx={{
                                    display: activeSlide === index ? 'block' : 'none',
                                    animation: 'fadeIn 0.8s ease-out'
                                }}
                            >
                                <Typography variant="h1" fontWeight={800} sx={{
                                    mb: 3,
                                    fontSize: '3.5rem',
                                    lineHeight: 1.1,
                                    background: 'linear-gradient(to right, #fff, #cbd5e1)',
                                    backgroundClip: 'text',
                                    textFillColor: 'transparent',
                                    userSelect: 'none'
                                }}>
                                    {slide.title}
                                </Typography>
                                <Typography variant="h5" sx={{
                                    fontWeight: 400,
                                    color: '#94a3b8',
                                    lineHeight: 1.6,
                                    maxWidth: '90%'
                                }}>
                                    {slide.subtitle}
                                </Typography>
                            </Box>
                        ))}
                    </Box>

                    {/* Progress Indicators */}
                    <Box sx={{ display: 'flex', gap: 1.5, mt: 8 }}>
                        {slides.map((_, i) => (
                            <Box
                                key={i}
                                onClick={() => setActiveSlide(i)}
                                sx={{
                                    height: 4,
                                    width: activeSlide === i ? 48 : 24,
                                    borderRadius: 4,
                                    bgcolor: activeSlide === i ? '#3b82f6' : 'rgba(255,255,255,0.1)',
                                    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                                    cursor: 'pointer',
                                    '&:hover': { bgcolor: activeSlide === i ? '#3b82f6' : 'rgba(255,255,255,0.3)' }
                                }}
                            />
                        ))}
                    </Box>
                </Box>
            </Box>

            {/* Right Side - Login Form */}
            <Box sx={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                p: { xs: 4, md: 8 },
                bgcolor: (theme) => theme.palette.mode === 'dark' ? '#0f172a' : '#ffffff',
                position: 'relative'
            }}>
                <Box sx={{ width: '100%', maxWidth: 420, mx: 'auto' }}>

                    <Box sx={{ mb: 5 }}>
                        <Box sx={{
                            width: 56,
                            height: 56,
                            borderRadius: 3,
                            background: 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            mb: 3,
                            boxShadow: '0 10px 25px -5px rgba(30, 58, 138, 0.5)'
                        }}>
                            <LockOutlinedIcon sx={{ color: 'white', fontSize: 28 }} />
                        </Box>
                        <Typography variant="h3" fontWeight={800} sx={{ mb: 1.5, color: 'text.primary' }}>
                            Welcome Back
                        </Typography>
                        <Typography variant="body1" color="text.secondary">
                            Enter your credentials to access the workspace.
                        </Typography>
                    </Box>

                    {error && (
                        <Alert severity="error" variant="filled" sx={{ mb: 3, borderRadius: 2 }}>
                            {error}
                        </Alert>
                    )}

                    <form onSubmit={handleSubmit}>
                        <TextField
                            fullWidth
                            label="Username"
                            variant="outlined"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <PersonOutlineIcon sx={{ color: 'text.secondary' }} />
                                    </InputAdornment>
                                ),
                            }}
                            sx={{
                                mb: 2.5,
                                '& .MuiOutlinedInput-root': {
                                    borderRadius: 3,
                                    bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.03)' : '#f8fafc',
                                    '& fieldset': { borderColor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : '#e2e8f0' },
                                    '&:hover fieldset': { borderColor: '#3b82f6' },
                                    '&.Mui-focused fieldset': { borderColor: '#3b82f6' }
                                }
                            }}
                        />
                        <TextField
                            fullWidth
                            label="Password"
                            type="password"
                            variant="outlined"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <LockOutlinedIcon sx={{ color: 'text.secondary' }} />
                                    </InputAdornment>
                                ),
                            }}
                            sx={{
                                mb: 4,
                                '& .MuiOutlinedInput-root': {
                                    borderRadius: 3,
                                    bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.03)' : '#f8fafc',
                                    '& fieldset': { borderColor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : '#e2e8f0' },
                                    '&:hover fieldset': { borderColor: '#3b82f6' },
                                    '&.Mui-focused fieldset': { borderColor: '#3b82f6' }
                                }
                            }}
                        />

                        <Button
                            fullWidth
                            type="submit"
                            variant="contained"
                            size="large"
                            endIcon={<ArrowForwardIcon />}
                            sx={{
                                py: 1.8,
                                fontSize: '1rem',
                                borderRadius: 3,
                                fontWeight: 700,
                                textTransform: 'none',
                                background: 'linear-gradient(to right, #1e3a8a, #3b82f6)',
                                boxShadow: '0 4px 12px rgba(30, 58, 138, 0.2)',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                    background: 'linear-gradient(to right, #1e40af, #2563eb)',
                                    transform: 'translateY(-2px)',
                                    boxShadow: '0 8px 20px rgba(30, 58, 138, 0.3)'
                                }
                            }}
                        >
                            Sign In to Dashboard
                        </Button>
                    </form>

                    <Box sx={{ mt: 5, textAlign: 'center', pt: 3, borderTop: '1px solid', borderColor: 'divider' }}>
                        <Typography variant="body2" color="text.secondary">
                            Restricted Access only. <br />
                            Contact your administrator for access help.
                        </Typography>
                    </Box>
                </Box>
            </Box>
        </Box>
    );
};

export default Login;
