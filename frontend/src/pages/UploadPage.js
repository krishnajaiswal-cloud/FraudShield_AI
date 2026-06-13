import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { MainLayout, FileUpload, ErrorState } from '../components';
import { useUploadAPK } from '../hooks/useUpload';
import { useCreateAnalysis, useRunAnalysis } from '../hooks/useAnalysis';
export const UploadPage = () => {
    const navigate = useNavigate();
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadError, setUploadError] = useState();
    const [isCreatingAnalysis, setIsCreatingAnalysis] = useState(false);
    const uploadAPK = useUploadAPK();
    const createAnalysis = useCreateAnalysis();
    const runAnalysis = useRunAnalysis();
    const handleFileSelect = (file) => {
        setSelectedFile(file);
        setUploadError(undefined);
    };
    const handleUpload = async () => {
        if (!selectedFile) {
            setUploadError('Please select an APK file');
            return;
        }
        try {
            setUploadError(undefined);
            const uploadResult = await uploadAPK.mutateAsync(selectedFile);
            // Create analysis record
            setIsCreatingAnalysis(true);
            const analysisResult = await createAnalysis.mutateAsync(uploadResult.file_path);
            // Run analysis
            await runAnalysis.mutateAsync(analysisResult.id);
            // Redirect to analysis progress page
            navigate(`/analysis/${analysisResult.id}`);
        }
        catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to upload APK';
            setUploadError(message);
        }
        finally {
            setIsCreatingAnalysis(false);
        }
    };
    const isLoading = uploadAPK.isPending || isCreatingAnalysis;
    return (_jsx(MainLayout, { children: _jsxs("div", { className: "max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12", children: [_jsxs("div", { className: "mb-12", children: [_jsx("h1", { className: "text-4xl font-bold text-white mb-4", children: "Upload APK for Analysis" }), _jsx("p", { className: "text-gray-400", children: "Select an Android APK file to analyze for security vulnerabilities and risks" })] }), uploadError && (_jsx("div", { className: "mb-8", children: _jsx(ErrorState, { title: "Upload Failed", description: uploadError, onRetry: () => {
                            setUploadError(undefined);
                            setSelectedFile(null);
                        } }) })), _jsxs("div", { className: "space-y-8", children: [_jsx(FileUpload, { onFileSelect: handleFileSelect, error: uploadAPK.error ? 'Failed to upload file' : undefined }), _jsxs("div", { className: "flex flex-col sm:flex-row gap-4", children: [_jsxs("button", { onClick: handleUpload, disabled: !selectedFile || isLoading, className: "flex-1 px-6 py-3 bg-gradient-to-r from-risk-critical to-risk-high text-white rounded-lg font-semibold hover:shadow-neon-red transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2", children: [isLoading && _jsx(Loader2, { className: "w-5 h-5 animate-spin" }), isLoading ? 'Uploading...' : 'Upload and Analyze'] }), _jsx("button", { onClick: () => navigate('/'), className: "px-6 py-3 border border-cyber-border text-white rounded-lg font-semibold hover:border-cyber-border/50 transition-colors", children: "Cancel" })] }), _jsxs("div", { className: "bg-cyber-card border border-cyber-border rounded-xl p-6", children: [_jsx("h3", { className: "text-lg font-semibold text-white mb-4", children: "About APK Analysis" }), _jsxs("ul", { className: "space-y-3 text-gray-400 text-sm", children: [_jsxs("li", { className: "flex items-start gap-3", children: [_jsx("span", { className: "text-risk-critical mt-1 flex-shrink-0", children: "\u2022" }), _jsx("span", { children: "Analyzes Android manifest for permissions" })] }), _jsxs("li", { className: "flex items-start gap-3", children: [_jsx("span", { className: "text-risk-critical mt-1 flex-shrink-0", children: "\u2022" }), _jsx("span", { children: "Extracts embedded URLs and domains" })] }), _jsxs("li", { className: "flex items-start gap-3", children: [_jsx("span", { className: "text-risk-critical mt-1 flex-shrink-0", children: "\u2022" }), _jsx("span", { children: "Detects suspicious components and behaviors" })] }), _jsxs("li", { className: "flex items-start gap-3", children: [_jsx("span", { className: "text-risk-critical mt-1 flex-shrink-0", children: "\u2022" }), _jsx("span", { children: "Generates comprehensive security report" })] })] })] })] })] }) }));
};
