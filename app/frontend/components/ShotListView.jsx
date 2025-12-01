/**
 * Shot List View Component
 * Displays the generated shot list.
 */
import React from 'react';

const ShotListView = ({ shotList, status }) => {
  return (
    <div className="space-y-4">
      {/* Header */}
      <h2 className="text-2xl font-bold text-[#2C3B4D]"> Shot List</h2>

      {/* Shot List Content */}
      <div className="bg-white rounded-lg shadow-xl border-2 border-[#C9C1B1] overflow-hidden">
        {shotList && shotList.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-[#C9C1B1]">
              <thead className="bg-[#2C3B4D]">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-bold text-white uppercase tracking-wider">
                    Shot #
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-white uppercase tracking-wider">
                    Scene
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-white uppercase tracking-wider">
                    Shot Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-white uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-white uppercase tracking-wider">
                    Duration
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-[#EEE9DF]">
                {shotList.map((shot, index) => (
                  <tr key={index} className="hover:bg-[#EEE9DF]/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-[#2C3B4D]">
                      {shot.shot_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-[#1B2632]">
                      {shot.scene}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className="px-2 py-1 bg-[#2C3B4D] text-white rounded font-semibold">
                        {shot.shot_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-[#1B2632] max-w-md">
                      {shot.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-[#A35139] font-medium">
                      {shot.duration || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Equipment Summary */}
            <div className="bg-gradient-to-r from-[#EEE9DF] to-[#C9C1B1] px-6 py-4 border-t-2 border-[#C9C1B1]">
              <h3 className="text-sm font-bold text-[#2C3B4D] mb-2"> Equipment Summary</h3>
              <div className="flex flex-wrap gap-2">
                {[...new Set(shotList.flatMap(shot => shot.equipment || []))].map((item, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-[#A35139] text-white rounded-full text-sm font-semibold shadow-md hover:bg-[#FFB162] transition-colors"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-16">
            {status?.status === 'running' ? (
              <div className="flex flex-col items-center space-y-4">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-[#FFB162]"></div>
                <p className="text-[#2C3B4D] text-lg font-semibold">Generating...</p>
              </div>
            ) : (
              <p className="text-[#C9C1B1]">No shot list yet</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ShotListView;



