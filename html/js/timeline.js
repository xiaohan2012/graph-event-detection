$(document).ready(function(){
    d3.json("data/timeline.json",
	    function(error, data) {
		console.log(data);
		var items = new vis.DataSet(data['items']);

		_.each(data['groups'], function(g){
		    g['content'] = g['terms'].join(' ');
		});
		var groups = new vis.DataSet();

		var container = document.getElementById('visualization');
		var options = {
		    start: data['start'],
		    end: data['end'],
		    editable: false,
		    type: 'point'
		};

		var timeline = new vis.Timeline(container, items, groups, options);

	    });
})
