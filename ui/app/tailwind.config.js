import {definePreset} from '@primeuix/themes'

module.exports = {
  darkMode: ['selector', '.p-dark'],
  content: ['./components/**/*.{vue,js,ts}', './pages/**/*.{vue,js,ts}'],
  theme: {
    extend: {},
  },
  // plugins: [require('tailwindcss-primeui')],
}
