"use strict";

// Just Like Python Range function.
window.range = function (start, stop, step) {
    if (stop == null) {
        stop = start || 0;
        start = 0;
    }
    step = step || 1;
    let length = Math.max(Math.ceil((stop - start) / step), 0);
    let arr = Array(length);
    let idx = 0;
    for (idx = 0; idx < length; idx++, start += step) {
        arr[idx] = start;
    }
    return arr;
};

window.random = function (max){
    // 数字伪随机串
    return window.range(max).map(function (n){
        return Math.floor(Math.random()*10).toString();
    }).join("");
};

window.randomInt = function (min, max){
    return Math.floor(Math.random() * (max - min + 1)) + min;
};

/**
    @ 自动在 数字 前面补零
    var number = 12;
    console.log(number.zfill(5));
    '0000012'
**/
window.Number.prototype.zfill = function (size){
    size  = size || 2;
    let s = this.toString();
    while (s.length < size) {
        s = "0" + s;
    }
    return s;
};

window.unichr = function (code){
    return String.fromCharCode(parseInt(code));
};
window.ord = function (char){
    return char.charCodeAt(0);
};

window.repr = function (s) {
    let bytes = s.bytes();
    let hex_codes = [];
    let is_unicode = bytes.every(function (byte, i){
        console.log( byte );
        let hex_code = byte.toString(16);
        hex_codes.push( hex_code );
        return hex_code == parseInt(hex_code).toString();
    });
    if ( is_unicode == true ) {
        return hex_codes.join("\\u");
    } else {
        return hex_codes.join("\\x");
    }
};

window.String.prototype.to_utf8 = function (){
    // http://monsur.hossa.in/2012/07/20/utf-8-in-javascript.html
    return unescape(encodeURIComponent(this));
};
window.String.prototype.from_utf8 = function (){
    try{
        return decodeURIComponent(escape(this));
    }catch(e){
        console.warn("invalid UTF-8 ...");
        return this;
    }
};

window.String.prototype.chars = function (){
    let self = this;
    return window.range(this.length).map(function (idx, i){
        return self[idx];
    });
};

/**
    let s = "Ab我和Ab";
    let utf8_slice    = s.to_utf8().bytes(); // [65, 98, 230, 136, 145, 229, 146, 140, 65, 98]
    let unicode_slice = s.bytes();           // [65, 98, 25105, 21644, 65, 98]
**/

window.String.prototype.bytes = function (){
    return this.chars().map(function (char, i){
        return char.charCodeAt(0);
    });
};

/**
    @ 排序算法

**/
window.Array.prototype.bubble = function () {
    let length, i, j, tmp;
    let items = this;
    length = items.length;
    for (i=(length-1); i>=0; i--) {
        for (j=(length-i); j>0; j--) {
            if (items[j] < items[j - 1]) {
                tmp = items[j];
                items[j] = items[j - 1];
                items[j - 1] = tmp;
            }
        }
    }
};

export default {};