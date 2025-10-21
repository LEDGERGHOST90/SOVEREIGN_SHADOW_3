import { motion } from "framer-motion";

export function FloatingCoin({ label, from="#2a2a2f", to="#0f0f12", text="#e5e7eb", size=88, drift=18, delay=0 }) {
  return (
    <motion.div
      initial={{ y: 0, rotate: 0 }}
      animate={{ y: [0, -drift, 0], rotate: [0, 2, 0] }}
      transition={{ duration: 6 + delay, repeat: Infinity, ease: "easeInOut" }}
      className="rounded-full shadow-xl"
      style={{ width: size, height: size, background: `linear-gradient(135deg, ${from}, ${to})` }}
    >
      <div className="grid h-full w-full place-items-center font-black" style={{ color: text, fontSize: Math.round(size * 0.32) }}>
        {label}
      </div>
    </motion.div>
  );
}

