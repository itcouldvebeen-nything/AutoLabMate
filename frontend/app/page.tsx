'use client'

import { useState } from 'react'
import { Upload, Play, Download, FileText, Edit } from 'lucide-react'
import FileUpload from './components/FileUpload'
import PlanEditor from './components/PlanEditor'
import ExecutionLogs from './components/ExecutionLogs'
import ReportViewer from './components/ReportViewer'

export default function Home() {
  const [currentStep, setCurrentStep] = useState<'upload' | 'plan' | 'execute' | 'report'>('upload')
  const [experimentId, setExperimentId] = useState<string | null>(null)
  const [plan, setPlan] = useState<any>(null)
  const [executionId, setExecutionId] = useState<string | null>(null)

  const handleUploadComplete = (expId: string) => {
    setExperimentId(expId)
    setCurrentStep('plan')
  }

  const handlePlanReady = (planData: any) => {
    setPlan(planData)
    setCurrentStep('execute')
  }

  const handleExecutionComplete = (execId: string) => {
    setExecutionId(execId)
    setCurrentStep('report')
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <FileText className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AutoLabMate</h1>
                <p className="text-sm text-gray-600">AI-Powered Lab Automation</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="https://github.com/yourusername/autolabmate"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                GitHub
              </a>
              <a
                href="/docs"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Docs
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Steps */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between">
            <StepIndicator
              number={1}
              label="Upload Dataset"
              active={currentStep === 'upload'}
              completed={currentStep !== 'upload'}
              icon={<Upload className="h-5 w-5" />}
            />
            <div className="flex-1 h-0.5 bg-gray-200 mx-4"></div>
            <StepIndicator
              number={2}
              label="Generate Plan"
              active={currentStep === 'plan'}
              completed={currentStep === 'execute' || currentStep === 'report'}
              icon={<Edit className="h-5 w-5" />}
            />
            <div className="flex-1 h-0.5 bg-gray-200 mx-4"></div>
            <StepIndicator
              number={3}
              label="Execute"
              active={currentStep === 'execute'}
              completed={currentStep === 'report'}
              icon={<Play className="h-5 w-5" />}
            />
            <div className="flex-1 h-0.5 bg-gray-200 mx-4"></div>
            <StepIndicator
              number={4}
              label="Download Report"
              active={currentStep === 'report'}
              completed={false}
              icon={<Download className="h-5 w-5" />}
            />
          </div>
        </div>

        {/* Content Area */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          {currentStep === 'upload' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Upload Your Dataset</h2>
              <FileUpload onComplete={handleUploadComplete} />
            </div>
          )}

          {currentStep === 'plan' && experimentId && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Analysis Plan</h2>
              <PlanEditor experimentId={experimentId} onReady={handlePlanReady} />
            </div>
          )}

          {currentStep === 'execute' && plan && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Execution Progress</h2>
              <ExecutionLogs plan={plan} onComplete={handleExecutionComplete} />
            </div>
          )}

          {currentStep === 'report' && executionId && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Report Ready</h2>
              <ReportViewer executionId={executionId} />
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-gray-600">
          <p>AutoLabMate - Making reproducible science accessible</p>
          <p className="mt-2">Ishaan Vikas © 2024</p>
        </footer>
      </div>
    </main>
  )
}

function StepIndicator({ number, label, active, completed, icon }: any) {
  const bgColor = active ? 'bg-primary-600' : completed ? 'bg-green-500' : 'bg-gray-300'
  const textColor = active ? 'text-primary-600' : completed ? 'text-green-500' : 'text-gray-500'

  return (
    <div className="flex flex-col items-center">
      <div className={`${bgColor} w-12 h-12 rounded-full flex items-center justify-center text-white mb-2 transition-colors`}>
        {completed ? '✓' : icon}
      </div>
      <span className={`text-sm font-medium ${textColor}`}>{label}</span>
    </div>
  )
}

