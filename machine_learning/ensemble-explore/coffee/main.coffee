
treeUi = require './tree.coffee'
query = require './query.coffee'
$ = require 'jquery'
d3 = require 'd3'
React = require 'react'
_ = require 'underscore'
jQueryUI = require 'jquery-ui-rjs'
jQueryUI.register($)


# colormap = [
#     '#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c',
#     '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928',
# ]
# leafFill = 'white'
# leafStroke = '#a0a0a0'
# getCategoryColor = (i) -> colormap[ (i%_.size(colormap)) ]

colormap = d3.scale.category20c()
leafFill = 'white'
leafStroke = '#a0a0a0'
getCategoryColor = (i) -> colormap(i)

mean = (values) ->
    if not values? or values.length == 0
        return null
    sum = 0
    sum += num for num in values
    return sum / values.length

SidebarText = React.createClass
    render: () ->
        React.DOM.div
            className: "sidebar-item-value"
            @props.text
    
SidebarItem = React.createClass
    getInitialState: -> { expanded: true }
    
    render: () ->
        React.DOM.div
            className: "sidebar-item"
            React.DOM.div
                className: "sidebar-item-title"
                @props.title
            React.DOM.button
                className: "sidebar-item-toggle"
                onClick: =>
                    @setState expanded: not (@state.expanded)
                if @state.expanded
                    React.DOM.i className: "fa fa-minus"
                else
                    React.DOM.i className: "fa fa-plus"
            React.DOM.div
                style:
                    display: if @state.expanded then null else 'none'
                @props.content

histStyle =
    margin: { top: 10, bottom: 10, left: 15, right: 15 }
    width: 300
    height: 120

SidebarDistHist = React.createClass
    getInitialState: () ->
        element = document.createElement('div')
        
        svg = d3.select(element)
            .append 'svg'
            .attr 'width', histStyle.width
            .attr 'height', histStyle.height

        svg.append('g').attr('id', 'axis')
        tickbar = svg.append('g').attr('id', 'tickbar')
        tickbar.append('g').attr('class', 'ticks')
        tickbar.append('g').attr('class', 'avg')
            .append('polygon')
            .attr('points', '-4,0 0,-5 4,0')

        return { element: element }
    
    componentDidMount: () ->
        container = @refs['hist-container'].getDOMNode()
        $(container).empty().append(@state.element)

    renderD3: () ->
        {width, height, margin} = histStyle
        bins = null
        x = null
        domain = null
        
        nBins = @props.numBins ? 15
        histogram = d3.layout.histogram().bins(nBins)

        data = @props.data
        bins = histogram(data)
        domain = [
            @props.min ? _.min(data),
            @props.max ? _.max(data)
        ]
        
        x = d3.scale.linear()
            .domain domain
            .range [margin.left, width - margin.right]

        xAxis = d3.svg.axis()
            .scale x
            # .tickValues bins.map (d) -> d.x
            .tickFormat d3.format(@props.tickFormat or '.3f')
            .tickSize 1
            .orient 'bottom'

        xAxisHeight = 30
        tickBarHeight = 8

        y = d3.scale.linear()
            .domain [0, d3.max(bins, (d) -> d.y)]
            .range [
                height - margin.bottom - xAxisHeight - tickBarHeight,
                margin.top + 10
            ]

        element = @state.element
        svg = d3.select(element).select('svg')
        
        bar = svg.selectAll('.bar').data(bins)

        enter = bar.enter().append('g').attr('class', 'bar')
        enter.append('text')
        enter.append('rect')
	
        bar.exit().remove()
        
        bar.attr 'transform', (d) -> "translate("+x(d.x)+", 0)"

        bar.select 'rect'
            .attr 'width', (d) ->
                Math.max(0, x(d.x + d.dx) - x(d.x) - 1)
            .transition().attr 'height', (d) -> y(0) - y(d.y)
            .attr 'y', (d) -> y(d.y)

        bar.select 'text'
            .style 'text-anchor', 'middle'
            .text (d,i) -> if d.y == 0 then "" else d.y+"" 
            .attr 'transform', (d) ->
                tx = (x(d.x + d.dx) - x(d.x) - 1) / 2
                ty = y(d.y)-10
                'translate('+tx+', '+ty+')'

        if @props.data?
            ticks = svg.select '#tickbar .ticks'
                .selectAll 'line'
                .data @props.data
            ticks.enter().append('line')
            ticks.exit().remove()
            ticks.attr 'x1', (d) -> x(d)
                .attr 'x2', (d) -> x(d)
                .attr 'y1', height - margin.bottom - xAxisHeight
                .attr 'y2', height - margin.bottom - xAxisHeight - tickBarHeight

            if @avg?
                avgCur = svg.select('#tickbar .avg')
                avgCur.attr 'transform',
                    'translate('+x(@avg)+', ' +
                    (height - margin.bottom - xAxisHeight)+')'

        axis = svg.select('#axis')
        axis.attr 'transform',
            'translate(0, '+(height - margin.bottom - xAxisHeight)+')'
            
        axis.select('*').remove()
        axis.append 'g'
            .call xAxis
            .selectAll 'text'
            .attr 'style', ''
            .style 'text-anchor', 'left'
            .attr 'transform', 'translate(5,0) rotate(60)'
    
    render: () ->
        try
            @renderD3()
            
        @avg = @props.avg or mean(@props.data)
        return React.DOM.div null,
            React.DOM.ul null,
                React.DOM.li null,
                    "avg: ", React.DOM.span(null, @avg+"")
            React.DOM.div
                ref: 'hist-container'
                className: 'sidebar-histogram'

