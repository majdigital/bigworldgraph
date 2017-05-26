var path = require("path");
var webpack = require("webpack");
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const extractSass = new ExtractTextPlugin({ filename: "./css/styles.min.css" });

module.exports = {
  devtool: "eval",
  entry: ["./scripts/main.js"],
  output: {
    path: path.join(__dirname, "dist"),
    filename: "./scripts/main.min.js",
    publicPath: "/dist/"
  },
  plugins: [new webpack.NoErrorsPlugin(), extractSass],
  watch: true,
  module: {
    loaders: [
      {
        test: /\.js$/,
        loaders: ["babel"],
        exclude: /node_modules/,
        include: path.join(__dirname, "client")
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
  }
};
