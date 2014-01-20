define([], function () {
	var C = {};
	C.TOTALTIMELINEHEIGHT = 220;
	C.CONTEXTSTRIPHEIGHT = 20;
	C.TIMELINEHEIGHT = C.TOTALTIMELINEHEIGHT - C.CONTEXTSTRIPHEIGHT;
	C.TIMELINEWIDTH = 800;
	// event-text outer width
	C.EVENTWIDTH = 184;
	// make the marker shorter to compensate for event-text margin and leading in text and padding
	C.MARKEREXTRAHEIGHT = 4 + 4;

	C.TRANSITIONDURATION = 150;

	C.INITIALTIMELINEMARGIN = 10;

	C.PANMARGIN = 50;
	C.ZOOMMIN = 0.5; // lower number means you can zoom out more
	C.ZOOMMAXFACTOR = 0.25; // higher number means that you can zoom in more

	return C;
});