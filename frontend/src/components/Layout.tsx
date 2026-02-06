import React, { type ReactNode } from 'react';
import { Box, CssBaseline, IconButton, Typography, AppBar, Toolbar, Breadcrumbs, Link } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import Sidebar from './Sidebar';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NotificationsOutlinedIcon from '@mui/icons-material/NotificationsOutlined';
import { useLocation } from 'react-router-dom';

interface LayoutProps {
    children: ReactNode;
}

import { useThemeContext } from '../context/ThemeContext';
import LightModeOutlinedIcon from '@mui/icons-material/LightModeOutlined';
import DarkModeOutlinedIcon from '@mui/icons-material/DarkModeOutlined';

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const [mobileOpen, setMobileOpen] = React.useState(false);
    const location = useLocation();
    const { mode, toggleColorMode } = useThemeContext();

    // Generate breadcrumbs based on path
    const pathnames = location.pathname.split('/').filter((x) => x);

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    return (
        <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
            <CssBaseline />

            {/* Desktop Sidebar */}
            <Box
                component="nav"
                sx={{ width: { md: 280 }, flexShrink: { md: 0 }, display: { xs: 'none', md: 'block' } }}
            >
                <Sidebar />
            </Box>

            {/* Main Content Area */}
            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', width: { md: `calc(100% - 280px)` }, overflowX: 'hidden' }}>

                {/* Header / Topbar */}
                <AppBar
                    position="sticky"
                    color="transparent"
                    elevation={0}
                    sx={{
                        backdropFilter: 'blur(10px)',
                        borderBottom: '1px solid',
                        borderColor: 'divider',
                        bgcolor: mode === 'dark' ? 'rgba(15, 23, 42, 0.7)' : 'rgba(255, 255, 255, 0.7)'
                    }}
                >
                    <Toolbar sx={{ justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <IconButton
                                color="inherit"
                                edge="start"
                                onClick={handleDrawerToggle}
                                sx={{ mr: 2, display: { md: 'none' } }}
                            >
                                <MenuIcon />
                            </IconButton>

                            {/* Breadcrumbs */}
                            <Breadcrumbs
                                separator={<NavigateNextIcon fontSize="small" />}
                                aria-label="breadcrumb"
                                sx={{ display: { xs: 'none', sm: 'flex' } }}
                            >
                                <Link underline="hover" color="inherit" href="/dashboard">
                                    Home
                                </Link>
                                {pathnames.map((value, index) => {
                                    const last = index === pathnames.length - 1;
                                    const to = `/${pathnames.slice(0, index + 1).join('/')}`;

                                    return last ? (
                                        <Typography color="text.primary" key={to} sx={{ textTransform: 'capitalize', fontWeight: 600 }}>
                                            {value}
                                        </Typography>
                                    ) : (
                                        <Link underline="hover" color="inherit" href={to} key={to} sx={{ textTransform: 'capitalize' }}>
                                            {value}
                                        </Link>
                                    );
                                })}
                            </Breadcrumbs>
                        </Box>

                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <IconButton
                                onClick={toggleColorMode}
                                color="inherit"
                                sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}
                            >
                                {mode === 'dark' ? <LightModeOutlinedIcon /> : <DarkModeOutlinedIcon />}
                            </IconButton>
                            <IconButton color="inherit" sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3 }}>
                                <NotificationsOutlinedIcon />
                            </IconButton>
                        </Box>
                    </Toolbar>
                </AppBar>

                {/* Page Content */}
                <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, md: 4 } }}>
                    {children}
                </Box>
            </Box>
        </Box>
    );
};

export default Layout;
