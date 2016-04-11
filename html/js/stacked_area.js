$('#dataset').on('change', function(){
	var ds = $(this).val();
	var time_format = null;

	if(ds == "enron_small"){
		time_format = "%b, %y";
	}
	else{
		time_format = "%b %d %H:00";
	}
	d3.json('data/' + ds + '/nvd3/data.json', function(error, data) {
		console.log(data);
		d3.selectAll("svg > *").remove();
		var chart;
		nv.addGraph(function() {
			chart = nv.models.stackedAreaChart()
				.useInteractiveGuideline(false)
				.x(function(d) { return d['ts'] })
				.y(function(d) { return d['c'] })
				.showControls(false)
				.controlLabels({stacked: "Stacked"})
				.duration(300)
				.order('reverse')
				.margin({'left': 100});

			chart.width(600)
				.height(500);

			chart.xAxis.tickFormat(
				function(d) { return d3.time.format(time_format)(new Date(d)) }
			);
			// chart.yAxis.tickFormat();
			// chart.legend.vers('furious');
			d3.select('#chart')
				.datum(data)
				.transition()
				.duration(1000)
				.call(chart)
				.each('start', function() {
					setTimeout(function() {
						d3.selectAll('#chart1 *').each(function() {
							if(this.__transition__)
								this.__transition__.duration = 1;
						})
							}, 0)
				});
			// nv.utils.windowResize(chart.update);
			return chart;
		})
	})

}).change();
