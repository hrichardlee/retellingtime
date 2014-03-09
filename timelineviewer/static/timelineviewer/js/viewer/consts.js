define([], function () {
	var C = {};
	C.CONTEXTSTRIPHEIGHT = 20;
	C.AXISHEIGHT = 21;
	C.SHORTTIMELINEHEIGHT = 299;
	C.TALLTIMELINEMARGIN = 250;
	// event-text outer width
	C.EVENTWIDTH = 188;
	// make the marker shorter to compensate for event-text margin and leading in text and padding
	C.MARKEREXTRAHEIGHT = 4 + 2;

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

	C.FGDARK_RGB = '88, 110, 117';
	C.CYAN_RGB = '42, 161, 152';

	return C;
});