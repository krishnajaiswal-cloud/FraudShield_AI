import { useMutation } from '@tanstack/react-query';
import { uploadApi } from '../api/uploadApi';

export const useUploadAPK = () => {
  return useMutation({
    mutationFn: (file: File) => uploadApi.uploadAPK(file),
    retry: 1,
  });
};
