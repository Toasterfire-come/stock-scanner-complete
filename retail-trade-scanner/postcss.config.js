module.exports = {
  plugins: [
    require('autoprefixer')({
      grid: 'autoplace'
    }),
    ...(process.env.NODE_ENV === 'production' ? [
      require('cssnano')({
        preset: ['default', {
          discardComments: {
            removeAll: true
          },
          normalizeWhitespace: true,
          minifySelectors: true,
          mergeRules: true
        }]
      })
    ] : [])
  ]
};