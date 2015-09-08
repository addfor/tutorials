$ = require 'jquery'
_ = require 'underscore'
React = require 'react'
d3 = require 'd3'

TreeComponent = React.createClass
    getInitialState: () ->
        element = document.createElement('div')

        svg = d3.select(element)
            .append('svg')
            .attr('width', window.innerWidth)
            .attr('height', window.innerHeight)

        dragArea = svg.append('g')
        zoomed = () =>
            dragArea.attr('transform',
                'translate('+d3.event.translate+') '+
                'scale('+d3.event.scale+')')

        zoom = d3.behavior.zoom()
            .scaleExtent [1, 100]
            .on 'zoom', zoomed
        svg.call(zoom)
        
        area = dragArea.append('g')
            .attr('class', 'area')
            .attr('transform',
                'translate(' + (window.innerWidth / 2.8) + ','+
                 (window.innerHeight / 2) + ')')
                 
        area.append('g').attr('class', 'tree')
        area.append('g').attr('class', 'selected')

        return {
            element: element
            shouldRenderTree: true
        }

    recomputeLayout: ->
        tree = @props.tree
        
        getAllChildren = (t) =>
            _.filter(
                _.map t.childrenIds, (id) -> tree[id],
                (n) -> n?)
            
        getChildren = (t) =>
            children = getAllChildren t
            _.filter children, (child) =>
                feature = @props.featuresInfo[child.featureId]
                if feature?.isFiltered?
                    feature.isFiltered
                else
                    true

        nodes = d3.layout.partition()
            .size [2 * Math.PI, 200*200*200]
            .value (n) => n.count / Math.pow(2, n.depth-1)
            .sort (a, b) ->
                -((a.count - b.count) or (a.id - b.id))
                # da = Math.abs(a.featureId - a.parent.featureId)
                # db = Math.abs(b.featureId - b.parent.featureId)
                # -((da - db) or (a.id - b.id))
            .children getAllChildren
            .nodes tree[0]

        @layoutNodes = {}
        for node in nodes
            @layoutNodes[node.id] = node
        
        f = Math.cbrt
        @arc ?= d3.svg.arc()
            .startAngle  (d) -> d.x 
            .endAngle    (d) -> d.x + d.dx 
            .innerRadius (d) -> f(d.y)
            .outerRadius (d) -> f(d.y + d.dy)

    renderTree: () ->
        d3.select(@state.element)
            .select 'svg'
            .attr 'width', window.innerWidth
            .attr 'height', window.innerHeight

        if not @layoutNodes? or not @arc?
            @recomputeLayout()

        nodes = _.values @layoutNodes

        if @props.treeVersion == 1
            nodes.forEach (n) -> n.visible = (n.depth <= 4)
        else if @props.mapFunc? and @state.lastMapFunc != @props.mapFunc
            nodes.forEach @props.mapFunc
        
        nodes = nodes.filter (n) -> n.visible ? true
        
        area = d3.select(@state.element).select('.area .tree')
        path = area.selectAll 'path.node'
            .data nodes, (n) -> n.id

        onSelect = @props.onSelect

        newPath = path.enter()
            .append('path')
            .attr 'class', 'node'
            .attr 'd', @arc
            #.append 'rect'
            #.attr 'x', (d) -> d.x
            #.attr 'y', (d) -> Math.sqrt(d.y)
            #.attr 'width', (d) -> d.dx
            #.attr 'height', (d) -> Math.sqrt(d.y+d.dy) - Math.sqrt(d.y)
            .on 'mouseover', (n) =>
                onSelect n, lock: false
            .on 'click', (n) =>
                onSelect n, lock: true
            .style 'vector-effect', 'non-scaling-stroke'
            # .style 'opacity', 0.0
            # .transition().style 'opacity', 1.0

        path.exit().transition()
            .style('opacity', 0.0).remove()
        
        path.style 'stroke', (n) =>
                n.stroke ?
                    @props?.featuresInfo[n.featureId]?.stroke ?
                    'white'
            .style 'visibility', (n) ->
                if n.visible ? (not n.parent?) then 'visible' else 'hidden'
            .style 'fill', (n) =>
                if n.fill?
                    n.fill
                else if not n.parent?    # root node
                    'transparent'
                else
                    feature = @props?.featuresInfo[n.featureId]
                    if not feature?
                        '#ff00ff'
                    else if feature.isFiltered == false
                        '#505050'
                    else
                        feature.fill

        # @rerendersCount ?= 0
        # @rerendersCount++
        # counter = area.select('.counter').data([@rerendersCount+""])
        # if counter.empty()
        #     counter = area.append('g').attr('class', 'counter')
        #     counter.append('text')
        # counter.select('text').text((n) -> n)

    renderSelectedNode: () ->
        if not @layoutNodes? or not @arc?
            @recomputeLayout()

        selNode = @props.selectedNode
        data = if selNode? then [ @layoutNodes[selNode.id] ] else []

        area = d3.select(@state.element).select('.area .selected')
        path = area.selectAll('path').data(data)
        path.enter().append('path')
        path.exit().remove()

        # setting 'fill' to any other value prevents the underlying
        # path's 'click' handler from being triggered
        path.attr 'd', @arc
                
    componentWillReceiveProps: (nextProps) ->
        treeChanged = (nextProps.treeVersion != @props.treeVersion)
        mapFuncChanged = (@props.mapFunc != nextProps.mapFunc)
        featuresInfoChanged = (@props.featuresInfo != nextProps.featuresInfo)
        @setState
            shouldRenderTree: treeChanged or mapFuncChanged or featuresInfoChanged
            shouldRenderSelectedNode: @props.selectedNode != nextProps.selectedNode

    componentDidMount: () ->
        container = @refs['container'].getDOMNode()
        $(container).empty().append(@state.element)
        $(window).resize () =>
            @shouldRenderTree = true

    render: () ->
        if @state.shouldRenderTree ? true
            @renderTree()
        if @state.shouldRenderSelectedNode ? true
           @renderSelectedNode()
            
        React.createElement 'div',
            ref: 'container'
            className: 'tree-area'


module.exports = { TreeComponent }

