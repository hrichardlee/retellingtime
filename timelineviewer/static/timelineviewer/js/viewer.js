requirejs.config({
	// this is ugly
	baseUrl: '/static/timelineviewer/js/lib',
	paths: {
		viewer: '../viewer'
	},
	shim: {
		underscore: {
			exports: '_'
		},
		d3: {
			exports: 'd3'
		}
	}
});

requirejs(['jquery', 'underscore', 'd3', 'viewer/tlevents', 'viewer/consts'], function ($, _, d3, tlevents, C) {
	var render = null;
	function bar() {


	}

	function foo() {
		$.get("/timelinedata/" + $("#query").val(), function(data) {
			// data should be a list of [{date, content, importance}, ...]
			// Turn data into Event objects
			var eventTemplate = _.template($("#event-template").html());
			var eventsHolder = $("#events-holder", this.$el);
			events = _.map(data, function(ev) {
				return new tlevents.Event(ev, eventsHolder, eventTemplate);
			}, this);

			render = {};

			// create scales
			render.x = d3.scale.linear().range([0, C.TIMELINEWIDTH]);
			render.x2 = d3.scale.linear().range([0, C.TIMELINEWIDTH]);
			// render.xAxis = d3.svg.axis().scale(x).orient("bottom"),
			// render.xAxis2 = d3.svg.axis().scale(x2).orient("bottom");

			render.x.domain([data[(data.length- 1)].date, data[0].date]);
			render.x2.domain(render.x.domain());

			// initialize svg and such
			var svg = d3.select("body").append("svg")
			    .attr("width", C.TOTALTIMELINEWIDTH)
			    .attr("height", C.TOTALTIMELINEHEIGHT);

			svg.append("defs").append("clipPath")
			    .attr("id", "clip")

			render.focus = svg.append("g")
			    // .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


			// now render
			_.each(events, function (e) { e.setLeft(render.x(e.date)); } );

			var scopedEvents = tlevents.setBottoms(events);

			var groups = render.focus.selectAll('g')
				.data(scopedEvents);
			groups.enter()
			  .append("g")
			  .attr("transform", function (d) {
			  	return "translate(" + d.left + ", " + (C.TIMELINEHEIGHT - d.bottom - d.height) + ")";
				})
			  .append("rect")
			  .attr("width", 2)
			  .attr("height", function (d) { return d.bottom + d.height - C.MARKEREXTRAHEIGHT; })
			  .attr("y", C.MARKEREXTRAHEIGHT)
			groups.append("foreignObject")
				.attr("height", function (d) {return d.height; })
				.attr("width", C.EVENTWIDTH)
				.append("xhtml:div")
				.html(function (d) { return d.html(); })
		});
	}

	$(function(){
		$('#query').keypress(function (e) {
			if (e.which == 13) {
				foo();
				return false;
			}
		})
	})
})