const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const uploadApi = {
    uploadAPK: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${API_URL}/api/v1/upload`, {
            method: 'POST',
            body: formData,
            // Note: Do NOT set Content-Type header for FormData
            // Browser will automatically set it with the correct boundary
        });
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        return (await response.json());
    },
};
