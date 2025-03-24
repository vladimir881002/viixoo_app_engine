import { useState, useEffect } from "react"

// Main function that gets the elapsed time
function getElapsedTime(startTimeString: string): string {
    // Convertir la fecha inicial a objeto Date
    const startTime = new Date(startTimeString);
    const now = new Date();
    
    // Calculate difference in milliseconds
    const difference = now.getTime() - startTime.getTime();
    
    // Convert to minutes and seconds
    const totalSeconds = Math.floor(difference / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
  
    // Format to 2 digits
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }
  
  // Hook for real-time update
  export function useElapsedTime(startTimeString: string) {
    const [elapsedTime, setElapsedTime] = useState('00:00');
  
    useEffect(() => {
      const interval = setInterval(() => {
        const time = getElapsedTime(startTimeString);
        setElapsedTime(time);
      }, 1000);
  
      return () => clearInterval(interval);
    }, [startTimeString]);
  
    return elapsedTime;
  }
  