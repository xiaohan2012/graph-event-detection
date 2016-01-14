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
