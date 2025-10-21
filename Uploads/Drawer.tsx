import React, { useEffect, useRef } from "react";
import { createPortal } from "react-dom";

/**
 * Dependency-free Tailwind Drawer (replaces `vaul`)
 * -------------------------------------------------
 * - Pure React + TailwindCSS (no extra packages)
 * - Accessible: role="dialog", aria-modal, ESC to close, focus return
 * - Click backdrop to dismiss
 * - Body scroll lock when open
 * - Sides: "right" | "bottom"
 * - Optional header title and footer actions
 *
 * Usage:
 *   const [open, setOpen] = useState(false)
 *   <Drawer open={open} onClose={()=>setOpen(false)} title="Quick Actions">
 *     ...content
 *   </Drawer>
 */

export type DrawerSide = "right" | "bottom";

export interface DrawerProps {
  open: boolean;
  onClose: () => void;
  side?: DrawerSide;
  title?: React.ReactNode;
  className?: string;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  /**
   * If provided, focus will move to this ref when the drawer opens.
   * Otherwise the drawer container itself is focused.
   */
  initialFocusRef?: React.RefObject<HTMLElement>;
}

function cn(...xs: Array<string | false | null | undefined>) {
  return xs.filter(Boolean).join(" ");
}

export default function Drawer({
  open,
  onClose,
  side = "right",
  title,
  className,
  children,
  footer,
  initialFocusRef,
}: DrawerProps) {
  const mountRef = useRef<HTMLElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const triggerRef = useRef<HTMLElement | null>(null);

  // Create portal mount node once
  useEffect(() => {
    if (!mountRef.current) {
      const el = document.createElement("div");
      el.setAttribute("data-nexus-drawer-root", "");
      document.body.appendChild(el);
      mountRef.current = el as unknown as HTMLElement;
    }
    return () => {
      if (mountRef.current) {
        mountRef.current.remove();
        mountRef.current = null;
      }
    };
  }, []);

  // Body scroll lock
  useEffect(() => {
    const prev = document.body.style.overflow;
    if (open) document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  // Focus management: store active element, move focus to drawer, restore on close
  useEffect(() => {
    const active = (document.activeElement as HTMLElement) || null;
    if (open) {
      triggerRef.current = active;
      const toFocus = initialFocusRef?.current || containerRef.current;
      setTimeout(() => toFocus?.focus(), 0);
    } else if (triggerRef.current) {
      setTimeout(() => triggerRef.current?.focus?.(), 0);
    }
  }, [open, initialFocusRef]);

  // ESC to close
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open || !mountRef.current) return null;

  const isRight = side === "right";

  return createPortal(
    <div
      className="fixed inset-0 z-50"
      aria-hidden={!open}
    >
      {/* Backdrop */}
      <button
        aria-label="Close drawer"
        className="absolute inset-0 h-full w-full cursor-default bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <div
        ref={containerRef}
        role="dialog"
        aria-modal="true"
        aria-label={typeof title === "string" ? title : undefined}
        tabIndex={-1}
        className={cn(
          "absolute flex max-h-[96vh] min-h-[40vh] w-full outline-none",
          isRight ? "right-0 top-0 h-full max-w-lg" : "bottom-0 left-0 max-w-none",
        )}
        onClick={(e) => e.stopPropagation()}
      >
        <div
          className={cn(
            "flex w-full flex-col rounded-t-2xl border border-white/10 bg-black/60 text-white shadow-2xl backdrop-blur-xl",
            isRight ? "h-full rounded-l-2xl rounded-tr-none" : "",
            className,
          )}
          style={{
            // simple slide-in animation (no deps)
            animation: `${isRight ? "nexus-slide-right" : "nexus-slide-up"} 220ms cubic-bezier(.2,.8,.16,1) both`,
          }}
        >
          <div className="flex items-center justify-between gap-4 border-b border-white/10 p-4">
            <div className="text-sm font-semibold text-white/90">{title}</div>
            <button
              onClick={onClose}
              className="rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-xs text-white/80 hover:bg-white/10"
            >
              Close
            </button>
          </div>

          <div className="min-h-0 flex-1 overflow-auto p-4">
            {children}
          </div>

          {footer && (
            <div className="border-t border-white/10 p-3">{footer}</div>
          )}
        </div>
      </div>

      {/* Keyframes */}
      <style>{`
        @keyframes nexus-slide-up { from { transform: translateY(16px); opacity: 0 } to { transform: translateY(0); opacity: 1 } }
        @keyframes nexus-slide-right { from { transform: translateX(16px); opacity: 0 } to { transform: translateX(0); opacity: 1 } }
      `}</style>
    </div>,
    mountRef.current,
  );
}

