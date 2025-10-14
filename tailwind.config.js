/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",   // todos os HTML do Flask
    "./app/static/scripts/**/*.js", // scripts do static
    "./app/static/src/**/*.css"     // se usar @apply em CSS
  ],
  theme: {
    extend: {
      colors: {
        begePrincipal: "#b7a696",
        begeForte: "#846c5b",
        begeFraco2: "#F0ECE6",
        brancoPrincipal: "#ffffff",
        brancoCinza: "#eeeeee",
        brancoBorda: "#CECECE",
        brancoForm: "#EBEBEB",
        bgSidebar: "#ad9a8a",
        cinza: "#ccc",
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'], // use o nome da fonte que escolheu
      },
      spacing: {
        '700': '700px'
      },
      screens: {
        'tablet': '800px'
      }
    },
  },
  plugins: [],
}