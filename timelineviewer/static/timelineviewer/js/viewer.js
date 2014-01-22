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

	function createRenderAndSvg() {
		// initialize svg and such
		var svg = d3.select("body").append("svg")
			.attr("height", C.TOTALTIMELINEHEIGHT);

		svg.append("defs").append("clipPath")
			.attr("id", "clip");

		render = {
			svg: svg
		}

		render.focus = svg.append("g");

		render.zoom = d3.behavior.zoom()
			.on("zoom", doRender);
		render.focus.call(render.zoom);
		render.x = d3.scale.linear();

		render.focus.append("rect")
			.attr("height", C.TIMELINEHEIGHT)
			.attr("class", "background");

		render.focus.append("g")
			.attr("class", "markers");
		render.focus.append("g")
			.attr("class", "text-elements");


		render.xAxisEl = svg.append("g")
			.attr("class", "x axis")
			.attr("height", C.AXISHEIGHT)
			.attr("transform", "translate(0," + C.TIMELINEHEIGHT + ")");

		render.xAxis = d3.svg.axis();


		var context = svg.append("g")
			.attr("height", C.CONTEXTSTRIPHEIGHT)
			.attr("transform", "translate(0," + (C.TIMELINEHEIGHT + C.AXISHEIGHT) + ")");

		render.contextX = d3.scale.linear();

		render.contextMarkersEl = context.append("g");

		render.brush = d3.svg.brush()
			.x(render.contextX)
			.on("brush", brushed);

		render.brushEl = context.append("g")
			.attr("class", "x brush");


		render.firstRender = true;
		render.secondRender = false;
	}
	function setRenderEvents(events) {
		render.events = events;
		render.dateDelta = events[0].date - events[(events.length - 1)].date;
		render.date0 = events[(events.length - 1)].date;
	}
	function setRenderWidth() {
		// local var for convenience
		var events = render.events;

		render.width = $(window).width();

		// create scales/axes
		render.x.range([0, render.width]);
		render.contextX.range([0, render.width]);
		render.xAxis.scale(render.x).orient("bottom");
		render.x.domain([events[(events.length- 1)].date,
			events[0].date]);
		render.xAxisEl.call(render.xAxis);

		// calculate values for initial/min scale
		var c = (events[0].date - events[(events.length- 1)].date)
				* render.width / (render.width - C.EVENTWIDTH - 2 * C.FIRST_RENDER_MARGIN)
				+ events[(events.length- 1)].date;
		var initialScale = (render.x.domain()[1] - render.x.domain()[0]) / (c - render.x.domain()[0]);

		// get max zoom, set zoom
		var minDist = null;
		for (var i = 0; i < events.length - 1; i++) {
			var dist = Math.abs(events[i].date - events[i+1].date);
			if ((!minDist || dist < minDist) && dist != 0) minDist = dist;
		}
		var zoomMax = minDist
			? (render.x.domain()[1] - render.x.domain()[0])
						* C.ZOOMMAXFACTOR / minDist
			: C.ZOOMMAXFACTOR;
		render.zoom
			.scaleExtent([initialScale, zoomMax])
		render.zoom.x(render.x);

		// set widths
		render.svg.attr("width", render.width);
		render.focus.select(".background").attr("width", render.width);
		render.contextMarkersEl.attr("width", render.width);

		// set context brush
		render.brushEl
			.call(render.brush)
			.selectAll("rect")
				.attr("y", 0)
				.attr("height", C.CONTEXTSTRIPHEIGHT);
		
		/* Set the initial scale/translate values */
		// We want to set the scale to be zoomed out initially so that we can
		// see the full text of the last event, as well as the initial margin,
		// which we will call M. Let a, b be the dates of the first and last
		// events. We need to find a date c such that when the timeline is
		// rendered from a to c, the rendering of b's event text box hits the
		// right edge of the timeline. Let W be the physical width of the
		// timeline and We be the width of the event text box. We are looking
		// for c such that
		// 	   (W - We - 2 * M) * (c - a) / W + a = b
		//		c = (b - a) * W / (W - We - 2 * M) + a
		// Now we can scale out to (b - a) / (c - a), and translate to M

		if (render.firstRender) {
			render.zoom
				.scale(zoomMax)
				.translate([-render.width * zoomMax / 2, 0]);
			doRender();

			render.secondRender = true;

			render.zoom
				.scale(initialScale)
				.translate([C.FIRST_RENDER_MARGIN, 0]);
			render.contextX.domain(render.x.domain());
			doRender();
			
			render.firstRender = false;
			render.secondRender = false;
		}
	}

	function doRender() {
		if (C.DEBUG) console.debug("render started")

		var onlyTranslate = true;

		// Modify events with new left/bottom coordinates

		// Depending on whether we've zoomed, brushed or are on our first
		// render, we will set s and t appropriately
		if (d3.event && d3.event.type == "zoom") {
			var t = d3.event.translate,
				s = d3.event.scale;

			t[0] = Math.min(C.PANMARGIN,	// upper bound
				Math.max(-render.width * (s - 1) - C.PANMARGIN - C.EVENTWIDTH, // lower bound
					t[0]));
			render.zoom.translate(t);
		} else if (d3.event && d3.event.type == "brush") {
			var s = render.dateDelta / (render.brush.extent()[1] - render.brush.extent()[0]);
			var t = [render.x(render.date0) - render.x(render.brush.extent()[0]), 0]

			render.zoom.translate(t);
			render.zoom.scale(s);
		} else {
			var s = render.zoom.scale();
			var t = render.zoom.translate();
		}

		// Next, set the left/bottom coordinates appropriately

		// prevTranslateX and prevScale are guaranteed to exist when they are
		// used because they are only used on the events, which will happen
		// after the first render
		if (render.firstRender || Math.abs(s - render.prevScale) > C.EPSILON) {
			render.prevScale = s;
			_.each(render.events, function (e) {
				e.reset();
				e.setLeft(render.x(e.date));
			} );
			render.scopedEvents = tlevents.setBottoms(render.events);
		} else {
			var deltaX = t[0] - render.prevTranslateX
			_.each(render.scopedEvents, function (e) {
				e.setLeft(e.left + deltaX);
			})
			onlyTranslate = true;
		}

		// If we didn't brush, render the brush to coincide with the current view
		if (!d3.event || d3.event.type != "brush") {
			render.brush.extent(render.x.domain());
			render.brushEl.call(render.brush);
		}
		
		render.prevTranslateX = t[0];


		// Render events with new left/bottom coordinates
		var textElements = render.focus.select('.text-elements').selectAll('g')
			.data(render.scopedEvents, function (e) { return e.id(); });
		var markers = render.focus.select('.markers').selectAll('rect')
			.data(render.scopedEvents, function (e) { return e.id(); });

		// only update:

		// If we are only translating elements, don't animate. If we are
		// scaling them, then animate. If we are rendering for the first time,
		// animate for longer.
		var transitionFn;
		if (onlyTranslate) {
			transitionFn = function (g) { return g; };
		} else if (render.firstRender) {
			transitionFn = function (g) {
				return g
					.transition()
					.duration(C.FIRST_RENDER_TRANSITION_DURATION)
					.ease(C.FIRST_RENDER_TRANSITION_EASING);
			};
		} else {
			transitionFn = function (g) {
				return g
					.transition()
					.duration(C.TRANSITIONDURATION)
					.ease("linear");
			}
		}

		// updateGroups
		transitionFn(textElements)
			.attr("transform", function (d) {
				return "translate(" + d.left + ", " + (C.TIMELINEHEIGHT - d.bottom - d.height) + ")";
			});
		transitionFn(markers)
			.attr("transform", function (d) {
				return "translate(" + d.left + ", " + (C.TIMELINEHEIGHT - d.bottom - d.height) + ")";
			})
			.attr("height", function (d) { return d.bottom + d.height - C.MARKEREXTRAHEIGHT; });
		textElements.style("opacity", 1);
		markers.style("opacity", 1);

		// only entering text elements
		var textElementsEnter = textElements.enter()
			.append("g")

		textElementsEnter
			.attr("transform", function (d) {
				return "translate(" + d.left + ", " + (C.TIMELINEHEIGHT - d.bottom - d.height) + ")";
			})
			.style("opacity", "0")
			.transition()
			.style("opacity", "1")
		textElementsEnter
			.append("foreignObject")
			.attr("height", function (d) {return d.height; })
			.attr("width", C.EVENTWIDTH)
			.append("xhtml:div")
			.html(function (d) { return d.html(); })

		// only entering marker elements
		markers.enter()
			.append("rect")
			.attr("transform", function (d) {
				return "translate(" + d.left + ", " + (C.TIMELINEHEIGHT - d.bottom - d.height) + ")";
			})
			.attr("width", C.MARKERWIDTH)
			.attr("y", C.MARKEREXTRAHEIGHT)
			.attr("height", function (d) { return d.bottom + d.height - C.MARKEREXTRAHEIGHT; })
			.style("opacity", "0")
			.transition()
			.style("opacity", "1")
		
		// only removed elements
		textElements.exit().transition().style("opacity", "0").remove();
		markers.exit().transition().style("opacity", "0").remove();
		
		// render xAxis
		render.xAxisEl.call(render.xAxis)

		if (render.secondRender) {
			// render context
			var contextMarkers = render.contextMarkersEl.selectAll('rect.marker')
				.data(render.events, function (e) { return e.id(); });

			contextMarkers.enter()
				.append('rect')
				.attr("class", "marker")
				.attr('width', C.MARKERWIDTH)
				.attr('height', C.CONTEXTSTRIPHEIGHT)
				.attr('x', function (d) { return render.contextX(d.date); })
		}

		if (C.DEBUG) console.debug("render finished");
	}
	function brushed() {
		if (!render.brush.empty()) {
			render.x.domain(render.brush.extent());

			doRender();
		}
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

			createRenderAndSvg();
			setRenderEvents(events);
			setRenderWidth();
			// doRender();
		});
	}

	$(function(){
		$('#query').keypress(function (e) {
			if (e.which == 13) {
				foo();
				return false;
			}
		})

		$(window).resize(function() {
			setRenderWidth();
			doRender();
		})
	})
})