requirejs.config({
	// this is ugly
	baseUrl: '/static/timelineviewer/js/lib',
	paths: {
		viewer: '../viewer'
	},
	shim: {
		underscore: {
			exports: '_'
		}
	}
});

requirejs(['jquery', 'underscore', 'viewer/tlevents', 'viewer/consts'], function ($, _, tlevents, C) {
	$(function(){
		$('#query').keypress(function (e) {
			if (e.which == 13) {
				$.get("/timelinedata/" + $("#query").val(), function(data) {
					// data should be a list of [{date, content, importance}, ...]

					// This is temporary--the d3 scales should replace this
					var dateMin = data[(data.length- 1)].date;
					var dateMax = data[0].date;
					var dateRange = dateMax - dateMin;

					var eventTemplate = _.template($("#event-template").html());
					// This is a one-time task
					var eventsHolder = $("#events", this.$el);
					var events = _.map(data, function(ev) {
						return new tlevents.Event(ev, eventsHolder, eventTemplate);
					}, this);

					// This needs to happen on every render
					// This is temporary--the d3 scales should replace this
					_.each(events, function (e) { e.setLeft((e.date - dateMin) / dateRange * C.TIMELINEWIDTH); } );

					var scopedEvents = tlevents.setBottoms(events);
				});
				return false;
			}
		})
	})
})