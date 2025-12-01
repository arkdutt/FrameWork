/**
 * Project Page
 * Displays a single project with all its details.
 */
import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import ProjectDashboard from '../../components/ProjectDashboard';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ProjectPage() {
  const router = useRouter();
  const { id } = router.query;

  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  // Fetch project data
  useEffect(() => {
    if (!id) return;

    const fetchProject = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/projects/${id}`);

        if (!response.ok) {
          throw new Error('Failed to fetch project');
        }

        const data = await response.json();
        setProject(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching project:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    // Fetch once on mount
    fetchProject();

    // NO MORE POLLING - WebSocket will handle real-time updates
    // Only refetch when explicitly needed

  }, [id]);

  // Run pipeline
  const runPipeline = async (forceRerun = false) => {
    try {
      setIsRunning(true);
      const response = await fetch(`${API_URL}/projects/${id}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ force_rerun: forceRerun }),
      });

      if (!response.ok) {
        throw new Error('Failed to start pipeline');
      }

      const data = await response.json();
      console.log('Pipeline started:', data);
    } catch (err) {
      console.error('Error running pipeline:', err);
      alert(`Error: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#EEE9DF] to-[#C9C1B1]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-[#FFB162] mx-auto"></div>
          <p className="mt-4 text-[#2C3B4D] font-medium">Loading project...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#EEE9DF] to-[#C9C1B1]">
        <div className="text-center">
          <div className="text-6xl mb-4"></div>
          <h1 className="text-2xl font-bold text-[#2C3B4D] mb-2">Error</h1>
          <p className="text-[#A35139] mb-4">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-gradient-to-r from-[#FFB162] to-[#A35139] text-white rounded-lg hover:from-[#A35139] hover:to-[#FFB162] transition-all shadow-lg font-semibold"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  // No project found
  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#EEE9DF] to-[#C9C1B1]">
        <div className="text-center">
          <div className="text-6xl mb-4"></div>
          <h1 className="text-2xl font-bold text-[#2C3B4D] mb-2">Project Not Found</h1>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-gradient-to-r from-[#FFB162] to-[#A35139] text-white rounded-lg hover:from-[#A35139] hover:to-[#FFB162] transition-all shadow-lg font-semibold"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Rerun Button - Only show if completed */}
      {project.status === 'completed' && (
        <div className="fixed bottom-8 right-8 z-50">
          <button
            onClick={() => runPipeline(true)}
            disabled={isRunning}
            className="px-6 py-3 bg-[#FFB162] text-white font-bold rounded-lg shadow-2xl hover:bg-[#A35139] disabled:bg-[#C9C1B1] disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-110"
          >
            {isRunning ? '⏳ Rerunning...' : ' Rerun Pipeline'}
          </button>
        </div>
      )}

      {/* Manual Run Button - Only show if pipeline failed or is stuck in 'created' state for too long */}
      {(project.status === 'failed' || project.status === 'created') && (
        <div className="fixed bottom-8 right-8 z-50">
          <button
            onClick={() => runPipeline(false)}
            disabled={isRunning}
            className="px-6 py-3 bg-gradient-to-r from-[#2C3B4D] to-[#1B2632] text-white font-bold rounded-lg shadow-2xl hover:from-[#FFB162] hover:to-[#A35139] disabled:bg-[#C9C1B1] disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-110"
          >
            {isRunning ? '⏳ Starting...' : ' Start Pipeline'}
          </button>
        </div>
      )}

      {/* Dashboard */}
      <ProjectDashboard project={project} />
    </div>
  );
}


