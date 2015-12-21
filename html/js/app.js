var width = 960,
height = 500;

var EDGE_BROADCAST = 1, EDGE_REPLY = 2, EDGE_RELAY = 3;
var palette = d3.scale.ordinal()
	.domain([EDGE_BROADCAST, EDGE_REPLY, EDGE_RELAY])
	.range(d3.scale.category10().range());

var format_time = d3.time.format("%Y-%m-%d");

var force = d3.layout.force()
    .charge(-120)
    .linkDistance(30)
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
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
	.append("svg:path")
    .attr("d", "M0,-5L10,0L0,5");

d3.json("data/id2interaction.json", function(error, id2interactions) {
	d3.json("data/id2people.json", function(error, id2people) {
		d3.json("data/result-greedy--U=005--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=cosine.json", function(error, graphs) {
			var tip = d3.tip()
				.attr('class', 'd3-tip')
			// .offset([100, 20])
				.html(function(n) {
					var i = id2interactions[n['message_id']];
					i['date'] = format_time(new Date(i['datetime']*1000));
					i['sender'] = id2people[i['sender_id']]['email'];
					i['recipients'] = _.map(i['recipient_ids'], function(k){
						return id2people[k]['email'];
					});
					return dict2html(i, ['subject', 'body', 'sender', 'recipients', 'date', 'message_id']);
				});
			
			svg.call(tip);

			var graph = graphs[0];

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
				.attr("stroke-width", 1.5)

			var node = svg.selectAll(".node")
				.data(graph.nodes)
				.enter().append("circle")
				.attr("class", "node")
				.attr("r", 10)
				.style("fill", palette(0))
				.call(force.drag)
				.on('mouseover', tip.show)
				.on('mouseout', tip.hide)


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
