import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Typography, Button, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Box, CircularProgress, Chip } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import DownloadIcon from '@mui/icons-material/Download';
import FolderIcon from '@mui/icons-material/Folder';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import api from '../api/axios';
import pLimit from 'p-limit';

const ProjectView: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [project, setProject] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);

    const fetchProject = async () => {
        try {
            const res = await api.get(`/projects/${id}`);
            setProject(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchProject();
    }, [id]);





    const processFiles = async (allFiles: File[]) => {
        setLoading(true);
        setUploadProgress(0);

        const BATCH_SIZE = 5; // Reduced from 50 to ensure progress bar moves frequently
        const totalBatches = Math.ceil(allFiles.length / BATCH_SIZE);

        let successCount = 0;
        let failCount = 0;
        let processedBatches = 0;

        const limit = pLimit(3); // Reduced concurrency to prevent network saturation

        const batchPromises = [];

        for (let i = 0; i < totalBatches; i++) {
            const start = i * BATCH_SIZE;
            const end = Math.min(start + BATCH_SIZE, allFiles.length);
            const batch = allFiles.slice(start, end);

            batchPromises.push(limit(async () => {
                const formData = new FormData();
                batch.forEach((file) => {
                    // @ts-ignore
                    const relPath = file.manualPath || file.webkitRelativePath || file.name;
                    formData.append('files', file, relPath);
                });

                try {
                    // No is_last_batch anymore
                    await api.post(`/projects/${id}/upload`, formData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    });
                    successCount += batch.length;
                } catch (err: any) {
                    console.error("Batch upload failed", err);
                    failCount += batch.length;
                }

                processedBatches++;
                const newProgress = Math.round((processedBatches / totalBatches) * 100);
                // Ensure we don't accidentally show >100 or stick at 100 too early if parallel
                setUploadProgress(prev => Math.max(prev, newProgress));
            }));
        }

        try {
            await Promise.all(batchPromises);

            // Final Step: Generate Reports
            try {
                // Determine if we need to call generation (only if there were successes)
                if (successCount > 0) {
                    await api.post(`/projects/${id}/generate_reports`);
                }
                setUploadProgress(100);

                // Show 100% for a moment for better UX
                await new Promise(resolve => setTimeout(resolve, 1000));

            } catch (rErr) {
                console.error("Report generation failed", rErr);
                alert("Upload finished but report generation failed.");
            }

            if (failCount > 0) {
                alert(`Upload complete. ${successCount} files processed. ${failCount} files failed.`);
            }

            await fetchProject();

        } catch (err: any) {
            console.error(err);
            alert("Critical upload error");
        } finally {
            setLoading(false);
            setUploadProgress(0);
        }
    };

    const handleFolderPicker = async () => {
        if (loading) return;

        try {
            // Check for browser support
            if (!('showDirectoryPicker' in window)) {
                alert("Your browser does not support the new folder picker. Please use Chrome, Edge, or Opera.");
                // Fallback could be triggering the hidden input, but for this task we focus on the fix
                return;
            }

            // @ts-ignore - File System Access API types might be missing
            const dirHandle = await window.showDirectoryPicker();

            setLoading(true); // temporary loading state while scanning

            const files: File[] = [];
            // Reset path to empty string for root
            await processDirectoryHandle(dirHandle, files, "");

            setLoading(false);

            if (files.length === 0) {
                alert("No valid files found in the selected folder.");
                return;
            }

            // Custom confirmation dialog with accurate count
            const confirmed = window.confirm(`Found ${files.length} files to upload.\n\nDo you want to proceed?`);

            if (confirmed) {
                // Determine batch size dynamically or use standard
                // If many files, we might want to ensure we don't block UI too much, but processFiles handles batching
                await processFiles(files);
            }

        } catch (err: any) {
            setLoading(false);
            if (err.name === 'AbortError') {
                // User cancelled the picker
                return;
            }
            console.error("Folder picker error:", err);
            alert("Failed to access folder. Please try again.");
        }
    };

    // Recursive function to traverse directories and collect files
    // @ts-ignore
    const processDirectoryHandle = async (dirHandle: any, fileList: File[], path = "") => {
        // @ts-ignore
        for await (const entry of dirHandle.values()) {
            const name = entry.name;
            const lowerName = name.toLowerCase();

            if (entry.kind === 'file') {
                try {
                    // Strict Requirement: Only count/upload PDF files
                    if (lowerName.endsWith('.pdf')) {
                        const file = await entry.getFile();
                        // @ts-ignore
                        file.manualPath = path + name; // Attach relative path
                        fileList.push(file);
                    }
                } catch (e) {
                    console.warn(`Could not read file: ${entry.name}`, e);
                }
            } else if (entry.kind === 'directory') {
                // Ignore system folders for performance/cleanliness, but still traverse others
                if (
                    !name.startsWith('.') &&
                    lowerName !== '__macosx' &&
                    lowerName !== '$recycle.bin' &&
                    lowerName !== 'system volume information'
                ) {
                    await processDirectoryHandle(entry, fileList, `${path}${name}/`);
                }
            }
        }
    };

    const handleDownload = async (type: 'transmittal' | 'log') => {
        try {
            const response = await api.get(`/projects/${id}/download/${type}`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', type === 'transmittal' ? `Transmittal.xlsx` : `DrawingLog.xlsx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Download failed", err);
            alert("Failed to download file. Have you uploaded any drawings yet?");
        }
    };

    if (!project) return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
            <CircularProgress color="primary" />
        </Box>
    );

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }} className="fade-in">
            {/* Header Section */}
            <Paper
                className="glass-panel"
                sx={{
                    p: 4,
                    mb: 4,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    borderRadius: 4,
                    background: 'linear-gradient(135deg, rgba(30,41,59,0.8) 0%, rgba(15,23,42,0.9) 100%)'
                }}
            >
                <Box>
                    <Typography variant="overline" sx={{ color: 'primary.light', fontWeight: 600, letterSpacing: '0.1em' }}>
                        PROJECT DASHBOARD
                    </Typography>
                    <Typography variant="h3" sx={{ fontWeight: 800, color: '#ffffff', letterSpacing: '-0.02em', mb: 1 }}>
                        {project.title}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                            Client:
                        </Typography>
                        <Chip label={project.client_name} variant="outlined" sx={{ color: '#ffffff', borderColor: 'rgba(255,255,255,0.2)' }} />
                    </Box>
                </Box>

                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                    <Button
                        variant="outlined"
                        startIcon={<DownloadIcon />}
                        onClick={() => handleDownload('log')}
                        sx={{ borderColor: 'rgba(255,255,255,0.2)', color: '#ffffff', '&:hover': { borderColor: 'primary.light', bgcolor: 'rgba(255,255,255,0.05)' } }}
                    >
                        Log
                    </Button>
                    <Button
                        variant="outlined"
                        startIcon={<DownloadIcon />}
                        onClick={() => handleDownload('transmittal')}
                        sx={{ borderColor: 'rgba(255,255,255,0.2)', color: '#ffffff', '&:hover': { borderColor: 'primary.light', bgcolor: 'rgba(255,255,255,0.05)' } }}
                    >
                        Transmittal
                    </Button>
                    <Button
                        variant="contained"

                        size="large"
                        startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <UploadFileIcon />}
                        onClick={async () => {
                            await handleFolderPicker();
                        }}
                        sx={{
                            px: 4,
                            py: 1.5,
                            background: 'linear-gradient(45deg, #2563eb 30%, #3b82f6 90%)',
                            boxShadow: '0 4px 14px 0 rgba(37,99,235,0.39)',
                            '&:hover': { background: 'linear-gradient(45deg, #1d4ed8 30%, #2563eb 90%)' }
                        }}
                    >
                        {loading ? `Uploading ${uploadProgress}%` : 'Upload Folder'}
                    </Button>
                </Box>
            </Paper>

            {/* Content Section: Folder Explorer */}
            <Paper
                className="glass-card"
                sx={{
                    width: '100%',
                    mb: 2,
                    overflow: 'hidden',
                    borderRadius: 4,
                    border: '1px solid rgba(255,255,255,0.05)',
                    p: 2
                }}
            >
                <FolderExplorer project={project} />
            </Paper>
        </Container>
    );
};

