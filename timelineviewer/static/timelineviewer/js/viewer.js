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
			var timeline = new tl.Timeline({
				data: data,
				eventTemplate: _.template($('#event-template').html()),
				invisibleEventsHolder: $('#invisible-events-holder'),
				headerTemplate: _.template($('#header-template').html()),
				timelineHolder: d3.select('#timelines')
			});
		});
	}

	$(function() {
		// This is extremely loosely based on http://azoff.github.io/overscroll/
		var $target = $('#frame')

		var posY;

		$target.on('mousedown', start);
		$target.on('mouseup mouseleave', stop); // also click?
		$target.on('select dragstart drag', ignore);

		function start(event) {
			event.preventDefault();
			$target.on('mousemove', drag)
			posY = event.pageY;
		}

		function drag(event) {
			event.preventDefault();
			$target.get(0).scrollTop -= event.pageY - posY;
			posY = event.pageY;
		}

		function stop(event) {
			$target.unbind('mousemove', drag);
			posy = false;
		}

		function ignore(event) {
			event.preventDefault();
		}





		// All timeline-adder stuff

		$('#options .option a').click(function (e) {
			// each link has an id of the form 't-26'. The 't-' is to
			// namespace these ids so they don't collide with other elements
			// on the page. substring(2) reverses this to get the id back. We
			// construct the /timelinedata/26/ url manually here. Ideally
			// there would be some way to use the {% url %} template tag, but
			// it's really not worth the trouble here. There isn't a great way
			// of solving either of these problems.
			addTimeline('/timelinedata/' + this.id.substring(2));
		})

		$('#options #customoption a').click(function (e) {
			addTimeline('/timelinedata/search/' + $('#query').val());
		})

		var prevQuery = [];

		$('#query').keyup(function (e) {
			var currOrigQuery = $('#query').val();
			var currLowerQuery = currOrigQuery.toLowerCase();
			var currQuery = currLowerQuery.split(/\s+/);
			currQuery = $.grep(currQuery, function (e) { return e.length > 0; });
			currQuery = $.unique(currQuery);

			// figure out whether whether we can skip some checks
			var addedTerms = $(currQuery).not(prevQuery).get();
			var removedTerms = $(prevQuery).not(currQuery).get();
			// if every removed term is a substring of an added term, then all
			// hidden items will remain hidden (includes cases where there are
			// no removed terms)
			var hiddenAllRemainHidden =
				_.every(removedTerms, function (removedTerm) {
					return _.some(addedTerms, function (addedTerm) {
						return addedTerm.indexOf(removedTerm) != -1;
					})
				});
			// if every added term is a substring of a removed term, then all
			// displayed items will remain displayed (includes cases where
			// there are no added terms)
			var displayedAllRemainDisplayed =
				_.every(addedTerms, function (addedTerm) {
					return _.some(removedTerms, function (removedTerm) {
						return removedTerm.indexOf(addedTerm) != -1;
					})
				});

			$('#options .option').each(function (i, el) {
				var text = $(el).text().toLowerCase();
				if ($(el).hasClass('hidden')) {
					if (!hiddenAllRemainHidden
						&& _.every(currQuery, function (t) {
							return text.indexOf(t) != -1; }))
						$(el).removeClass('hidden');
				} else {
					if (!displayedAllRemainDisplayed
						&& _.some(addedTerms, function (t) {
							return text.indexOf(t) == -1; }))
						$(el).addClass('hidden');
				}
			});

			prevQuery = currQuery;

			// check for exact match
			var exactMatch = _.find(visible, function (el) {
				return $('a', el).text().toLowerCase() == currLowerQuery;
			});
			if (currLowerQuery.length == 0 || exactMatch) {
				$('#options #customoption').addClass('hidden')
			} else {
				$('#options #customoption #query-text').text(currOrigQuery.replace(/ /g, '&nbsp;'));
				$('#options #customoption').removeClass('hidden')
			}

			// on enter, if there is only one matched option or there is an
			// exact match, add that timeline. if no timelines are matched,
			// then look for the exactly specified Wikipedia page
			if (e.which == 13) {
				var visible = $('#options .option').not('.hidden');
				if (visible.length == 1) {
					$('a', visible).click();
				} else if (exactMatch) {
					$('a', exactMatch).click();
				} else if (visible.length == 0) {
					$('#options #customoption a').click();
				}
			}
		})
	})
})