SidebarDistribution = React.createClass
    render: () ->
        data = @props.data
        
        if not data? or data.length == 0
            React.createElement SidebarText, text: "N/A"
        else if data.length == 1
            React.createElement SidebarText, text: data[0]+""
        else if data.length < 3
            React.DOM.ul null,
                React.DOM.li null, data[0]+"",
                React.DOM.li null, data[1]+""
        else
            React.createElement SidebarDistHist,
                data: data
                min: @props.min
                max: @props.max
                tickFormat: @props.tickFormat
            
SidebarChildrenBtn = React.createClass
    render: () ->
        if @props.isLeaf or not @props.count? or @props.count == 0
            React.createElement SidebarText,
                text: @props.count or 'N/A'
        else
            React.DOM.button
                className: "btn-load-children " +
                    if @props.disabled then 'disabled' else ''
                onClick: @props.onClick
                @props.count
                React.DOM.i className: 'fa fa-download'

SidebarFeatureList = React.createClass
    getInitialState: -> { importanceAlgo: 'gini' }
    
    render: () ->
        features = @props.featuresInfo
        
        importanceAttrName = 'importance_' + @state.importanceAlgo
        getImportance = (f) -> f[importanceAttrName]
        
        leafInfo = _.extend features["-2"], id: "-2"
        features = _.omit features, "-2"
        featuresList = _.map features, (f, id) -> _.extend(f, id: id)
        featuresList = _.sortBy featuresList, (f) -> -getImportance(f)
        if leafInfo
            featuresList = [leafInfo].concat(featuresList)
            
        importances = _.map features, getImportance
        maxImportance = _.max importances
        minImportance = _.min importances
        importanceRange = maxImportance - minImportance

        onFilterChange = @props.onFilterChange

        head = React.DOM.tr className: 'header',
            React.DOM.td className: 'cursorSpace',
            React.DOM.td className: 'selection',
                React.DOM.div
                    className: 'checkbox'
                    onClick: =>
                        @props.onFilterChange? 'toggleAll'
                    '*'
            React.DOM.td className: 'importance',
                React.DOM.div className: 'name',
                    'select/deselect all features'

        rows = for f in featuresList
            featureId = f.id
            selected = (featureId == @props.selectedNode?.featureId+"")

            cursorSpace = React.DOM.td 
                className: "cursorSpace " +
                    (if selected then 'selected' else ''),
                style:
                    textAlign: 'right'
                    visibility: if selected then 'visible' else 'hidden'
                React.DOM.span null, '▶'

            selection = React.DOM.td
                className: 'selection',
                React.DOM.div
                    className: 'checkbox ' +
                        (if f.isFiltered then 'on' else '')
                    onClick: ((featureId) -> ->
                        onFilterChange? 'toggle', featureId)(featureId)

            importance = getImportance(f)
            if importance < 0
                marginPerc = (importance - minImportance)
                widthPerc = -importance
            else
                marginPerc = -Math.min(minImportance, 0)
                widthPerc = importance
                
            marginPerc = marginPerc / importanceRange * 100
            widthPerc = widthPerc / importanceRange * 100
            
            importance = React.DOM.td className: 'importance',
                React.DOM.span
                    className: 'name'
                    f.name
                React.DOM.div
                    key: @state.importanceAlgo
                    className: 'bar'
                    style:
                        width: widthPerc+'%'
                        marginLeft: marginPerc+'%'
                        backgroundColor: f.fill
                        borderColor: f.stroke

            React.DOM.tr
                className: if f.isFiltered then 'ui-selected' else ''
                # attribute is spelt in camelCase for jQuery
                'data-feature-id': featureId
                cursorSpace, selection, importance

        table = React.DOM.table
            key: 'features-table'
            className: 'unselectable'
            style:
                width: '360px'
            React.DOM.thead null, head
            React.DOM.tbody null, rows

        algoSelect = React.DOM.select
            className: 'algo-select'
            value: @state.importanceAlgo
            onChange: (event) => 
                @setState importanceAlgo: event.target.value
            React.DOM.option { value: 'gini' }, 'Gini index decrease'
            React.DOM.option { value: 'oob' },  'OOB estimation accuracy decrease'
        
        React.DOM.div
            className: 'sidebar-feature-list'
            algoSelect
            React.DOM.div
                ref: 'container'
                style:
                    position: 'relative'
                table

    componentDidMount: () -> @reinstallSelectable()
    
    reinstallSelectable: () ->
        container = @refs['container'].getDOMNode()
        $(container).find("table tbody").selectable
            distance: 20
            delay: 100
            filter: 'tr:not(.header)'
            appendTo: container
            stop: (event) =>
                ids = []
                $(event.target).find(".ui-selected").each (i, e) ->
                    # the attribute is spelt 'data-feature-id' for React
                    id =  $(e).data('featureId')
                    if id? then ids.push id
                if ids.length > 0
                    @props.onFilterChange? 'only', ids

