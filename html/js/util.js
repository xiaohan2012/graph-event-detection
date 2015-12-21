function dict2html(d, fields){
	var html="";
	if(typeof fields === "undefined"){
		_.each(d, function(v, k, lst){
			html += ("<div><strong>" + k + ":  </strong>");
			html += ("<span>" + d[k] + "</span></div>");
		});
	}
	else{
		_.each(fields, function(k){
			html += ("<div><strong>" + k + ":  </strong>");
			html += ("<span>" + d[k] + "</span></div>");
		});
	}
	return html;
}
