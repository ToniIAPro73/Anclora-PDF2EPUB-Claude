// routerConfig.ts
import { startTransition } from "react";

// This is a workaround to suppress React Router future flag warnings
// by monkey-patching the console.warn function
const originalWarn = console.warn;

// Filter out specific React Router warnings
console.warn = function(...args) {
  // Check if this is a React Router future flag warning
  const isRouterWarning = args.length > 0 && 
    typeof args[0] === 'string' && 
    args[0].includes('React Router Future Flag Warning');
  
  // Only log warnings that are not React Router future flag warnings
  if (!isRouterWarning) {
    originalWarn.apply(console, args);
  }
};

// Export a function to wrap state updates in startTransition
export function wrapInStartTransition(callback: () => void) {
  startTransition(callback);
}
