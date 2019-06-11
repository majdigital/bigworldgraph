var path = require('path');
var webpack = require('webpack');

module.exports = {
  devtool: 'eval',
  entry: ['./scripts/main.js', './scss/styles.scss'],
  output: {
    path: path.join(__dirname, 'dist'),
    filename: './scripts/main.min.js',
    publicPath: '/dist/'
  },
  plugins: [new webpack.NoEmitOnErrorsPlugin()],
  watch: true,
  watchOptions: {
    poll: true
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        loaders: ['babel-loader'],
        exclude: ['/node_modules/', '/scripts/vendor/'],
        include: path.join(__dirname, 'scripts')
      },
      {
        test: /\.json$/,
        loader: 'json-loader'
      },
      {
        test: /\.css$/,
        loader: 'style-loader!css'
      },
      {
        test: /\.scss$/,
        exclude: /node_modules/,
        loader:
          'style-loader!css-loader?sourceMap!sass-loader?sourceMap&sourceComments'
      }
    ]
  }
};
