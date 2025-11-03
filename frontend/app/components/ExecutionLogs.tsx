'use client'

import { useState, useEffect } from 'react'
import { CheckCircle, AlertCircle, Loader } from 'lucide-react'
import axios from 'axios'

interface ExecutionLogsProps {
  plan: any
  onComplete: (executionId: string) => void
}

export default function ExecutionLogs({ plan, onComplete }: ExecutionLogsProps) {
  const [logs, setLogs] = useState<string[]>([])
  const [currentStep, setCurrentStep] = useState(0)
  const [status, setStatus] = useState<'running' | 'completed' | 'error'>('running')
  const [executionId, setExecutionId] = useState<string>('')

  useEffect(() => {
    executePlan()
  }, [])

  const executePlan = async () => {
    const mockExecutionId = `exec_${Date.now()}`
    setExecutionId(mockExecutionId)

    // Simulate execution with mock logs
    const mockLogs = [
      '🚀 Starting analysis execution...',
      `📋 Plan: ${plan.plan_id}`,
      ''
    ]

    for (let i = 0; i < plan.steps.length; i++) {
      setCurrentStep(i + 1)
      
      const step = plan.steps[i]
      mockLogs.push(`\n📍 Step ${i + 1}: ${step.name}`)
      mockLogs.push(`   Action: ${step.action}`)
      
      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      mockLogs.push(`   ✅ Completed successfully`)
      
      setLogs([...mockLogs])
    }

    mockLogs.push(`\n🎉 All steps completed successfully!`)
    mockLogs.push(`📊 Generating final report...`)
    
    setLogs([...mockLogs])
    setStatus('completed')
    
    // Wait a bit before calling onComplete
    await new Promise(resolve => setTimeout(resolve, 1500))
    onComplete(mockExecutionId)
  }

  const getLogIcon = (log: string) => {
    if (log.includes('✅')) return <CheckCircle className="h-4 w-4 text-green-500" />
    if (log.includes('⚠️') || log.includes('❌')) return <AlertCircle className="h-4 w-4 text-red-500" />
    if (log.includes('📍')) return <Loader className="h-4 w-4 text-blue-500 animate-spin" />
    return null
  }

  return (
    <div className="space-y-6">
      {/* Progress Bar */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Progress</span>
          <span className="text-sm text-gray-600">
            {currentStep} / {plan.steps?.length || 0} steps
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-primary-600 h-3 rounded-full transition-all duration-300"
            style={{
              width: `${(currentStep / (plan.steps?.length || 1)) * 100}%`
            }}
          />
        </div>
      </div>

      {/* Status Badge */}
      <div className="flex items-center space-x-3">
        {status === 'running' && (
          <>
            <Loader className="h-5 w-5 text-blue-500 animate-spin" />
            <span className="text-blue-700 font-medium">Executing Analysis...</span>
          </>
        )}
        {status === 'completed' && (
          <>
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-green-700 font-medium">Execution Completed</span>
          </>
        )}
        {status === 'error' && (
          <>
            <AlertCircle className="h-5 w-5 text-red-500" />
            <span className="text-red-700 font-medium">Execution Failed</span>
          </>
        )}
      </div>

      {/* Logs */}
      <div className="bg-gray-900 rounded-lg p-6 font-mono text-sm overflow-auto max-h-96">
        {logs.map((log, idx) => (
          <div key={idx} className="flex items-start mb-1">
            {getLogIcon(log)}
            <span
              className={`
                ml-2
                ${log.includes('✅') ? 'text-green-400' : ''}
                ${log.includes('❌') || log.includes('⚠️') ? 'text-red-400' : ''}
                ${log.includes('📍') ? 'text-blue-400' : ''}
                ${log.includes('🚀') || log.includes('🎉') ? 'text-yellow-400' : 'text-gray-300'}
              `}
            >
              {log}
            </span>
          </div>
        ))}
        {status === 'running' && (
          <div className="flex items-center text-gray-500">
            <Loader className="h-3 w-3 animate-spin mr-2" />
            Processing...
          </div>
        )}
      </div>

      {/* Current Step Info */}
      {status === 'running' && currentStep > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            Current step: <strong>{plan.steps[currentStep - 1]?.name}</strong>
          </p>
        </div>
      )}
    </div>
  )
}

