/*!
 * humanize-ms - index.js
 * Copyright(c) 2014 dead_horse <dead_horse@qq.com>
 * MIT Licensed
 */

'use strict';

/**
 * Module dependencies.
 */

var ms = require('ms');

module.exports = function (t) {
  if (typeof t === 'number') return t;
  return ms(t);
};
