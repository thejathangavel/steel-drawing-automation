import React from 'react';
import { Box, List, ListItemButton, ListItemIcon, ListItemText, Typography, Avatar, alpha } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import FolderIcon from '@mui/icons-material/Folder';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Sidebar: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { logout, user } = useAuth() as { logout: () => void, user: { username: string } | null };

    const menuItems = [
        { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
        { text: 'Projects', icon: <FolderIcon />, path: '/projects' },
        { text: 'Reports', icon: <AssessmentIcon />, path: '/reports' },
        { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
    ];

    return (
        <Box
            sx={{
                width: 280,
                height: '100vh',
                bgcolor: 'background.paper',
                borderRight: '1px solid',
                borderColor: 'divider',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '4px 0 24px rgba(0,0,0,0.02)',
                zIndex: 1200,
                position: 'relative'
            }}
        >
            {/* Logo Area */}
            <Box sx={{ p: 3, pt: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box
                    sx={{
                        width: 42,
                        height: 42,
                        background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                        borderRadius: "12px",
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: '0 8px 16px -4px rgba(37, 99, 235, 0.4)'
                    }}
                >
                    <Typography variant="h6" sx={{ fontWeight: 800, color: 'white' }}>S</Typography>
                </Box>
                <Box>
                    <Typography variant="h6" sx={{ fontWeight: 800, color: 'text.primary', lineHeight: 1 }}>
                        SteelFlow
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 500 }}>
                        Workflow System
                    </Typography>
                </Box>
            </Box>

            <Box sx={{ height: 24 }} /> {/* Spacer */}

            {/* Menu */}
            <List sx={{ px: 2, flexGrow: 1 }}>
                <Typography variant="caption" sx={{
                    px: 2,
                    mb: 1.5,
                    display: 'block',
                    fontWeight: 700,
                    color: 'text.secondary',
                    fontSize: '0.75rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                }}>
                    Main Menu
                </Typography>

                {menuItems.map((item) => {
                    const active = location.pathname === item.path || (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
                    return (
                        <ListItemButton
                            key={item.text}
                            onClick={() => navigate(item.path)}
                            sx={{
                                mb: 0.5,
                                borderRadius: 2,
                                py: 1.5,
                                px: 2.5,
                                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                                bgcolor: active ? alpha('#3b82f6', 0.1) : 'transparent',
                                color: active ? 'primary.main' : 'text.secondary',
                                position: 'relative',
                                overflow: 'hidden',
                                '&:hover': {
                                    bgcolor: active ? alpha('#3b82f6', 0.15) : 'action.hover',
                                    color: active ? 'primary.main' : 'text.primary',
                                    transform: 'translateX(4px)'
                                }
                            }}
                        >
                            {active && (
                                <Box sx={{
                                    position: 'absolute',
                                    left: 0,
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    height: '50%',
                                    width: 4,
                                    bgcolor: 'primary.main',
                                    borderRadius: '0 4px 4px 0',
                                    boxShadow: '0 0 8px rgba(59, 130, 246, 0.5)'
                                }} />
                            )}
                            <ListItemIcon sx={{
                                color: 'inherit',
                                minWidth: 36,
                                '& .MuiSvgIcon-root': { fontSize: '1.4rem' }
                            }}>
                                {item.icon}
                            </ListItemIcon>
                            <ListItemText
                                primary={item.text}
                                primaryTypographyProps={{
                                    fontWeight: active ? 600 : 500,
                                    fontSize: '0.95rem'
                                }}
                            />
                        </ListItemButton>
                    );
                })}
            </List>

            {/* Footer / User Profile */}
            <Box sx={{ p: 2, pb: 4 }}>
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                        p: 1.5,
                        mb: 2,
                        pl: 2
                    }}
                >
                    <Avatar sx={{
                        width: 42,
                        height: 42,
                        bgcolor: 'slate.700',
                        color: 'white',
                        fontSize: '1rem',
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #475569 0%, #64748b 100%)'
                    }}>
                        {user?.username?.[0]?.toUpperCase() || 'U'}
                    </Avatar>
                    <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'text.primary', fontSize: '0.95rem' }} noWrap>
                            {user?.username || 'User'}
                        </Typography>
                        <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', lineHeight: 1.2 }}>
                            Administrator
                        </Typography>
                    </Box>
                </Box>

                <ListItemButton
                    onClick={logout}
                    sx={{
                        borderRadius: 3,
                        color: 'error.main',
                        justifyContent: 'center',
                        border: '1px solid',
                        borderColor: alpha('#ef4444', 0.2),
                        py: 1.2,
                        transition: 'all 0.2s',
                        '&:hover': {
                            bgcolor: alpha('#ef4444', 0.05),
                            borderColor: 'error.main',
                            transform: 'translateY(-2px)'
                        }
                    }}
                >
                    <LogoutIcon fontSize="small" sx={{ mr: 1, fontSize: '1.2rem' }} />
                    <Typography variant="button" sx={{
                        fontSize: '0.9rem',
                        fontWeight: 600,
                        textTransform: 'none'
                    }}>
                        Sign Out
                    </Typography>
                </ListItemButton>
            </Box>
        </Box>
    );
};

export default Sidebar;
