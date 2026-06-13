/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cyber theme colors
        "cyber-darker": "#0a0e27",
        "cyber-dark": "#0f172a",
        "cyber-card": "#1e293b",
        "cyber-light": "#1e293b",
        "cyber-lighter": "#334155",
        "cyber-border": "#475569",
        
        // Risk level colors
        "risk-safe": "#22c55e",
        "risk-low": "#3b82f6",
        "risk-medium": "#eab308",
        "risk-high": "#f97316",
        "risk-critical": "#dc2626",
        
        // Status colors
        safe: "#22c55e",
        low: "#3b82f6",
        medium: "#eab308",
        high: "#f97316",
        critical: "#dc2626",
        success: {
          50: "#f0fdf4",
          500: "#22c55e",
          900: "#15803d",
        },
        warning: {
          50: "#fefce8",
          500: "#eab308",
          900: "#713f12",
        },
        danger: {
          50: "#fef2f2",
          500: "#ef4444",
          900: "#7f1d1d",
        },
      },
      backgroundColor: {
        "dark-primary": "#0f172a",
        "dark-secondary": "#1e293b",
        "dark-tertiary": "#334155",
      },
      textColor: {
        "dark-primary": "#f1f5f9",
        "dark-secondary": "#cbd5e1",
      },
      fontSize: {
        xs: "0.75rem",
        sm: "0.875rem",
        base: "1rem",
        lg: "1.125rem",
        xl: "1.25rem",
        "2xl": "1.5rem",
        "3xl": "1.875rem",
        "4xl": "2.25rem",
      },
      boxShadow: {
        cyber: "0 4px 6px rgba(0, 0, 0, 0.3)",
        "neon-red": "0 0 20px rgba(220, 38, 38, 0.5)",
        "neon-blue": "0 0 20px rgba(59, 130, 246, 0.5)",
        "neon-yellow": "0 0 20px rgba(234, 179, 8, 0.5)",
        "neon-green": "0 0 20px rgba(34, 197, 94, 0.5)",
      },
      keyframes: {
        glow: {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.7 },
        },
        pulse: {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.5 },
        },
        shimmer: {
          "0%": { backgroundPosition: "-1000px 0" },
          "100%": { backgroundPosition: "1000px 0" },
        },
      },
      animation: {
        glow: "glow 2s ease-in-out infinite",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        shimmer: "shimmer 2s infinite",
      },
    },
  },
  plugins: [],
}
