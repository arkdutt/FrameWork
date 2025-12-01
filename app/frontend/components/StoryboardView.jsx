/**
 * Storyboard View Component
 * Displays the generated storyboard frames.
 */
import React from 'react';

const StoryboardView = ({ storyboard, status }) => {
  return (
    <div className="space-y-4">
      {/* Header */}
      <h2 className="text-2xl font-bold text-[#2C3B4D]"> Storyboard</h2>

      {/* Storyboard Content */}
      <div className="bg-white rounded-lg shadow-xl p-6 border-2 border-[#C9C1B1]">
        {storyboard && storyboard.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {storyboard.map((frame, index) => (
              <div
                key={index}
                className="border-2 border-[#C9C1B1] rounded-lg overflow-hidden hover:shadow-2xl transition-all hover:border-[#FFB162] hover:scale-105 duration-300"
              >
                {/* Frame Image Placeholder */}
                <div className="bg-[#EEE9DF] aspect-video flex items-center justify-center">
                  {frame.image_url ? (
                    <img
                      src={frame.image_url}
                      alt={`Frame ${frame.frame_number}`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-[#C9C1B1] text-center p-4">
                      <div className="text-4xl mb-2"></div>
                      <div className="text-sm">Frame {frame.frame_number}</div>
                    </div>
                  )}
                </div>

                {/* Frame Details */}
                <div className="p-4 space-y-2 bg-gradient-to-b from-white to-[#EEE9DF]/30">
                  <div className="font-bold text-lg text-[#2C3B4D]">Frame {frame.frame_number}</div>
                  
                  {frame.camera_angle && (
                    <div className="text-sm text-[#A35139]">
                      <span className="font-semibold"> Camera:</span> {frame.camera_angle}
                    </div>
                  )}
                  
                  <div className="text-sm text-[#1B2632]">
                    {frame.description}
                  </div>
                  
                  {frame.dialogue && (
                    <div className="text-sm italic text-[#A35139] border-l-2 border-[#FFB162] pl-2">
                      "{frame.dialogue}"
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            {status?.status === 'running' ? (
              <div className="flex flex-col items-center space-y-4">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-[#FFB162]"></div>
                <p className="text-[#2C3B4D] text-lg font-semibold">Generating...</p>
              </div>
            ) : (
              <p className="text-[#C9C1B1]">No storyboard yet</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StoryboardView;


