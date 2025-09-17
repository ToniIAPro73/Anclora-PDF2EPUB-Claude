// suppressRouterWarnings.ts
/**
 * This file suppresses specific React Router warnings about future flags
 * by monkey-patching the console.warn function.
 * 
 * This is a temporary solution until we upgrade to React Router v7.
 */

// Store the original console.warn function
const originalWarn = console.warn;

// Replace console.warn with a filtered version
console.warn = function(...args) {
  // Check if this is a React Router future flag warning
  const isRouterWarning = args.length > 0 && 
    typeof args[0] === 'string' && 
    (args[0].includes('React Router Future Flag Warning') ||
     args[0].includes('v7_startTransition') ||
     args[0].includes('v7_relativeSplatPath'));
  
  // Only log warnings that are not React Router future flag warnings
  if (!isRouterWarning) {
    originalWarn.apply(console, args);
  }
};

export {};
