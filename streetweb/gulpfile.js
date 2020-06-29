
"use strict";

var fs = require("fs");

var gulp   = require('gulp');
var uglify = require('gulp-uglify');

var rename = require('gulp-rename');
var sourcemaps = require('gulp-sourcemaps');
var assign = require('lodash.assign');
// var gutil   = require('gulp-util');

var watchify   = require('watchify');
var browserify = require('browserify');
var babelify   = require('babelify');
const hmr = require('browserify-hmr');

var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var es     = require('event-stream');

const connect = require('gulp-connect');
const history = require('connect-history-api-fallback');
const { createProxyMiddleware } = require('http-proxy-middleware');
const url = require('url');
const runSequence = require('run-sequence');

var ENTRIES = [
    './src/admin.js',
];

// Source Map
var DEBUG = true;
var BROWSERIFY_CONFIG = {
    "entries": ENTRIES,
    "extensions": ['.js'],
    "debug": DEBUG
};
var BROWSERIFY_CONFIG_WECHAT = {
    "entries": ['./src/admin.js'],
    "extensions": ['.js'],
    "debug": DEBUG
}
var BABEL_OPTIONS = {
    "presets": ['es2015', 'react'],
    "ignore": [/\.\/node_modules\//],
    "plugins":[
        ["import",{"libraryName":"antd"}],
    ] ,
    "sourceMaps": true,
    "sourceMapsAbsolute": true,
};

function bundler() {
    return browserify(BROWSERIFY_CONFIG).transform('babelify', BABEL_OPTIONS);
}
var opts = assign({}, watchify.args, BROWSERIFY_CONFIG_WECHAT);
var b = watchify(browserify(opts)).transform('babelify', BABEL_OPTIONS);
function on_error(err){
    console.error(err);
    this.emit('end');
}

function reversion(){
    var template = fs.readFileSync("index.html", "utf8");

    ["admin.css", "admin.bundle.js"].forEach(function (fname, i){
        var re   = new RegExp(fname+"(.)*\"");
        var rnd  = Math.random().toString();
        template = template.replace(re, fname+"?_rnd="+rnd+'"');
    });
    fs.writeFileSync("index.html", template);
}

function dev() {
    create_dev_env();
    var jobs = ENTRIES.map(function (entry){
        var browserify_config = BROWSERIFY_CONFIG;
        browserify_config["entries"] = [entry];

        var bundle = watchify(browserify(BROWSERIFY_CONFIG)).transform('babelify', BABEL_OPTIONS);

        return bundle.bundle()
            .on('error', on_error)
            .pipe(source(entry))
            .pipe(buffer())
            .pipe(rename({
                dirname: '',
                suffix: '.bundle',
            }))
            .pipe(gulp.dest('./assets/js'));
    });

    reversion();

    return es.merge.apply(null, jobs);
}
function wechat_h5() {
    create_dev_env();
    return b.bundle()
        // 如果有错误发生，记录这些错误
        .on('error', on_error)
        .pipe(source('./src/admin.js'))
        .pipe(rename_bundle())
        // 可选项，如果你不需要缓存文件内容，就删除
        .pipe(buffer())
        .pipe(gulp.dest('./assets/js'));
}

function build() {
    DEBUG = false;
    process.env.NODE_ENV = 'development';
    create_build_env();

    var _bundler = bundler();

    var jobs = ENTRIES.map(function (entry){
        var browserify_config = BROWSERIFY_CONFIG;
        browserify_config["entries"] = [entry];

        var bundle = browserify(BROWSERIFY_CONFIG).transform('babelify', BABEL_OPTIONS);
        console.log(entry);
        return bundle.bundle()
            .on('error', on_error)
            .pipe(source(entry))
            .pipe(buffer())
            .pipe(rename({
                dirname: '',
                suffix: '.bundle'
            }))
            .pipe(gulp.dest('./assets/js'));
    });

    reversion();

    return es.merge.apply(null, jobs);
}
function build_r() {
    DEBUG = false;
    process.env.NODE_ENV = 'production';
    create_buildr_env();

    var _bundler = bundler();

    var jobs = ENTRIES.map(function (entry){
        var browserify_config = BROWSERIFY_CONFIG;
        browserify_config["entries"] = [entry];

        var bundle = browserify(BROWSERIFY_CONFIG).transform('babelify', BABEL_OPTIONS);
        return bundle.bundle()
            .on('error', on_error)
            .pipe(source(entry))
            .pipe(buffer())
            .pipe(rename({
                dirname: '',
                suffix: '.bundle'
            }))
            .pipe(gulp.dest('./assets/js'));
    });

    reversion();

    return es.merge.apply(null, jobs);
}
function create_dev_env (){
    var environ = JSON.stringify({});
    try{
        delete environ["production"];
    }catch(e){

    }
    fs.writeFileSync('./src/environ.json', environ);
}
function create_build_env (){
    var environ = JSON.stringify(process.env);
    fs.writeFileSync('./src/environ.json', environ);
}
function create_buildr_env (){
    process.env.production = "true";
    var environ = JSON.stringify(process.env);
    fs.writeFileSync('./src/environ.json', environ);
}
gulp.task('watch-w', wechat_h5);
b.on('update', function(ids) {  //监测文件改动
    ids.forEach(function(v) {
        if (v.indexOf('json') === -1) {
            console.log('bundle changed file:' + v);  //记录改动的文件名
        }
    });

    gulp.start('watch-w');  //触发打包js任务
  });


gulp.task('hmr', () => {
    const b = browserify({
        ...BROWSERIFY_CONFIG,
        plugin: [hmr, watchify],
    }).transform(babelify, BABEL_OPTIONS);

    const bundle = () => {
        b.bundle()
            .on('error', err => {
                console.log(`Browserify Error ${err.message}`);
            })
            .pipe(source(ENTRIES[0]))
            .pipe(buffer())
            .pipe(sourcemaps.init({loadMaps: true}))
            .pipe(sourcemaps.write('./maps'))
            .pipe(rename({
                dirname: '',
                suffix: '.bundle'
            }))
            .pipe(gulp.dest('./assets/js'));
    };

    b.on('update', bundle);
    bundle();
});

// gulp watch --env=production
gulp.task('build', build);
gulp.task('build-r', build_r);


gulp.task('watch', function () {
    gulp.watch('./src/**/*.*', () => {
        runSequence('build', 'reload');
    });
});

gulp.task('webserver', () => {
    connect.server({
        livereload: true,
        port: 2333,
        middleware: (conn, opt) => ([
            createProxyMiddleware('/admin', {
                target: 'http://server.fzstack.com',
                changeOrigin: true,
            }),
            createProxyMiddleware('/static', {
                target: 'http://server.fzstack.com',
                changeOrigin: true,
            }),
            history(),
        ])
    });
});

gulp.task('reload', () => {
    gulp.src("./src/**/*.*")
        .pipe(connect.reload());
});

gulp.task('dev', ['build', 'webserver', 'watch'], () => {
    console.log('dev')
});

gulp.task('default', ['dev']);
