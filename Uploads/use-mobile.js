import { useEffect, useState } from "react";

export default function useMobile(bp = 768) {
  const [m, setM] = useState(false);
  
  useEffect(() => {
    const q = () => setM(window.innerWidth < bp);
    q();
    window.addEventListener('resize', q);
    return () => window.removeEventListener('resize', q);
  }, [bp]);
  
  return m;
}

// Also export the existing hook for compatibility
export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(undefined);

  useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${768 - 1}px)`);
    const onChange = () => {
      setIsMobile(window.innerWidth < 768);
    };
    mql.addEventListener("change", onChange);
    setIsMobile(window.innerWidth < 768);
    return () => mql.removeEventListener("change", onChange);
  }, []);

  return !!isMobile;
}