Breadcrumbs = React.createClass
    render: () ->
        path = []
        n = @props.node
        while n?.parent?
            path.push(n)
            n = n.parent
        path.reverse()

        crumbs = _.map path, (node) =>
            onClick = () => @props.onNodeSelect(node)
            f = @props.featuresInfo[node.featureId]
            React.DOM.div
                className: 'leaf item',
                onClick: onClick,
                React.DOM.span null,
                    f.name
                    if node.featureId != "-2"
                        React.DOM.i className: 'fa fa-caret-right'
                React.DOM.div
                    className: 'underline-box'
                    style:
                        backgroundColor: f.fill
                        borderColor: f.stroke

        React.DOM.div className: 'breadcrumbs',
            crumbs

Sidebar = React.createClass
    render: ->
        clsName = if @props.node? then 'sidebar' else 'sidebar-null'
        featuresInfo = @props.featuresInfo
        node = @props.node
        
        panes = []

        panes.push React.createElement SidebarItem,
            key: 'sidebar-id'
            title: 'ID'
            content: React.createElement SidebarText,
                text: node?.id or "N/A"

        panes.push React.createElement SidebarItem,
            key: 'sidebar-count'
            title: 'Count',
            content: React.createElement SidebarText,
                text: node?.count or 'N/A'

        childrenBtnDisabled =
            if node?
                _.all node.childrenIds, (childId) =>
                    @props.tree[childId].visible
            
        panes.push React.createElement SidebarItem,
            key: 'sidebar-children'
            title: 'Children',
            content: React.createElement SidebarChildrenBtn,
                count: node?.numChildren
                isLeaf: node?.isLeaf ? false
                disabled: childrenBtnDisabled
                onClick: () => @props.onChildrenRequest(node.id)

        panes.push React.createElement SidebarItem,
            key: 'sidebar-item'
            title: 'Map program'
            content: React.createElement MapProgramInput,
                onMapProgramChange: (args...) =>
                    @props.onMapProgramChange(args...)
        
        panes.push React.createElement SidebarItem,
            title: 'Features'
            content: React.createElement SidebarFeatureList,
                featuresInfo: @props.featuresInfo
                selectedNode: node,
                onFilterChange: @props.onFilterChange
    
        if node?
            panes.push React.createElement SidebarItem,
                key: 'sidebar-value'
                title: 'Output values'
                content: React.DOM.div null,
                    for outputId, outputVals of node.outputs
                        React.createElement SidebarDistribution,
                            data: outputVals
                            min: _.min @props.tree[0].outputs[outputId]
                            max: _.max @props.tree[0].outputs[outputId]

        panes.push React.createElement SidebarItem,
            key: 'sidebar-threshold'
            title: 'Thresholds'
            content: React.createElement SidebarDistribution,
                data: node?.threshold

        panes.push React.createElement SidebarItem,
            key: 'sidebar-num-samples'
            title: '# Samples',
            content: React.createElement SidebarDistribution,
                data: node?.num_samples
                tickFormat: '.0f'
                
        React.DOM.div
            id: "sidebar"
            className: clsName
            panes

