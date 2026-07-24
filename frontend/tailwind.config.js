/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          500: '#0284c7',
          600: '#0284c7',
          900: '#0c4a6e',
        },
        slate: {
          850: '#111827',
          900: '#0f172a',
          950: '#020617',
        }
      }
    },
  },
  plugins: [],
}
