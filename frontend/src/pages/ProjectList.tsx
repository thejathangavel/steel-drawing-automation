import React, { useEffect, useState } from 'react';
import {
    Container, Grid, Card, Typography, Box,
    Button, Chip, Dialog, DialogTitle,
    DialogContent, DialogActions, TextField, Paper, IconButton
} from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import DeleteIcon from '@mui/icons-material/Delete';
import api from '../api/axios';
import { useNavigate } from 'react-router-dom';

const ProjectList: React.FC = () => {
    const navigate = useNavigate();
    const [projects, setProjects] = useState<any[]>([]);

    // Create Project Dialog State
    const [openNewProjectDialog, setOpenNewProjectDialog] = useState(false);
    const [newProjectTitle, setNewProjectTitle] = useState('');
    const [newClientName, setNewClientName] = useState('');

    // Delete Dialog State
    const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
    const [projectToDelete, setProjectToDelete] = useState<any>(null);

    const fetchProjects = async () => {
        try {
            const res = await api.get('/projects/');
            setProjects(res.data);
        } catch (err) {
            console.error("Failed to fetch projects", err);
        }
    };

    useEffect(() => {
        fetchProjects();
    }, []);

    const handleCreateProject = async () => {
        if (!newProjectTitle || !newClientName) return;
        try {
            await api.post('/projects/', {
                title: newProjectTitle,
                client_name: newClientName
            });
            await fetchProjects();
            setOpenNewProjectDialog(false);
            setNewProjectTitle('');
            setNewClientName('');
        } catch (err: any) {
            console.error("Failed to create project", err);
            alert("Failed to create project: " + (err.response?.data?.detail || err.message));
        }
    };

    const handleDeleteProject = (e: React.MouseEvent, project: any) => {
        e.stopPropagation();
        setProjectToDelete(project);
        setOpenDeleteDialog(true);
    };

    const confirmDeleteProject = async () => {
        if (!projectToDelete) return;
        try {
            await api.delete(`/projects/${projectToDelete.id}`);
            setOpenDeleteDialog(false);
            setProjectToDelete(null);
            await fetchProjects();
        } catch (err: any) {
            console.error("Failed to delete project", err);
            alert("Failed to delete project: " + (err.response?.data?.detail || err.message));
        }
    };

    return (
        <Container maxWidth="xl" className="fade-in" sx={{ mt: 4, mb: 4 }}>
            {/* Header */}
            <Box sx={{ mb: 5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                    <Typography variant="overline" sx={{ color: 'primary.main', fontWeight: 700, letterSpacing: '0.1em' }}>
                        PROJECTS
                    </Typography>
                    <Typography
                        variant="h3"
                        sx={{
                            fontWeight: 800,
                            mt: 1,
                            background: (theme) => theme.palette.mode === 'dark'
                                ? 'linear-gradient(to right, #fff, #94a3b8)'
                                : 'linear-gradient(to right, #1e293b, #3b82f6)',
                            backgroundClip: 'text',
                            textFillColor: 'transparent',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent'
                        }}
                    >
                        My Projects
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mt: 1, maxWidth: 600 }}>
                        Manage and track all your steel detailing projects in one place.
                    </Typography>
                </Box>
                <Button
                    variant="contained"
                    startIcon={<AddCircleOutlineIcon />}
                    size="large"
                    onClick={() => setOpenNewProjectDialog(true)}
                    sx={{
                        px: 4,
                        py: 1.5,
                        borderRadius: 3,
                        fontWeight: 700,
                        textTransform: 'none',
                        fontSize: '1rem',
                        background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                        boxShadow: '0 8px 20px -4px rgba(59, 130, 246, 0.5)',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 12px 24px -4px rgba(59, 130, 246, 0.6)',
                        }
                    }}
                >
                    Create Project
                </Button>
            </Box>

            {/* Projects Grid */}
            <Grid container spacing={4}>
                {projects.length > 0 ? (
                    projects.map((project) => (
                        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={project.id}>
                            <Card
                                sx={{
                                    height: '100%',
                                    borderRadius: 5,
                                    border: '1px solid',
                                    borderColor: 'divider',
                                    bgcolor: 'background.paper',
                                    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                                    cursor: 'pointer',
                                    position: 'relative',
                                    overflow: 'hidden',
                                    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)',
                                    '&:hover': {
                                        transform: 'translateY(-8px)',
                                        boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)',
                                        borderColor: 'primary.main',
                                        '& .icon-box': {
                                            transform: 'scale(1.1) rotate(5deg)',
                                            bgcolor: 'primary.main',
                                            color: '#fff'
                                        }
                                    }
                                }}
                                onClick={() => navigate(`/projects/${project.id}`)}
                            >
                                {/* Top gradient accent */}
                                <Box sx={{ height: 6, background: 'linear-gradient(to right, #3b82f6, #60a5fa)' }} />

                                <Box sx={{
                                    p: 3,
                                    display: 'flex',
                                    flexDirection: 'column',
                                    height: 'calc(100% - 6px)'
                                }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
                                        <Box
                                            className="icon-box"
                                            sx={{
                                                width: 56,
                                                height: 56,
                                                borderRadius: '50%',
                                                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(59, 130, 246, 0.2)' : '#eff6ff',
                                                color: 'primary.main',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                transition: 'all 0.4s ease',
                                                boxShadow: 'inset 0 2px 4px 0 rgba(0,0,0,0.06)'
                                            }}
                                        >
                                            <FolderIcon sx={{ fontSize: 28 }} />
                                        </Box>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Chip
                                                label="Active"
                                                size="small"
                                                sx={{
                                                    height: 24,
                                                    fontWeight: 600,
                                                    bgcolor: 'rgba(16, 185, 129, 0.1)',
                                                    color: '#059669'
                                                }}
                                            />
                                            <IconButton
                                                onClick={(e) => handleDeleteProject(e, project)}
                                                size="small"
                                                sx={{
                                                    color: 'text.secondary',
                                                    '&:hover': {
                                                        color: 'error.main',
                                                        bgcolor: 'rgba(239, 68, 68, 0.1)'
                                                    }
                                                }}
                                            >
                                                <DeleteIcon fontSize="small" />
                                            </IconButton>
                                        </Box>
                                    </Box>

                                    <Box sx={{ mb: 3 }}>
                                        <Typography variant="h5" fontWeight={700} sx={{ mb: 0.5, lineHeight: 1.2 }}>
                                            {project.title}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary" fontWeight={500}>
                                            {project.client_name}
                                        </Typography>
                                    </Box>

                                    <Box sx={{ mt: 'auto', pt: 2, borderTop: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Typography variant="body2" fontWeight={600} color="text.primary">
                                                {project.drawings ? project.drawings.length : 0}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                Drawings
                                            </Typography>
                                        </Box>

                                        <IconButton
                                            size="small"
                                            sx={{
                                                color: 'primary.main',
                                                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(59, 130, 246, 0.1)' : '#eff6ff',
                                                '&:hover': { bgcolor: 'primary.main', color: '#fff' }
                                            }}
                                        >
                                            <ArrowForwardIcon fontSize="small" />
                                        </IconButton>
                                    </Box>
                                </Box>
                            </Card>
                        </Grid>
                    ))
                ) : (
                    <Grid size={{ xs: 12 }}>
                        <Paper sx={{
                            p: 8,
                            textAlign: 'center',
                            borderRadius: 6,
                            border: '2px dashed',
                            borderColor: 'divider',
                            bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.02)' : '#f8fafc',
                            transition: 'all 0.3s',
                            '&:hover': { borderColor: 'primary.light', bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.04)' : '#f1f5f9' }
                        }}>
                            <Box sx={{
                                width: 80, height: 80, borderRadius: '50%', bgcolor: 'background.paper',
                                display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 3,
                                boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
                            }}>
                                <FolderIcon sx={{ fontSize: 40, color: 'text.secondary', opacity: 0.5 }} />
                            </Box>
                            <Typography variant="h5" fontWeight={700} gutterBottom>No projects yet</Typography>
                            <Typography color="text.secondary" sx={{ mb: 3, maxWidth: 400, mx: 'auto' }}>
                                Start by creating your first project to manage drawings, fabrication logs, and approvals efficiently.
                            </Typography>
                            <Button
                                variant="outlined"
                                onClick={() => setOpenNewProjectDialog(true)}
                                sx={{ borderRadius: 3, textTransform: 'none', fontWeight: 600 }}
                            >
                                Create New Project
                            </Button>
                        </Paper>
                    </Grid>
                )}
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

            {/* Delete Confirmation Dialog */}
            <Dialog
                open={openDeleteDialog}
                onClose={() => setOpenDeleteDialog(false)}
                PaperProps={{ sx: { borderRadius: 3, minWidth: 350 } }}
            >
                <DialogTitle sx={{ fontWeight: 700 }}>Delete Project?</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete <b>{projectToDelete?.title}</b>?
                        <br />
                        This action cannot be undone and will remove all associated drawings.
                    </Typography>
                </DialogContent>
                <DialogActions sx={{ p: 2 }}>
                    <Button onClick={() => setOpenDeleteDialog(false)} color="inherit">Cancel</Button>
                    <Button onClick={confirmDeleteProject} color="error" variant="contained" autoFocus>
                        Delete
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default ProjectList;
