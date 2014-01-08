$(function(){
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

	var Event = Backbone.Model.extend();
	var Events = Backbone.Collection.extend({
		model: Event
	});

	// Requires: model, options.importance (supplied by model)
	// options.dateX, options.hide, options.chain, options.chainIndex, options.blockIndex
	var EventView = Backbone.View.extend({
		tagName: "div",
		template: _.template($("#event-template").html()),
		initialize: function(options) {
			this.options = options || {};
			this.options.importance = this.model.attributes["importance"];
		},
		render: function() {
			this.$el.html(this.template(this.model.toJSON()));

			this.text = $(".event-text", this.$el);
			this.marker = $(".event-marker", this.$el);

			this.$el.addClass("invisible");
			this._textHeight = undefined;
			return this;
		},
		// must be called after adding to the DOM
		textHeight: function() {
			if (!this._textHeight && this.text)
				this._textHeight = this.text.outerHeight(true); // true includes margins
			return this._textHeight;
		},
		top: function() {
			return this.textHeight() + this.options.bottom;
		},
		right: function() {
			return this.options.dateX + C.EVENTWIDTH;
		},
		// must be called after adding to the DOM
		place: function(bottom) {
			this.text.css("left", (this.options.dateX + C.EVENTMARKEROFFSET) + "px");
			this.marker.css("left", this.options.dateX + "px");
			this.text.css("bottom", (bottom + C.DATESTRIPOFFSET) + "px");
			this.marker.css("height", (bottom + C.DATESTRIPOFFSET - C.MARKEREXTRAHEIGHT + this.textHeight()) + "px");

			this.options.bottom = bottom;

			return this;
		},
		show: function() {
			this.options.hide = false;
			this.$el.removeClass("invisible");
		}
	});

	/* Rendering strategy
		1. Layout all the blocks:
			a. Horizontal position for blocks is predetermined
			b. Place the right-most block at ground level
			c. For each subsequent block, place it at ground level
				If it overlaps a ground-level block, move it up until it has no overlaps
				This block is considered part of the block chain defined by the ground-level block
		2. Now, for each block chain, starting from the left
			a. For each block in the block chain, if there is an overlapping block to the left
				move the block (and all blocks above it in the block chain) up until that block
				clears the block chain to the left
			b. The block depends on the block immediately below it, whether it is part of the same
				block chain or whether it is part of the previous block chain. The chain of dependent
				blocks (terminating at a ground block) is the dependent chain for that block
			c. If a block exceeds the vertical height, take the a set of the least important blocks
				in its dependent chain that are not already hidden such that these blocks are at least
				as tall as the excess height, and hide these blocks.
			d. Repeat starting from 2.a. with the block immediately above the hidden block that is
				most to the left and bottom
	 */

	// Requires collection to be sorted from future to past
	var TimelineView = Backbone.View.extend({
		el: $("#events-holder"),
		// If just a block is passed in, the dependent chain is extended from the block
		// just below it. If a prevChainBlock is passed in, the dependent chain is extended
		// from that block 
		setDependentChain: function (block, prevChainBlock) {
			var blockIndex = block.options.blockIndex;
			// set dependentChain
			if (blockIndex == 0) {
				block.options.dependentChain = {leftMostChainIndex: block.options.chainIndex};
				block.options.dependentChain[block.options.chainIndex] = {lo: blockIndex, hi: blockIndex};
			} else if (prevChainBlock) {
				block.options.dependentChain = $.extend(true, prevChainBlock.options.dependentChain); // true for deep copy
				block.options.dependentChain[block.options.chainIndex] = {lo: blockIndex, hi: blockIndex};
			} else {
				// by default the block just needs to add one more block to the current range's hi
				var prevDependentChain = block.options.chain[blockIndex - 1].options.dependentChain;
				block.options.dependentChain = $.extend(true, {}, prevDependentChain);
				block.options.dependentChain[block.options.chainIndex].hi = blockIndex;
			}
		},
		// hides the least important blocks in dependentChain until the
		// height of the blocks removed equals or exceeds verticalHeight
		hideDependentBlocks: function (dependentChain, chains, verticalHeight) {
			var i = dependentChain.leftMostChainIndex;
			var blocks = [];
			while (dependentChain[i]) {
				blocks = blocks.concat(
					chains[i].slice(dependentChain[i].lo, dependentChain[i].hi + 1));
				i -= 1;
			}
			blocks = _.filter(blocks, function (b) { return !b.options.hide; });
			// should use a priority queue hahaha
			blocks.sort(function(a, b) { return a.options.importance - b.options.importance; });
			i = 0;
			var removedHeight = 0;
			var leftMostChain = null;
			var lowestBlock = null;
			while (removedHeight < verticalHeight) {
				blocks[i].options.hide = true;
				removedHeight += blocks[i].textHeight();
				if (leftMostChain == null
					|| blocks[i].options.chainIndex > leftMostChain) {
					leftMostChain = blocks[i].options.chainIndex; 
				}
				if (lowestBlock == null
					|| (blocks[i].options.chainIndex == leftMostChain
						&& blocks[i].options.blockIndex < lowestBlock)) {
					lowestBlock = blocks[i].options.blockIndex;
				}
				i += 1;
			}
			return {chainIndex: leftMostChain, blockIndex: lowestBlock}
		},
		// params should be {topOfBelowBlock, prevChainBlock}. prevChainBlock may be null
		// returns params {topOfBelowBlock and prevChainBlock}, but appropriately for calling with the next block
		placeBlock: function (block, params) {
			var topOfBelowBlock = params.topOfBelowBlock;
			var prevChainBlock = params.prevChainBlock;
			var height = block.textHeight();
			var bottom = topOfBelowBlock;

			this.setDependentChain(block);

			// penultimatePrevChainBlock ends up being the block that the next block in the current chain needs to check for overlap
			var penultimatePrevChainBlock = prevChainBlock;
			// check for overlaps
			while (prevChainBlock
				&& prevChainBlock.options.bottom < bottom + height
				&& prevChainBlock.right() > block.options.dateX) {
				// the while conditions plus this if condition guarantee overlap
				if (prevChainBlock.top() > bottom) {
					bottom = prevChainBlock.top();
					// this case requires adding a new chain to the dependentChain
					this.setDependentChain(block, prevChainBlock);
				}

				if (prevChainBlock.options.blockIndex + 1 >= prevChainBlock.options.chain.length) {
					break;
				} else {
					// advance to the next block in the previous chain
					penultimatePrevChainBlock = prevChainBlock;
					prevChainBlock = prevChainBlock.options.chain[prevChainBlock.options.blockIndex + 1];
				}
			}

			block.place(bottom);

			return {topOfBelowBlock: bottom + height, prevChainBlock: penultimatePrevChainBlock}
		},
		layoutViewChains: function(chains) {
			var i, j;

			// layout remaining chains
			i = chains.length - 1;
			var reset = null;
			while (i >= 0 || reset) {
				var params = {};
				if (reset) {
					i = reset.chainIndex;
					j = reset.blockIndex + 1;
					params.topOfBelowBlock = chains[i][reset.blockIndex].options.bottom; // we know j > 0
					reset = null;
				} else {
					j = 0;
					params.topOfBelowBlock = 0;
				}
				var currChain = chains[i];
				params.prevChainBlock = i + 1 < chains.length ? chains[i + 1][0] : null;

				while (j < currChain.length
					&& !reset)  {
					if (!currChain[j].options.hide) {
						params = this.placeBlock(currChain[j], params);

						// check for vertical height
						if (params.topOfBelowBlock > C.TIMELINEHEIGHT) {
							// remove blocks and relayout
							var reset = this.hideDependentBlocks(
								currChain[j].options.dependentChain,
								chains,
								params.topOfBelowBlock - C.TIMELINEHEIGHT);
						}
					}
					j++;
				}
				i--;
			}
		},
		render: function() {
			var evs = this.collection;

			// get dates
			var dateMin = evs.at(evs.length- 1).attributes["date"];
			var dateMax = evs.at(0).attributes["date"];
			var dateRange = dateMax - dateMin;

			// create views and add to the DOM as invisible (required for knowing heights)
			var views = evs.map(function(ev) {
				var view = new EventView({
					model: ev,
					dateX: (ev.attributes["date"] - dateMin) / dateRange * C.TIMELINEWIDTH,
					hide: false
				});
				this.$el.append(view.render().$el);
				return view;
			}, this);

			// create view chains
			var chains = [];
			var chain;
			for (var i = 0; i < views.length; i++) {
				if (i == 0 ||
					views[i].right() < chain[0].options.dateX) { // create a new chain
					chain = [views[i]];
					chains.push(chain);
				} else { // add to the existing chain
					chain.push(views[i]);
				}
				views[i].options.chain = chain;
				views[i].options.chainIndex = chains.length - 1;
				views[i].options.blockIndex = chain.length - 1;
			}

			this.layoutViewChains(chains);

			// show all the elements
			_.each(views, function(v) { if (!v.options.hide) { v.show(); } })
		}
	});

	$.get("/timelinedata/test1", function(data) {
		var events = new Events(data);
		var timeline = new TimelineView({collection: events});
		timeline.render();
	});
})