MapProgramInput = React.createClass
    getInitialState: -> {
        timeoutID: null,
        exception: null,
        enabled: true
    }
    
    render: ->
        onTimeout = =>
            if @state.enabled
                text = @refs['input'].getDOMNode().value
                @setState exception: null
                try
                    ast = query.parseProgram text
                catch e
                    @setState exception: e
                @props.onMapProgramChange ast
            else
                @props.onMapProgramChange null
        
        React.DOM.div className: 'map-program',
            React.DOM.textarea
                ref: 'input'
                onChange: if @props.onMapProgramChange? then () =>
                    if @timeoutID?
                        window.clearTimeout @timeoutID
                    @timeoutID = setTimeout(onTimeout, 600)
            React.DOM.label null,
                React.DOM.input
                    type: 'checkbox'
                    checked: @state.enabled
                    onChange: (event) =>
                        @setState enabled: event.target.checked
                        # actual delay is clamped to a minimum value
                        # of 4ms, as per HTML5 spec; but we don't
                        # care, we just want the minimum
                        @timeoutID = setTimeout(onTimeout, 0)
                'Enabled'
            if @state.exception?
                exc = @state.exception
                if exc.hasOwnProperty "ast"
                    React.DOM.div className: 'status exception',
                        exc.ast.start+": "+exc.ast.end+": "+exc.message
                else
                    React.DOM.div className: 'status exception',
                        exc.message
            else
                React.DOM.div className: 'status ok',
                    "OK"

                    
