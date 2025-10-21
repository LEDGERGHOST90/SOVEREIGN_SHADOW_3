import { motion } from 'framer-motion'
import { Zap } from 'lucide-react'

/**
 * Loading Spinner Component for NEXUS Protocol
 * 
 * Displays an animated loading state with the NEXUS branding
 */

const LoadingSpinner = ({ message = "Initializing NEXUS Protocol..." }) => {
  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center z-50">
      <div className="text-center">
        <motion.div
          animate={{ 
            rotate: 360,
            scale: [1, 1.1, 1]
          }}
          transition={{ 
            rotate: { duration: 2, repeat: Infinity, ease: "linear" },
            scale: { duration: 1, repeat: Infinity, ease: "easeInOut" }
          }}
          className="mb-6"
        >
          <Zap className="h-16 w-16 text-purple-400 mx-auto" />
        </motion.div>
        
        <motion.h2
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-2xl font-bold text-white mb-2"
        >
          NEXUS PROTOCOL
        </motion.h2>
        
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="text-purple-200"
        >
          {message}
        </motion.p>
        
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: "100%" }}
          transition={{ delay: 1, duration: 2, ease: "easeInOut" }}
          className="mt-6 h-1 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full max-w-xs mx-auto"
        />
      </div>
    </div>
  )
}

export default LoadingSpinner

