// Start: data_loader_standalone.js
/* This is the version of the data loader that is used in the
 * non-standalone, web-server-backed version of the application */
window.DataLoader = {
    _treeNodes: {{ tree|safe }},
    _featuresInfo: {{ features_info|safe }},

    getTreeNodes: function (cb) {
		cb(DataLoader._treeNodes);
    },

    getFeaturesInfo: function(cb) {
		cb(DataLoader._featuresInfo);
    },
};
// End: data_loader_standalone.js