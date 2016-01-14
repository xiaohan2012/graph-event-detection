function dict2html(d, fields){
	var html="";
	var truncate_len = 2000;
	if(typeof fields === "undefined"){
		_.each(d, function(v, k, lst){
			html += ("<div><strong>" + k + ":  </strong>");
			html += ("<span>" + truncate_string(d[k], truncate_len) + "</span></div>");
		});
	}
	else{
		_.each(fields, function(k){
			html += ("<div><strong>" + k + ":  </strong>");
			html += ("<span>" + truncate_string(d[k], truncate_len) + "</span></div>");
		});
	}
	return html;
}

function list2html(items){
	var list = _.map(items, function(i){
		return '<li>' + i + '</li>';
	})
	return '<ul>' + list.join('') + '</ul>';
}

function is_string(o){
	return (typeof o === 'string');
}

function truncate_string(s, len){
	if(s.length > len){
		return s.substring(0, len) + '...';
	}
	else{
		return s;
	}
}

function init_dataset_and_paths_widget(paths_json_name){
	$('#dataset').on('change', function(){
		d3.json("data/" + $(this).val() + "/" + paths_json_name,
				function(error, result_paths) {
					$('#dataPathSelection').children().remove();
					_.each(result_paths.sort(), function(p, index){
						var opt;
						if(index == 0){
							opt = $("<option selected='selected'>");
						}
						else{
							opt = $("<option>");
						}
						opt.val(p);
						opt.text(p);
						$('#dataPathSelection').append(opt);
					});
				});
	});
}
