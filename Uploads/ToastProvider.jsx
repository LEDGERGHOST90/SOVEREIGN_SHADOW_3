import React, { createContext, useCallback, useContext, useMemo, useRef, useState } from "react";
import { AlertTriangle, CheckCircle2, Info } from "lucide-react";

const ToastCtx = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  const push = useCallback(({ title, description, variant = "info", duration = 4000 }) => {
    const id = ++idRef.current;
    const toast = { id, title, description, variant };
    setToasts((t) => [...t, toast]);
    if (duration > 0) setTimeout(() => dismiss(id), duration);
    return id;
  }, []);

  const dismiss = useCallback((id) => setToasts((t) => t.filter((x) => x.id !== id)), []);

  const api = useMemo(() => ({ push, dismiss }), [push, dismiss]);

  return (
    <ToastCtx.Provider value={api}>
      {children}
      <Toaster toasts={toasts} onDismiss={dismiss} />
    </ToastCtx.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastCtx);
  if (!ctx) throw new Error("useToast must be used within <ToastProvider>");
  return ctx;
}

export function Toaster({ toasts, onDismiss }) {
  return (
    <div className="pointer-events-none fixed right-4 top-4 z-[1000] flex w-[22rem] flex-col gap-3">
      {toasts.map((t) => (
        <div
          key={t.id}
          className="pointer-events-auto overflow-hidden rounded-xl border border-white/15 bg-black/60 shadow-[0_10px_30px_rgba(0,0,0,0.45)] backdrop-blur-xl"
        >
          <div className="flex items-start gap-3 p-3">
            <Icon variant={t.variant} />
            <div className="flex-1">
              <div className="text-sm font-semibold text-white/95">{t.title}</div>
              {t.description && <div className="mt-0.5 text-xs text-white/70">{t.description}</div>}
            </div>
            <button
              onClick={() => onDismiss(t.id)}
              className="ml-2 rounded-md bg-white/5 px-2 py-1 text-xs text-white/70 hover:bg-white/10"
            >
              Dismiss
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

function Icon({ variant }) {
  const cls = "h-4 w-4";
  switch (variant) {
    case "error":   return <AlertTriangle className={cls + " text-amber-300"} />;
    case "success": return <CheckCircle2 className={cls + " text-emerald-300"} />;
    default:        return <Info className={cls + " text-sky-300"} />;
  }
}

