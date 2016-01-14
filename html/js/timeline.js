function showMicro(json_url){
    d3.json(json_url,
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
					var link_type_freq_str = '';
					console.log(g['link_type_freq']);
					if(is_string(g['link_type_freq'])){
						link_type_freq_str = g['link_type_freq'];
					}
					else{
						link_type_freq_str = dict2html(g['link_type_freq']);
					}
					g['content'] += '<h3>link type frequency</h3>' + link_type_freq_str;
				});
				var groups = new vis.DataSet(data['groups']);

				var container = document.getElementById('visualization');
				var options = {
					start: data['start'],
					end: data['end'],
					editable: false,
					type: 'point',
					orientation: 'top',
				};

				var timeline = new vis.Timeline(container, items, groups, options);
			});
}

function showMacro(json_url){
    d3.json(json_url,
			function(error, data) {
				console.log(data);
				var items = new vis.DataSet(
					_.map(data['groups'], function(g){
						g['content'] = g['terms'].join(' ');
						g['group'] = g['id'];
						return g;
					})
				);

				_.each(data['groups'], function(g){
					g['content'] = '<h3>time</h3>' + g['start'] + ' - ' + g['end'] + '(' + g['days'] + ' days)';
					g['content'] += '<h3>link type frequency</h3>' + dict2html(g['link_type_freq']);
					g['content'] = '';
				});
				var groups = new vis.DataSet(data['groups']);

				var container = document.getElementById('visualization');
				var options = {
					start: data['start'],
					end: data['end'],
					editable: false,
					type: 'point',
					orientation: 'top',
					stack: false
				};

				var timeline = new vis.Timeline(container, items, groups, options);
			});
}
