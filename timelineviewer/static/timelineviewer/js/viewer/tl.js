define(['jquery', 'underscore', 'd3', 'viewer/tlevents', 'viewer/consts'], function ($, _, d3, tlevents, C) {

	var Timeline = (function() {
		// static class variables
		var allTimelines = [];
		var allFirstDate = false;
		var allLastDate = false;

		// class methods
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
				this.resetRenderWidth = false;
			},
			setRenderEvents: function (events) {
				this.events = events;
			},
			setRenderWidth: function () {
				// local var for convenience
				var events = this.events;

				// get first and last date
				var firstDate = events[(events.length- 1)].date;
				var lastDate = events[0].date;

				if (this.synced) {
					var allRangeModified = false;
					if (allFirstDate === false || firstDate < allFirstDate) {
						allFirstDate = firstDate;
						allRangeModified = true;
					} else {
						firstDate = allFirstDate;
					}
					if (allLastDate === false || lastDate > allLastDate) {
						allLastDate = lastDate;
						allRangeModified = true;
					} else {
						lastDate = allLastDate;
					}

					if (allRangeModified) {
						_.each(allTimelines, function (other) {
							if (other !== this) { other.setRenderWidth(); }
						});
					}
				}

				this.dateDelta = lastDate - firstDate;
				this.firstDate = firstDate;

				this.width = $(window).width();

				// create scales/axes
				this.x.range([0, this.width]);
				this.contextX.range([0, this.width]);
				this.xAxis.scale(this.x).orient("bottom");
				this.x.domain([firstDate, lastDate]);
				this.xAxisEl.call(this.xAxis);

				// calculate values for initial/min scale
				var c = (lastDate - firstDate)
						* this.width / (this.width - C.EVENTWIDTH - 2 * C.FIRST_RENDER_MARGIN)
						+ firstDate;
				var initialScale = (lastDate - firstDate)
						/ (c - firstDate);

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
						.scale(initialScale * 2)
						.translate([-this.width * (initialScale ) / 2, 0]);
					this.doRender();

					this.secondRender = true;
					this.firstRender = false;

					this.zoom
						.scale(initialScale)
						.translate([C.FIRST_RENDER_MARGIN, 0]);
					this.contextX.domain(this.x.domain());
					this.doRender();
					
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

					this.resetRenderWidth = true;
					this.doRender();
					this.resetRenderWidth = false;
				}
			},
			doRender: function (s, t) {
				if (C.DEBUG) console.debug("render started");

				var p = this.renderUpdateZoomBrushEvents(s, t);
				console.log(p.s + ", " + p.t);
				this.renderUpdateTimelineBody(p.onlyTranslate);
				this.xAxisEl.call(this.xAxis);
				if (this.secondRender || this.resetRenderWidth) this.renderUpdateContextStrip();

				if (this.synced && !(s && t)) {
					var that = this;
					_.each(allTimelines, function (other) {
						if (other !== that && other.synced	) other.doRender(p.s, p.t);
					})
				}

				if (C.DEBUG) console.debug("render finished");
			},
			renderUpdateZoomBrushEvents: function (s, t) {
				var onlyTranslate = true;

				console.log(s + ", " + t);
				var setZoom = true;
				var setBrush = true;

				// enforce limits on translate, make zoom and brush cohere
				if (s && t) {
					// we will set brush and zoom by default to s and t
				} else if (d3.event && d3.event.type == "zoom") {
					t = d3.event.translate;
					s = d3.event.scale;

					t[0] = Math.min(C.PANMARGIN,	// upper bound
						Math.max(-this.width * (s - 1) - C.PANMARGIN - C.EVENTWIDTH, // lower bound
							t[0]));
					this.zoom.translate(t);

					setZoom = false;
				} else if (d3.event && d3.event.type == "brush") {
					s = this.dateDelta / (this.brush.extent()[1] - this.brush.extent()[0]);
					t = [this.x(this.firstDate) - this.x(this.brush.extent()[0]), 0]

					setBrush = false;
				} else {
					// this means that this is the first render or it's a
					// resetRenderWidth
					s = this.zoom.scale();
					t = this.zoom.translate();
				}

				if (setZoom) {
					this.zoom.translate(t);
					this.zoom.scale(s);
				}
				if (setBrush) {
					this.brush.extent(this.x.domain());
					this.brushEl.call(this.brush);
				}

				// Set the left/bottom coordinates appropriately
				// Note: prevTranslateX and prevScale are guaranteed to exist
				// because of firstRender
				if (this.firstRender || this.resetRenderWidth || Math.abs(s - this.prevScale) > C.EPSILON) {
					this.prevScale = s;
					_.each(this.events, function (e) {
						e.reset();
						e.setLeft(this.x(e.date));
					}, this);
					this.scopedEvents = tlevents.setBottoms(this.events);
					onlyTranslate = false;
				} else {
					var deltaX = t[0] - this.prevTranslateX
					_.each(this.scopedEvents, function (e) {
						e.setLeft(e.left + deltaX);
					}, this)
					onlyTranslate = true;
				}
				
				this.prevTranslateX = t[0];

				return { onlyTranslate: onlyTranslate, s: s, t: t }
			},
			renderUpdateTimelineBody: function (onlyTranslate) {
				// Note on transitions. Calling transition() on an element
				// when another transition is in progress will cancel the
				// existing transition. There are two bad scenarios that can
				// happen with a naive implementation.
				// 1. Object enters, then is moved before fade in finishes.
				//    The fade in will be not finish and the object is left
				//    semi-visible.
				//  - The solution is that there is a root element that only
				//    handles opacity transitions, and a child element that
				//    handles transform transitions. (The opacity one being
				//    root is necessary because the remove() call at the end
				//    of the fade out transition.) For text elements, the root
				//    object is a g .text-root and the transform-handling
				//    child is a g .text- transform. For markers, the root is
				//    a g, and the child is a line.
				// 2. Object exits, then is supposed to re-enter before the
				//    fade out finishes.
				//  - The solution is to mark all exiting objects (in this
				//    case with class 'exiting'). On an update, these objects
				//    will not show up in the enter() selection. They will
				//    show up in the update selection. So we check the update
				//    selection for '.exiting' objects, and start a new
				//    transition on them to cancel the fade out transition and
				//    bring them back to full opacity

				// - References
				//  - https://groups.google.com/forum/#!topic/d3-js/H7mLE0dF6-E
				//  - http://jsfiddle.net/xbfSU/ http://stackoverflow.com/questions/16335781/d3-js-stop-transitions-being-interrupted

				// First, create transition functions. If we are only
				// translating elements, don't animate. If we are rendering
				// for the first time, animate for longer. If we are scaling
				// them, then animate.
				var transformTransitionFn;
				if (onlyTranslate) {
					transformTransitionFn = function (g) { return g; };
				} else if (this.secondRender) {
					transformTransitionFn = function (g) {
						return g.transition().duration(C.FIRST_RENDER_TRANSITION_DURATION).ease(C.FIRST_RENDER_TRANSITION_EASING);
					};
				} else {
					transformTransitionFn = function (g) {
						return g.transition().duration(C.TRANSFORM_TRANSITION_DURATION).ease(C.TRANSFORM_TRANSITION_EASING);
					}
				}
				var fadeIn = function (g, reset) {
					if (reset) g.style("opacity", "0");
					g.transition().duration(C.OPACITY_TRANSITION_DURATION).ease(C.OPACITY_TRANSITION_EASING)
						.style("opacity", "1");
				};
				var fadeOut = function (g) {
					g.transition().duration(C.OPACITY_TRANSITION_DURATION).ease(C.OPACITY_TRANSITION_EASING)
						.style("opacity", "0")
						.remove();
				};

				// select elements
				var textElements = this.focus.select('.text-elements').selectAll('g.text-root')
					.data(this.scopedEvents, function (e) { return e.id(); });
				var markers = this.focus.select('.markers').selectAll('g')
					.data(this.scopedEvents, function (e) { return e.id(); });

				// update elements
				transformTransitionFn(textElements.select("g.text-transform"))
					.attr("transform", function (d) {
						return "translate(" + d.left + ", " + (C.TIMELINEHEIGHT - d.bottom - d.height) + ")";
					});
				transformTransitionFn(markers.select("line"))
					.attr("transform", function (d) {
						return "translate(" + d.left + ", " + (C.TIMELINEHEIGHT - d.bottom - d.height) + ")";
					})
					.attr("y2", function (d) { return d.bottom + d.height; });
				// this catches elements that are transitioning for exiting,
				// have not finished their transition yet, and were
				// reintroduced.
				var reenteringTexts = textElements.filter('.exiting').classed('exiting', false);
				fadeIn(reenteringTexts, false);
				var reenteringMarkers = markers.filter('.exiting').classed('exiting', false);
				fadeIn(reenteringMarkers, false);

				// only entering text elements
				var textElementsEnter = textElements.enter()
					.append("g")
					.attr("class", "text-root")
				fadeIn(textElementsEnter, true)
				var textInnerTransformGroup = textElementsEnter
					.append("g")
					.attr("class", "text-transform")
					.attr("transform", function (d) {
						return "translate(" + d.left + ", " + (C.TIMELINEHEIGHT - d.bottom - d.height) + ")";
					})
					.append("foreignObject")
					.attr("height", function (d) {return d.height; })
					.attr("width", C.EVENTWIDTH)
					.append("xhtml:div")
					.html(function (d) { return d.html(); })

				// only entering marker elements
				var markersEnter = markers.enter()
					.append("g");
				fadeIn(markersEnter, true);
				markersEnter.append("line")
					.attr("transform", function (d) {
						return "translate(" + d.left + ", " + (C.TIMELINEHEIGHT - d.bottom - d.height) + ")";
					})
					.attr("x1", "0")
					.attr("x2", "0")
					.attr("y1", C.MARKEREXTRAHEIGHT)
					.attr("y2", function (d) { return d.bottom + d.height; })
				
				// only removed elements
				var exitingTexts = textElements.exit().classed('exiting', true);
				fadeOut(exitingTexts);
				var exitingMarkers = markers.exit().classed('exiting', true);
				fadeOut(exitingMarkers);
			},
			renderUpdateContextStrip: function () {
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
		}

		// constructor
		function Timeline(p) {
			// Takes one parameter p that should have the following
			// properties: data, eventTemplate, invisibleEventsHolder,
			// headerTemplate timelineHolder. data should be [metadata:
			// {short_title, url}, events: [{date, content, importance}, ...]]
			var that = this;
			this.synced = true;

			$(window).on('resize', function () {
				that.setRenderWidth();
			});

			var events = _.map(p.data.events, function(ev) {
				return new tlevents.Event(ev, p.invisibleEventsHolder, p.eventTemplate);
			});

			this.createRenderAndSvg(p.timelineHolder, p.headerTemplate, p.data.metadata);
			this.setRenderEvents(events);
			this.setRenderWidth();

			allTimelines.push(this);
		}
		Timeline.prototype = baseObject;

		return Timeline;
	})();


	return { Timeline: Timeline };
})