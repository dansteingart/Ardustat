/* taxman by Marcello Bastea-Forte - zlib license */
var EventEmitter = require('events').EventEmitter

module.exports = function(factory) {
    var cached, emitter
    function cacher(callback) {
        if (cached) {
            callback && callback(null, cacher.value)
        } else if (emitter) {
            callback && emitter.once('done', callback)
        } else {
            emitter = new EventEmitter
            factory(function(error, value) {
                if (!error) {
                    cacher.value = value
                    cached = true
                }
                callback && callback(error, value)
                if (emitter) {
                    emitter.emit('done', error, value)
                    emitter = null
                }
            })
        }
    }
    cacher.reset = function() {
        cached = false
        delete cacher.value
        if (emitter) {
            emitter.removeAllListeners('done')
            emitter = null
        }
    }
    return cacher
}