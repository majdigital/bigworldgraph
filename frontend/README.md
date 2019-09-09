# Bigworldgraph frontend

Project based on [this boilerplate](https://github.com/wbkd/webpack-starter).


### Installation

```
npm install
```

### Start Dev Server

```
npm run dev
```

### Build Prod Version

```
npm run build
```

### Features:

* ES6 Support via [babel](https://babeljs.io/) (v7)
* SASS Support via [sass-loader](https://github.com/jtangelder/sass-loader)
* Linting via [eslint-loader](https://github.com/MoOx/eslint-loader)

When you run `npm run build` we use the [mini-css-extract-plugin](https://github.com/webpack-contrib/mini-css-extract-plugin) to move the css to a separate file. The css file gets included in the head of the `index.html`.

### Production server

```
npm run start
```

It will start an http-server instance.