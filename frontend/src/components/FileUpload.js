import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React from 'react';
import { Upload, X } from 'lucide-react';
import { Card } from './Common';
export const FileUpload = ({ onFileSelect, error, }) => {
    const [isDragActive, setIsDragActive] = React.useState(false);
    const [selectedFile, setSelectedFile] = React.useState(null);
    const fileInputRef = React.useRef(null);
    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragActive(true);
        }
        else if (e.type === 'dragleave') {
            setIsDragActive(false);
        }
    };
    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragActive(false);
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            const file = files[0];
            if (file.name.endsWith('.apk')) {
                setSelectedFile(file);
                onFileSelect(file);
            }
            else {
                alert('Please select a valid APK file');
            }
        }
    };
    const handleChange = (e) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            const file = files[0];
            if (file.name.endsWith('.apk')) {
                setSelectedFile(file);
                onFileSelect(file);
            }
            else {
                alert('Please select a valid APK file');
            }
        }
    };
    const handleClick = () => {
        fileInputRef.current?.click();
    };
    return (_jsxs("div", { onDragEnter: handleDrag, onDragLeave: handleDrag, onDragOver: handleDrag, onDrop: handleDrop, children: [_jsx(Card, { onClick: handleClick, className: `border-2 border-dashed transition-all cursor-pointer ${isDragActive
                    ? 'border-risk-critical bg-risk-critical/5'
                    : 'border-cyber-border hover:border-cyber-border/80'} ${selectedFile ? 'bg-cyber-darker' : ''}`, children: _jsxs("div", { className: "flex flex-col items-center justify-center py-12 gap-4", children: [_jsxs("div", { className: "relative", children: [_jsx(Upload, { className: `w-12 h-12 ${isDragActive ? 'text-risk-critical' : 'text-gray-400'} transition-colors` }), isDragActive && (_jsx("div", { className: "absolute inset-0 bg-risk-critical/20 blur-lg" }))] }), selectedFile ? (_jsxs("div", { className: "text-center", children: [_jsx("p", { className: "text-white font-semibold", children: selectedFile.name }), _jsxs("p", { className: "text-gray-400 text-sm", children: [(selectedFile.size / 1024 / 1024).toFixed(2), " MB"] })] })) : (_jsx(_Fragment, { children: _jsxs("div", { className: "text-center", children: [_jsx("p", { className: "text-white font-semibold mb-1", children: isDragActive ? 'Drop your APK here' : 'Drag and drop your APK file' }), _jsx("p", { className: "text-gray-400 text-sm", children: "or click to browse" })] }) }))] }) }), _jsx("input", { ref: fileInputRef, type: "file", accept: ".apk", onChange: handleChange, className: "hidden" }), error && (_jsxs("div", { className: "mt-4 p-4 bg-risk-critical/10 border border-risk-critical rounded-lg flex items-start gap-3", children: [_jsx(X, { className: "w-5 h-5 text-risk-critical flex-shrink-0 mt-0.5" }), _jsx("p", { className: "text-risk-critical text-sm", children: error })] })), selectedFile && (_jsx("button", { onClick: () => setSelectedFile(null), className: "mt-4 w-full px-4 py-2 bg-cyber-darker text-gray-300 rounded-lg hover:bg-cyber-border transition-colors", children: "Clear Selection" }))] }));
};
