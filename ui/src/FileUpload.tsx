
// FileUpload.tsx
import React, { useState } from 'react';
import Button from '@mui/material/Button';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { AxiosResponse } from 'axios';
import axios from 'axios';

const apiUrl = process.env.REACT_APP_API_URL + '/resources/inputs/'


const FileUpload: React.FC = () => {
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (files) {
            const fileArray = Array.from(files);
            setSelectedFiles(fileArray);
        }
    };

    const handleUpload = async () => {
        if (selectedFiles.length === 0) {
            alert('Please select files to upload.');
            return;
        }

        try {
            const formData = new FormData();

            selectedFiles.forEach((file, index) => {
                formData.append(`files`, file);
            });

            const response: AxiosResponse = await axios.post(apiUrl, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            if (response.status === 200) {
                alert('Files uploaded successfully.');
                setSelectedFiles([]);
            } else {
                alert('File upload failed.');
            }
        } catch (error) {
            console.error('An error occurred:', error);
            alert('File upload failed.');
        }
    };

    return (
        <div>
            <input
                type="file"
                // accept=".pdf,.jpg,.jpeg,.png"
                multiple
                onChange={handleFileChange}
                id="file-upload-input"
                style={{ display: 'none' }}
            />
            <label htmlFor="file-upload-input">
                <Button
                    variant="contained"
                    component="span"
                    startIcon={<CloudUploadIcon />}
                >
                    Upload Inputs
                </Button>
            </label>
            {selectedFiles.length > 0 && (
                <div>
                    <p>Selected Files:</p>
                    <ul>
                        {selectedFiles.map((file, index) => (
                            <li key={index}>{file.name}</li>
                        ))}
                    </ul>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleUpload}
                    >
                        Upload
                    </Button>
                </div>
            )}
        </div>
    );
};

export default FileUpload;
