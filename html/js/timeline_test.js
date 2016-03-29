var margin = {top: 20, right: 100, bottom: 30, left: 100},
width = 960 - margin.left - margin.right,
height = 500 - margin.top - margin.bottom;

var time_formater = d3.time.format('%Y-%m-%d %H:%M:%S');

var dataset = [
	{
		"end": "2001-08-27 06:00:00",
		"days": 24,
		"link_type_freq": {
			"broadcast": 9,
			"reply": 1,
			"relay": 4
		},
		"start": "2001-08-02 14:00:00",
		"participants": {
			"1482": 10,
			"812": 1,
			"800": 1,
			"124": 1,
			"347": 1
		},
		"terms": [
			"ees",
			"ect",
			"steven",
			"ferc",
			"please",
			"market",
			"information",
			"confidential",
			"forwarded",
			"enronxgate"
		],
		"id": 1,
		"text_above": {
			"direction": 120, 
			"length": 50
		},
		"text_below": {
			"direction": 240, 
			"length": 50
		},
	},
	{
		"end": "2001-07-31 06:00:00",
		"days": 25,
		"link_type_freq": {
			"broadcast": 9,
			"reply": 0,
			"relay": 1
		},
		"start": "2001-07-06 01:00:00",
		"participants": {
			"1490": 10,
			"5827": 1
		},
		"terms": [
			"power",
			"state",
			"ees",
			"ect",
			"california",
			"energy",
			"electricity",
			"steven",
			"davis",
			"e-mail"
		],
		"id": 3,
		"text_above": {
			"direction": 120, 
			"length": 50
		},
		"text_below": {
			"direction": 320, 
			"length": 50
		},
	}];

var xScale = d3.time.scale()
	.domain(
		[d3.min(dataset, function(d){ return time_formater.parse(d.start); }),
		 d3.max(dataset, function(d){ return time_formater.parse(d.end); })]
	).range([0, width]);


var xAxis = d3.svg.axis()
	.scale(xScale)
	.orient("bottom")
	.tickPadding(50);
/*  .innerTickSize(-height)
	.outerTickSize(0)
	.tickPadding(10);
*/

var svg = d3.select("body").append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
	.append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height / 2 + ")")
    .call(xAxis)


var events = svg.selectAll('g.event')
	.data(dataset)
	.enter()
	.append('g')
	.classed('event', true)
	.attr('transform', function(d){
		var start = time_formater.parse(d.start);
		var end = time_formater.parse(d.end);
		var mid = new Date((start.getTime() + end.getTime()) / 2);
		return "translate(" + xScale(mid) + ", " + height / 2 + ")";
	})

var size_multiplier = 5;
var colors = d3.scale.category10();

events.append("circle")
	.attr('r', function(d){
		var r = size_multiplier * d3.sum(_.values(d.participants))
		d['r'] = r
		return r;
	})
	.attr('opacity', 0.5)
	.attr('fill', function(d, i){
		return colors(i);
	})

function add_milestone_line(which){
	events.append('line')
		.attr('x1', function(d){
			d[which]['angle'] = d[which]['direction'] / 180 * Math.PI
			d[which]['x1'] = d['r'] * Math.cos(d[which]['angle'])
			return d[which]['x1'];
		})
		.attr('y1', function(d){
			d[which]['y1'] = - d['r'] * Math.sin(d[which]['angle']);
			return d[which]['y1']
		})
		.attr('x2', function(d){
			d[which]['x2'] = (d['r'] + d[which]['length']) * Math.cos(d[which]['angle'])
			return d[which]['x2'];
		})
		.attr('y2', function(d){
			d[which]['y2'] = - (d['r'] + d[which]['length']) * Math.sin(d[which]['angle'])
			return d[which]['y2'];
		})
		.attr('stroke', 'black');	
}

add_milestone_line('text_above');
var which = 'text_above';
events.append('text')
	.classed(which, true)
	.attr('x', function(d){
		return d[which]['x2'] - 50;
	})
	.attr('y', function(d){
		return d[which]['y2'] - 6;
	})
	.text(function(d){
		return 'Days: ' + d['days'];
	});

add_milestone_line('text_below');

which = 'text_below';

events.append('text')
	.classed(which, true)
	.attr('x', function(d){
		return d[which]['x2'] - 50;
	})
	.attr('y', function(d){
		return d[which]['y2'] + 6;
	})
	.text(function(d){
		return d['terms'].join(" ");
	});
