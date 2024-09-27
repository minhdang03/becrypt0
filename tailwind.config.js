module.exports = {
  purge: ['./templates/**/*.html', './static/**/*.js'],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      colors: {
        customBlue: '#1DA1F2',
        customYellow: '#FFAD1F',
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
}