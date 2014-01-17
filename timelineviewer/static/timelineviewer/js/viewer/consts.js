define([], function () {
	var C = {};
	C.TOTALTIMELINEHEIGHT = 500;
	C.DATESTRIPOFFSET = 30;
	// leave space for the datestrip and the margin
	C.TIMELINEHEIGHT = C.TOTALTIMELINEHEIGHT - C.DATESTRIPOFFSET;
	C.TOTALTIMELINEWIDTH = 800;
	// event-text outer width + EVENTMARKEROFFSET + event marker width
	C.EVENTWIDTH = 187;
	// this is the amount of space that dates can be positioned on
	C.TIMELINEWIDTH = C.TOTALTIMELINEWIDTH - C.EVENTWIDTH;
	// space between event marker and text
	C.EVENTMARKEROFFSET = 4;
	// make the marker shorter to compensate for event-text margin and leading in text and padding
	C.MARKEREXTRAHEIGHT = 4 + 4;

	return C;
});