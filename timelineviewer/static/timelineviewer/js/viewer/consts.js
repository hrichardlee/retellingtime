define([], function () {
	var C = {};
	C.TOTALTIMELINEHEIGHT = 340;
	C.CONTEXTSTRIPHEIGHT = 20;
	C.AXISHEIGHT = 21;
	C.TIMELINEHEIGHT = C.TOTALTIMELINEHEIGHT - C.AXISHEIGHT - C.CONTEXTSTRIPHEIGHT;
	// event-text outer width
	C.EVENTWIDTH = 188;
	// make the marker shorter to compensate for event-text margin and leading in text and padding
	C.MARKEREXTRAHEIGHT = 4 + 2;
	C.MARKERWIDTH = 2;

	C.TRANSFORM_TRANSITION_DURATION = 250;
	C.TRANSFORM_TRANSITION_EASING = 'linear';
	C.FIRST_RENDER_TRANSITION_DURATION = 250;
	C.FIRST_RENDER_TRANSITION_EASING = 'easeOutExpo'
	C.OPACITY_TRANSITION_DURATION = 250;
	C.OPACITY_TRANSITION_EASING = 'easeInOutSine';

	C.FIRST_RENDER_MARGIN = 30;

	C.PANMARGIN = 30;
	C.ZOOMMAXFACTOR = 0.25; // higher number means that you can zoom in more

	C.DEBUG = false;

	C.EPSILON = 0.000001;

	return C;
});