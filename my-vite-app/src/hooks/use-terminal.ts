import { useEffect, useRef, useCallback } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';

/**
 * Custom hook for managing xterm terminal instances with proper resize handling.
 * 
 * This hook addresses the PostHog error:
 * "TypeError: Cannot read properties of undefined (reading 'dimensions')"
 * 
 * The error occurs when FitAddon.fit() is called but the terminal's internal
 * _renderService is undefined. This happens in the following scenarios:
 * - Terminal component is hidden (CSS `display: none`) when tab switching
 * - ResizeObserver fires during terminal disposal/unmount
 * - Terminal is not fully initialized when fit() is called
 * 
 * The fix adds explicit checks before calling fit() to ensure the terminal
 * is in a valid state, avoiding the need for try-catch error suppression.
 */

interface UseTerminalOptions {
  onData?: (data: string) => void;
  onResize?: (cols: number, rows: number) => void;
}

interface UseTerminalReturn {
  terminalRef: React.RefObject<HTMLDivElement | null>;
  terminal: Terminal | null;
  fitTerminal: () => void;
}

/**
 * Check if the terminal is ready for fit operations.
 * This prevents the "Cannot read properties of undefined (reading 'dimensions')" error.
 */
function isTerminalReady(
  terminal: Terminal | null,
  fitAddon: FitAddon | null,
  containerElement: HTMLDivElement | null
): boolean {
  // Check terminal instance exists and is opened
  if (!terminal || !fitAddon) {
    return false;
  }

  // Check container element exists
  if (!containerElement) {
    return false;
  }

  // Check element is visible (not display: none)
  // When display is none, offsetParent is null (except for body/html)
  if (containerElement.offsetParent === null && 
      containerElement !== document.body && 
      getComputedStyle(containerElement).display === 'none') {
    return false;
  }

  // Check element has dimensions
  const { clientWidth, clientHeight } = containerElement;
  if (clientWidth === 0 || clientHeight === 0) {
    return false;
  }

  // Check terminal has an element (is opened)
  if (!terminal.element) {
    return false;
  }

  return true;
}

export function useTerminal(options: UseTerminalOptions = {}): UseTerminalReturn {
  const { onData, onResize } = options;
  
  const terminalRef = useRef<HTMLDivElement | null>(null);
  const terminalInstanceRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const isDisposedRef = useRef(false);

  const fitTerminal = useCallback(() => {
    const terminal = terminalInstanceRef.current;
    const fitAddon = fitAddonRef.current;
    const container = terminalRef.current;

    // Skip if terminal has been disposed
    if (isDisposedRef.current) {
      return;
    }

    // Only fit if terminal is in a valid state
    // This prevents the "dimensions" error without needing try-catch
    if (!isTerminalReady(terminal, fitAddon, container)) {
      return;
    }

    // Safe to call fit() - all preconditions are met
    fitAddon!.fit();

    // Notify about resize if callback provided
    if (onResize && terminal) {
      onResize(terminal.cols, terminal.rows);
    }
  }, [onResize]);

  useEffect(() => {
    const container = terminalRef.current;
    if (!container) return;

    isDisposedRef.current = false;

    // Create terminal instance
    const terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
      },
    });

    // Create and load fit addon
    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);

    // Store references
    terminalInstanceRef.current = terminal;
    fitAddonRef.current = fitAddon;

    // Open terminal in container
    terminal.open(container);

    // Initial fit after terminal is opened
    // Use requestAnimationFrame to ensure DOM is ready
    requestAnimationFrame(() => {
      if (!isDisposedRef.current) {
        fitTerminal();
      }
    });

    // Set up data handler
    const dataDisposable = onData ? terminal.onData(onData) : null;

    // Set up resize observer
    const resizeObserver = new ResizeObserver(() => {
      // Debounce resize events
      requestAnimationFrame(() => {
        if (!isDisposedRef.current) {
          fitTerminal();
        }
      });
    });
    resizeObserver.observe(container);

    // Cleanup
    return () => {
      isDisposedRef.current = true;
      resizeObserver.disconnect();
      dataDisposable?.dispose();
      terminal.dispose();
      terminalInstanceRef.current = null;
      fitAddonRef.current = null;
    };
  }, [fitTerminal, onData]);

  return {
    terminalRef,
    terminal: terminalInstanceRef.current,
    fitTerminal,
  };
}

export default useTerminal;
