var path = require("path");
var webpack = require("webpack");

module.exports = {
  devtool: "eval",
  entry: ["./scripts/main.js", "./scss/styles.scss"],
  output: {
    path: path.join(__dirname, "dist"),
    filename: "./scripts/main.min.js",
    publicPath: "/dist/"
  },
  plugins: [
    new webpack.NoErrorsPlugin()
    ],
  watch: true,
  watchOptions: {
   poll: true
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        loaders: ["babel"],
        exclude: ["/node_modules/","/scripts/vendor/"],
        include: path.join(__dirname, "scripts")
      },
      {
        test: /\.json$/,
        loader: "json"
      },
      {
        test: /\.css$/,
        loader: "style!css"
      },
      {
        test: /\.scss$/,
        exclude: /node_modules/,
        loader: 'style!css?sourceMap!sass?sourceMap&sourceComments'
      }
    ]
  }
};
