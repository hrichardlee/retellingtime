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
	function initializeRender(events) {
		render = {};
		render.events = events;
		render.width = $(window).width();

		// create scales
		render.x = d3.scale.linear().range([0, render.width]);
		// render.x2 = d3.scale.linear().range([0, render.width]);
		render.xAxis = d3.svg.axis().scale(render.x).orient("bottom"),
		// render.xAxis2 = d3.svg.axis().scale(x2).orient("bottom");

		render.x.domain([render.events[(render.events.length- 1)].date,
			render.events[0].date]);
				
		// render.x2.domain(render.x.domain());

		// get max zoom
		var minDist = null;
		for (var i = 0; i < render.events.length - 1; i++) {
			var dist = render.events[i].date - render.events[i+1].date;
			if (!minDist
				|| dist < minDist)
				minDist = dist;
		}
		var zoomMax = (render.x.domain()[1] - render.x.domain()[0]) / minDist * C.ZOOMMAXFACTOR;

		// initialize svg and such
		var svg = d3.select("body").append("svg")
		    .attr("width", render.width)
		    .attr("height", C.TOTALTIMELINEHEIGHT);

		svg.append("defs").append("clipPath")
		    .attr("id", "clip")

		// what happens if zoomed before data is loaded
		render.zoom = d3.behavior.zoom()
			.scaleExtent([C.ZOOMMIN, zoomMax])
			.on("zoom", doRender);

		render.focus = svg.append("g")
			svg.call(render.zoom);

		render.focus.append("rect")
			.attr("height", C.TOTALTIMELINEHEIGHT)
			.attr("width", render.width)
			.classed("background", true)

		render.xAxisEl = svg.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + C.TIMELINEHEIGHT + ")")
			.call(render.xAxis)

		render.zoom.x(render.x);


		// We want to set the scale to be zoomed out initially so that we can
		// see the full text of the last event, as well as the initial margin,
		// which we will call M. Let a, b be the dates of the first and last
		// events. We need to find a date c such that when the timeline is
		// rendered from a to c, the rendering of b's event text box hits the
		// right edge of the timeline. Let W be the physical width of the
		// timeline and We be the width of the event text box. We are looking
		// for c such that

		// 		(W - We - 2 * M) * (c - a) / W + a = b
		//		c = (b - a) * W / (W - We - 2 * M) + a

		// Now we can scale out to (b - a) / (c - a), and translate to M
		var c = 
			(render.events[0].date - render.events[(render.events.length- 1)].date)
				* render.width / (render.width - C.EVENTWIDTH - 2 * C.INITIALTIMELINEMARGIN)
				+ render.events[(render.events.length- 1)].date;
		render.zoom
			.scale((render.x.domain()[1] - render.x.domain()[0]) / (c - render.x.domain()[0]))
			.translate([C.INITIALTIMELINEMARGIN, 0])

		render.prevScale = render.zoom.scale();
		render.prevTranslateX = render.zoom.translate()[0];

// render.context = svg.append("g")
//     .attr("transform", "translate(" + 0 + "," + 510 + ")");
		// .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	}

	function doRender() {
		console.debug("render started")

		function rerenderScale() {
			_.each(render.events, function (e) {
				e.reset();
				e.setLeft(render.x(e.date));
			} );
			render.scopedEvents = tlevents.setBottoms(render.events);
		}

		var onlyTranslate = false;

		if (d3.event && d3.event.type == "zoom") {
			var t = d3.event.translate,
				s = d3.event.scale;

			t[0] = Math.min(C.PANMARGIN,	// upper bound
				// the min should be such that

				// min + W 
				Math.max(-render.width * (s - 1) - C.PANMARGIN - C.EVENTWIDTH, // lower bound
					t[0]));
			render.zoom.translate(t);

			if (s != render.prevScale) {
				render.prevScale = s;
				rerenderScale();
			} else {
				var deltaX = t[0] - render.prevTranslateX
				_.each(render.scopedEvents, function (e) {
					e.setLeft(e.left + deltaX);
				})
				onlyTranslate = true;
			}

			render.prevTranslateX = t[0];
		} else {
			rerenderScale();
		}

		var groups = render.focus.selectAll('g')
			.data(render.scopedEvents, function (e) { return e.id(); });

		// only update:
		groups
			.style("opacity", "1") // kind of a hack, transitions don't always finish cleanly
		var updateGroups = onlyTranslate
			? groups
			: groups
				.transition()
				.duration(C.TRANSITIONDURATION)
				.ease("linear")
		updateGroups
			.attr("transform", function (d) {
				return "translate(" + d.left + ", " + (C.TIMELINEHEIGHT - d.bottom - d.height) + ")";
			})
			.selectAll("rect")
			.attr("height", function (d) { return d.bottom + d.height - C.MARKEREXTRAHEIGHT; })

		// only enter
		var groupsenter = groups.enter()
			.append("g")

		groupsenter
			.attr("transform", function (d) {
				return "translate(" + d.left + ", " + (C.TIMELINEHEIGHT - d.bottom - d.height) + ")";
			})
			.style("opacity", "0")
			.transition()
			.style("opacity", "1")

		groupsenter.append("foreignObject")
			.attr("height", function (d) {return d.height; })
			.attr("width", C.EVENTWIDTH)
			.append("xhtml:div")
			.html(function (d) { return d.html(); })
		groupsenter.append("rect")
			.attr("width", 2)
			.attr("y", C.MARKEREXTRAHEIGHT)
			.attr("height", function (d) { return d.bottom + d.height - C.MARKEREXTRAHEIGHT; })
		
		// only removed elements
		groups.exit().transition().style("opacity", "0").remove();
		
		render.xAxisEl.call(render.xAxis)

		console.debug("render finished")
	}

	function foo() {
		$.get("/timelinedata/" + $("#query").val(), function(data) {
			// data should be a list of [{date, content, importance}, ...]
			// Turn data into Event objects
			var eventTemplate = _.template($("#event-template").html());
			var eventsHolder = $("#events-holder", this.$el);
			var events = _.map(data, function(ev) {
				return new tlevents.Event(ev, eventsHolder, eventTemplate);
			}, this);

			initializeRender(events);
			doRender();
		});
	}

	$(function(){
		$('#query').keypress(function (e) {
			if (e.which == 13) {
				foo();
				return false;
			} else if (String.fromCharCode(e.which) == '`') {
				render.x.domain([1940, 1960]);
				doRender();
			}
		})
	})
})