var path = require("path");
var webpack = require("webpack");
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const extractSass = new ExtractTextPlugin({ filename: "./css/styles.min.css" });

module.exports = {
  entry: ["./scripts/main.js", "./scss/styles.scss"],
  output: {
    path: path.join(__dirname, "dist"),
    filename: "./scripts/main.min.js",
    publicPath: "/dist/",
    sourceMapFilename: '[name].map'
  },
  module: {
        loaders: [
        {
          test: /\.js$/,
          loaders: ["babel-loader"],
          exclude: /node_modules/,
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
        use: extractSass.extract({
          use: [
            {
              loader: "css-loader"
            },
            {
              loader: "sass-loader"
            }
          ],
          // use style-loader in development
          fallback: "style-loader"
        })
      }
      ]
    },
  plugins: [
    new webpack.LoaderOptionsPlugin({
      minimize: true,
      debug: false
    }),
    new webpack.optimize.UglifyJsPlugin({
      beautify: false,
      mangle: {
        screw_ie8: true,
        keep_fnames: true
      },
      compress: {
        screw_ie8: true
      },
      comments: false
    }),
    extractSass
  ]
}