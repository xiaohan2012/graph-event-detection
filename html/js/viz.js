function load_event_1(config){
	console.log('config.force:', config.force);
	var force = d3.layout.force()
		.charge(config.force.charge)
		.linkDistance(config.force.linkDistance)
		.size([config.svg.width,
			   config.svg.height]);

	var svg = d3.select("body").append("svg")
		.attr("width", config.svg.width)
		.attr("height", config.svg.height);

	svg.append("svg:defs")
		.append("svg:marker")
		.attr("id", "triangle")
		.attr("viewBox", "0 -5 10 10")
		.attr("refX", 15)
		.attr("refY", -1.5)
		.attr("markerWidth", 5)
		.attr("markerHeight", 5)
		.attr("orient", "auto")
		.append("svg:path")
		.attr("d", "M0,-5L10,0L0,5");

	d3.json(config.graph_data_url, function(error, graphs) {
		var tip = d3.tip()
			.attr('class', 'd3-tip')
			.offset(config.tip.offset)
			.html(function(d){
				return config.tip.html(d);
			});
		
		svg.call(tip);

		var graph = graphs[config.event_index];
		console.log(config.event_index + ' / ' + graphs.length);

		var participants = _.uniq(_.map(graph.nodes, function(n){
			return n.sender_id;
		}));
		console.log('participants:', participants);

		var people_color = d3.scale.ordinal()
			.domain(participants)
			.range(d3.scale.category10().range())

		if (error) throw error;

		force
			.nodes(graph.nodes)
			.links(graph.edges)
			.start();

		var call_func_or_just_value = function(obj){
			return _.isFunction(obj) ?
				function(d){
					return obj(d);
				} : obj;
		}
		console.log('config.link.stroke', config.link.stroke);
		var glinks = svg.selectAll('g.glink')
			.data(graph.edges)
			.enter()
			.append('g')
			.classed('glink', true);
		
		var link = glinks.append("line")
			.attr("class", "link")
			.attr("marker-end", "url(#triangle)")
			.attr("stroke", call_func_or_just_value(config.link.stroke))
			.attr("stroke-width", call_func_or_just_value(config.link.strokeWidth))
			.attr("opacity", config.link.opacity);
		
		var costs = _.map(graph.edges, function(e){
			return e['c'];
		});
		var link_weight = d3.scale.quantize()
			.domain([d3.min(costs), d3.max(costs)])
			.range([100, 200, 300, 400, 500, 600, 700, 800, 900]);

		var link_labels = glinks.append("text")
			.text(call_func_or_just_value(config.link.label))
			.attr('font-size', 10)
			.attr('font-weight', function(d){
				return link_weight(d['c']);
			})

		var gnodes = svg.selectAll('g.gnode')
			.data(graph.nodes)
			.enter()
			.append('g')
			.classed('gnode', true);
		

		var node = gnodes.append("circle")
			.attr('stroke', config.node.stroke)
			.attr('stroke-width', config.node['stroke-width'])
			.attr("class", "node")
			.attr("r", call_func_or_just_value(config.node.r))
			// .style("fill", config.node.fill)
			.style("fill", function(d){
				return people_color(d.sender_id);
			})
			.attr('opacity', 0.3)
			.call(force.drag)
			.on('mousein', tip.show)
			.on('mouseout',  tip.hide)
			.on('click', function(d){
				var text = d3.select(this.nextSibling);
				console.log(text);
				console.log(text.style('display'));
				if (text.style('display') == 'none'){
					text.style('display', 'inline');
					d3.select(this).attr('opacity', 1.0);
				}
				else{
					text.style('display', 'none');
					d3.select(this).attr('opacity', 0.5);

				}
				// text.toggle();
			})

		if(true){
			var node_labels = gnodes.append("text")
				.text(config.node.label)
				.attr('font-size', 16)
				.attr('font-weight', 'bold')
				.style('display', 'none')
				.style('text-anchor', 'middle');
		}

		force.on("tick", function() {
			gnodes[0].x = config.svg.width / 2;
			gnodes[0].y = config.svg.height / 2;

			link.attr("x1", function(d) { return d.source.x; })
				.attr("y1", function(d) { return d.source.y; })
				.attr("x2", function(d) { return d.target.x; })
				.attr("y2", function(d) { return d.target.y; });

			// gnode.attr("cx", function(d) { return d.x; })
			// 	.attr("cy", function(d) { return d.y; });
			gnodes.attr("transform", function(d) { 
				return 'translate(' + [d.x, d.y] + ')'; 
			}); 

			link_labels.attr("transform", function(d) { 
				var x = (d.source.x + d.target.x) / 2;
				var y = (d.source.y + d.target.y) / 2;
				return 'translate(' + [x, y] + ')';
			});
			node_labels.attr('transform', function(d){
				return 'translate(' + [0, -12] + ')'; 
			})

		});
	});
}
