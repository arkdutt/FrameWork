/**
 * Home Page
 * Landing page with project creation form.
 */
import { useState } from 'react';
import { useRouter } from 'next/router';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const router = useRouter();
  const [prompt, setPrompt] = useState('');
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/projects/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_prompt: prompt,
          title: title || null,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create project');
      }

      const data = await response.json();
      console.log('Project created:', data);

      // Auto-trigger the pipeline immediately
      try {
        const runResponse = await fetch(`${API_URL}/projects/${data._id}/run`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ force_rerun: false }),
        });

        if (runResponse.ok) {
          console.log(' Pipeline auto-started');
        } else {
          console.warn('  Pipeline auto-start failed, user can manually start it');
        }
      } catch (pipelineErr) {
        console.error('Pipeline auto-start error:', pipelineErr);
        // Continue anyway - user can manually start pipeline
      }

      // Redirect to project page
      router.push(`/project/${data._id}`);
    } catch (err) {
      console.error('Error creating project:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#EEE9DF] to-[#C9C1B1]">
      <div className="max-w-4xl mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-[#1B2632] mb-4">
             FrameWork
          </h1>
          <p className="text-xl text-[#2C3B4D]">
            Your Pre-Production AI Agent Suite
          </p>
          <p className="text-[#A35139] mt-2 font-medium">
            Generate scripts, storyboards, and shot lists with AI
          </p>
        </div>

        {/* Create Project Form */}
        <div className="bg-white rounded-2xl shadow-2xl p-8 border border-[#C9C1B1]">
          <h2 className="text-2xl font-bold text-[#2C3B4D] mb-6">
            Create New Project
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Title Input */}
            <div>
              <label
                htmlFor="title"
                className="block text-sm font-medium text-[#2C3B4D] mb-2"
              >
                Project Title
              </label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="My Awesome Film"
                className="w-full px-4 py-3 border border-[#C9C1B1] rounded-lg focus:ring-2 focus:ring-[#FFB162] focus:border-transparent outline-none transition bg-[#EEE9DF]/30"
              />
            </div>

            {/* Prompt Input */}
            <div>
              <label
                htmlFor="prompt"
                className="block text-sm font-medium text-[#2C3B4D] mb-2"
              >
                Describe Your Project <span className="text-[#A35139]">*</span>
              </label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Example: Create a short film about a lonely astronaut discovering life on Mars. It should be dramatic, visually stunning, and about 5 minutes long."
                rows={6}
                className="w-full px-4 py-3 border border-[#C9C1B1] rounded-lg focus:ring-2 focus:ring-[#FFB162] focus:border-transparent outline-none transition resize-none bg-[#EEE9DF]/30"
                required
              />
              <p className="mt-2 text-sm text-[#A35139]">
                Be as detailed as possible. Include genre, tone, duration, key scenes, etc.
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-[#A35139]/10 border-l-4 border-[#A35139] p-4 rounded">
                <p className="text-[#A35139] font-medium">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-[#FFB162] to-[#A35139] hover:from-[#A35139] hover:to-[#FFB162] text-white font-bold py-4 px-6 rounded-lg transition-all duration-300 disabled:bg-[#C9C1B1] disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Creating Project...</span>
                </>
              ) : (
                <>
                  <span></span>
                  <span>Create Project</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Features */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6 text-center border border-[#C9C1B1] hover:shadow-lg transition-shadow hover:border-[#FFB162]">
            <div className="text-4xl mb-3"></div>
            <h3 className="font-bold text-lg mb-2 text-[#2C3B4D]">Scripts</h3>
            <p className="text-[#A35139] text-sm">
              Professional screenplay format with dialogue and scene descriptions
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 text-center border border-[#C9C1B1] hover:shadow-lg transition-shadow hover:border-[#FFB162]">
            <div className="text-4xl mb-3"></div>
            <h3 className="font-bold text-lg mb-2 text-[#2C3B4D]">Storyboards</h3>
            <p className="text-[#A35139] text-sm">
              Visual representations of key scenes with camera angles
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 text-center border border-[#C9C1B1] hover:shadow-lg transition-shadow hover:border-[#FFB162]">
            <div className="text-4xl mb-3"></div>
            <h3 className="font-bold text-lg mb-2 text-[#2C3B4D]">Shot Lists</h3>
            <p className="text-[#A35139] text-sm">
              Detailed technical breakdown with equipment and timing
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}


