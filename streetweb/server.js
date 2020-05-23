"use strict";

const http    = require('http');
const fs      = require('fs');
const express = require('express');

const getRawBody = require('raw-body');
const typer      = require('media-typer');

const app = express();

const admin_index_handle = function (req, res){
    var content = fs.readFileSync("./index.html", "utf8");
    res.status(200);
    res.send(content);
};

app.use(function (req, res, next) {
    let options = {
        length: req.headers['content-length'], limit: '1mb',
        // encoding: typer.parse(req.headers['content-type']).parameters.charset
    };
    let cb = function (err, string) {
        if (err) string = "";
        req.bodyBytes = string;
        next();
    };
    getRawBody(req, options, cb);
});

app.use("/assets",  express.static("assets"));

var request = function (method, path, headers, body, callback){
    var proxy_host = "dw.airm2m.com"; // dw.airm2m.com, lottery.dsnminsu.com , 127.0.0.1:9001
    var proxy_port = 80;
    var handler = function(response) {
        var reply = '';
        response.on('data', function(chunk) {
            reply += chunk;
        });
        response.on('end', function() {
            callback(response.statusCode, response.headers, reply);
        });
    };
    var options = {
        host: proxy_host,
        path: path,
        port: proxy_port,
        method : method.toLocaleUpperCase(),
        headers: headers
    };
    headers.host = proxy_host;
    var request = http.request(options, handler);
    request.write(body);
    request.end();
};
["/street_machine/adminpage/",'/street_machine/adminpage/*'].forEach(function (path, i){
    app.get(path, admin_index_handle);
});
app.use("/street_machine/admin", function (req, res){
    // let url = proxy_host + req.originalUrl;
    // if ( url.indexOf("?") != -1 ) {
    //     url += "&token=" + AUTH_TOKEN;
    // } else {
    //     url += "?token=" + AUTH_TOKEN;
    // }
    let path    = "/street_machine/admin"+req.path;
    let method  = req.method.toLowerCase();
    let rawBody = req.bodyBytes.toString();
    let index = 0;
    for (var key in req.query) {
        if (index === 0) {
            path = path + "?" + key + "=" + req.query[key];
        } else {
            path = path + "&" + key + "=" + req.query[key];
        }
        index++;
    }

    let callback = function (status_code, headers, raw_body){
        res.writeHead(status_code, headers);
        //console.log(raw_body);
        res.write(raw_body);
        res.end();
    };
    if ( "accept-encoding" in req.headers ) {
        delete req.headers["accept-encoding"];
    }
    request(method, path, req.headers, rawBody, callback);
});




var server = app.listen(8088, function () {
    var host = server.address().address;
    var port = server.address().port;
    console.log('Example app listening at http://%s:%s', host, port);
});
