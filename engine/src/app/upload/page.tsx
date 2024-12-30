"use client"

import React, { useState } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import Papa from 'papaparse';

const Upload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    if (selectedFile.type !== 'text/csv') {
      setError('Please upload a CSV file.');
      return;
    }
    setFile(selectedFile);
    setError(null); // Clear any previous errors
  };

  const validateFileFields = (data: any) => {
    const requiredFields = [
      'Name', 'Description', 'URL', 'Size', 'Stars', 'Forks', 'Issues', 'Watchers', 'Language', 'Topics'
    ];

    console.log('data', data)

    // Check if columns match the order exactly
    for (let i = 0; i < requiredFields.length; i++) {
      console.log(data[0][requiredFields[i]]);
      if (data[0][requiredFields[i]] === undefined) {
        return `Missing required field: ${requiredFields[i]}`;
      }
      // Check if columns are in the exact order
      if (Object.keys(data[0])[i] !== requiredFields[i]) {
        return `Columns must be in the following order: ${requiredFields.join(', ')}`;
      }
    }

    return null;
  };

  const processTopics = (topics: string) => {
    // Split the Topics string into an array of strings
    return topics.split(',').map(topic => topic.trim());
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      // Process CSV file using PapaParse
      Papa.parse(file, {
        complete: async (result) => {
          const validationError = validateFileFields(result.data);
          if (validationError) {
            setError(validationError);
            setLoading(false);
            return;
          }

          // Process Topics field to be an array of strings
          const processedData = result.data.map((row: any) => {
            return {
              ...row,
              Topics: processTopics(row.Topics),  // Convert Topics to an array of strings
            };
          });

          // Make API call with processed data
          await axios.post('http://localhost:4000/api/upload', processedData);
          alert('File uploaded successfully!');
          setLoading(false);
        },
        header: true,
        skipEmptyLines: true,
      });
    } catch (err) {
      setError('An error occurred during upload.');
      setLoading(false);
    }
  };

  return (
    <div className=" relative ">
      <div className="absolute top-6 left-12">

      </div>
      <div className="max-w-lg mx-auto p-6 bg-white shadow-md rounded-lg">
        <h2 className="text-xl font-bold mb-4">Upload CSV File</h2>
        <div>
          <Label htmlFor="file" className="block mb-2 text-gray-700">Choose a File</Label>
          <Input
            id="file"
            type="file"
            onChange={handleFileChange}
            className="block w-full mb-4 border border-gray-300 rounded px-3 py-2"
          />
        </div>

        {error && <p className="text-red-600 mb-4">{error}</p>}

        <Button
          onClick={handleUpload}
          disabled={loading || !file}
          className="w-full bg-blue-500 text-white p-3 rounded-lg hover:bg-blue-600"
        >
          Upload
        </Button>
      </div>
    </div>
  );
};

export default Upload;
