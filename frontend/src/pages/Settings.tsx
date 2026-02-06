import React from 'react';
import {
    Container, Typography, Box, Paper, List, ListItem, ListItemButton,
    ListItemIcon, ListItemText, Divider, Avatar,
    Grid
} from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';
import PersonIcon from '@mui/icons-material/Person';
import PrivacyTipIcon from '@mui/icons-material/PrivacyTip';
import LogoutIcon from '@mui/icons-material/Logout';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import SecurityIcon from '@mui/icons-material/Security';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Settings: React.FC = () => {
    const { logout } = useAuth() as any;
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <Container maxWidth="lg" className="fade-in" sx={{ mt: 6, mb: 10 }}>
            {/* Header */}
            <Box sx={{ mb: 6 }}>
                <Typography variant="overline" sx={{
                    fontWeight: 800,
                    letterSpacing: '0.2em',
                    display: 'block',
                    mb: 1,
                    background: 'linear-gradient(90deg, #3b82f6, #8b5cf6)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    width: 'fit-content'
                }}>
                    CONFIGURATION
                </Typography>
                <Typography variant="h3" fontWeight={900} sx={{
                    mb: 2,
                    background: (theme) => theme.palette.mode === 'dark'
                        ? 'linear-gradient(to right, #fff, #cbd5e1)'
                        : 'linear-gradient(to right, #0f172a, #334155)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    letterSpacing: '-0.03em'
                }}>
                    Settings
                </Typography>
                <Typography variant="h6" color="text.secondary" fontWeight={400} sx={{ maxWidth: 700, lineHeight: 1.6 }}>
                    Manage your account preferences, security settings, and view application details.
                </Typography>
            </Box>

            <Grid container spacing={4}>
                {/* Left Column: Accounts Centre */}
                <Grid size={{ xs: 12, md: 8 }}>
                    <Box sx={{ mb: 2 }}>
                        <Paper
                            elevation={0}
                            sx={{
                                border: '1px solid',
                                borderColor: 'divider',
                                borderRadius: 6,
                                overflow: 'hidden',
                                bgcolor: 'background.paper',
                                boxShadow: '0 10px 40px -10px rgba(0,0,0,0.05)',
                                transition: 'all 0.3s ease'
                            }}
                        >
                            <Box sx={{
                                p: 4,
                                background: (theme) => theme.palette.mode === 'dark'
                                    ? 'linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0) 100%)'
                                    : 'linear-gradient(180deg, #f8fafc 0%, #ffffff 100%)',
                                borderBottom: '1px solid',
                                borderColor: 'divider',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 2
                            }}>
                                <Box sx={{
                                    p: 1.5,
                                    borderRadius: 3,
                                    bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(59, 130, 246, 0.2)' : '#eff6ff',
                                    color: 'primary.main',
                                    display: 'flex'
                                }}>
                                    <SecurityIcon fontSize="medium" />
                                </Box>
                                <Box>
                                    <Typography variant="h6" fontWeight={800} sx={{ lineHeight: 1.2 }}>Accounts Centre</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Control your profile information and security.
                                    </Typography>
                                </Box>
                            </Box>

                            <List disablePadding sx={{ p: 2 }}>
                                <ListItem disablePadding sx={{ mb: 1 }}>
                                    <ListItemButton sx={{
                                        py: 2.5, px: 2, borderRadius: 3, transition: 'all 0.2s',
                                        '&:hover': { bgcolor: 'action.hover', transform: 'translateX(4px)' }
                                    }}>
                                        <ListItemIcon>
                                            <Avatar variant="rounded" sx={{ bgcolor: 'rgba(59, 130, 246, 0.1)', color: 'primary.main', width: 48, height: 48, borderRadius: 3 }}>
                                                <LockIcon />
                                            </Avatar>
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={<Typography variant="subtitle1" fontWeight={700}>Password and Security</Typography>}
                                            secondary={<Typography variant="body2" color="text.secondary">Update password and secure your account</Typography>}
                                        />
                                        <ChevronRightIcon color="action" />
                                    </ListItemButton>
                                </ListItem>

                                <ListItem disablePadding sx={{ mb: 1 }}>
                                    <ListItemButton sx={{
                                        py: 2.5, px: 2, borderRadius: 3, transition: 'all 0.2s',
                                        '&:hover': { bgcolor: 'action.hover', transform: 'translateX(4px)' }
                                    }}>
                                        <ListItemIcon>
                                            <Avatar variant="rounded" sx={{ bgcolor: 'rgba(16, 185, 129, 0.1)', color: 'success.main', width: 48, height: 48, borderRadius: 3 }}>
                                                <PersonIcon />
                                            </Avatar>
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={<Typography variant="subtitle1" fontWeight={700}>Customer Details</Typography>}
                                            secondary={<Typography variant="body2" color="text.secondary">Personal information and contact data</Typography>}
                                        />
                                        <ChevronRightIcon color="action" />
                                    </ListItemButton>
                                </ListItem>

                                <ListItem disablePadding sx={{ mb: 1 }}>
                                    <ListItemButton sx={{
                                        py: 2.5, px: 2, borderRadius: 3, transition: 'all 0.2s',
                                        '&:hover': { bgcolor: 'action.hover', transform: 'translateX(4px)' }
                                    }}>
                                        <ListItemIcon>
                                            <Avatar variant="rounded" sx={{ bgcolor: 'rgba(245, 158, 11, 0.1)', color: 'warning.main', width: 48, height: 48, borderRadius: 3 }}>
                                                <PrivacyTipIcon />
                                            </Avatar>
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={<Typography variant="subtitle1" fontWeight={700}>Account Privacy</Typography>}
                                            secondary={<Typography variant="body2" color="text.secondary">Manage data sharing and visibility</Typography>}
                                        />
                                        <ChevronRightIcon color="action" />
                                    </ListItemButton>
                                </ListItem>

                                <Divider sx={{ my: 1, borderColor: 'divider' }} />

                                <ListItem disablePadding>
                                    <ListItemButton onClick={handleLogout} sx={{
                                        py: 2.5, px: 2, borderRadius: 3, transition: 'all 0.2s',
                                        '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(239, 68, 68, 0.1)' : '#fef2f2', transform: 'translateX(4px)' }
                                    }}>
                                        <ListItemIcon>
                                            <Avatar variant="rounded" sx={{ bgcolor: 'rgba(239, 68, 68, 0.1)', color: 'error.main', width: 48, height: 48, borderRadius: 3 }}>
                                                <LogoutIcon />
                                            </Avatar>
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={<Typography variant="subtitle1" fontWeight={700} color="error.main">Logout</Typography>}
                                            secondary={<Typography variant="body2" color="error.light">Sign out of your session</Typography>}
                                        />
                                        <ChevronRightIcon sx={{ color: 'error.main', opacity: 0.5 }} />
                                    </ListItemButton>
                                </ListItem>
                            </List>
                        </Paper>
                    </Box>

                </Grid>

                {/* Right Column: About SteelFlow */}
                <Grid size={{ xs: 12, md: 4 }}>
                    <Paper
                        elevation={0}
                        sx={{
                            p: 4,
                            borderRadius: 6,
                            color: 'white',
                            position: 'relative',
                            overflow: 'hidden',
                            background: 'linear-gradient(135deg, #0f172a 0%, #334155 100%)',
                            boxShadow: '0 20px 40px -10px rgba(15, 23, 42, 0.3)'
                        }}
                    >
                        {/* Decorative Circle */}
                        <Box sx={{
                            position: 'absolute',
                            top: -20,
                            right: -20,
                            width: 100,
                            height: 100,
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                            opacity: 0.2
                        }} />

                        <Typography variant="overline" sx={{ color: 'primary.light', fontWeight: 600, letterSpacing: '0.1em' }}>
                            SYSTEM
                        </Typography>
                        <Typography variant="h5" fontWeight={800} sx={{ mb: 3 }}>
                            About SteelFlow
                        </Typography>

                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.1)', pb: 1 }}>
                                <Typography variant="body2" sx={{ opacity: 0.7 }}>Version</Typography>
                                <Typography variant="body2" fontWeight={700}>2.4.0</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.1)', pb: 1 }}>
                                <Typography variant="body2" sx={{ opacity: 0.7 }}>Build</Typography>
                                <Typography variant="body2" fontWeight={700}>Stable</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography variant="body2" sx={{ opacity: 0.7 }}>License</Typography>
                                <Typography variant="body2" fontWeight={700}>Enterprise</Typography>
                            </Box>
                        </Box>
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default Settings;
