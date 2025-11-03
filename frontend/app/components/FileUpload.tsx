'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, CheckCircle } from 'lucide-react'
import axios from 'axios'

interface FileUploadProps {
  onComplete: (experimentId: string,filePath: string) => void
}

export default function FileUpload({ onComplete }: FileUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [uploaded, setUploaded] = useState(false)
  const [fileName, setFileName] = useState<string>('')
  const [experimentId, setExperimentId] = useState<string>('')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploading(true)
    setFileName(file.name)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      setUploaded(true)
      setExperimentId(response.data.experiment_id)
      onComplete(response.data.experiment_id,response.data.file_path || response.data.dataset_path)
    } catch (error: any) {
      console.error('Upload error:', error)
      alert(`Upload failed: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploading(false)
    }
  }, [onComplete])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'text/plain': ['.txt']
    }
  })

  return (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-gray-50'}
          ${uploading ? 'pointer-events-none opacity-50' : 'hover:border-primary-400 hover:bg-primary-25'}
        `}
      >
        <input {...getInputProps()} />
        
        {!uploaded ? (
          <>
            <Upload className={`h-16 w-16 mx-auto mb-4 ${isDragActive ? 'text-primary-600' : 'text-gray-400'}`} />
            <p className="text-lg font-medium text-gray-700 mb-2">
              {isDragActive ? 'Drop your dataset here' : 'Drag & drop your dataset'}
            </p>
            <p className="text-sm text-gray-500">
              or click to browse • Supports CSV, JSON, TXT
            </p>
          </>
        ) : (
          <>
            <CheckCircle className="h-16 w-16 mx-auto mb-4 text-green-500" />
            <p className="text-lg font-medium text-gray-700 mb-2">Upload Successful!</p>
            <p className="text-sm text-gray-500">{fileName}</p>
          </>
        )}
      </div>

      {uploading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-blue-700">Uploading {fileName}...</span>
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          </div>
        </div>
      )}

      {uploaded && experimentId && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <File className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-green-700">Dataset uploaded successfully. Proceeding to plan generation...</span>
          </div>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="font-semibold mb-3">Supported Formats</h3>
        <ul className="space-y-2 text-sm text-gray-600">
          <li>• <strong>CSV</strong> - Comma-separated values with headers</li>
          <li>• <strong>JSON</strong> - JSON arrays or objects</li>
          <li>• <strong>TXT</strong> - Plain text logs and data files</li>
        </ul>
      </div>
    </div>
  )
}

