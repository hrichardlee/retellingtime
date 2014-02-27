define(['jquery', 'underscore', 'd3', 'viewer/tlevents', 'viewer/consts'], function ($, _, d3, tlevents, C) {

	var render = null;



	var Timeline = (function() {
		var render;

		var baseObject = {
			brushed: function () {
				if (!this.brush.empty()) {
					this.x.domain(this.brush.extent());

					this.doRender();
				}
			},
			createRenderAndSvg: function (timelineholder, headerTemplate, metadata) {
				var that = this;

				var baseEl = timelineholder.append("div");
				baseEl.append("div").html(headerTemplate(metadata));

				// initialize svg and such
				this.svg = baseEl.append("svg")
					.attr("height", C.TOTALTIMELINEHEIGHT);
				this.svg.attr("width", "100%");

				this.svg.append("defs").append("clipPath")
					.attr("id", "clip");


				this.focus = this.svg.append("g");

				this.zoom = d3.behavior.zoom()
					.on("zoom", function () { that.doRender(); });
				this.focus.call(this.zoom);
				this.x = d3.scale.linear();

				this.focus.append("rect")
					.attr("height", C.TIMELINEHEIGHT)
					.attr("class", "background")
					.attr("width", "100%");

				this.focus.append("g")
					.attr("class", "markers");
				this.focus.append("g")
					.attr("class", "text-elements");


				this.xAxisEl = this.svg.append("g")
					.attr("class", "x axis")
					.attr("height", C.AXISHEIGHT)
					.attr("transform", "translate(0," + C.TIMELINEHEIGHT + ")");

				this.xAxis = d3.svg.axis();


				var context = this.svg.append("g")
					.attr("height", C.CONTEXTSTRIPHEIGHT)
					.attr("transform", "translate(0," + (C.TIMELINEHEIGHT + C.AXISHEIGHT) + ")");

				this.contextX = d3.scale.linear();

				this.contextMarkersEl = context.append("g")
					.attr("width", "100%");

				this.brush = d3.svg.brush()
					.x(this.contextX)
					.on("brush", function () { that.brushed(); } );

				this.brushEl = context.append("g")
					.attr("class", "x brush");

				this.firstRender = true;
				this.secondRender = false;
			},
			setRenderEvents: function (events) {
				this.events = events;
				this.dateDelta = events[0].date - events[(events.length - 1)].date;
				this.date0 = events[(events.length - 1)].date;
			},
			setRenderWidth: function () {
				// local var for convenience
				var events = this.events;

				this.width = $(window).width();

				// create scales/axes
				this.x.range([0, this.width]);
				this.contextX.range([0, this.width]);
				this.xAxis.scale(this.x).orient("bottom");
				this.x.domain([events[(events.length- 1)].date,
					events[0].date]);
				this.xAxisEl.call(this.xAxis);

				// calculate values for initial/min scale
				var c = (events[0].date - events[(events.length- 1)].date)
						* this.width / (this.width - C.EVENTWIDTH - 2 * C.FIRST_RENDER_MARGIN)
						+ events[(events.length- 1)].date;
				var initialScale = (events[0].date - events[(events.length- 1)].date)
						/ (c - events[(events.length- 1)].date);

				// get max zoom, set zoom
				var minDist = null;
				for (var i = 0; i < events.length - 1; i++) {
					var dist = Math.abs(events[i].date - events[i+1].date);
					if ((!minDist || dist < minDist) && dist != 0) minDist = dist;
				}
				var zoomMax = minDist
					? (this.x.domain()[1] - this.x.domain()[0])
								* C.ZOOMMAXFACTOR / minDist
					: C.ZOOMMAXFACTOR;
				this.zoom
					.scaleExtent([initialScale, zoomMax])
				this.zoom.x(this.x);

				// set context brush
				this.brushEl
					.call(this.brush)
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

				if (this.firstRender) {
					this.zoom
						.scale(zoomMax)
						.translate([-this.width * zoomMax / 2, 0]);
					this.doRender();

					this.secondRender = true;

					this.zoom
						.scale(initialScale)
						.translate([C.FIRST_RENDER_MARGIN, 0]);
					this.contextX.domain(this.x.domain());
					this.doRender();
					
					this.firstRender = false;
					this.secondRender = false;
				} else {
					// this is just to set the contextX domain correctly
					this.zoom
						.scale(initialScale)
						.translate([C.FIRST_RENDER_MARGIN, 0]);
					this.contextX.domain(this.x.domain());

					this.zoom
						.scale(this.prevScale)
						.translate([this.prevTranslateX, 0]);
				}
			},
			doRender: function () {
				if (C.DEBUG) console.debug("render started")

				var onlyTranslate = true;
				var resize = false;

				// Modify events with new left/bottom coordinates

				// Depending on whether we've zoomed, brushed or are on our first
				// render, we will set s and t appropriately
				if (d3.event && d3.event.type == "zoom") {
					var t = d3.event.translate,
						s = d3.event.scale;

					t[0] = Math.min(C.PANMARGIN,	// upper bound
						Math.max(-this.width * (s - 1) - C.PANMARGIN - C.EVENTWIDTH, // lower bound
							t[0]));
					this.zoom.translate(t);
				} else if (d3.event && d3.event.type == "brush") {
					var s = this.dateDelta / (this.brush.extent()[1] - this.brush.extent()[0]);
					var t = [this.x(this.date0) - this.x(this.brush.extent()[0]), 0]

					this.zoom.translate(t);
					this.zoom.scale(s);
				} else {
					var s = this.zoom.scale();
					var t = this.zoom.translate();

					// not zoom or brush means this is the first render or
					// it's a resize
					resize = !this.firstRender;
				}

				// Next, set the left/bottom coordinates appropriately

				// prevTranslateX and prevScale are guaranteed to exist when they are
				// used because they are only used on the events, which will happen
				// after the first render
				if (this.firstRender || resize || Math.abs(s - this.prevScale) > C.EPSILON) {
					this.prevScale = s;
					_.each(this.events, function (e) {
						e.reset();
						e.setLeft(this.x(e.date));
					}, this);
					this.scopedEvents = tlevents.setBottoms(this.events);
				} else {
					var deltaX = t[0] - this.prevTranslateX
					_.each(this.scopedEvents, function (e) {
						e.setLeft(e.left + deltaX);
					}, this)
					onlyTranslate = true;
				}

				// If we didn't brush, render the brush to coincide with the current view
				if (!d3.event || d3.event.type != "brush") {
					this.brush.extent(this.x.domain());
					this.brushEl.call(this.brush);
				}
				
				this.prevTranslateX = t[0];


				// Render events with new left/bottom coordinates
				var textElements = this.focus.select('.text-elements').selectAll('g')
					.data(this.scopedEvents, function (e) { return e.id(); });
				var markers = this.focus.select('.markers').selectAll('rect')
					.data(this.scopedEvents, function (e) { return e.id(); });

				// only update:

				// If we are only translating elements, don't animate. If we are
				// scaling them, then animate. If we are rendering for the first time,
				// animate for longer.
				var transitionFn;
				if (onlyTranslate) {
					transitionFn = function (g) { return g; };
				} else if (this.firstRender) {
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
				this.xAxisEl.call(this.xAxis)

				if (this.secondRender || resize) {
					// render context
					var contextMarkers = this.contextMarkersEl.selectAll('rect.marker')
						.data(this.events, function (e) { return e.id(); });

					var that = this;
					contextMarkers.enter()
						.append('rect')

					contextMarkers
						.attr("class", "marker")
						.attr('width', C.MARKERWIDTH)
						.attr('height', C.CONTEXTSTRIPHEIGHT)
						.attr('x', function (d) { return that.contextX(d.date); })
				}

				if (C.DEBUG) console.debug("render finished");
			}
		}
		function Timeline(p) {
			// Takes one parameter p that should have the following
			// properties: data, eventTemplate, invisibleEventsHolder,
			// headerTemplate timelineHolder. data should be [metadata:
			// {short_title, url}, events: [{date, content, importance}, ...]]
			var that = this;
			$(window).on('resize', function () {
				that.setRenderWidth();
				that.doRender();
			});

			var events = _.map(p.data.events, function(ev) {
				return new tlevents.Event(ev, p.invisibleEventsHolder, p.eventTemplate);
			});

			this.createRenderAndSvg(p.timelineHolder, p.headerTemplate, p.data.metadata);
			this.setRenderEvents(events);
			this.setRenderWidth();
		}
		Timeline.prototype = baseObject;
		return Timeline;
	})();


	return { Timeline: Timeline };
})