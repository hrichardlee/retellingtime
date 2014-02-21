requirejs.config({
	// this is ugly
	baseUrl: '/static/timelineviewer/js/lib',
	paths: {
		viewer: '../viewer'
	},
	shim: {
		underscore: {
			exports: '_'
		},
		d3: {
			exports: 'd3'
		}
	}
});

requirejs(['jquery', 'underscore', 'd3', 'viewer/tlevents', 'viewer/tl'], function ($, _, d3, tlevents, tl) {

	var timelines;

	function addTimeline(url) {
		$.get(url, function(data) {
			// data should be a list of [{date, content, importance}, ...]
			// Turn data into Event objects
			var eventTemplate = _.template($("#event-template").html());
			var eventsHolder = $("#invisible-events-holder");
			var events = _.map(data, function(ev) {
				return new tlevents.Event(ev, eventsHolder, eventTemplate);
			});

			var timeline = new tl.Timeline($(window), d3.select('#timelines'), events);
		});
	}

	$(function() {
		$('a', '#options').click(function (e) {
			// each link has an id of the form "t-26". The "t-" is to
			// namespace these ids so they don't collide with other elements
			// on the page. substring(2) reverses this to get the id back. We
			// construct the /timelinedata/26/ url manually here. Ideally
			// there would be some way to use the {% url %} template tag, but
			// it's really not worth the trouble here. There isn't a great way
			// of solving either of these problems.
			addTimeline("/timelinedata/" + this.id.substring(2));
		})

		$('#query').keypress(function (e) {
			if (e.which == 13) {
				foo();
				return false;
			}
		})
	})
})