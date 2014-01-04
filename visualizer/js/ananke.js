$(function(){
	var data = [{"date":2012,"content":"<a href=\"/wiki/Higgs_boson\" title=\"Higgs boson\">Higgs-Boson</a>-like particle discovered at CERN's Large Hadron Collider (LHC).","importance":63312},{"date":2000,"content":"Tau neutrino proved distinct from other neutrinos at <a href=\"/wiki/Fermilab\" title=\"Fermilab\">Fermilab</a>.","importance":12637},{"date":1995,"content":"<a href=\"/wiki/Top_quark\" title=\"Top quark\">Top quark</a> discovered at <a href=\"/wiki/Fermilab\" title=\"Fermilab\">Fermilab</a>;","importance":13825.5},{"date":1983,"content":"<a href=\"/wiki/Carlo_Rubbia\" title=\"Carlo Rubbia\">Carlo Rubbia</a> and <a href=\"/wiki/Simon_van_der_Meer\" title=\"Simon van der Meer\">Simon van der Meer</a> discovered the <a href=\"/wiki/W_and_Z_bosons\" title=\"W and Z bosons\">W and Z bosons</a>;","importance":7693.333333333333},{"date":1979,"content":"<a href=\"/wiki/Gluon\" title=\"Gluon\">Gluon</a> observed indirectly in <a class=\"mw-redirect\" href=\"/wiki/Three_jet_events\" title=\"Three jet events\">three jet events</a> at <a href=\"/wiki/DESY\" title=\"DESY\">DESY</a>;","importance":11306.666666666666},{"date":1977,"content":"<a class=\"mw-redirect\" href=\"/wiki/Upsilon_particle\" title=\"Upsilon particle\">Upsilon particle</a> discovered at <a href=\"/wiki/Fermilab\" title=\"Fermilab\">Fermilab</a>, demonstrating the existence of the <a href=\"/wiki/Bottom_quark\" title=\"Bottom quark\">bottom quark</a>;","importance":5645.333333333333},{"date":1977,"content":"<a href=\"/wiki/Martin_Lewis_Perl\" title=\"Martin Lewis Perl\">Martin Lewis Perl</a> discovered the <a class=\"mw-redirect\" href=\"/wiki/Tau_lepton\" title=\"Tau lepton\">Tau lepton</a> after a series of experiments;","importance":4735.5},{"date":1974,"content":"<a href=\"/wiki/Burton_Richter\" title=\"Burton Richter\">Burton Richter</a> and <a class=\"mw-redirect\" href=\"/wiki/Samuel_Ting\" title=\"Samuel Ting\">Samuel Ting</a> discovered the <a class=\"mw-redirect\" href=\"/wiki/J/%CF%88_particle\" title=\"J/ψ particle\">J/ψ particle</a>;","importance":5701.666666666667},{"date":1967,"content":"<a href=\"/wiki/Bruno_Pontecorvo\" title=\"Bruno Pontecorvo\">Bruno Pontecorvo</a> postulated the <a href=\"/wiki/Neutrino_oscillation\" title=\"Neutrino oscillation\">Neutrino oscillation</a>;","importance":15406},{"date":1962,"content":"<a href=\"/wiki/Leon_M._Lederman\" title=\"Leon M. Lederman\">Leon M. Lederman</a>, <a href=\"/wiki/Melvin_Schwartz\" title=\"Melvin Schwartz\">Melvin Schwartz</a> and <a href=\"/wiki/Jack_Steinberger\" title=\"Jack Steinberger\">Jack Steinberger</a> discovered the muon neutrino;","importance":9181.333333333334},{"date":1957,"content":"<a href=\"/wiki/Bruno_Pontecorvo\" title=\"Bruno Pontecorvo\">Bruno Pontecorvo</a> postulated the flavor oscillation;","importance":7583},{"date":1956,"content":"<a href=\"/wiki/Clyde_Cowan\" title=\"Clyde Cowan\">Clyde Cowan</a> and <a href=\"/wiki/Frederick_Reines\" title=\"Frederick Reines\">Frederick Reines</a> discovered the <a href=\"/wiki/Neutrino\" title=\"Neutrino\">neutrino</a>;","importance":19317.666666666668},{"date":1955,"content":"<a href=\"/wiki/Owen_Chamberlain\" title=\"Owen Chamberlain\">Owen Chamberlain</a>, <a class=\"mw-redirect\" href=\"/wiki/Emilio_Segr%C3%A8\" title=\"Emilio Segrè\">Emilio Segrè</a>, <a href=\"/wiki/Clyde_Wiegand\" title=\"Clyde Wiegand\">Clyde Wiegand</a>, and <a href=\"/wiki/Thomas_Ypsilantis\" title=\"Thomas Ypsilantis\">Thomas Ypsilantis</a> discovered the <a href=\"/wiki/Antiproton\" title=\"Antiproton\">Antiproton</a>;","importance":6244.4},{"date":1947,"content":"<a class=\"mw-redirect\" href=\"/wiki/Cecil_Powell\" title=\"Cecil Powell\">Cecil Powell</a>, <a href=\"/wiki/C%C3%A9sar_Lattes\" title=\"César Lattes\">César Lattes</a> and <a href=\"/wiki/Giuseppe_Occhialini\" title=\"Giuseppe Occhialini\">Giuseppe Occhialini</a> discovered the <a href=\"/wiki/Pion\" title=\"Pion\">pion</a>;","importance":5933},{"date":1947,"content":"<a href=\"/wiki/George_Rochester\" title=\"George Rochester\">George Dixon Rochester</a> and <a href=\"/wiki/Clifford_Charles_Butler\" title=\"Clifford Charles Butler\">Clifford Charles Butler</a> discovered the <a href=\"/wiki/Kaon\" title=\"Kaon\">Kaon</a>, the first <a class=\"mw-redirect\" href=\"/wiki/Strange_particle\" title=\"Strange particle\">strange particle</a>;","importance":4920.25},{"date":1936,"content":"<a class=\"mw-redirect\" href=\"/wiki/Carl_D._Anderson\" title=\"Carl D. Anderson\">Carl D. Anderson</a> discovered the <a href=\"/wiki/Muon\" title=\"Muon\">muon</a> while he studied cosmic radiation;","importance":11279},{"date":1935,"content":"<a href=\"/wiki/Hideki_Yukawa\" title=\"Hideki Yukawa\">Hideki Yukawa</a> predicted the existence of mesons as the carrier particles of the <a class=\"mw-redirect\" href=\"/wiki/Strong_nuclear_force\" title=\"Strong nuclear force\">strong nuclear force</a>;","importance":6282},{"date":1932,"content":"<a href=\"/wiki/James_Chadwick\" title=\"James Chadwick\">James Chadwick</a> discovered the <a href=\"/wiki/Neutron\" title=\"Neutron\">Neutron</a>;","importance":27812.5},{"date":1932,"content":"<a class=\"mw-redirect\" href=\"/wiki/Carl_D._Anderson\" title=\"Carl D. Anderson\">Carl D. Anderson</a> discovered the <a href=\"/wiki/Positron\" title=\"Positron\">Positron</a>;","importance":5717.5},{"date":1930,"content":"<a href=\"/wiki/Wolfgang_Pauli\" title=\"Wolfgang Pauli\">Wolfgang Pauli</a> postulated the <a href=\"/wiki/Neutrino\" title=\"Neutrino\">neutrino</a> to explain the energy spectrum of <a href=\"/wiki/Beta_decay\" title=\"Beta decay\">beta decays</a>;","importance":25351.666666666668},{"date":1928,"content":"<a href=\"/wiki/Paul_Dirac\" title=\"Paul Dirac\">Paul Dirac</a> postulated the existence of positrons as a consequence of the <a href=\"/wiki/Dirac_equation\" title=\"Dirac equation\">Dirac equation</a>;","importance":27591},{"date":1919,"content":"<a href=\"/wiki/Ernest_Rutherford\" title=\"Ernest Rutherford\">Ernest Rutherford</a> discovered the <a href=\"/wiki/Proton\" title=\"Proton\">proton</a>;","importance":21531},{"date":1905,"content":"<a href=\"/wiki/Albert_Einstein\" title=\"Albert Einstein\">Albert Einstein</a> hypothesized the <a href=\"/wiki/Photon\" title=\"Photon\">photon</a> to explain the <a href=\"/wiki/Photoelectric_effect\" title=\"Photoelectric effect\">photoelectric effect</a>.","importance":41650.333333333336},{"date":1900,"content":"<a class=\"mw-redirect\" href=\"/wiki/Paul_Villard\" title=\"Paul Villard\">Paul Villard</a> discovered the <a href=\"/wiki/Gamma_ray\" title=\"Gamma ray\">Gamma ray</a> in uranium decay.","importance":19064.5},{"date":1899,"content":"<a href=\"/wiki/Ernest_Rutherford\" title=\"Ernest Rutherford\">Ernest Rutherford</a> discovered the <a href=\"/wiki/Alpha_particle\" title=\"Alpha particle\">alpha</a> and <a href=\"/wiki/Beta_particle\" title=\"Beta particle\">beta particles</a> emitted by <a href=\"/wiki/Uranium\" title=\"Uranium\">uranium</a>;","importance":21742.75},{"date":1897,"content":"<a href=\"/wiki/J._J._Thomson\" title=\"J. J. Thomson\">J. J. Thomson</a> discovered the <a href=\"/wiki/Electron\" title=\"Electron\">electron</a>;","importance":34348.5},{"date":1886,"content":"<a class=\"mw-redirect\" href=\"/wiki/Eugene_Goldstein\" title=\"Eugene Goldstein\">Eugene Goldstein</a> produced <a class=\"mw-redirect\" href=\"/wiki/Anode_rays\" title=\"Anode rays\">Anode rays</a>;","importance":2935},{"date":1874,"content":"<a href=\"/wiki/George_Johnstone_Stoney\" title=\"George Johnstone Stoney\">George Johnstone Stoney</a> hypothesizes a minimum unit of electric charge. In 1891, he coins the word <a href=\"/wiki/Electron\" title=\"Electron\">electron</a> for it;","importance":29922},{"date":1858,"content":"<a href=\"/wiki/Julius_Pl%C3%BCcker\" title=\"Julius Plücker\">Julius Plücker</a> produced <a class=\"mw-redirect\" href=\"/wiki/Cathode_rays\" title=\"Cathode rays\">Cathode rays</a>;","importance":8633.5},{"date":1838,"content":"<a href=\"/wiki/Richard_Laming\" title=\"Richard Laming\">Richard Laming</a> hypothesized a subatomic particle carrying <a href=\"/wiki/Electric_charge\" title=\"Electric charge\">electric charge</a>;","importance":10285},{"date":1815,"content":"<a href=\"/wiki/William_Prout\" title=\"William Prout\">William Prout</a> <a href=\"/wiki/Prout%27s_hypothesis\" title=\"Prout's hypothesis\">hypothesizes</a> that all matter is built up from <a href=\"/wiki/Hydrogen\" title=\"Hydrogen\">hydrogen</a>, adumbrating the <a href=\"/wiki/Proton\" title=\"Proton\">proton</a>;","importance":17338}];

	var C = {};
	C.TOTALTIMELINEHEIGHT = 500;
	C.DATESTRIPOFFSET = 30;
	// leave space for the datestrip and the margin
	C.TIMELINEHEIGHT = C.TOTALTIMELINEHEIGHT - C.DATESTRIPOFFSET;
	C.TOTALTIMELINEWIDTH = 800;
	C.EVENTWIDTH = 180;
	// this is the amount of space that dates can be positioned on
	C.TIMELINEWIDTH = C.TOTALTIMELINEWIDTH - C.EVENTWIDTH;
	// space between event marker and text
	C.EVENTMARKEROFFSET = 4;
	// make the marker shorter to compensate for leading in text and padding
	C.MARKEREXTRALEADING = 4;

	var Event = Backbone.Model.extend();
	var Events = Backbone.Collection.extend({
		model: Event
	});

	// Requires: model; Optionally: options.place
	var EventView = Backbone.View.extend({
		tagName: "div",
		template: _.template($("#event-template").html()),
		initialize: function(options) {
			this.options = options || {};
		},
		render: function() {
			this.$el.html(this.template(this.model.toJSON()));

			this.text = $(".event-text", this.$el);
			this.marker = $(".event-marker", this.$el);

			this.$el.addClass("invisible");
			return this;
		},
		// must be called after adding to the DOM
		textHeight: function() {
			return this.text ? this.text.outerHeight() : null;
		},
		// must be called after adding to the DOM
		placeAndShow: function(place) {
			this.text.css("left", (place.left + C.EVENTMARKEROFFSET) + "px");
			this.marker.css("left", place.left + "px");
			this.text.css("bottom", (place.bottom + C.DATESTRIPOFFSET) + "px");
			this.marker.css("height", (place.bottom + C.DATESTRIPOFFSET - C.MARKEREXTRALEADING + this.textHeight()) + "px");

			this.$el.removeClass("invisible")
		},
		importance: function() {
			return this.model.attributes["importance"];
		}
	});

	/* Rendering strategy
	 * Some notes:
	 *  Each block is defined by {pos: {left, right, bottom, top}, importance}
	 *  A block chain is a sequence of blocks where each block's layout depends on the block
	 *  A block is placed at ground level (bottom = 0) unless it overlaps a block to its right,
	 *  in which case it is placed above it.
	 * Get all block chains
	 * If a block chain is taller than the allowed vertical height
	 *  remove the least important block and recalculate block chains
	 * Repeat until no block chain is taller than the allowed vertical height
	 */

	// Requires collection
	var TimelineView = Backbone.View.extend({
		el: $("#events-holder"),
		render: function() {
			var evs = this.collection;

			var dateMin = evs.at(evs.length- 1).attributes["date"];
			var dateMax = evs.at(0).attributes["date"];
			var dateRange = dateMax - dateMin;

			// at the beginning of each iteration of the loop,
			// (prevX, prevY) is the upper left corner of the item rendered in the previous iteration
			var prevX = C.TIMELINEWIDTH;
			var prevY = 0;
			for (var i = 0; i < evs.length; i++) {
				var view = new EventView({
					model: evs.at(i)
				});

				// x coordinate for the date marker
				var dateX = (view.model.attributes["date"] - dateMin) / dateRange * C.TIMELINEWIDTH;
				var eventEl = view.render().$el;
				this.$el.append(eventEl);

				if (dateX + C.EVENTWIDTH < prevX) {
					view.placeAndShow({left: dateX, bottom: 0});
					prevX = dateX;
					prevY = $(".event-text", view.$el).outerHeight();
				} else {
					view.placeAndShow({left: dateX, bottom: prevY});
					prevX = dateX;
					prevY += $(".event-text", view.$el).outerHeight();
				}
			}
		}
	});

	var events = new Events(data);
	var timeline = new TimelineView({collection: events});
	timeline.render();

	window.t = timeline;
	window.d = data;
	window.EV = EventView;
})