/**
 * Project Dashboard Component
 * Main dashboard for viewing project status and outputs.
 */
import React, { useState, useEffect } from 'react';
import ScriptView from './ScriptView';
import StoryboardView from './StoryboardView';
import ShotListView from './ShotListView';
import useProjectStatus from '../hooks/useProjectStatus';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const ProjectDashboard = ({ project: initialProject }) => {
  const [project, setProject] = useState(initialProject);
  const { status, isConnected, lastUpdate } = useProjectStatus(project._id);

  // Fetch fresh project data whenever WebSocket sends an update
  useEffect(() => {
    const fetchLatestProject = async () => {
      try {
        const response = await fetch(`${API_URL}/projects/${project._id}`);
        if (response.ok) {
          const data = await response.json();
          setProject(data);
          console.log(' Project data refreshed');
        }
      } catch (err) {
        console.error('Error fetching latest project:', err);
      }
    };

    // Refresh whenever lastUpdate changes (WebSocket message received)
    fetchLatestProject();
  }, [lastUpdate, project._id]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#EEE9DF] to-[#C9C1B1]">
      {/* Header */}
      <header className="bg-[#2C3B4D] shadow-lg border-b-4 border-[#FFB162]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">
                {project.title || 'Untitled Project'}
              </h1>
              <p className="mt-1 text-sm text-[#C9C1B1]">
                Project ID: {project._id}
              </p>
            </div>

            {/* Connection Status */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-[#1B2632] px-4 py-2 rounded-lg">
                <div
                  className={`w-3 h-3 rounded-full ${
                    isConnected ? 'bg-[#FFB162] animate-pulse' : 'bg-[#A35139]'
                  }`}
                />
                <span className="text-sm text-white">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              {/* Overall Status */}
              <div className="px-4 py-2 bg-[#FFB162] text-[#1B2632] rounded-lg font-bold shadow-md">
                {status.overall}
              </div>
            </div>
          </div>

          {/* User Prompt */}
          <div className="mt-4 p-4 bg-[#1B2632] rounded-lg border border-[#FFB162]/30">
            <p className="text-sm font-semibold text-[#FFB162] mb-1">Original Prompt:</p>
            <p className="text-white">{project.user_prompt}</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Error Display */}
          {status.error && (
            <div className="bg-[#A35139]/10 border-l-4 border-[#A35139] p-4 rounded-lg shadow-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <span className="text-2xl"></span>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-[#A35139]">Error</h3>
                  <p className="mt-1 text-sm text-[#2C3B4D]">{status.error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Script Section */}
          <ScriptView script={project.script} status={status.script} projectId={project._id} />

          {/* Storyboard Section */}
          <StoryboardView storyboard={project.storyboard} status={status.storyboard} />

          {/* Shot List Section */}
          <ShotListView shotList={project.shot_list} status={status.shot_list} />
        </div>
      </main>
    </div>
  );
};

export default ProjectDashboard;


