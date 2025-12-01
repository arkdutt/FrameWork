/**
 * Script View Component
 * Displays and allows editing of the generated script.
 */
import React, { useState, useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const ScriptView = ({ script, status, projectId }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedScript, setEditedScript] = useState(script || '');
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null); // null | 'success' | 'analyzing' | 'regenerating'
  const [analysisResult, setAnalysisResult] = useState(null);

  // Update editedScript when script prop changes
  useEffect(() => {
    if (script) {
      setEditedScript(script);
    }
  }, [script]);

  const handleEdit = () => {
    setIsEditing(true);
    setSaveStatus(null);
    setAnalysisResult(null);
  };

  const handleCancel = () => {
    setEditedScript(script || '');
    setIsEditing(false);
    setSaveStatus(null);
    setAnalysisResult(null);
  };

  const handleSave = async () => {
    if (!editedScript.trim()) {
      alert('Script cannot be empty');
      return;
    }

    setIsSaving(true);
    setSaveStatus('analyzing');

    try {
      const response = await fetch(`${API_URL}/projects/${projectId}/script`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ script: editedScript }),
      });

      if (!response.ok) {
        throw new Error('Failed to save script');
      }

      const result = await response.json();
      setAnalysisResult(result);

      if (result.should_regenerate) {
        setSaveStatus('regenerating');
        console.log(' Script changes detected, regenerating downstream artifacts...');
        console.log(`   Reason: ${result.reason}`);
        console.log(`   Change %: ${result.change_percentage}%`);
      } else {
        setSaveStatus('success');
        console.log(' Script saved (no regeneration needed)');
        console.log(`   Reason: ${result.reason}`);
      }

      // Exit editing mode after a delay
      setTimeout(() => {
        setIsEditing(false);
        if (!result.should_regenerate) {
          setSaveStatus(null);
        }
      }, 3000);

    } catch (error) {
      console.error('Error saving script:', error);
      alert('Failed to save script. Please try again.');
      setSaveStatus(null);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header with Edit/Save buttons */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-[#2C3B4D]"> Script</h2>
        
        {script && (
          <div className="flex items-center space-x-3">
            {/* Save Status Indicator */}
            {saveStatus === 'analyzing' && (
              <div className="flex items-center space-x-2 text-[#FFB162]">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#FFB162]"></div>
                <span className="text-sm font-medium">Analyzing changes...</span>
              </div>
            )}
            {saveStatus === 'success' && (
              <div className="flex items-center space-x-2 text-green-600">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium">Saved! No regeneration needed</span>
              </div>
            )}
            {saveStatus === 'regenerating' && (
              <div className="flex items-center space-x-2 text-[#A35139]">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#A35139]"></div>
                <span className="text-sm font-medium">Regenerating storyboard & shot list...</span>
              </div>
            )}

            {/* Edit/Save/Cancel Buttons */}
            {!isEditing ? (
              <button
                onClick={handleEdit}
                className="px-4 py-2 bg-[#2C3B4D] text-white rounded-lg hover:bg-[#1B2632] transition-colors font-medium flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span>Edit Script</span>
              </button>
            ) : (
              <div className="flex space-x-2">
                <button
                  onClick={handleCancel}
                  disabled={isSaving}
                  className="px-4 py-2 bg-[#C9C1B1] text-[#2C3B4D] rounded-lg hover:bg-[#EEE9DF] transition-colors font-medium disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={isSaving || editedScript === script}
                  className="px-4 py-2 bg-gradient-to-r from-[#FFB162] to-[#A35139] text-white rounded-lg hover:from-[#A35139] hover:to-[#FFB162] transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {isSaving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Saving...</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Save Changes</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Analysis Result Message */}
      {analysisResult && (
        <div className={`p-4 rounded-lg border-2 ${
          analysisResult.should_regenerate 
            ? 'bg-[#FFB162]/10 border-[#FFB162]' 
            : 'bg-green-50 border-green-400'
        }`}>
          <div className="flex items-start space-x-3">
            {analysisResult.should_regenerate ? (
              <svg className="w-6 h-6 text-[#A35139] flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            )}
            <div className="flex-1">
              <h3 className="font-bold text-[#2C3B4D] mb-1">
                {analysisResult.should_regenerate ? ' Regenerating Downstream Artifacts' : ' Script Updated Successfully'}
              </h3>
              <p className="text-sm text-[#1B2632] mb-2">{analysisResult.reason}</p>
              <div className="text-xs text-[#2C3B4D]/70 space-y-1">
                <p><strong>Change Summary:</strong> {analysisResult.change_summary}</p>
                <p><strong>Change Percentage:</strong> {analysisResult.change_percentage}%</p>
                {analysisResult.should_regenerate && (
                  <p className="mt-2 text-[#A35139] font-medium">
                    ⏳ Storyboard and shot list are being regenerated. This may take 1-2 minutes.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Script Content */}
      <div className="bg-white rounded-lg shadow-xl p-6 border-2 border-[#C9C1B1]">
        {script ? (
          isEditing ? (
            <textarea
              value={editedScript}
              onChange={(e) => setEditedScript(e.target.value)}
              className="w-full h-[500px] font-mono text-sm leading-relaxed text-[#1B2632] border-2 border-[#FFB162] rounded-lg p-4 focus:outline-none focus:ring-2 focus:ring-[#A35139] resize-none"
              placeholder="Enter your script here..."
            />
          ) : (
            <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed text-[#1B2632]">
              {script}
            </pre>
          )
        ) : (
          <div className="text-center py-16">
            {status?.status === 'running' ? (
              <div className="flex flex-col items-center space-y-4">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-[#FFB162]"></div>
                <p className="text-[#2C3B4D] text-lg font-semibold">Generating...</p>
              </div>
            ) : (
              <p className="text-[#C9C1B1]">No script yet</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ScriptView;
