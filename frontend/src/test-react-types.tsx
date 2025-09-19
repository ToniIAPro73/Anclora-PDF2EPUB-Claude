import React, { useEffect, useState } from 'react';

// Simple component to test React type definitions
const TestComponent: React.FC = () => {
  const [count, setCount] = useState<number>(0);
  
  useEffect(() => {
    console.log('Component mounted');
    return () => console.log('Component unmounted');
  }, []);
  
  return (
    <div>
      <h1>Test Component</h1>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
};

export default TestComponent;