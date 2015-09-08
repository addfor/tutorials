# ensemble-explore

The application is composed of two main parts: a Python server (also available as a module), and a web client.

The web client's code and stylesheets are written in [CoffeeScript](http://coffeescript.org) and [Less](http://lesscss.org). For this reason, an intermediate compilation step is required.

The server module doesn't need any compilation/building, but the following Python packages need to be installed (all of them are available on the Python Package Index, and therefore are installable simply using `pip`):

* flask
* flask-bower
* scikit-learn
* pandas
* numpy
* enum34

The server is only compatible with, and tested only on, Python 2.7.

## Building the client

All needed tools run on the Node.js platform. A working installation of Node.js and npm is the only requirement for the user. All other dependencies are automatically retrieved using npm, and the compilation process is mostly automatic.

1. If you haven't done it already, install Node. You can directly follow the instructions on [the official site](https://nodejs.org/). The Node Package Manager, `npm`, is included with the standard Node distribution.

2. Install all dependencies. It's sufficient to run the following command from the project directory:
```sh
npm install
```

3. To build the project, we'll use a number of executables installed by `npm install`. To make them available from the command line without specifying the full path every time, add the `node_modules/.bin` directory to the executable find path.
On most Unix shells, assuming the current working directory is the project's base directory, you can do:
```sh
export PATH=$PATH:$(npm bin)
```

4. Now run the actual compilation. The `exorcist` program also generates separate source maps, which are useful if you want to continue the development, either contributing to this repository, or on your own.
(This is also the only step you need to repeat if you modify the app's code or stylesheets.)
You just need the following commands:
```sh
browserify coffee/main.coffee --debug | exorcist static/app.js.map > static/app.js
lessc less/style.less > static/style.css
```
*(In the future, an automatic build system based on Gulp.js will be added. Anyway, those two are the only commands needed to build the app completely.)*


