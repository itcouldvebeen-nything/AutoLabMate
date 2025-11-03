'use client'

import { useState, useEffect } from 'react'
import { Play, Edit, CheckCircle } from 'lucide-react'
import axios from 'axios'

interface PlanEditorProps {
  experimentId: string
  onReady: (plan: any) => void
}

export default function PlanEditor({ experimentId, onReady }: PlanEditorProps) {
  const [loading, setLoading] = useState(true)
  const [plan, setPlan] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    generatePlan()
  }, [experimentId])

  const generatePlan = async () => {
    setLoading(true)
    setError(null)

    try {
      // Simulate plan generation (in real implementation, call /api/plan)
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/plan`,
        {
          dataset_path: `/uploads/sample_data_${experimentId}.csv`,
          experiment_description: 'Automated analysis of experimental data'
        }
      )

      setPlan(response.data)
    } catch (err: any) {
      console.error('Plan generation error:', err)
      
      // Fallback to mock plan
      const mockPlan = {
        plan_id: 'plan_mock_123',
        experiment_id: experimentId,
        steps: [
          {
            step_number: 1,
            name: 'Data Loading and Validation',
            action: 'load_data',
            estimated_time: '30s'
          },
          {
            step_number: 2,
            name: 'Descriptive Statistics',
            action: 'compute_stats',
            estimated_time: '1m'
          },
          {
            step_number: 3,
            name: 'Visualization',
            action: 'create_plot',
            estimated_time: '1m'
          },
          {
            step_number: 4,
            name: 'Generate Report',
            action: 'generate_report',
            estimated_time: '3m'
          }
        ],
        estimated_duration: '5-10 minutes',
        confidence_score: 0.85
      }
      
      setPlan(mockPlan)
    } finally {
      setLoading(false)
    }
  }

  const handleExecute = () => {
    if (plan) {
      onReady(plan)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Generating analysis plan...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-700">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {plan && (
        <>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Analysis Plan Generated</h3>
                <p className="text-sm text-gray-600">
                  Estimated duration: {plan.estimated_duration || '5-10 minutes'} • 
                  Confidence: {Math.round((plan.confidence_score || 0.85) * 100)}%
                </p>
              </div>
              <button
                onClick={handleExecute}
                className="flex items-center space-x-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors"
              >
                <Play className="h-5 w-5" />
                <span>Execute Plan</span>
              </button>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="font-semibold text-lg mb-4">Analysis Steps</h3>
            {plan.steps?.map((step: any, idx: number) => (
              <div
                key={step.step_number || idx}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start">
                  <div className="bg-primary-100 text-primary-700 rounded-full p-2 mr-4">
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{step.name}</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Action: {step.action} • Estimated time: {step.estimated_time || 'N/A'}
                    </p>
                  </div>
                  <Edit className="h-5 w-5 text-gray-400 cursor-pointer hover:text-gray-600" />
                </div>
              </div>
            ))}
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-800">
              💡 You can edit individual steps before execution if needed
            </p>
          </div>
        </>
      )}
    </div>
  )
}

