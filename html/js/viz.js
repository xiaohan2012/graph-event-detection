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

	d3.json(config.id2interaction_url, function(error, id2interactions) {
		d3.json(config.id2people_url, function(error, id2people) {
			var data_bunch = {
				'id2interactions': id2interactions,
				'id2people': id2people
			};
			d3.json(config.graph_data_url, function(error, graphs) {
				var tip = d3.tip()
					.attr('class', 'd3-tip')
					.offset(config.tip.offset)
					.html(function(d){
						return config.tip.html(d, data_bunch);
					});
				
				svg.call(tip);

				var graph = graphs[config.event_index];
				console.log(config.event_index + ' / ' + graphs.length);

				if (error) throw error;

				force
					.nodes(graph.nodes)
					.links(graph.edges)
					.start();

				var call_func_or_just_value = function(obj){
					return _.isFunction(obj) ?
						function(d){
							return obj(d, data_bunch);
						} : obj;
				}
				console.log('config.link.stroke', config.link.stroke);
				var link = svg.selectAll(".link")
					.data(graph.edges)
  					.enter().append("line")
					.attr("class", "link")
					.attr("marker-end", "url(#triangle)")
					.attr("stroke", call_func_or_just_value(config.link.stroke))
					.attr("stroke-width", call_func_or_just_value(config.link.strokeWidth))
					.attr("opacity", config.link.opacity);
				
				var gnodes = svg.selectAll('g.gnode')
					.data(graph.nodes)
					.enter()
					.append('g')
					.classed('gnode', true);
				

				// var node = svg.selectAll(".node")
				// 	.data(graph.nodes)
				// 	.enter()
				var node = gnodes.append("circle")
					.attr("class", "node")
					.attr("r", config.node.r)
					.style("fill", config.node.fill)
					.call(force.drag)
					.on('mouseover', tip.show)
					.on('mouseout',  tip.hide)

				var labels = gnodes.append("text")
					.text(function(d){
						return config.node.label(d, data_bunch);
					})
					.attr('font-size', 10)
					.attr('font-weight', 'bold');

				force.on("tick", function() {
					link.attr("x1", function(d) { return d.source.x; })
						.attr("y1", function(d) { return d.source.y; })
						.attr("x2", function(d) { return d.target.x; })
						.attr("y2", function(d) { return d.target.y; });

					// gnode.attr("cx", function(d) { return d.x; })
					// 	.attr("cy", function(d) { return d.y; });
					  gnodes.attr("transform", function(d) { 
						  return 'translate(' + [d.x, d.y] + ')'; 
					  }); 
				});
			});
		});
	});
}



// ######## DEPRECATED ########
function load_event(data_path, kth){
	var width = 960,
	height = 1000;

	var EDGE_BROADCAST = 1, EDGE_REPLY = 2, EDGE_RELAY = 3;
	var palette = d3.scale.ordinal()
		.domain([EDGE_BROADCAST, EDGE_REPLY, EDGE_RELAY])
		.range(d3.scale.category10().range());

	var format_time = d3.time.format("%Y-%m-%d");

	var force = d3.layout.force()
		.charge(-150)
		.linkDistance(500)
		.size([width, height]);

	var svg = d3.select("body").append("svg")
		.attr("width", width)
		.attr("height", height);

	svg.append("svg:defs")
		.append("svg:marker")
		.attr("id", "triangle")
		.attr("viewBox", "0 -5 10 10")
		.attr("refX", 15)
		.attr("refY", -1.5)
		.attr("markerWidth", 3)
		.attr("markerHeight", 3)
		.attr("orient", "auto")
		.append("svg:path")
		.attr("d", "M0,-5L10,0L0,5");

	d3.json("data/id2interaction.json", function(error, id2interactions) {
		d3.json("data/id2people.json", function(error, id2people) {
			d3.json(data_path, function(error, graphs) {
				var tip = d3.tip()
					.attr('class', 'd3-tip')
				// .offset([100, 20])
					.html(function(n) {
						var i = id2interactions[n['message_id']];
						i['date'] = format_time(new Date(i['datetime']*1000));
						i['sender'] = id2people[i['sender_id']]['email'].replace("@enron.com", "");
						i['recipients'] = _.map(i['recipient_ids'], function(k){
							return id2people[k]['email'].replace("@enron.com", "");
						}).join("    ");
						console.log('iteraction:', i);
						return dict2html(i, ['subject', 'body', 'sender', 'recipients', 'date', 'message_id']);
					});
				
				svg.call(tip);

				var graph = graphs[kth];

				if (error) throw error;

				force
					.nodes(graph.nodes)
					.links(graph.edges)
					.start();

				var link = svg.selectAll(".link")
					.data(graph.edges)
  					.enter().append("line")
					.attr("class", "link")
					.attr("marker-end", "url(#triangle)")
					.attr("stroke", function(d){
						var s = d['source'], t = d['target'];
						if(s["sender_id"] == t["sender_id"]){
							return palette(EDGE_BROADCAST); // broadcast
						}
						else if(_.intersection(s["recipient_ids"], [t["sender_id"]]) && 
								_.intersection(t["recipient_ids"], [s["sender_id"]])){
							return palette(EDGE_REPLY); // reply
						}
						else if(_.intersection(s["recipient_ids"], [t["sender_id"]]) && 
								!_.intersection(t["recipient_ids"], [s["sender_id"]])){
							return palette(EDGE_RELAY); // relay
						}
					})
					.attr("stroke-width", function(d){
						if(d['event']){
							return 4;
						}else{
							return 1;
						}
					})
					.attr("opacity", function(d){
						if(d['event']){
							return 1;
						}else{
							return 0.5;
						}
					});

				function mouseover_wrapper(d){					
					tip.show(d);
					link.style('stroke-width', function(l) {
						if (d === l.source)
							return 2;
						else
							return 1;
					});
				}
				function mouseout_wrapper(d){					
					tip.hide(d);
					link.style('stroke-width', 1);
				}
				var node = svg.selectAll(".node")
					.data(graph.nodes)
					.enter().append("circle")
					.attr("class", "node")
					.attr("r", 5)
				// .style("fill", palette(0))
					.style("fill", function(d){
						if(d['event']){
							return palette(0);
						}else{
							return '#eee';
						}
					})
					.call(force.drag)			
					// .on('mouseover', tip.show)
					// .on('mouseout', tip.hide)
					.on('mouseover', mouseover_wrapper)
					.on('mouseout',  mouseout_wrapper)


				force.on("tick", function() {
					link.attr("x1", function(d) { return d.source.x; })
						.attr("y1", function(d) { return d.source.y; })
						.attr("x2", function(d) { return d.target.x; })
						.attr("y2", function(d) { return d.target.y; });

					node.attr("cx", function(d) { return d.x; })
						.attr("cy", function(d) { return d.y; });
				});
			});
		});
	});
}
