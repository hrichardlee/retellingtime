define([], function () {
	var C = {};
	C.TOTALTIMELINEHEIGHT = 200;
	// leave space for the datestrip and the margin
	C.TIMELINEHEIGHT = C.TOTALTIMELINEHEIGHT;
	C.TOTALTIMELINEWIDTH = 800;
	// event-text outer width
	C.EVENTWIDTH = 184;
	// this is the amount of space that dates can be positioned on
	C.TIMELINEWIDTH = C.TOTALTIMELINEWIDTH - C.EVENTWIDTH;
	// make the marker shorter to compensate for event-text margin and leading in text and padding
	C.MARKEREXTRAHEIGHT = 4 + 4;

	return C;
});