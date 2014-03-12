define(['jquery', 'underscore', 'd3', 'viewer/tlevents', 'viewer/consts'], function ($, _, d3, tlevents, C) {

	var Timeline = (function() {
		// static class variables and functions

		// date stuff
		function isLeap(y) {
			if (y % 400 === 0) {
				return true;
			} else if (y % 100 === 0) {
				return false;
			} else if (y % 4 === 0) {
				return true;
			} else {
				return false;
			}
		}
		var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
		var monthLengthsCommon =    [31, 28, 31, 30, 31,  30,  31,  31,  30,  31,  30,  31]
		var monthCumLengthsCommon = [0,  31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
		var monthLengthsLeap =      [31, 29, 31, 30, 31,  30,  31,  31,  30,  31,  30,  31]
		var monthCumLengthsLeap =   [0,  31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
		var monthFractionsCommon = _.map(monthLengthsCommon, function (x) { return x / 365; });
		var monthCumFractionsCommon = _.map(monthCumLengthsCommon, function (x) { return x / 365; });
		var monthFractionsLeap = _.map(monthLengthsLeap, function (x) { return x / 366; });
		var monthCumFractionsLeap = _.map(monthCumLengthsLeap, function (x) { return x / 366; });
		function monthDayFromFraction(f, year) {
			if (isLeap(year)) {
				var monthFractions = monthFractionsCommon;
				var monthCumFractions = monthCumFractionsCommon;
				var monthLengths = monthLengthsCommon;
			} else {
				var monthFractions = monthFractionsLeap;
				var monthCumFractions = monthCumFractionsLeap;
				var monthLengths = monthLengthsLeap;
			}

			var monthIndex = monthCumFractions.indexOf(
				_.find(monthCumFractions, function (x) {
					return x > f;
				})
			) - 1;
			var monthStart = monthCumFractions[monthIndex];
			var day = Math.round((f - monthStart) / monthFractions[monthIndex] * monthLengths[monthIndex]) + 1;
			if (day > monthLengths[monthIndex]) {
				day = 1;
				monthIndex += 1;
			}
			var yearAdjust = 0;
			if (monthIndex > 11) {
				monthIndex = 1;
				yearAdjust = 1;
			}

			//return [monthNames[monthIndex], day];
			return [yearAdjust, day + ' ' + monthNames[monthIndex]];
		}
		function closestMonthStartFromFraction(f, year) {
			if (isLeap(year)) {
				var monthFractions = monthFractionsCommon;
				var monthCumFractions = monthCumFractionsCommon;
				var monthLengths = monthLengthsCommon;
			} else {
				var monthFractions = monthFractionsLeap;
				var monthCumFractions = monthCumFractionsLeap;
				var monthLengths = monthLengthsLeap;
			}

			var monthIndex = monthCumFractions.indexOf(
				_.find(monthCumFractions, function (x) {
					return x > f;
				})
			) - 1;
			var a = monthCumFractions[monthIndex];
			var b = monthCumFractions[monthIndex + 1];
			return Math.abs(f - a) < Math.abs(f - b) ? a : b;
		}

		function tickValuesFn(t0, t1) {
			var m = t1 - t0 < 2 ? 8 : 10;

			// this code is taken from
			// https://github.com/mbostock/d3/blob/c247e1626118de41b3d40e2a711354f76e004343/src/scale/linear.js
			var span = t1 - t0;
			var step = Math.pow(10, Math.floor(Math.log(span / m) / Math.LN10));
			var err = m / span * step;

			// Filter ticks to get closer to the desired count.
			if (err <= .15) step *= 10;
			else if (err <= .35) step *= 5;
			else if (err <= .75) step *= 2;

			// Round start and stop values to step interval.
			t0 = Math.ceil(t0 / step) * step;
			t1 = Math.floor(t1 / step) * step + step * .5; // inclusive

			var origTicks = _.range(t0, t1, step);
			// End copied code
			var newTicks = _.map(origTicks, function (d) {
				if (d > 0) {
					if (d === (d|0)) {
						return d;
					} else {
						if (step > 60/365) {
							var frac = d - (d|0);
							var year = d|0;
							var closest = closestMonthStartFromFraction(frac, year);
							return year + closest;
						} else {
							return d;
						}
					}
				} else if (d >= -10001) {
					if (step > 4) {
						return d + 1;
					} else {
						return d;
					}
				} else { // d < -10001
					if (step > 2000) {
						return d + 1950;	
					} else if (step > 200) {
						return d + 50;
					} else {
						return d;
					}
				}
			});
			return newTicks;
		}

		function tickFormatFn(d) {
			if (d > 0) {
				// d = [1, infinity] = d AD
				if (d === (d|0)) {
					return d.toString();	
				} else {
					var frac = d - (d|0);
					var year = d|0;
					var monthDay = monthDayFromFraction(frac, year);
					return monthDay[1] + ' ' + (year + monthDay[0]).toString();
				}
			} else if (d >= -10001) {
				// d = [-10001, 0] = (-d + 1) BC
				return (-d + 1).toString() + ' BC';
			} else {
				// d = [-infinity, -100002] = (-d + 1950) / 1000000 Ma
				return d3.format(",.0f")((-d + 1950) / 1000000) + ' Ma';
			}
		}

		// static variables and functions
		var allTimelines = [];
		function setHash() {
			window.location.hash =
				_.map(allTimelines, function (t) {
					return t.title;
				}).join('&');
		}
		var widthParams = {
			minDistFromEvents: function (events) {
				var minDist = null;
				for (var i = 0; i < events.length - 1; i++) {
					var dist = Math.abs(events[i].date - events[i+1].date);
					if ((!minDist || dist < minDist) && dist != 0)
						minDist = dist;
				}
				return minDist;
			},
			addNewEvents: function (events) {
				// Returns whether or not the parameters were changed. If events
				// is passed in, we assume that only those events were added. If
				// no events are passed in, then we assume that events were
				// removed and check allTimelines
				if (widthParams.isFocused) {
					widthParams.removeFocus();
					_.each(allTimelines, function (t) {
						t.resetFocus(false);
					});
				}

				var widthParamsModified = false;

				var newFirstDate = events[(events.length- 1)].date;
				var newLastDate = events[0].date;

				if (!widthParams.firstDate || newFirstDate < widthParams.firstDate) {
					widthParams.firstDate = newFirstDate;
					widthParamsModified = true;
				}
				if (!widthParams.lastDate || newLastDate > widthParams.lastDate) {
					widthParams.lastDate = newLastDate;
					widthParamsModified = true;
				}

				// get minDist

				var newMinDist = widthParams.minDistFromEvents(events);

				if (newMinDist && (!widthParams.minDist || newMinDist < widthParams.minDist)) {
					widthParamsModified = true;
					widthParams.minDist = newMinDist;
				}

				return widthParamsModified;
			},
			removedTimelines: function () {
				if (widthParams.isFocused) {
					widthParams.removeFocus();
					_.each(allTimelines, function (t) {
						t.resetFocus(false);
					});
				}

				var widthParamsModified = false;

				// timeline was removed
				var newFirstDate = _.min(
					_.map(allTimelines, function (t) {
						return t.events[(t.events.length - 1)].date;
					})
				);
				var newLastDate = _.max(
					_.map(allTimelines, function (t) {
						return t.events[0].date;
					})
				);

				if (newFirstDate != widthParams.firstDate || newLastDate != widthParams.lastDate) {
					widthParamsModified = true;
				}
				widthParams.firstDate = newFirstDate;
				widthParams.lastDate = newLastDate;

				// get minDist
				var newMinDist = _.min(
					_.map(allTimelines, function (t) {
						return widthParams.minDistFromEvents(t.events);
					})
				);

				if (newMinDist != widthParams.minDist) {
					widthParamsModified = true;
				}
				widthParams.minDist = newMinDist;

				if (allTimelines.length == 1) {
					allTimelines[0].setRenderHeight(Math.max($(window).height() - C.TALLTIMELINEMARGIN, C.SHORTTIMELINEHEIGHT));
				}

				return widthParamsModified;
			},
			setFocus: function (firstDate, lastDate) {
				widthParams.oldFirstDate = widthParams.firstDate;
				widthParams.oldLastDate = widthParams.lastDate;

				widthParams.firstDate = firstDate;
				widthParams.lastDate = lastDate;

				widthParams.isFocused = true;
			},
			removeFocus: function () {
				widthParams.firstDate = widthParams.oldFirstDate;
				widthParams.lastDate = widthParams.oldLastDate;

				widthParams.isFocused = false;
			},
			init: function () {
				if (!widthParams.x) {
					widthParams.x = d3.scale.linear();
					widthParams.contextX = d3.scale.linear();
					widthParams.isFocused = false;
					$(window).on('resize', function () {
						widthParams.setWidth(true);
					});
				}
			},
			setWidth: function (retainWindow) {
				// we're still using the "old" parameters here:
				if (retainWindow && allTimelines.length > 0) {
					// this is pretty hacky, caused by having multiple zooms/brushes for each timeline
					var a = allTimelines[0].x.invert(0);
					var b = allTimelines[0].x.invert(widthParams.width);
				}

				// a/b is the smallest/largest visible date in the old scale
				// once we create the new scale x0, we want to set the initial scale/translate
				// such that x(a) = 0 and x(b) = width remains true. s, t modify x0 to produce x
				// in the following way:
				// 		x(d) = x0(d) * s + t 
				// Now we simply solve the equations:
				// 		x0(a) * s + t = 0
				//		x0(b) * s + t = width
				// To find
				// 		=>	t = -x0(a) * s
				//			t = width - x0(b) * s
				// 		=>	-x0(a) * s = width - x0(b) * s
				//		=>	s = width / (x0(b) - x0(a))

				// now use the old parameters
				widthParams.width = $(window).width();

				if (widthParams.isFocused) {
					widthParams.initialScale = 1;
					widthParams.initialTranslate = 0;
					widthParams.secondRenderScale = 1;
					widthParams.secondRenderTranslate = 0;
				} else {
					// calculate values for initial/min scale:
					// - We want to set the scale to be zoomed out initially so that we can
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
					var c = (widthParams.lastDate - widthParams.firstDate)
							* widthParams.width / (widthParams.width - C.EVENTWIDTH - 2 * C.FIRST_RENDER_MARGIN)
							+ widthParams.firstDate;
					widthParams.initialScale = (widthParams.lastDate - widthParams.firstDate) /
							(c - widthParams.firstDate);
					widthParams.initialTranslate = C.FIRST_RENDER_MARGIN;
				}

				widthParams.x.range([0, widthParams.width]);
				widthParams.contextX.range([0, widthParams.width]);
				widthParams.x.domain([widthParams.firstDate, widthParams.lastDate]);

				if (retainWindow) {
					// see notes above about retaining the view in the window
					widthParams.secondRenderScale = widthParams.width / (widthParams.x(b) - widthParams.x(a));
					widthParams.secondRenderTranslate = -widthParams.x(a) * widthParams.secondRenderScale;
				} else {
					widthParams.secondRenderScale = widthParams.initialScale;
					widthParams.secondRenderTranslate = widthParams.initialTranslate;
				}

				widthParams.zoomMax = widthParams.minDist
					? (widthParams.x.domain()[1] - widthParams.x.domain()[0])
								* C.ZOOMMAXFACTOR / widthParams.minDist
					: C.ZOOMMAXFACTOR;

				_.each(allTimelines, function (t) {
					t.setRenderWidth();
				});
			}
		};
		// class methods
		var baseObject = {
			brushed: function () {
				if (!this.brush.empty()) {
					this.x.domain(this.brush.extent());

					this.doRender();
				}
			},
			createHeaderActions: function (headerEl) {
				this.headerEl = headerEl;

				var that = this;
				$('a#remove-link', headerEl).click(function (e) {
					// TODO: need to deal with allTimelines, allFirstDate, allLastDate
					that.baseEl.remove();
					var index = allTimelines.indexOf(that);
					if (index > -1) {
						allTimelines.splice(index, 1);
					}
					if (widthParams.removedTimelines() || allTimelines.length == 1) {
						widthParams.setWidth(false);
					}
					setHash();

					if (that.resizeFn) {
						$(window).off('resize', that.resizeFn);
					}
				})

				$('a#set-focus-link #active', headerEl).addClass('hidden');
				$('a#set-focus-link', headerEl).click(function (e) {
					if (!$('a#set-focus-link #inactive', headerEl).hasClass('hidden') && $('a#set-focus-link #active', headerEl).hasClass('hidden')) {
						var domain = that.x.domain();
						widthParams.setFocus(domain[0], domain[1]);
						_.each(allTimelines, function (t) {
							t.resetFocus(true);
						});
					} else {
						widthParams.removeFocus();
						_.each(allTimelines, function (t) {
							t.resetFocus(false);
						});
					}

					widthParams.setWidth(true);
				})
			},
			resetFocus: function (isactive) {
				var active = $('a#set-focus-link #active', this.headerEl);
				var inactive = $('a#set-focus-link #inactive', this.headerEl);

				if (isactive) {
					active.removeClass('hidden');
					inactive.addClass('hidden');
				} else {
					inactive.removeClass('hidden');
					active.addClass('hidden');
				}
			},
			createBaseEl: function (timelineHolder, height) {
				var baseEl = timelineHolder.append('div');
				this.baseEl = baseEl;

				baseEl.append('div')
					.classed('loading-indicator', true)
					.text('loading...');
			},
			createRenderAndSvg: function (headerTemplate, metadata) {
				var that = this;

				widthParams.init();
				var baseEl = this.baseEl;
				baseEl.text('');
				var headerEl = baseEl.append('div')
					.classed('timeline-header', true)
					.html(headerTemplate(metadata));
				this.createHeaderActions(headerEl[0][0])

				this.zoomableHolder = baseEl.append('div')
					.classed('zoomable-holder', true)
				this.textElementsHolder = this.zoomableHolder.append('div')
					.classed('text-elements-holder', true);

				// initialize svg and such
				this.focus = this.zoomableHolder.append('svg');
				this.focus.attr('width', '100%');

				this.zoom = d3.behavior.zoom()
					.on('zoom', function () { that.doRender(); });
				this.zoomableHolder.call(this.zoom);

				this.focus.append('rect')
					.classed('background', true)
					.attr('width', '100%');

				this.focus.append('g')
					.classed('markers', true);
				this.focus.append('g')
					.classed('range-lines', true);


				this.axisSvg = baseEl.append('svg')
					.attr('height', C.AXISHEIGHT + C.CONTEXTSTRIPHEIGHT)
					.attr('width', '100%');

				this.xAxisEl = this.axisSvg.append('g')
					.classed({'x': true, 'axis': true})
					.attr('height', C.AXISHEIGHT);


				this.xAxis = d3.svg.axis()
					.tickValues(function () {
						return tickValuesFn(that.x.domain()[0], that.x.domain()[1]);
					})
					.tickFormat(tickFormatFn);

				var context = this.axisSvg.append('g')
					.attr('height', C.CONTEXTSTRIPHEIGHT)
					.attr('transform', 'translate(0,' + C.AXISHEIGHT + ')');
				this.context = context;

				this.contextMarkersEl = context.append('g')
					.attr('width', '100%')
					.classed('context-markers', true);

				this.brush = d3.svg.brush()
					.x(widthParams.contextX)
					.on('brush', function () { that.brushed(); } );

				this.brushEl = context.append('g')
					.classed({'x': true, 'brush': true});

				this.firstRender = false;
				this.secondRender = false;
				this.resetRenderWidth = false;
			},
			setRenderEvents: function (events) {
				this.events = events;
				widthParams.addNewEvents(events)
			},
			setRenderHeight: function (height) {
				this.height = height;

				this.focus.attr('height', height);
				this.focus.select('.background').attr('height', height);
				this.zoomableHolder.style('height', height + 'px');
				this.textElementsHolder.style('height', height + 'px');
			},
			setRenderWidth: function () {
				this.dateDelta = widthParams.lastDate - widthParams.firstDate;
				this.firstDate = widthParams.firstDate;

				// create axes
				// this is pretty hacky, caused by having multiple zooms/brushes
				this.x = widthParams.x.copy();
				this.xAxis.scale(this.x).orient('bottom');
				this.xAxisEl.call(this.xAxis);

				// set max zoom
				this.zoom
					.scaleExtent([widthParams.initialScale, widthParams.zoomMax])
				this.zoom.x(this.x);

				// set context brush
				this.brushEl
					.call(this.brush)
					.selectAll('rect')
						.attr('y', 0)
						.attr('height', C.CONTEXTSTRIPHEIGHT);

				if (this.firstRender) {
					this.zoom
						.scale(widthParams.initialScale * 2)
						.translate([-widthParams.width * (widthParams.initialScale ) / 2, 0]);
					this.doRender(null, null, true);

					this.secondRender = true;
					this.firstRender = false;

					this.zoom
						.scale(widthParams.initialScale)
						.translate([widthParams.initialTranslate, 0]);
					widthParams.contextX.domain(this.x.domain());
					this.doRender(null, null, true);
					
					this.secondRender = false;
				} else {
					// this is just to set the contextX domain correctly
					this.zoom
						.scale(widthParams.initialScale)
						.translate([widthParams.initialTranslate, 0]);
					widthParams.contextX.domain(this.x.domain());

					this.prevScale = widthParams.secondRenderScale;
					this.prevTranslateX = widthParams.secondRenderTranslate;
					this.zoom
						.scale(this.prevScale)
						.translate([this.prevTranslateX, 0]);

					this.resetRenderWidth = true;
					this.doRender(null, null, true);
					this.resetRenderWidth = false;
				}
			},
			doRender: function (s, t, dontpropagate) {
				if (C.DEBUG) console.debug('render started');

				var p = this.renderUpdateZoomBrushEvents(s, t);
				this.renderUpdateTimelineBody(p.onlyTranslate);
				this.xAxisEl.call(this.xAxis);
				//if (this.secondRender || this.resetRenderWidth)
					this.renderUpdateContextStrip();

				if (!(s && t) && !dontpropagate) {
					var that = this;
					_.each(allTimelines, function (other) {
						if (other !== that) other.doRender(p.s, p.t);
					})
				}

				if (C.DEBUG) console.debug('render finished');
			},
			renderUpdateZoomBrushEvents: function (s, t) {
				var onlyTranslate = true;

				var setZoom = true;
				var setBrush = true;

				// enforce limits on translate, make zoom and brush cohere
				if (s && t) {
					// we will set brush and zoom by default to s and t
				} else if (d3.event && d3.event.type == 'zoom') {
					t = d3.event.translate;
					s = d3.event.scale;

					if (widthParams.isFocused) {
						var upperBound = 0;
						var lowerBound = -widthParams.width * (s - 1);
						// lowerBound 
					} else {
						var upperBound = C.PANMARGIN;
						var lowerBound = -widthParams.width * (s - 1) - C.PANMARGIN - C.EVENTWIDTH;
					}
					t[0] = Math.min(upperBound, Math.max(lowerBound, t[0]));

					this.zoom.translate(t);

					setZoom = false;
				} else if (d3.event && d3.event.type == 'brush') {
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

				var that = this;

				// Set the left/bottom coordinates appropriately
				// Note: prevTranslateX and prevScale are guaranteed to exist
				// because of firstRender
				if (this.firstRender || this.resetRenderWidth || Math.abs(s - this.prevScale) > C.EPSILON) {
					this.prevScale = s;
					widthParams.prevScale = s; // we need separate global and local copies because of the if check above
					_.each(this.events, function (e) {
						e.reset();
						e.setLeft(that.x(e.date));
					}, this);
					this.scopedEvents = tlevents.setBottoms(this.events, this.height);
					_.each(this.events, function (e) {
						e.height_from_top = that.height - e.bottom - e.height;
					})
					onlyTranslate = false;
				} else {
					var deltaX = t[0] - this.prevTranslateX
					_.each(this.scopedEvents, function (e) {
						e.setLeft(e.left + deltaX);
					}, this)
					onlyTranslate = true;
				}
				
				this.prevTranslateX = t[0];
				widthParams.prevTranslateX = t[0];

				this.scopedAndFilteredEvents = _.filter(this.scopedEvents, function (e) {
					return e.right >= -C.EVENTWIDTH && e.left <= widthParams.width + C.EVENTWIDTH;
				});

				// set data for range lines
				this.rangeLinesEvents = _.filter(this.scopedAndFilteredEvents, function (e) {
					return e.date_length > 0;
				});
				var rangeTriangleLocal = 'l ' + (-C.RANGETRIANGLEWIDTH) + ' ' + (C.RANGETRIANGLEHEIGHT / 2) + ' l 0 ' + (-C.RANGETRIANGLEHEIGHT) + ' z'
				_.each(this.rangeLinesEvents, function (e) {
					var rightEnd = that.x(e.date + e.date_length) - e.left;
					if (rightEnd >= 3) {
						e.date_length_x = rightEnd - 3;
						e.triangle_path = 'M ' + rightEnd + ' 0 ' + rangeTriangleLocal;
					} else {
						e.date_length_x = 0;
						e.triangle_path = '';
					}
				});

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
					if (reset) g.style('opacity', '0');
					g.transition().duration(C.OPACITY_TRANSITION_DURATION).ease(C.OPACITY_TRANSITION_EASING)
						.style('opacity', '1');
				};
				var fadeOut = function (g) {
					g.transition().duration(C.OPACITY_TRANSITION_DURATION).ease(C.OPACITY_TRANSITION_EASING)
						.style('opacity', '0')
						.remove();
				};

				// select elements
				var textElements = this.textElementsHolder.selectAll('div.text-root')
					.data(this.scopedAndFilteredEvents, function (e) { return e.id(); });
				var markers = this.focus.select('.markers').selectAll('g')
					.data(this.scopedAndFilteredEvents, function (e) { return e.id(); });
				var rangeLines = this.focus.select('.range-lines').selectAll('g.range-line-root')
					.data(this.rangeLinesEvents, function (e) { return e.id(); });

				// update elements
				var that = this;
				transformTransitionFn(textElements.select('div.text-transform'))
					.style('top', function (d) { return d.height_from_top + 'px'; })
					.style('left', function (d) { return d.left + 'px'; });
				transformTransitionFn(markers.select('line'))
					.attr('transform', function (d) {
						return 'translate(' + d.left + ', ' + d.height_from_top + ')';
					})
					.attr('y2', function (d) { return d.bottom + d.height; });
				transformTransitionFn(rangeLines.select('g.range-line-transform'))
					.attr('transform', function (d) {
						return 'translate(' + d.left + ', ' + (d.height_from_top + d.height - C.RANGELINEBOTTOMPADDING) + ')';
					});
				transformTransitionFn(rangeLines.select('line'))
					.attr('x2', function (d) { return d.date_length_x; });
				transformTransitionFn(rangeLines.select('path'))
					.attr('d', function (d) { return d.triangle_path; });
				// this catches elements that are transitioning for exiting,
				// have not finished their transition yet, and were
				// reintroduced.
				var reenteringTexts = textElements.filter('.exiting').classed('exiting', false);
				fadeIn(reenteringTexts, false);
				var reenteringMarkers = markers.filter('.exiting').classed('exiting', false);
				fadeIn(reenteringMarkers, false);
				var reenteringRangeLines = rangeLines.filter('.exiting').classed('exiting', false);
				fadeIn(reenteringRangeLines, false);

				// only entering text elements
				var textElementsEnter = textElements.enter()
					.append('div')
					.classed('text-root', true);
				fadeIn(textElementsEnter, true);
				var textInnerTransformGroup = textElementsEnter
					.append('div')
					.classed('text-transform', true)
					.style('top', function (d) { return d.height_from_top + 'px'; })
					.style('left', function (d) { return d.left + 'px'; })
					.html(function (d) { return d.html(); })

				// only entering marker elements
				var markersEnter = markers.enter()
					.append('g');
				fadeIn(markersEnter, true);
				markersEnter.append('line')
					.attr('transform', function (d) {
						return 'translate(' + d.left + ', ' + d.height_from_top + ')';
					})
					.attr('x1', '0')
					.attr('x2', '0')
					.attr('y1', C.MARKEREXTRAHEIGHT)
					.attr('y2', function (d) { return d.bottom + d.height; })

				// only entering range lines
				var rangeLinesEnter = rangeLines.enter()
					.append('g')
					.classed('range-line-root', true);
				fadeIn(rangeLinesEnter, true);
				var rangeLineInnerTransformGroup = rangeLinesEnter
					.append('g')
					.classed('range-line-transform', true)
					.attr('transform', function (d) {
						return 'translate(' + d.left + ', ' + (d.height_from_top + d.height - C.RANGELINEBOTTOMPADDING) + ')';
					});
				rangeLineInnerTransformGroup
					.append('line')
					.attr('x1', '0')
					.attr('x2', function (d) { return d.date_length_x; })
					.attr('y1', '0')
					.attr('y2', '0');
				rangeLineInnerTransformGroup
					.append('path')
					.attr('d', function (d) { return d.triangle_path; });
				
				// only removed elements
				var exitingTexts = textElements.exit().classed('exiting', true);
				fadeOut(exitingTexts);
				var exitingMarkers = markers.exit().classed('exiting', true);
				fadeOut(exitingMarkers);
				var exitingRangeLines = rangeLines.exit().classed('exiting', true);
				fadeOut(exitingRangeLines);
			},
			renderUpdateContextStrip: function () {
				// render context
				var contextMarkers = this.contextMarkersEl.selectAll('line.marker')
					.data(this.events, function (e) { return e.id(); });

				var that = this;
				contextMarkers.enter()
					.append('line')
					.classed('marker', true)
					.attr('y1', 0)
					.attr('y2', C.CONTEXTSTRIPHEIGHT)

				contextMarkers
					.style('stroke', function (e) { return that.contextMarkerColor(e); })
					.attr('x1', function (e) { return widthParams.contextX(e.date); })
					.attr('x2', function (e) { return widthParams.contextX(e.date); })
			},
			contextMarkerColor: function (event) {
				// requires that this.maxImportance gets set
				if (!this.maxImportance) {
					this.maxImportance = Math.max.apply(null, _.map(this.events, function (e) { return e.importance; }));
				}

				var scaledImportance = Math.max(0, event.importance / this.maxImportance);
				var intensity = Math.min(1, scaledImportance * 0.9 + 0.15);

				var hidden = event.hidden || event.date <= this.x.domain()[0] || event.date >= this.x.domain()[1];

				return hidden
					? 'rgba(' + C.FGDARK_RGB + ', ' + intensity + ')'
					: 'rgba(' + C.CYAN_RGB + ', ' + intensity + ')';
			}
		}

		// constructor
		function Timeline(url, p) {
			// Takes one parameter p that should have the following
			// properties: data, eventTemplate, invisibleEventsHolder,
			// headerTemplate timelineHolder. data should be [metadata:
			// {title, short_title, url}, events: [{date, content,
			// importance}, ...]]
			var that = this;

			this.createBaseEl(p.timelineHolder,
				allTimelines.length == 0
				? Math.max($(window).height() - C.TALLTIMELINEMARGIN, C.SHORTTIMELINEHEIGHT)
				: C.SHORTTIMELINEHEIGHT);

			$.get(url)
				.done(function(data) {
					that.title = data.metadata.title;

					that.createRenderAndSvg(p.headerTemplate, data.metadata);

					var events = _.map(data.events, function(ev) {
						return new tlevents.Event(ev, p.invisibleEventsHolder, p.eventTemplate);
					});

					allTimelines.push(that);

					if (allTimelines.length == 1) {
						that.setRenderHeight(Math.max($(window).height() - C.TALLTIMELINEMARGIN, C.SHORTTIMELINEHEIGHT));
					} else {
						_.each(allTimelines, function (t) {
							t.setRenderHeight(C.SHORTTIMELINEHEIGHT)
						});
					}

					that.setRenderEvents(events);
					widthParams.setWidth(false);

					setHash();
				})
				.fail(function() {
					that.baseEl.remove();
				});

			this.resizeFn = function () {
				if (allTimelines.length == 1) {
					// This is only in the case where this is the only timeline
					that.setRenderHeight(Math.max($(window).height() - C.TALLTIMELINEMARGIN, C.SHORTTIMELINEHEIGHT));
					that.doRender();
				}
			}

			$(window).on('resize', this.resizeFn);

		}
		Timeline.prototype = baseObject;

		return Timeline;
	})();


	return { Timeline: Timeline };
})