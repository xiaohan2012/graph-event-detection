$(document).ready(function(){
	function get_meta_config(){
		return {
			'dataset': $('#dataset').find(":selected").val(),
			'base_name': $('#dataPathSelection').find(":selected").val(),
			'graph_type': $('#graphTypeForm').find(":checked").val(),
			'context_flag': $('#contextFlagForm').find(":checked").val(),
			'event_index': $('#eventIndexSelection').find(':selected').val()
		}
	}

	function get_graph_data_url(mc){
		return "data/"+ mc.dataset + "/" + mc.context_flag + "/" + mc.graph_type + "/"  + mc.base_name;
	}

	function get_id2interaction_url(mc){
		return "data/"+ mc.dataset + "/id2interactions.json";
	}
	function get_id2people_url(mc){
		return "data/"+ mc.dataset + "/id2people.json";
	}

	
	var EDGE_BROADCAST = 1, EDGE_REPLY = 2, EDGE_RELAY = 3,	NODE_EVENT = 4;
	var palette = d3.scale.ordinal()
		.domain([EDGE_BROADCAST, EDGE_REPLY, EDGE_RELAY])
		.range(d3.scale.category10().range());
	var format_time = d3.time.format("%Y-%m-%d");


	function get_config(mc){
		var url_dict = {
			id2interaction_url: get_id2interaction_url(mc),
			id2people_url: get_id2people_url(mc),
			graph_data_url: get_graph_data_url(mc)
		};
		var context_flag_config = {
			'event': {
				force: {charge: -300, linkDistance: 10}
			},
			'contexted_event': {
				force: {charge: -200, linkDistance: 200}
			}
		};
		var get_people_id_func = function(info) {
			return info['id'];
		}
		var dataset_config = {
			enron: {
				people_repr: function(info){
					return info['email'].replace("@enron.com", "");
				}
			},
			islamic: {
				people_repr: get_people_id_func
			},
			sklearn: {
				people_repr: get_people_id_func
			},
			bloomberg: {
				people_repr: get_people_id_func,
			}
		}
		var dataset_setting = $.extend(
			{
				node_label: function(d){						
					return '(' + d['r'] * (Math.pow(10, 4)) + ')' + d.subject;
				}
			},
			dataset_config[mc.dataset]
		);
		
		var graph_type_config = {
			'original_graph': {
				force: {charge: -500, linkDistance: 100},
				tip: {
					html: function(d){
						return dict2html(d);
					}
				},
				node: {
					label: function(d){
						return d.name;
					}
				}
			},
			'meta_graph': {
				svg: {width: 1280, height: 1500},
				force: {charge: -1000, linkDistance: 150},
				tip: {
					html: function(d){
						console.log('iteraction:', d);
						d['date'] = format_time(new Date(d['timestamp']*1000));

						d['sender_str'] = d.sender.name;
						d['recipients_str'] = _.map(d['recipients'], function(r){
							return r.name;
						}).join(',  ');
						return dict2html(d, ['subject', 'body', 'sender_str', 'recipients_str', 'date', 'message_id']);
					}
				},
				node: {
					fill: 'red',
					r: 8,
					label: dataset_setting.node_label
				},
				link: {
					stroke: function(d){
						var s = d['source'], t = d['target'];
						if(s["sender_id"] == t["sender_id"]){
							console.log("broadcast..")
							return palette(EDGE_BROADCAST); // broadcast
						}
						else if(_.intersection(s["recipient_ids"], [t["sender_id"]]) && 
								_.intersection(t["recipient_ids"], [s["sender_id"]])){
							console.log("reply..")
							return palette(EDGE_REPLY); // reply
						}
						else if(_.intersection(s["recipient_ids"], [t["sender_id"]]) && 
								!_.intersection(t["recipient_ids"], [s["sender_id"]])){
							console.log("relay..")
							return palette(EDGE_RELAY); // relay
						}else{
							throw new Exception("impossible!");
						}
					},
					label: function(d){
						return d['c'].toFixed(3);
					}
				}
			}
		};
		var ret = $.extend(
			true, // deep
			{
				svg: {width: 960, height: 1000},
				force: {charge: -150, linkDistance: 500},
				tip: {
					offset: [0, 0],
					html: function(d){
						return "boiler-plate";
					}
				},
				link: {
					stroke: "gray",
					strokeWidth: 1.5,
					opacity: 1,
					label: ''
				},
				node: {
					r: function(d){
						if(d['event']){
							return 8;
						}
						else{
							return 5;
						}
					},
					fill: function(d){
						if(d['event']){
							return palette(NODE_EVENT);
						}
						else{
							return '#bbb';
						}
					},
					label: function(d){
						return '';
					}
				}
			},
			context_flag_config[mc.context_flag],
			graph_type_config[mc.graph_type],
			mc,
			url_dict
		);
		console.log('ret["force"]:', ret['force']);
		var charge_from_input = parseInt($("#charge").val());
		if(charge_from_input){
			ret.force.charge = charge_from_input;
		}
		var linkDistance_from_input = parseInt($("#linkDistance").val());
		if(linkDistance_from_input){
			ret.force.linkDistance = linkDistance_from_input;
		}
		return ret;
	};

	var CLEAR_SVG = true;
	init_dataset_and_paths_widget("event_names.json")
	
	$('#submitButton').on('click', function(){
		var mc = get_meta_config();
		var data_path = get_graph_data_url(mc);
		if(CLEAR_SVG){
			$('svg').remove();
		}
		console.log(mc);
		// console.log(data_path);
		load_event_1(get_config(mc));
	});
	/*
	// load_event(result_paths[0], 0);
	$('#dataPathSelection').on('change', function(){
	var path = $(this).find(":selected").val();

	load_event(path, 0);	 
	})
	$('#eventIndexSelection').on('change', function(){	 
	var index = parseInt($(this).find(":selected").val());
	console.log("change to index: ", index);
	var path = $('#dataPathSelection').find(":selected").val();
	if(CLEAR_SVG){
	$('svg').remove();
	}
	load_event(path, index);
	});
	*/
	$('#dataset option:eq(0)').change();
})
