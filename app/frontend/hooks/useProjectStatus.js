/**
 * Custom hook for managing project status via WebSocket.
 * 
 * This version is optimized to handle React Strict Mode in development.
 */
import { useState, useEffect, useRef } from 'react';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

// Global WebSocket cache to survive React Strict Mode remounts
const wsCache = {};

export const useProjectStatus = (projectId) => {
  const [status, setStatus] = useState({
    script: { status: 'pending', message: '' },
    storyboard: { status: 'pending', message: '' },
    shot_list: { status: 'pending', message: '' },
    overall: 'created',
    error: null,
  });

  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(Date.now());
  const reconnectTimeoutRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 10;

  useEffect(() => {
    if (!projectId) return;

    console.log(' Setting up WebSocket for project:', projectId);

    // Check if we already have a connection for this project
    let ws = wsCache[projectId];
    
    // Create new connection only if needed
    if (!ws || ws.readyState === WebSocket.CLOSED || ws.readyState === WebSocket.CLOSING) {
      console.log(' Creating new WebSocket connection...');
      ws = new WebSocket(`${WS_URL}/ws/${projectId}`);
      wsCache[projectId] = ws;

      ws.onopen = () => {
        console.log(' WebSocket connected');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;

        // Clear existing heartbeat if any
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
        }

        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            try {
              ws.send('ping');
            } catch (err) {
              console.error(' Heartbeat error:', err);
            }
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          // Handle heartbeat pong
          if (event.data === 'pong') {
            return;
          }

          // Parse JSON messages
          const data = JSON.parse(event.data);
          console.log(' WebSocket message:', data);

          // Handle progress updates
          if (data.type === 'progress') {
            setStatus((prev) => ({
              ...prev,
              [data.stage]: {
                status: data.status,
                message: data.message || '',
              },
            }));
            setLastUpdate(Date.now());
          }

          // Handle completion
          if (data.type === 'completed') {
            setStatus((prev) => ({
              ...prev,
              overall: 'completed',
            }));
            setLastUpdate(Date.now());
          }

          // Handle errors
          if (data.type === 'error') {
            setStatus((prev) => ({
              ...prev,
              error: data.error,
            }));
            setLastUpdate(Date.now());
          }
        } catch (err) {
          console.error(' Parse error:', err);
        }
      };

      ws.onerror = (error) => {
        console.error(' WebSocket error');
        setIsConnected(false);
      };

      ws.onclose = (event) => {
        console.log(' WebSocket closed:', event.code);
        setIsConnected(false);
        delete wsCache[projectId];

        // Clear heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
          heartbeatIntervalRef.current = null;
        }

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttemptsRef.current += 1;
          
          if (!reconnectTimeoutRef.current) {
            reconnectTimeoutRef.current = setTimeout(() => {
              console.log(` Reconnecting... (${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})`);
              reconnectTimeoutRef.current = null;
              // Trigger re-render to reconnect
              setIsConnected(false);
            }, 5000);
          }
        } else {
          console.error(' Max reconnection attempts reached');
        }
      };
    } else {
      // Reuse existing connection
      console.log('  Reusing existing WebSocket connection');
      setIsConnected(ws.readyState === WebSocket.OPEN);
      
      // Re-attach message handler for this component instance
      ws.onmessage = (event) => {
        try {
          if (event.data === 'pong') return;
          
          const data = JSON.parse(event.data);
          console.log(' WebSocket message:', data);
          
          if (data.type === 'progress') {
            setStatus((prev) => ({
              ...prev,
              [data.stage]: {
                status: data.status,
                message: data.message || '',
              },
            }));
            setLastUpdate(Date.now());
          }
          
          if (data.type === 'completed') {
            setStatus((prev) => ({
              ...prev,
              overall: 'completed',
            }));
            setLastUpdate(Date.now());
          }
          
          if (data.type === 'error') {
            setStatus((prev) => ({
              ...prev,
              error: data.error,
            }));
            setLastUpdate(Date.now());
          }
        } catch (err) {
          console.error(' Parse error:', err);
        }
      };
    }

    // Cleanup function - DON'T close the WebSocket, just cleanup timers
    return () => {
      console.log(' Cleanup (keeping WebSocket alive)');
      
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      
      // Don't clear heartbeat - let it continue
      // Don't close WebSocket - let it persist
    };
  }, [projectId]);

  const reconnect = () => {
    console.log(' Manual reconnect triggered');
    // Clear cache to force new connection
    if (wsCache[projectId]) {
      try {
        wsCache[projectId].close();
      } catch (e) {
        // Ignore errors
      }
      delete wsCache[projectId];
    }
    setIsConnected(false);
  };

  return {
    status,
    isConnected,
    reconnect,
    lastUpdate,
  };
};

export default useProjectStatus;