UI = React.createClass
    getInitialState: () ->
        return {
            selectedNode: null
            nodesById: {}
            treeVersion: 0
            featuresInfo: {}
            reloading: false
            mapProgram: null
        }

    reload: ->
        @setState reloading: true

        @loadNodes('all')
        @reloadFeatures()

    loadNodes: (rootId=0, maxDepth) ->
        options = {}
        if rootId != 'all' and not maxDepth?
            options.maxDepth = 3
            
        $.getJSON "/tree/nodes/"+rootId,
            options,
            (data) =>
                @addNodes(data)
                @setState reloading: false

    reloadFeatures: ->
        $.getJSON "/tree/features_info", (featuresInfo) =>
            colorIdx = 0
            
            for featId of featuresInfo
                featuresInfo[featId] = _.extend featuresInfo[featId],
                    isFiltered: true
                    fill: getCategoryColor(colorIdx)
                    stroke: '#fcfcfc'
                colorIdx++
            
            featuresInfo["-2"] = {
                name: "(leaf)"
                isFiltered: true
                fill: leafFill
                stroke: leafStroke
            }
            
            @setState featuresInfo: featuresInfo
        
    addNodes: (tree) ->
        nodesById = @state.nodesById
        _.each _.keys(tree), (id) ->
            node = tree[id]
            node.id = id
            node.isLeaf = (node.featureId == "-2")
            
            # NOTE: getting undefined's into node.children causes exceptions
            # in D3 (3.5.5)
            # NOTE: d3.partition overwrites some properties in each node
            # For this reason, another names have been chosen:
            #   children -> childrenIds
            #   value -> outputs
            node.childrenIds = tree[id].children
            node.numChildren = node.childrenIds?.length or 0
            node.outputs = tree[id].value

            nodesById[id] = node

        @recollectOutputs()
        
        if @isMounted()
            @setState
                nodesById: nodesById
                treeVersion: (@state.treeVersion + 1)

    recollectOutputs: (nodeId) ->
        nodeId ?= 0
        node = @state.nodesById[nodeId]

        if node.childrenIds.length == 0
            return

        # see the comment about renaming some attributes in
        # the `addNodes' method. `outputs' is one of them
        node.outputs = {}
        nodeOut = node.outputs
        for childId in node.childrenIds
            @recollectOutputs(childId)
            child = @state.nodesById[childId]
            for outputId, outputVals of child.outputs
                nodeOut[outputId] ?= []
                nodeOut[outputId] = nodeOut[outputId].concat(outputVals)
        
    onNodeSelect: (node, options) ->
        if not node.parent # root node can't be selected
            return
            
        lock = options?.lock or false
        if @state.selectionLocked and !lock
            return
        
        @setState
            selectedNode: node,
            selectionLocked: lock

    setFilter: (mode, ids, value) ->
        if ids == 'all'
            ids = _.keys(@state.featuresInfo)

        ids = [].concat(ids)

        newFeatures = _.clone @state.featuresInfo
        switch mode
            when 'set'
                ids.forEach (id) ->
                    newFeatures[id].isFiltered = value
            when 'only'
                for id, f of newFeatures
                    f.isFiltered = false
                ids.forEach (id) ->
                    newFeatures[id].isFiltered = true
            when 'toggleAll'
                # false only if at least one feature is not filtered
                value = true
                for id, f of newFeatures
                    if f.isFiltered == true
                        value = false
                        break
                for id, f of newFeatures
                    f.isFiltered = value
            when 'toggle'
                ids.forEach (id) ->
                    oldVal = newFeatures[id].isFiltered
                    newFeatures[id].isFiltered = not oldVal
            else
                return
                
        @setState featuresInfo: newFeatures

    componentDidMount: ->  
        @reload()

    render: ->
        if not @state.nodesById? or _.size(@state.nodesById) == 0
            if @state.reloading
                return React.DOM.div
                    id: "nothing-loaded"
                    key: "nothing-loaded"
                    '(loading...)',
                    toolbar
            else
                return React.DOM.div
                    id: "nothing-loaded"
                    key: "nothing-loaded"
                    '(nothing loaded yet)',
                    toolbar

        React.DOM.div
            id: "ui"
            key: "ui"

            React.createElement treeUi.TreeComponent,
                key: 'tree'
                tree: @state.nodesById
                treeVersion: @state.treeVersion
                onSelect: @onNodeSelect
                selectedNode: @state.selectedNode
                featuresInfo: @state.featuresInfo
                mapFunc: @state.mapProgram
                
            React.DOM.div
                id: "toolbar"
                key: "toolbar"
                if @state.selectionLocked
                    React.DOM.button
                        key: 'btn-unlock'
                        className: 'btn-unlock'
                        onClick: () => @setState selectionLocked: false
                        "Unlock "
                        React.DOM.i className: 'fa fa-unlock'
                else
                    React.DOM.button
                        key: 'btn-unlock'
                        className: 'btn-unlock disabled'
                        "Unlocked "
                        React.DOM.i className: 'fa fa-crosshairs'
                React.DOM.button
                    id: "btn-reload"
                    key: "btn-reload"
                    onClick: () => @reload()
                    "Reload data"
            
            if @state.selectedNode?
                React.createElement Breadcrumbs,
                    key: 'breadcrumbs'
                    featuresInfo: @state.featuresInfo
                    node: @state.selectedNode
                    onNodeSelect: (node) => @onNodeSelect node, lock: true

            React.createElement Sidebar,
                key: 'sidebar'
                node: @state.selectedNode
                tree: @state.nodesById
                featuresInfo: @state.featuresInfo
                selectionLocked: @state.selectionLocked
                onFilterChange: @setFilter
                onMapProgramChange: (ast) =>
                    @setState
                        mapProgram: query.compileAST ast
                        treeVersion: (@state.treeVersion + 1)
                onChildrenRequest: (nodeId) =>
                    node = @state.nodesById[nodeId]
                    _.each node.children, (child) ->
                        child.visible = true
                    @setState treeVersion: (@state.treeVersion + 1)
                    @forceUpdate()
                    
$ ->
    ui = React.createElement(UI)
    element = document.getElementById('main-area')
    React.render(ui, element)
    
