$(document).ready(function(){
    d3.json("data/islamic/timeline.json",
			function(error, data) {
				console.log(data);
				var items = new vis.DataSet(data['items']);

				_.each(data['groups'], function(g){
					g['content'] = '<h3>terms:</h3>' + list2html(g['terms']);
					var participants = _.map(g['participants'], function(v, k){
						return [k, v];
					})
					participants = _.sortBy(participants, function(o){
						return o[1];
					});
					participants.reverse();
					g['content'] += '<h3>participants</h3>' + list2html(
						_.map(participants, function(o){
							return o[0] + '('+ o[1] + ')';
						})
					);
					g['content'] += '<h3>time</h3>' + g['start'] + ' - ' + g['end'] + '(' + g['days'] + ' days)';
					g['content'] += '<h3>link type frequency</h3>' + dict2html(g['link_type_freq']);
				});
				var groups = new vis.DataSet(data['groups']);

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
