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
  const [status, setStatus] = useState<'running' | 'completed' | 'error'>('running')
  const [executionId, setExecutionId] = useState<string>('')

  useEffect(() => {
    executePlan()
  }, [])

  const executePlan = async () => {
    try {
      setLogs(['🚀 Starting real analysis execution...', `📋 Plan: ${plan.plan_id}`])
      setStatus('running')

      // 🔹 Call real backend endpoint
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/execute`,
        {
          plan_id: plan.plan_id,
          steps: plan.steps,
        },
        { timeout: 600000 } // allow long processing time
      )

      const data = response.data
      const execId = data.plan_id || `exec_${Date.now()}`
      setExecutionId(execId)

      setLogs(prev => [
        ...prev,
        '\n✅ Execution finished successfully.',
        `📄 Report path: ${data.report_path}`,
        '\n🎉 Analysis completed!',
      ])

      setStatus('completed')

      // Pass execution ID back to parent
      onComplete(execId)
    } catch (error: any) {
      console.error('Execution error:', error)
      setLogs(prev => [
        ...prev,
        `❌ Execution failed: ${error.response?.data?.detail || error.message}`,
      ])
      setStatus('error')
    }
  }

  const getLogIcon = (log: string) => {
    if (log.includes('✅')) return <CheckCircle className="h-4 w-4 text-green-500" />
    if (log.includes('⚠️') || log.includes('❌')) return <AlertCircle className="h-4 w-4 text-red-500" />
    if (log.includes('📍')) return <Loader className="h-4 w-4 text-blue-500 animate-spin" />
    return null
  }

  return (
    <div className="space-y-6">
      {/* Status */}
      <div className="flex items-center space-x-3">
        {status === 'running' && (
          <>
            <Loader className="h-5 w-5 text-blue-500 animate-spin" />
            <span className="text-blue-700 font-medium">Executing Plan...</span>
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
                ${log.includes('❌') ? 'text-red-400' : ''}
                ${log.includes('🚀') ? 'text-yellow-400' : 'text-gray-300'}
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
    </div>
  )
}
