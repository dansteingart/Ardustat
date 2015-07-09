/* Waiter by Marcello Bastea-Forte - zlib license */
module.exports = function() {
    var unfinishedResults = [],
        finalCallback,
        timeoutHandle,
        lastError

    function resultFinished(result, error, value) {
        unfinishedResults = unfinishedResults.filter(function(o) { return o !== result })
        if (value) result.value = value
        if (error) result.error = lastError = error
        if (lastError || unfinishedResults.length == 0) {
            if (timeoutHandle) clearTimeout(timeoutHandle)
            if (finalCallback) finalCallback(lastError)
            finalCallback = undefined
        }
    }

    function waiter(callback) {
        if (finalCallback) throw new Error("Cannot create a waiter after waitForAll has been called")
        var result = function(error, value) { resultFinished(result, error, value) }
        unfinishedResults.push(result)
        callback && callback(result)
        return result
    }
    waiter.waitForAll = function(callback, timeout) {
        finalCallback = callback
        if (unfinishedResults.length == 0) {
            finalCallback(lastError)
        } else if (timeout) {
            timeoutHandle = setTimeout(function() {
                unfinishedResults.forEach(function(result) {
                    resultFinished(result, new Error("Timeout after "+timeout+" ms"))
                })
            }, timeout)
        }
    }
    Array.prototype.slice.call(arguments).forEach(waiter)
    return waiter
}