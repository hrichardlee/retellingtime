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
			svg: svg,
			// these two need to be set so that we know to set a good default
			// when the timeline is first rendered
			prevScale: null,
			prevTranslateX: null
		}

		render.focus = svg.append("g");

		render.focus.append("rect")
			.attr("height", C.TOTALTIMELINEHEIGHT)
			.attr("class", "background");

		render.focus.append("g")
			.attr("class", "markers")
		render.focus.append("g")
			.attr("class", "text-elements")

		render.xAxisEl = svg.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + C.TIMELINEHEIGHT + ")");

		render.zoom = d3.behavior.zoom()
			.on("zoom", doRender);
		render.svg.call(render.zoom);

		render.firstRender = true;
	}
	function setRenderWidth() {
		// copy over old information
		render = {
				focus: render.focus,
				xAxisEl: render.xAxisEl,
				prevScale: render.prevScale,
				prevTranslateX: render.prevTranslateX,
				events: render.events,
				svg: render.svg,
				zoom: render.zoom,
				firstRender: render.firstRender
			}
		// local var for convenience
		var events = render.events;

		render.width = $(window).width();

		// create scales/axes
		render.x = d3.scale.linear().range([0, render.width]);
		// render.x2 = d3.scale.linear().range([0, render.width]);
		render.xAxis = d3.svg.axis().scale(render.x).orient("bottom"),
		// render.xAxis2 = d3.svg.axis().scale(x2).orient("bottom");
		render.x.domain([events[(events.length- 1)].date,
			events[0].date]);
		// render.x2.domain(render.x.domain());
		render.xAxisEl.call(render.xAxis)

		// get max zoom, set zoom
		var minDist = null;
		for (var i = 0; i < events.length - 1; i++) {
			var dist = events[i].date - events[i+1].date;
			if (!minDist || dist < minDist) minDist = dist;
		}
		var zoomMax = (render.x.domain()[1] - render.x.domain()[0])
						* C.ZOOMMAXFACTOR / minDist ;
		render.zoom
			.scaleExtent([C.ZOOMMIN, zoomMax])
		render.zoom.x(render.x);

		// set widths
		render.svg.attr("width", render.width);
		render.focus.select(".background").attr("width", render.width);
		
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
			var c = (events[0].date - events[(events.length- 1)].date)
					* render.width / (render.width - C.EVENTWIDTH - 2 * C.FIRST_RENDER_MARGIN)
					+ events[(events.length- 1)].date;
			var initialScale = (render.x.domain()[1] - render.x.domain()[0]) / (c - render.x.domain()[0]);

			render.zoom
				.scale(zoomMax)
				.translate([-render.width * zoomMax / 2, 0])

			doRender();

			render.zoom
				.scale(initialScale)
				.translate([C.FIRST_RENDER_MARGIN, 0])

			doRender();
			
			render.firstRender = false;
		}

// render.context = svg.append("g")
//     .attr("transform", "translate(" + 0 + "," + 510 + ")");
		// .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	}

	function doRender() {
		console.debug("render started")

		// Modify events with new left/bottom coordinates
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

			if (render.firstRender || s != render.prevScale) {
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

		// Render events with new left/bottom coordinates
		var textElements = render.focus.select('.text-elements').selectAll('g')
			.data(render.scopedEvents, function (e) { return e.id(); });
		var markers = render.focus.select('.markers').selectAll('rect')
			.data(render.scopedEvents, function (e) { return e.id(); });

		//only update:
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
			.attr("width", 2)
			.attr("y", C.MARKEREXTRAHEIGHT)
			.attr("height", function (d) { return d.bottom + d.height - C.MARKEREXTRAHEIGHT; })
			.style("opacity", "0")
			.transition()
			.style("opacity", "1")
		
		// only removed elements
		textElements.exit().transition().style("opacity", "0").remove();
		markers.exit().transition().style("opacity", "0").remove();
		
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

			createRenderAndSvg();
			render.events = events;
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