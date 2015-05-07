from __future__ import print_function # For py 2.7 compat

from IPython.html import widgets # Widget definitions
from IPython.display import display # Used to display widgets in the notebook
from IPython.utils.traitlets import Unicode # Used to declare attributes of our widget

class HandsonTableWidget(widgets.DOMWidget):
    _view_name = Unicode('HandsonTableView', sync=True)
    value = Unicode(sync=True)

JS = """
var table_id = 0;
require(["widgets/js/widget"], function(WidgetManager){    
    // Define the HandsonTableView
    var HandsonTableView = IPython.DOMWidgetView.extend({
        
        render: function(){
            // CREATION OF THE WIDGET IN THE NOTEBOOK.
            
            // Add a <div> in the widget area.
            this.$table = $('<div />')
                .attr('id', 'table_' + (table_id++))
                .appendTo(this.$el);
            // Create the Handsontable table.
            this.$table.handsontable({
            });
            
        },
        
        update: function() {
            // PYTHON --> JS UPDATE.
            
            // Get the model's JSON string, and parse it.
            var data = $.parseJSON(this.model.get('value'));
            // Give it to the Handsontable widget.
            this.$table.handsontable({data: data});
            
            // Don't touch this...
            return HandsonTableView.__super__.update.apply(this);
        },
        
        // Tell Backbone to listen to the change event of input controls.
        events: {"change": "handle_table_change"},
        
        handle_table_change: function(event) {
            // JS --> PYTHON UPDATE.
            
            // Get the table instance.
            var ht = this.$table.handsontable('getInstance');
            // Get the data, and serialize it in JSON.
            var json = JSON.stringify(ht.getData());
            // Update the model with the JSON string.
            this.model.set('value', json);
            
            // Don't touch this...
            this.touch();
        },
    });
    
    // Register the HandsonTableView with the widget manager.
    WidgetManager.register_widget_view('HandsonTableView', HandsonTableView);
});
"""

from IPython.display import display, Javascript

display(Javascript(JS))


import StringIO
import numpy as np
import pandas as pd

class DataSheet(object):
    def __init__(self, data):
        self.df = pd.DataFrame(data)
        self._widget = HandsonTableWidget()
        self._widget.on_trait_change(self._on_data_changed, 'value')
        self._widget.on_displayed(self._on_displayed)
        
    def _on_displayed(self, e):
        # DataFrame ==> Widget (upon initialization only)
        json = self.df.to_json(orient='values')
        self._widget.value = json
        
    def _on_data_changed(self, e, val):
        # Widget ==> DataFrame (called every time the user
        # changes a value in the graphical widget)
        buf = StringIO.StringIO(val)
        self.df = pd.read_json(buf, orient='values')
                
    def edit(self):
        display(self._widget)
        
    def _repr_html_(self):
        return self.df._repr_html_()

    
