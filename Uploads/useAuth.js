import { useState, useEffect } from 'react'

/**
 * Authentication Hook for NEXUS Protocol
 * 
 * Manages authentication state, login/logout functionality,
 * and session persistence using localStorage.
 */

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [user, setUser] = useState(null)

  // Check for existing session on mount
  useEffect(() => {
    const checkAuthStatus = () => {
      try {
        const savedAuth = localStorage.getItem('nexus_auth')
        const savedUser = localStorage.getItem('nexus_user')
        
        if (savedAuth === 'true' && savedUser) {
          setIsAuthenticated(true)
          setUser(JSON.parse(savedUser))
        }
      } catch (error) {
        console.error('Error checking auth status:', error)
        // Clear corrupted data
        localStorage.removeItem('nexus_auth')
        localStorage.removeItem('nexus_user')
      } finally {
        setIsLoading(false)
      }
    }

    checkAuthStatus()
  }, [])

  const signIn = async (email, password) => {
    setIsLoading(true)
    
    try {
      // Simulate API call - replace with real authentication
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Mock user data - replace with real user data from API
      const userData = {
        id: '1',
        email: email,
        name: email.split('@')[0],
        role: 'trader',
        lastLogin: new Date().toISOString(),
        permissions: ['read', 'trade', 'hedge']
      }

      // Save to localStorage
      localStorage.setItem('nexus_auth', 'true')
      localStorage.setItem('nexus_user', JSON.stringify(userData))
      
      setIsAuthenticated(true)
      setUser(userData)
      
      return { success: true, user: userData }
    } catch (error) {
      console.error('Sign in error:', error)
      return { success: false, error: 'Authentication failed' }
    } finally {
      setIsLoading(false)
    }
  }

  const signOut = () => {
    // Clear localStorage
    localStorage.removeItem('nexus_auth')
    localStorage.removeItem('nexus_user')
    
    // Reset state
    setIsAuthenticated(false)
    setUser(null)
  }

  const updateUser = (userData) => {
    setUser(userData)
    localStorage.setItem('nexus_user', JSON.stringify(userData))
  }

  return {
    isAuthenticated,
    isLoading,
    user,
    signIn,
    signOut,
    updateUser
  }
}

