define([], function () {
	var C = {};
	C.TOTALTIMELINEHEIGHT = 220;
	C.CONTEXTSTRIPHEIGHT = 20;
	C.AXISHEIGHT = 21;
	C.TIMELINEHEIGHT = C.TOTALTIMELINEHEIGHT - C.AXISHEIGHT - C.CONTEXTSTRIPHEIGHT;
	// event-text outer width
	C.EVENTWIDTH = 184;
	// make the marker shorter to compensate for event-text margin and leading in text and padding
	C.MARKEREXTRAHEIGHT = 4 + 4;
	C.MARKERWIDTH = 2;

	C.TRANSITIONDURATION = 250;
	C.FIRST_RENDER_TRANSITION_DURATION = 300;
	C.FIRST_RENDER_TRANSITION_EASING = "easeOutExpo"

	C.FIRST_RENDER_MARGIN = 30;

	C.PANMARGIN = 30;
	C.ZOOMMAXFACTOR = 0.25; // higher number means that you can zoom in more

	C.DEBUG = false;

	C.EPSILON = 0.000001;

	return C;
});