// --- Folder Explorer Component ---

const FolderExplorer = ({ project }: { project: any }) => {
    // Navigation State
    // View Level: 0 = Project Root, 1 = Subfolders, 2 = File List
    const [viewLevel, setViewLevel] = useState(0);
    const [selectedType, setSelectedType] = useState<string | null>(null);

    // Compute counts
    const counts = {
        SHOP: project.drawings?.filter((d: any) => d.drawing_type === 'SHOP').length || 0,
        PART: project.drawings?.filter((d: any) => d.drawing_type === 'PART').length || 0,
        ERECTION: project.drawings?.filter((d: any) => d.drawing_type === 'ERECTION').length || 0
    };

    const handleRootClick = () => {
        setViewLevel(1);
    };

    const handleSubfolderClick = (type: string) => {
        setSelectedType(type);
        setViewLevel(2);
    };



    const handleBreadcrumbClick = (level: number) => {
        if (level === 0) {
            setViewLevel(0);
            setSelectedType(null);
        } else if (level === 1) {
            setViewLevel(1);
            setSelectedType(null);
        }
    };

    // --- RENDERERS ---

    // Level 0: Project Root Folder
    if (viewLevel === 0) {
        return (
            <Box>
                <Box sx={{ p: 2, borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="h6" fontWeight={600}>File Explorer</Typography>
                </Box>
                <Box sx={{ p: 4, display: 'flex', gap: 4 }}>
                    <Box
                        onClick={handleRootClick}
                        sx={{
                            textAlign: 'center',
                            cursor: 'pointer',
                            width: 120,
                            p: 2,
                            borderRadius: 2,
                            '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' }
                        }}
                    >
                        <FolderIcon sx={{ fontSize: 80, color: '#f59e0b' }} />
                        <Typography variant="body2" fontWeight={600} sx={{ mt: 1 }}>{project.title}</Typography>
                        <Typography variant="caption" color="text.secondary">{project.drawings?.length || 0} items</Typography>
                    </Box>
                </Box>
            </Box>
        );
    }

    // Level 1: Subfolders
    if (viewLevel === 1) {
        return (
            <Box>
                {/* Breadcrumbs */}
                <Box sx={{ p: 2, borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography
                        variant="body2"
                        color="text.secondary"
                        onClick={() => handleBreadcrumbClick(0)}
                        sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                    >
                        Home
                    </Typography>
                    <Typography variant="body2" color="text.secondary"> / </Typography>
                    <Typography variant="body2" fontWeight={600}>{project.title}</Typography>
                </Box>

                <Box sx={{ p: 4, display: 'flex', gap: 4 }}>
                    <FolderItem
                        label="Shop Drawings"
                        count={counts.SHOP}
                        color="#3b82f6"
                        onClick={() => handleSubfolderClick('SHOP')}
                    />
                    <FolderItem
                        label="Part Drawings"
                        count={counts.PART}
                        color="#10b981"
                        onClick={() => handleSubfolderClick('PART')}
                    />
                    <FolderItem
                        label="Erection Drawings"
                        count={counts.ERECTION}
                        color="#ef4444"
                        onClick={() => handleSubfolderClick('ERECTION')}
                    />
                </Box>
            </Box>
        );
    }

    // Level 2: File List
    const filteredDrawings = project.drawings?.filter((d: any) => d.drawing_type === selectedType) || [];

    return (
        <Box>
            {/* Breadcrumbs */}
            <Box sx={{ p: 2, borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography
                    variant="body2"
                    color="text.secondary"
                    onClick={() => handleBreadcrumbClick(0)}
                    sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                >
                    Home
                </Typography>
                <Typography variant="body2" color="text.secondary"> / </Typography>
                <Typography
                    variant="body2"
                    color="text.secondary"
                    onClick={() => handleBreadcrumbClick(1)}
                    sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                >
                    {project.title}
                </Typography>
                <Typography variant="body2" color="text.secondary"> / </Typography>
                <Typography variant="body2" fontWeight={600}>
                    {selectedType === 'SHOP' ? 'Shop Drawings' : selectedType === 'PART' ? 'Part Drawings' : 'Erection Drawings'}
                </Typography>
            </Box>

            <TableContainer sx={{ maxHeight: 600 }}>
                <Table stickyHeader aria-label="sticky table">
                    <TableHead>
                        <TableRow>
                            <TableCell>Drawing No</TableCell>
                            <TableCell>Rev</TableCell>
                            <TableCell>Description</TableCell>
                            <TableCell>Status</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {filteredDrawings.length > 0 ? (
                            filteredDrawings.map((d: any) => (
                                <TableRow hover role="checkbox" tabIndex={-1} key={d.id} sx={{ '&:hover': { bgcolor: 'rgba(255,255,255,0.02)' } }}>
                                    <TableCell component="th" scope="row" sx={{ fontWeight: 500, color: 'primary.light', display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <InsertDriveFileIcon fontSize="small" color="disabled" />
                                        {d.drawing_no}
                                    </TableCell>
                                    <TableCell>{d.revision_no}</TableCell>
                                    <TableCell sx={{ color: 'text.secondary' }}>{d.description}</TableCell>
                                    <TableCell>
                                        <Box
                                            sx={{
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: 1,
                                                px: 1.5,
                                                py: 0.5,
                                                bgcolor: d.status === 'Active' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                                                color: d.status === 'Active' ? '#34d399' : '#f87171',
                                                borderRadius: 2,
                                                fontSize: '0.75rem',
                                                fontWeight: 600
                                            }}
                                        >
                                            <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: 'currentColor', boxShadow: d.status === 'Active' ? '0 0 8px #34d399' : 'none' }} />
                                            {d.status}
                                        </Box>
                                    </TableCell>
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={4} align="center" sx={{ py: 8 }}>
                                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: 0.5 }}>
                                        <FolderIcon sx={{ fontSize: 48, mb: 2, color: 'text.secondary' }} />
                                        <Typography variant="h6" color="textSecondary">Folder is empty</Typography>
                                    </Box>
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
};

const FolderItem = ({ label, count, color, onClick }: any) => (
    <Box
        onClick={onClick}
        sx={{
            textAlign: 'center',
            cursor: 'pointer',
            width: 120,
            p: 2,
            borderRadius: 2,
            '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' }
        }}
    >
        <FolderIcon sx={{ fontSize: 60, color: color }} />
        <Typography variant="body2" fontWeight={600} sx={{ mt: 1 }}>{label}</Typography>
        <Typography variant="caption" color="text.secondary">{count} items</Typography>
    </Box>
);

export default ProjectView;
