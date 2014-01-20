define([], function () {
	var C = {};
	C.TOTALTIMELINEHEIGHT = 220;
	C.CONTEXTSTRIPHEIGHT = 20;
	C.TIMELINEHEIGHT = C.TOTALTIMELINEHEIGHT - C.CONTEXTSTRIPHEIGHT;
	// event-text outer width
	C.EVENTWIDTH = 184;
	// make the marker shorter to compensate for event-text margin and leading in text and padding
	C.MARKEREXTRAHEIGHT = 4 + 4;

	C.TRANSITIONDURATION = 250;
	C.FIRST_RENDER_TRANSITION_DURATION = 1000;
	C.FIRST_RENDER_TRANSITION_EASING = "easeOutExpo"

	C.FIRST_RENDER_MARGIN = 10;

	C.PANMARGIN = 50;
	C.ZOOMMIN = 0.5; // lower number means you can zoom out more
	C.ZOOMMAXFACTOR = 0.25; // higher number means that you can zoom in more

	return C;
});