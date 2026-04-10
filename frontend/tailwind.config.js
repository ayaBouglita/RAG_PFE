/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          400: '#4C9CDA',
          500: '#006EC3',
          600: '#12239E',
          700: '#12239E',
        },
        accent: {
          400: '#8BAFCE',
          500: '#7FBF2A',
        },
      }
    },
  },
  plugins: [],
}
