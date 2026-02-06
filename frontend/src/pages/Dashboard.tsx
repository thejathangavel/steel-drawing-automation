import React, { useEffect, useState } from 'react';
import {
    Container, Grid, Card, CardContent, Typography, Box, Paper,
    Button, Select, MenuItem, InputLabel, FormControl, Table, TableBody,
    TableCell, TableContainer, TableHead, TableRow, Chip, Avatar, IconButton, Divider, alpha,
    Dialog, DialogTitle, DialogContent, DialogActions, TextField
} from '@mui/material';
import {
    ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import AssessmentIcon from '@mui/icons-material/Assessment';
import DownloadIcon from '@mui/icons-material/Download';
import HistoryIcon from '@mui/icons-material/History';
import api from '../api/axios';
import { useNavigate } from 'react-router-dom';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import DeleteIcon from '@mui/icons-material/Delete';

// Types
interface Stats {
    totalProjects: number;
    totalDrawings: number;
    revisedDrawings: number;
    errors: number;
}

interface Activity {
    id: number | string;
    message: string;
    time: string;
    type: 'upload' | 'revision' | 'warning' | 'info';
}

import { useAuth } from '../context/AuthContext';

const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const { user } = useAuth() as any;

    // State
    const [projects, setProjects] = useState<any[]>([]);
    const [selectedProjectId, setSelectedProjectId] = useState<string | number>('');
    const [globalStats, setGlobalStats] = useState<Stats>({
        totalProjects: 0,
        totalDrawings: 0,
        revisedDrawings: 0,
        errors: 0
    });
    // Removed setter to fix lint error
    // Removed hardcoded recentActivity state


    // Create Project Dialog State
    const [openNewProjectDialog, setOpenNewProjectDialog] = useState(false);
    const [newProjectTitle, setNewProjectTitle] = useState('');
    const [newClientName, setNewClientName] = useState('');

    // Drawing Log Dialog State
    const [openDrawingLogDialog, setOpenDrawingLogDialog] = useState(false);

    // Derived State for Active Project
    const selectedProject = projects.find(p => p.id === selectedProjectId) || null;

    // Derived Data
    const drawingStats = React.useMemo(() => {
        if (!selectedProject?.drawings) return [];
        const stats = {
            SHOP: { total: 0, approved: 0, pending: 0 },
            PART: { total: 0, approved: 0, pending: 0 },
            ERECTION: { total: 0, approved: 0, pending: 0 }
        };

        selectedProject.drawings.forEach((d: any) => {
            // Normalize type check
            const type = (d.drawing_type || 'UNKNOWN').toUpperCase();
            if (stats[type as keyof typeof stats]) {
                const key = type as keyof typeof stats;
                stats[key].total++;
                if (d.status === 'Approved') stats[key].approved++;
                else stats[key].pending++;
            }
        });

        return Object.entries(stats).map(([type, data]) => ({
            type: type.charAt(0) + type.slice(1).toLowerCase() + ' Drawings',
            ...data,
            completion: data.total > 0 ? Math.round((data.approved / data.total) * 100) : 0
        }));
    }, [selectedProject]);

    const drawingTypeData = React.useMemo(() => {
        if (!selectedProject?.drawings) return [];
        return [
            { name: 'Shop', value: selectedProject.drawings.filter((d: any) => d.drawing_type === 'SHOP').length },
            { name: 'Part', value: selectedProject.drawings.filter((d: any) => d.drawing_type === 'PART').length },
            { name: 'Erection', value: selectedProject.drawings.filter((d: any) => d.drawing_type === 'ERECTION').length },
        ].filter(d => d.value > 0);
    }, [selectedProject]);

    const recentActivity = React.useMemo<Activity[]>(() => {
        if (!selectedProject) return [];

        const finalActs: Activity[] = [];

        const formatActivityTime = (dateStr: string) => {
            if (!dateStr) return 'Unknown date';
            // Backend stores generic UTC (datetime.utcnow) which often returns ISO string without 'Z'
            // We must treat it as UTC to get correct local conversion.
            const utcDateStr = dateStr.endsWith('Z') ? dateStr : `${dateStr}Z`;

            return new Date(utcDateStr).toLocaleString('en-US', {
                year: 'numeric',
                month: 'numeric',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        };

        // A. Add Drawings (Newest First)
        if (selectedProject.drawings) {
            // Sort by created_at descending
            const sorted = [...selectedProject.drawings].sort((a: any, b: any) => {
                const dateA = a.created_at ? (a.created_at.endsWith('Z') ? a.created_at : `${a.created_at}Z`) : 0;
                const dateB = b.created_at ? (b.created_at.endsWith('Z') ? b.created_at : `${b.created_at}Z`) : 0;
                return new Date(dateB).getTime() - new Date(dateA).getTime();
            }).slice(0, 5);

            sorted.forEach(d => {
                finalActs.push({
                    id: `dwg-${d.id || d.drawing_no}`,
                    message: `Uploaded Drawing ${d.drawing_no}`,
                    time: formatActivityTime(d.created_at),
                    type: 'upload'
                });
            });
        }

        // B. Add Project Creation
        if (selectedProject.created_at) {
            finalActs.push({
                id: 'create',
                message: `Project Created`,
                time: formatActivityTime(selectedProject.created_at),
                type: 'info'
            });
        }

        return finalActs;
    }, [selectedProject]);

    const COLORS = ['#3b82f6', '#10b981', '#f59e0b'];

    useEffect(() => {
        fetchProjects();
    }, []);

    const fetchProjects = async () => {
        try {
            const res = await api.get('/projects/');
            const projs = res.data;
            setProjects(projs);

            if (projs.length > 0 && !selectedProjectId) {
                setSelectedProjectId(projs[0].id);
            }

            // Calculate Global Stats
            let dwgCount = 0;
            // Mocking revised/error stats for now as backend might not return them yet
            projs.forEach((p: any) => {
                dwgCount += (p.drawings ? p.drawings.length : 0);
            });

            setGlobalStats({
                totalProjects: projs.length,
                totalDrawings: dwgCount,
                revisedDrawings: Math.floor(dwgCount * 0.1), // Mock 10%
                errors: Math.floor(dwgCount * 0.05) // Mock 5%
            });

        } catch (err) {
            console.error("Failed to fetch projects", err);
        }
    };

    const handleProjectChange = (event: any) => {
        setSelectedProjectId(event.target.value);
    };

    const handleCreateProject = async () => {
        if (!newProjectTitle || !newClientName) return;
        try {
            const res = await api.post('/projects/', {
                title: newProjectTitle,
                client_name: newClientName
            });
            await fetchProjects();
            setOpenNewProjectDialog(false);
            setNewProjectTitle('');
            setNewClientName('');
            // Optionally select the new project
            if (res.data && res.data.id) {
                setSelectedProjectId(res.data.id);
            }
        } catch (err: any) {
            console.error("Failed to create project", err);
            const status = err.response?.status || "Unknown";
            const detail = err.response?.data?.detail || err.message;
            const url = err.config?.baseURL + err.config?.url;
            alert(`Failed: ${detail}\nStatus: ${status}\nURL: ${url}`);
        }
    };

    // Delete Project Logic
    const [openDeleteConfirm, setOpenDeleteConfirm] = useState(false);

    const handleDeleteProject = async () => {
        if (!selectedProjectId) return;
        try {
            await api.delete(`/projects/${selectedProjectId}`);
            setOpenDeleteConfirm(false);
            setSelectedProjectId(''); // Reset selection
            await fetchProjects(); // Refresh list
        } catch (err: any) {
            console.error("Failed to delete project", err);
            alert("Failed to delete project: " + (err.response?.data?.detail || err.message));
        }
    };

    // --- Sub-components (Redesigned) ---

    const StatCard = ({ title, value, icon, color, subtext }: any) => (
        <Card sx={{
            height: '100%',
            position: 'relative',
            overflow: 'hidden',
            borderRadius: 4,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            border: '1px solid',
            borderColor: alpha(color, 0.1),
            background: `linear-gradient(135deg, ${alpha(color, 0.05)} 0%, ${alpha(color, 0.01)} 100%)`,
            '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: `0 12px 24px -10px ${alpha(color, 0.3)}`,
                borderColor: alpha(color, 0.3),
            }
        }}>
            <Box sx={{
                position: 'absolute',
                top: -40,
                right: -40,
                width: 150,
                height: 150,
                background: `radial-gradient(circle, ${alpha(color, 0.2)} 0%, transparent 70%)`,
                filter: 'blur(30px)',
                borderRadius: '50%'
            }} />
            <CardContent sx={{ p: 4, display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
                    <Box sx={{
                        p: 2,
                        borderRadius: "16px",
                        background: `linear-gradient(135deg, ${color} 0%, ${alpha(color, 0.8)} 100%)`,
                        color: '#fff',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: `0 8px 16px -4px ${alpha(color, 0.4)}`
                    }}>
                        {icon}
                    </Box>
                    {subtext && <Chip label={subtext} size="small" sx={{
                        bgcolor: alpha(color, 0.1),
                        color: color,
                        fontWeight: 700,
                        border: 'none'
                    }} />}
                </Box>
                <Box>
                    <Typography variant="h2" fontWeight={800} sx={{
                        mb: 0.5,
                        letterSpacing: '-0.03em',
                        color: 'text.primary' // Ensure good contrast
                    }}>
                        {value}
                    </Typography>
                    <Typography variant="body1" color="text.secondary" fontWeight={600} sx={{ letterSpacing: '0.02em' }}>
                        {title}
                    </Typography>
                </Box>
            </CardContent>
        </Card>
    );

    const QuickActionButton = ({ icon, label, onClick, color = 'primary' }: any) => {
        const themeColor = color === 'primary' ? '#3b82f6' : '#10b981';
        return (
            <Button
                onClick={onClick}
                sx={{
                    p: 3,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2,
                    height: '100%',
                    width: '100%',
                    justifyContent: 'center',
                    textAlign: 'center',
                    borderRadius: 4,
                    bgcolor: 'background.paper',
                    border: '1px solid',
                    borderColor: 'divider',
                    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.02)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: `0 12px 20px -8px ${alpha(themeColor, 0.2)}`,
                        borderColor: alpha(themeColor, 0.3),
                        '& .icon-box': {
                            transform: 'scale(1.1)',
                            bgcolor: themeColor,
                            color: 'white'
                        }
                    }
                }}
            >
                <Box className="icon-box" sx={{
                    color: themeColor,
                    p: 2,
                    borderRadius: "50%",
                    bgcolor: alpha(themeColor, 0.1),
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    {icon}
                </Box>
                <Typography variant="body2" fontWeight={700} color="text.primary">{label}</Typography>
            </Button>
        );
    };

    return (
        <Container maxWidth="xl" className="fade-in" sx={{ pb: 6, pt: 2 }}>

            {/* 1. Page Header */}
            <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <Box>
                    <Typography variant="caption" sx={{
                        display: 'block',
                        mb: 1,
                        color: 'primary.main',
                        fontWeight: 700,
                        letterSpacing: '0.05em',
                        textTransform: 'uppercase'
                    }}>
                        Home &gt; Dashboard
                    </Typography>
                    <Typography variant="h3" fontWeight={800} sx={{
                        letterSpacing: '-0.03em',
                        color: 'text.primary'
                    }}>
                        Dashboard Overview
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mt: 1, fontWeight: 500 }}>
                        Welcome back, {user?.username}! Here's what's happening today.
                    </Typography>
                </Box>
                <Box>
                    <Button
                        variant="contained"
                        startIcon={<AddCircleOutlineIcon />}
                        size="large"
                        onClick={() => setOpenNewProjectDialog(true)}
                        sx={{
                            borderRadius: 3,
                            px: 4,
                            py: 1.5,
                            fontWeight: 700,
                            textTransform: 'none',
                            fontSize: '1rem',
                            background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                            boxShadow: '0 8px 16px -4px rgba(37, 99, 235, 0.5)',
                            transition: 'all 0.3s ease',
                            '&:hover': {
                                transform: 'translateY(-2px)',
                                boxShadow: '0 12px 20px -4px rgba(37, 99, 235, 0.6)',
                            }
                        }}
                    >
                        New Project
                    </Button>
                </Box>
            </Box>

            {/* 2. Global Summary Stats */}
            <Box sx={{ mb: 6 }}>
                <Grid container spacing={3}>
                    <Grid size={{ xs: 12, sm: 6 }}>
                        <StatCard
                            title="Total Projects"
                            value={globalStats.totalProjects}
                            icon={<FolderIcon fontSize="large" />}
                            color="#3b82f6"
                        />
                    </Grid>
                    <Grid size={{ xs: 12, sm: 6 }}>
                        <StatCard
                            title="Total Drawings"
                            value={globalStats.totalDrawings}
                            icon={<DescriptionIcon fontSize="large" />}
                            color="#10b981"
                        />
                    </Grid>
                </Grid>
            </Box>

            <Grid container spacing={4}>

                {/* 3. Main Column: Active Project & Actions */}
                <Grid size={{ xs: 12, lg: 8 }}>

                    {/* Project Overview Card */}
                    <Paper sx={{
                        mb: 4,
                        overflow: 'hidden',
                        borderRadius: 4,
                        boxShadow: '0 4px 24px rgba(0,0,0,0.03)',
                        border: '1px solid',
                        borderColor: 'divider'
                    }}>
                        <Box sx={{
                            p: 3,
                            borderBottom: '1px solid',
                            borderColor: 'divider',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            bgcolor: 'action.hover'
                        }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Box sx={{
                                    p: 1,
                                    borderRadius: 2,
                                    bgcolor: 'primary.main',
                                    color: 'white',
                                    display: 'flex'
                                }}>
                                    <FolderIcon fontSize="small" />
                                </Box>
                                <Typography variant="h6" fontWeight={700}>Active Project</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <FormControl size="small" sx={{ minWidth: 240 }}>
                                    <InputLabel>Select Project</InputLabel>
                                    <Select
                                        value={selectedProjectId}
                                        label="Select Project"
                                        onChange={handleProjectChange}
                                        sx={{ borderRadius: 2, bgcolor: 'background.paper' }}
                                    >
                                        {projects.map((p) => (
                                            <MenuItem key={p.id} value={p.id}>{p.title}</MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                                <IconButton
                                    onClick={() => setOpenDeleteConfirm(true)}
                                    disabled={!selectedProjectId}
                                    color="error"
                                    sx={{
                                        bgcolor: alpha('#ef4444', 0.1),
                                        borderRadius: 2,
                                        '&:hover': { bgcolor: alpha('#ef4444', 0.2) }
                                    }}
                                >
                                    <DeleteIcon />
                                </IconButton>
                            </Box>
                        </Box>

                        {/* Delete Confirmation Dialog */}
                        <Dialog open={openDeleteConfirm} onClose={() => setOpenDeleteConfirm(false)}>
                            <DialogTitle>Delete Project?</DialogTitle>
                            <DialogContent>
                                <Typography>
                                    Are you sure you want to delete <b>{selectedProject?.title}</b>?
                                    This action cannot be undone.
                                </Typography>
                            </DialogContent>
                            <DialogActions sx={{ p: 2 }}>
                                <Button onClick={() => setOpenDeleteConfirm(false)}>Cancel</Button>
                                <Button onClick={handleDeleteProject} color="error" variant="contained">Delete</Button>
                            </DialogActions>
                        </Dialog>

                        {selectedProject ? (
                            <Box sx={{ p: 4, pt: 5 }}>
                                <Grid container spacing={4}>
                                    <Grid size={{ xs: 12, md: 7 }}>
                                        <Box sx={{ mb: 5 }}>
                                            <Typography variant="overline" color="text.secondary" fontWeight={700} letterSpacing="0.05em">
                                                PROJECT TITLE
                                            </Typography>
                                            <Typography variant="h3" fontWeight={800} sx={{
                                                mb: 2,
                                                color: 'text.primary',
                                                lineHeight: 1.1
                                            }}>
                                                {selectedProject.title}
                                            </Typography>

                                            <Box sx={{ display: 'flex', gap: 4, mt: 3 }}>
                                                <Box>
                                                    <Typography variant="caption" color="text.secondary" fontWeight={600} display="block" sx={{ mb: 0.5 }}>CLIENT</Typography>
                                                    <Typography variant="subtitle1" fontWeight={700}>{selectedProject.client_name || 'ACME Corp'}</Typography>
                                                </Box>
                                                <Box>
                                                    <Typography variant="caption" color="text.secondary" fontWeight={600} display="block" sx={{ mb: 0.5 }}>LAST UPDATED</Typography>
                                                    <Typography variant="subtitle1" fontWeight={700}>{new Date(selectedProject.created_at).toLocaleDateString()}</Typography>
                                                </Box>
                                                <Box>
                                                    <Typography variant="caption" color="text.secondary" fontWeight={600} display="block" sx={{ mb: 0.5 }}>STATUS</Typography>
                                                    <Chip
                                                        label="Active"
                                                        color="success"
                                                        size="small"
                                                        sx={{
                                                            fontWeight: 700,
                                                            bgcolor: alpha('#10b981', 0.1),
                                                            color: '#059669',
                                                            borderRadius: 1
                                                        }}
                                                    />
                                                </Box>
                                            </Box>
                                        </Box>

                                        <Box sx={{
                                            p: 3,
                                            borderRadius: 3,
                                            bgcolor: alpha('#3b82f6', 0.04),
                                            border: '1px solid',
                                            borderColor: alpha('#3b82f6', 0.1)
                                        }}>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                                                <Typography variant="subtitle2" fontWeight={700} color="primary.main">Extraction Progress</Typography>
                                                <Typography variant="subtitle2" fontWeight={700} color="primary.main">
                                                    {(selectedProject.drawings?.length || 0) > 0 ? '100%' : '0%'}
                                                </Typography>
                                            </Box>
                                            <Box sx={{ width: '100%', height: 10, bgcolor: 'rgba(59, 130, 246, 0.1)', borderRadius: 5, overflow: 'hidden' }}>
                                                <Box sx={{
                                                    width: (selectedProject.drawings?.length || 0) > 0 ? '100%' : '0%',
                                                    height: '100%',
                                                    background: 'linear-gradient(90deg, #3b82f6 0%, #2563eb 100%)',
                                                    borderRadius: 5,
                                                    transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
                                                    boxShadow: '0 0 12px rgba(59, 130, 246, 0.5)'
                                                }} />
                                            </Box>
                                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.5, fontWeight: 500 }}>
                                                {selectedProject.drawings ? selectedProject.drawings.length : 0} drawings processed and ready for review.
                                            </Typography>
                                        </Box>
                                    </Grid>
                                    <Grid size={{ xs: 12, md: 5 }} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <Box sx={{ position: 'relative', width: 220, height: 220 }}>
                                            <ResponsiveContainer width="100%" height="100%">
                                                <PieChart>
                                                    <Pie
                                                        data={drawingTypeData}
                                                        cx="50%"
                                                        cy="50%"
                                                        innerRadius={70}
                                                        outerRadius={90}
                                                        paddingAngle={4}
                                                        dataKey="value"
                                                        cornerRadius={4}
                                                    >
                                                        {drawingTypeData.map((_, index) => (
                                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} strokeWidth={0} />
                                                        ))}
                                                    </Pie>
                                                </PieChart>
                                            </ResponsiveContainer>
                                            <Box sx={{
                                                position: 'absolute',
                                                top: '50%',
                                                left: '50%',
                                                transform: 'translate(-50%, -50%)',
                                                textAlign: 'center',
                                                display: 'flex',
                                                flexDirection: 'column',
                                                alignItems: 'center'
                                            }}>
                                                <Typography variant="h3" fontWeight={800} color="text.primary" sx={{ lineHeight: 1 }}>
                                                    {selectedProject.drawings ? selectedProject.drawings.length : 0}
                                                </Typography>
                                                <Typography variant="caption" fontWeight={600} color="text.secondary" sx={{ textTransform: 'uppercase', fontSize: '0.7rem', mt: 0.5 }}>
                                                    Drawings
                                                </Typography>
                                            </Box>
                                        </Box>
                                    </Grid>
                                </Grid>
                            </Box>
                        ) : (
                            <Box sx={{ p: 10, textAlign: 'center', opacity: 0.5 }}>
                                <FolderIcon sx={{ fontSize: 64, mb: 2, color: 'text.disabled' }} />
                                <Typography variant="h6" color="text.secondary">Select a project to view details</Typography>
                            </Box>
                        )}
                    </Paper>

                    {/* Quick Actions Grid */}
                    <Box sx={{ mb: 4 }}>
                        <Typography variant="h6" fontWeight={700} sx={{ mb: 2.5, px: 1 }}>Quick Actions</Typography>
                        <Grid container spacing={2}>
                            <Grid size={{ xs: 6, sm: 3 }}>
                                <QuickActionButton
                                    icon={<AddCircleOutlineIcon fontSize="medium" />}
                                    label="New Project"
                                    onClick={() => setOpenNewProjectDialog(true)}
                                />
                            </Grid>
                            <Grid size={{ xs: 6, sm: 3 }}>
                                <QuickActionButton
                                    icon={<UploadFileIcon fontSize="medium" />}
                                    label="Upload Folder"
                                    onClick={() => selectedProject && navigate(`/projects/${selectedProjectId}`)}
                                />
                            </Grid>
                            <Grid size={{ xs: 6, sm: 3 }}>
                                <QuickActionButton
                                    icon={<AssessmentIcon fontSize="medium" />}
                                    label="Drawing Log"
                                    onClick={() => selectedProject && navigate(`/projects/${selectedProjectId}`)}
                                />
                            </Grid>
                            <Grid size={{ xs: 6, sm: 3 }}>
                                <QuickActionButton
                                    icon={<DownloadIcon fontSize="medium" />}
                                    label="Transmittal"
                                    onClick={() => { }}
                                    color="success"
                                />
                            </Grid>
                        </Grid>
                    </Box>

                    {/* Drawing Stats Table */}
                    <Paper sx={{ overflow: 'hidden', borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.02)', border: '1px solid', borderColor: 'divider' }}>
                        <Box sx={{ p: 2.5, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'space-between', bgcolor: 'action.hover' }}>
                            <Typography variant="subtitle1" fontWeight={700} fontSize="1rem">Drawing Status Breakdown</Typography>
                            <IconButton size="small"><MoreVertIcon fontSize="small" /></IconButton>
                        </Box>
                        <TableContainer>
                            <Table>
                                <TableHead sx={{ bgcolor: 'action.hover' }}>
                                    <TableRow>
                                        <TableCell sx={{ fontWeight: 700, fontSize: '0.8rem', color: 'text.secondary' }}>TYPE</TableCell>
                                        <TableCell align="right" sx={{ fontWeight: 700, fontSize: '0.8rem', color: 'text.secondary' }}>TOTAL</TableCell>
                                        <TableCell align="right" sx={{ fontWeight: 700, fontSize: '0.8rem', color: 'text.secondary' }}>APPROVED</TableCell>
                                        <TableCell align="right" sx={{ fontWeight: 700, fontSize: '0.8rem', color: 'text.secondary' }}>PENDING</TableCell>
                                        <TableCell align="right" sx={{ fontWeight: 700, fontSize: '0.8rem', color: 'text.secondary' }}>COMPLETION</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {drawingStats.length > 0 ? drawingStats.map((row) => (
                                        <TableRow hover key={row.type}>
                                            <TableCell sx={{ fontWeight: 600, color: 'text.primary' }}>{row.type}</TableCell>
                                            <TableCell align="right" sx={{ fontWeight: 600 }}>{row.total}</TableCell>
                                            <TableCell align="right" sx={{ color: 'success.main', fontWeight: 600 }}>{row.approved}</TableCell>
                                            <TableCell align="right" sx={{ color: 'warning.main', fontWeight: 600 }}>{row.pending}</TableCell>
                                            <TableCell align="right">
                                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 1 }}>
                                                    <Box sx={{ width: 60, height: 6, bgcolor: 'divider', borderRadius: 3, overflow: 'hidden' }}>
                                                        <Box sx={{
                                                            width: `${row.completion}%`,
                                                            height: '100%',
                                                            bgcolor: row.completion === 100 ? 'success.main' : 'primary.main'
                                                        }} />
                                                    </Box>
                                                    <Typography variant="caption" fontWeight={600}>{row.completion}%</Typography>
                                                </Box>
                                            </TableCell>
                                        </TableRow>
                                    )) : (
                                        <TableRow>
                                            <TableCell colSpan={5} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                                                No drawings found. Upload a folder to see stats.
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>

                </Grid>

                {/* 4. Right Column: Activity & Logs */}
                <Grid size={{ xs: 12, lg: 4 }}>

                    {/* Recent Activity Panel */}
                    <Paper sx={{
                        p: 0,
                        height: '100%',
                        borderRadius: 4,
                        boxShadow: '0 4px 24px rgba(0,0,0,0.03)',
                        border: '1px solid',
                        borderColor: 'divider',
                        overflow: 'hidden',
                        display: 'flex',
                        flexDirection: 'column'
                    }}>
                        <Box sx={{
                            p: 3,
                            borderBottom: '1px solid',
                            borderColor: 'divider',
                            bgcolor: 'action.hover'
                        }}>
                            <Typography variant="h6" fontWeight={700}>Recent Activity</Typography>
                        </Box>

                        <Box sx={{ p: 3, flexGrow: 1 }}>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0, position: 'relative' }}>
                                {/* Continuous Timeline Line */}
                                <Box sx={{
                                    position: 'absolute',
                                    left: 17,
                                    top: 10,
                                    bottom: 10,
                                    width: 2,
                                    borderRadius: 1,
                                    background: 'linear-gradient(to bottom, #3b82f6 0%, rgba(59, 130, 246, 0.1) 100%)',
                                    opacity: 0.3
                                }} />

                                {recentActivity.map((activity) => (
                                    <Box key={activity.id} sx={{ display: 'flex', gap: 2.5, position: 'relative', pb: 4, '&:last-child': { pb: 0 } }}>
                                        <Avatar sx={{
                                            width: 36, height: 36,
                                            bgcolor: 'background.paper',
                                            color: activity.type === 'upload' ? 'primary.main' :
                                                activity.type === 'warning' ? 'error.main' :
                                                    'text.secondary',
                                            border: '2px solid',
                                            borderColor: activity.type === 'upload' ? 'primary.main' :
                                                activity.type === 'warning' ? 'error.main' :
                                                    'divider',
                                            boxShadow: (theme) => `0 0 0 4px ${theme.palette.background.paper}`, // Mask the line behind
                                            zIndex: 1,
                                            fontSize: '1rem'
                                        }}>
                                            {activity.type === 'upload' ? <UploadFileIcon fontSize="inherit" /> :
                                                activity.type === 'warning' ? <ErrorOutlineIcon fontSize="inherit" /> :
                                                    <HistoryIcon fontSize="inherit" />}
                                        </Avatar>
                                        <Box sx={{ pt: 0.5 }}>
                                            <Typography variant="body2" fontWeight={600} sx={{ lineHeight: 1.2, mb: 0.5, color: 'text.primary' }}>
                                                {activity.message}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary" fontWeight={500} display="block">
                                                {activity.time}
                                            </Typography>
                                        </Box>
                                    </Box>
                                ))}
                            </Box>
                        </Box>

                        <Divider />

                        <Box sx={{ p: 3, bgcolor: 'action.hover' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                <Typography variant="subtitle2" fontWeight={700}>Drawing Log Preview</Typography>
                                <Button
                                    size="small"
                                    sx={{ fontSize: '0.75rem', fontWeight: 600 }}
                                    onClick={() => setOpenDrawingLogDialog(true)}
                                >
                                    View All
                                </Button>
                            </Box>

                            <Box sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', overflow: 'hidden', bgcolor: 'background.paper' }}>
                                <Table size="small">
                                    <TableHead sx={{ bgcolor: 'action.hover' }}>
                                        <TableRow>
                                            <TableCell sx={{ color: 'text.secondary', fontWeight: 600, fontSize: '0.7rem' }}>DWG NO</TableCell>
                                            <TableCell sx={{ color: 'text.secondary', fontWeight: 600, fontSize: '0.7rem' }}>REV</TableCell>
                                            <TableCell align="right" sx={{ color: 'text.secondary', fontWeight: 600, fontSize: '0.7rem' }}>STATUS</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {selectedProject?.drawings && selectedProject.drawings.length > 0 ? (
                                            [...selectedProject.drawings].reverse().slice(0, 5).map((dwg: any, i: number) => (
                                                <TableRow key={i} hover>
                                                    <TableCell sx={{ fontSize: '0.8rem', fontWeight: 500 }}>{dwg.drawing_no}</TableCell>
                                                    <TableCell sx={{ fontSize: '0.8rem' }}>{dwg.revision_no || '-'}</TableCell>
                                                    <TableCell align="right">
                                                        <Chip
                                                            label={dwg.status || 'Active'}
                                                            size="small"
                                                            sx={{
                                                                height: 20,
                                                                fontSize: '0.65rem',
                                                                fontWeight: 600,
                                                                bgcolor: (dwg.status || '').includes('Fabrication') ? alpha('#ec4899', 0.1) :
                                                                    (dwg.status || '').includes('Approval') ? alpha('#0ea5e9', 0.1) : undefined,
                                                                color: (dwg.status || '').includes('Fabrication') ? '#ec4899' :
                                                                    (dwg.status || '').includes('Approval') ? '#0ea5e9' : undefined,
                                                                border: '1px solid transparent', // alignment
                                                            }}
                                                            color={
                                                                (dwg.status || '').includes('Approved') ? "success" :
                                                                    ((dwg.status || '').includes('Fabrication') || (dwg.status || '').includes('Approval')) ? "default" : "primary"
                                                            }
                                                            variant={(dwg.status || '').includes('Fabrication') || (dwg.status || '').includes('Approval') ? "outlined" : "filled"}
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        ) : (
                                            <TableRow>
                                                <TableCell colSpan={3} align="center" sx={{ fontSize: '0.8rem', color: 'text.secondary', py: 2 }}>
                                                    No recent drawings
                                                </TableCell>
                                            </TableRow>
                                        )}
                                    </TableBody>
                                </Table>
                            </Box>
                        </Box>

                    </Paper>
                </Grid>
            </Grid>

            {/* Create Project Dialog */}
            <Dialog
                open={openNewProjectDialog}
                onClose={() => setOpenNewProjectDialog(false)}
                PaperProps={{
                    sx: {
                        borderRadius: 3,
                        bgcolor: 'background.paper',
                        backgroundImage: 'none',
                        minWidth: 400
                    }
                }}
            >
                <DialogTitle sx={{ pb: 1, fontWeight: 700 }}>Create New Project</DialogTitle>
                <DialogContent>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Enter the details for the new steel project.
                    </Typography>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Project Title"
                        fullWidth
                        variant="outlined"
                        value={newProjectTitle}
                        onChange={(e) => setNewProjectTitle(e.target.value)}
                        sx={{ mb: 2 }}
                    />
                    <TextField
                        margin="dense"
                        label="Client Name"
                        fullWidth
                        variant="outlined"
                        value={newClientName}
                        onChange={(e) => setNewClientName(e.target.value)}
                    />
                </DialogContent>
                <DialogActions sx={{ p: 3, pt: 1 }}>
                    <Button onClick={() => setOpenNewProjectDialog(false)} color="inherit" sx={{ borderRadius: 2 }}>Cancel</Button>
                    <Button
                        onClick={handleCreateProject}
                        variant="contained"
                        disabled={!newProjectTitle || !newClientName}
                        sx={{ borderRadius: 2 }}
                    >
                        Create Project
                    </Button>
                </DialogActions>
            </Dialog>
            {/* Full Drawing Log Dialog */}
            <Dialog
                open={openDrawingLogDialog}
                onClose={() => setOpenDrawingLogDialog(false)}
                maxWidth="lg"
                fullWidth
                PaperProps={{
                    sx: {
                        borderRadius: 3,
                        bgcolor: 'background.paper',
                        backgroundImage: 'none',
                        height: '80vh'
                    }
                }}
            >
                <DialogTitle sx={{ pb: 1, fontWeight: 700, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h6">Full Drawing Log</Typography>
                    <Box>
                        <Chip
                            label={`${selectedProject?.drawings?.length || 0} Drawings`}
                            size="small"
                            color="primary"
                            variant="outlined"
                        />
                        <Button onClick={() => setOpenDrawingLogDialog(false)} sx={{ minWidth: 0, p: 1, ml: 2 }}>Close</Button>
                    </Box>
                </DialogTitle>
                <DialogContent dividers>
                    <TableContainer>
                        <Table stickyHeader size="small">
                            <TableHead>
                                <TableRow>
                                    <TableCell>Drawing No</TableCell>
                                    <TableCell>Rev</TableCell>
                                    <TableCell>Description</TableCell>
                                    <TableCell align="right">Status</TableCell>
                                    <TableCell align="right">Date</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {selectedProject?.drawings && selectedProject.drawings.length > 0 ? (
                                    [...selectedProject.drawings].sort((a: any, b: any) =>
                                        (a.drawing_no || '').localeCompare(b.drawing_no || '', undefined, { numeric: true, sensitivity: 'base' })
                                    ).map((dwg: any, i: number) => (
                                        <TableRow key={i} hover>
                                            <TableCell sx={{ fontWeight: 500 }}>{dwg.drawing_no}</TableCell>
                                            <TableCell>{dwg.revision_no || '-'}</TableCell>
                                            <TableCell sx={{ color: 'text.secondary', maxWidth: 300, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                {dwg.description}
                                            </TableCell>
                                            <TableCell align="right">
                                                <Chip
                                                    label={dwg.status || 'Active'}
                                                    size="small"
                                                    sx={{
                                                        height: 24,
                                                        ...(
                                                            (dwg.status || '').includes('Fabrication') ? {
                                                                bgcolor: 'rgba(236, 72, 153, 0.1)',
                                                                color: '#ec4899',
                                                                borderColor: '#ec4899'
                                                            } :
                                                                (dwg.status || '').includes('Approval') ? {
                                                                    bgcolor: 'rgba(14, 165, 233, 0.1)',
                                                                    color: '#0ea5e9',
                                                                    borderColor: '#0ea5e9'
                                                                } : {}
                                                        )
                                                    }}
                                                    color={
                                                        (dwg.status || '').includes('Approved') ? "success" :
                                                            ((dwg.status || '').includes('Fabrication') || (dwg.status || '').includes('Approval')) ? "default" : "primary"
                                                    }
                                                    variant="outlined"
                                                />
                                            </TableCell>
                                            <TableCell align="right" sx={{ color: 'text.secondary' }}>
                                                {dwg.drawing_date || '-'}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={5} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                                            No drawings found.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </DialogContent>
            </Dialog>
        </Container >
    );
};

export default Dashboard;
