var test = require('tap').test;
var mdeps = require('module-deps');
var bpack = require('browser-pack');
var insert = require('../');
var concat = require('concat-stream');
var vm = require('vm');

test('always insert', function (t) {
    t.plan(6);
    var s = mdeps({
        transform: inserter,
        modules: {
            buffer: require.resolve('buffer/')
        }
    });
    s.pipe(bpack({ raw: true })).pipe(concat(function (src) {
        var c = {
            t: t,
            self: { xyz: 555 }
        };
        vm.runInNewContext(src, c);
    }));
    s.end(__dirname + '/always/main.js');
});

function inserter (file) {
    return insert(file, { always: true });
}
