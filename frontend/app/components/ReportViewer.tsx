'use client'

import { useState } from 'react'
import { Download, FileText, ExternalLink, CheckCircle } from 'lucide-react'

interface ReportViewerProps {
  executionId: string
}

export default function ReportViewer({ executionId }: ReportViewerProps) {
  const [downloading, setDownloading] = useState(false)

  const handleDownload = async () => {
    setDownloading(true)
    
    try {
      // In real implementation, download PDF from backend
      const blob = new Blob(['Mock PDF Content'], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `autolabmate_report_${executionId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Download error:', error)
      alert('Download failed. Please try again.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Success Message */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-center">
          <CheckCircle className="h-8 w-8 text-green-500 mr-4" />
          <div>
            <h3 className="text-lg font-semibold text-green-900">Report Generated Successfully!</h3>
            <p className="text-sm text-green-700 mt-1">
              Your lab report is ready for download
            </p>
          </div>
        </div>
      </div>

      {/* Report Preview */}
      <div className="bg-gray-50 rounded-lg p-8 border-2 border-dashed border-gray-300">
        <FileText className="h-24 w-24 text-gray-400 mx-auto mb-4" />
        <div className="text-center">
          <h4 className="text-xl font-semibold text-gray-900 mb-2">
            AutoLabMate Lab Report
          </h4>
          <p className="text-gray-600 mb-4">
            Generated: {new Date().toLocaleString()}
          </p>
          <p className="text-sm text-gray-500">
            Preview will be available in production version
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="flex-1 flex items-center justify-center space-x-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download className="h-5 w-5" />
          <span>{downloading ? 'Downloading...' : 'Download PDF Report'}</span>
        </button>
        
        <button className="flex-1 flex items-center justify-center space-x-2 bg-gray-200 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-300 transition-colors">
          <FileText className="h-5 w-5" />
          <span>Download Notebook</span>
        </button>
        
        <button className="flex items-center justify-center space-x-2 bg-gray-200 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-300 transition-colors">
          <ExternalLink className="h-5 w-5" />
          <span>View on GitHub</span>
        </button>
      </div>

      {/* Report Summary */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="font-semibold mb-4">Report Summary</h3>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-gray-500">Experiment ID</dt>
            <dd className="font-mono text-gray-900">{executionId}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Status</dt>
            <dd className="text-green-600 font-medium">Completed</dd>
          </div>
          <div>
            <dt className="text-gray-500">Analysis Steps</dt>
            <dd className="text-gray-900">4 steps executed</dd>
          </div>
          <div>
            <dt className="text-gray-500">File Size</dt>
            <dd className="text-gray-900">~2.3 MB</dd>
          </div>
        </dl>
      </div>

      {/* Next Steps */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3">What's Next?</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>• Review the generated report for accuracy</li>
          <li>• Share the reproducible notebook with your team</li>
          <li>• Schedule follow-up experiments using calendar integration</li>
          <li>• Contribute insights back to the knowledge base</li>
        </ul>
      </div>
    </div>
  )
}

