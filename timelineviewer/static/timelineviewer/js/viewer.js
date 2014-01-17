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
		},
		hide: function() {
			this.options.hide = true;
			this.$el.addClass("invisible");

			if (this.options.nextBlock)
				this.options.nextBlock.options.prevBlock = this.options.prevBlock;
			if (this.options.prevBlock)
				this.options.prevBlock.options.nextBlock = this.options.nextBlock;
			else
				this.options.chain.firstBlock = this.options.nextBlock;
			if (this.options.dependentBlock) {
				this.options.dependentBlock.options.dependingBlocks.remove(this);
				this.options.dependingBlocks.each(function (b) {
					this.options.dependentBlock.options.dependingBlocks.add(b);
				}, this);
			}
			this.options.dependingBlocks.each(function (b) {
				b.options.dependentBlock = this.options.dependentBlock;
			}, this)
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
	var EventsView = Backbone.View.extend({
		el: $("#events-and-datestrip"),
		// params should be {topOfBelowBlock, prevChainBlock}. prevChainBlock
		// may be null. returns params {topOfBelowBlock and prevChainBlock},
		// but appropriately for calling with the next block
		placeBlock: function (block, prevChainBlock) {
			var bottom = block.options.prevBlock ? block.options.prevBlock.top() : 0;

			if (block.options.dependentBlock) block.options.dependentBlock.options.dependingBlocks.remove(block);
			block.options.dependentBlock = block.options.prevBlock;
			if (block.options.dependentBlock) block.options.dependentBlock.options.dependingBlocks.add(block);

			// penultimatePrevChainBlock ends up being the block that the next block in the current chain needs to check for overlap
			var penultimatePrevChainBlock = prevChainBlock;
			// check for overlaps
			while (prevChainBlock
				&& prevChainBlock.options.bottom < bottom + block.textHeight()
				&& prevChainBlock.right() > block.options.dateX) {
				// the while conditions plus this if condition guarantee overlap
				if (prevChainBlock.top() > bottom) {
					bottom = prevChainBlock.top();
					// this case requires adding a new chain to the dependentChain
					if (block.options.dependentBlock) block.options.dependentBlock.options.dependingBlocks.remove(block);
					block.options.dependentBlock = prevChainBlock;
					block.options.dependentBlock.options.dependingBlocks.add(block);
				}

				// advance to the next block in the previous chain
				penultimatePrevChainBlock = prevChainBlock;
				prevChainBlock = prevChainBlock.options.nextBlock;
			}

			block.place(bottom);
			block.show();

			return penultimatePrevChainBlock;
		},
		// hides the least important blocks in the dependentBlock chain of
		// block until height of the blocks removed equals or exceeds
		// verticalHeight. If the lowest (left-most then bottom-most) block is
		// not the original block passed in, that block will be returned.
		// Otherwise, null is returned.
		hideDependentBlocks: function (block, verticalHeight) {
			var blocks = [];
			var origBlock = block;
			var i = 0;
			var lowestBlock = null;
			while (block) {
				blocks.push({block: block, i: i});
				block = block.options.dependentBlock;
				i++;
			}
			// should use a priority queue hahaha
			blocks.sort(function(a, b) { return a.block.options.importance - b.block.options.importance; });
			i = 0;
			var removedHeight = 0;
			var leftMostChain = null;
			var lowestBlock = null;
			while (removedHeight < verticalHeight) {
				blocks[i].block.hide();
				removedHeight += blocks[i].block.textHeight();
				if (!lowestBlock || lowestBlock.i < blocks[i].i) {
					lowestBlock = blocks[i];
				}
				i++;
			}
			// relies on EventView.hide not removing the nextBlock pointer
			if (lowestBlock.block.cid != origBlock.cid) {
				if (lowestBlock.block.options.prevBlock) {
					this.layoutDependentChains(lowestBlock.block.options.prevBlock);
				} else {
					this.layoutDependentChainBlock(lowestBlock.block.options.chain.firstBlock)
				}
				
				if (origBlock.top() > C.TIMELINEHEIGHT) {
					this.hideDependentBlocks(origBlock, origBlock.top() - C.TIMELINEHEIGHT);
				}
			}
		},
		// Given a block, does not reposition it, and calls
		// layoutDependentChainBlock on the dependingBlocks. Each chain
		// coresponding to a dependingBlock is allowed to finish execution. If
		// all chains return true, then true is returned. If at least one
		// chain returns false, then false is returned.
		layoutDependentChains: function (block) {	
			var nextBlocks = [];
			block.options.dependingBlocks.each(function (b) {
				nextBlocks.push(b);
			}, this);
			nextBlocks.sort(function (a, b) { return b.options.chainIndex - a.options.chainIndex; })
			var success = true;
			_.each(nextBlocks, function (b) {
				success = success && this.layoutDependentChainBlock(b);
			}, this);
			return success;
		},
		// Given a block, repositions that block and then walks the
		// dependingBlocks chain (starting with the left-most if there is a
		// choice) until all of the blocks have been laid out. In most cases,
		// this should result in each block being moved downward. There are
		// three possibilities for the result of this function:
		// 1. In the process of laying out the dependingBlocks, a block is
		//    positioned above the maximum vertical height of the timeline.
		// 2. In the process of laying out the dependingBlocks, a block is
		//    about to be repositioned, but it turns out it cannot be moved
		//    successfully
		// 3. All blocks in the dependingBlocks chain are repositioned
		//    successfully
		// 
		// In cases 1 and 2, this function will return false, and in case 3
		// will return true
		layoutDependentChainBlock: function (block) {
			var prevBottom = block.options.bottom;
			// todo, be better at holding onto prevChainBlock
			this.placeBlock(block,
				block.options.prevChain
					? block.options.prevChain.firstBlock
					: null);

			if (block.options.bottom >= prevBottom
				|| block.top() > C.TIMELINEHEIGHT) {
				return false;
			} else {
				return this.layoutDependentChains(block);
			}
		},
		layoutViewChains: function(chains) {
			var i = chains.length - 1;
			var reset = null;
			while (i >= 0 || reset) {
				var block = chains[i].firstBlock;
				var prevChainBlock = block.options.prevChain
					? block.options.prevChain.firstBlock
					: null;
				while (block) {
					prevChainBlock = this.placeBlock(block, prevChainBlock);

					// if vertical height is too high, remove blocks and relayout
					if (block.top() > C.TIMELINEHEIGHT) {
						this.hideDependentBlocks(block, block.top() - C.TIMELINEHEIGHT);
					}
					
					block = block.options.nextBlock;
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

			var eventsHolder = $("#events", this.$el);

			// create views and add to the DOM as invisible (required for knowing heights)
			var views = evs.map(function(ev) {
				var view = new EventView({
					model: ev,
					dateX: (ev.attributes["date"] - dateMin) / dateRange * C.TIMELINEWIDTH,
					hide: false,
					dependingBlocks: new Set(function (b) { return b.cid; })
				});
				eventsHolder.append(view.render().$el);
				return view;
			}, this);

			// create view chains. Each chains[i] is a block that should be
			// rendered at the base of the timeline. The chain is doubly-
			// linked through chains[i].options.nextBlock and prevBlock
			var chains = [];
			var prevBlock = null;
			for (var i = 0; i < views.length; i++) {
				if (i == 0 ||
					views[i].right() < chains[chains.length - 1].firstBlock.options.dateX) { // create a new chain
					chains.push({firstBlock: views[i]});
					views[i].options.prevBlock = null;
				} else { // add to the existing chain
					views[i].options.prevBlock = prevBlock;
					if (prevBlock) prevBlock.options.nextBlock = views[i];
				}
				
				prevBlock = views[i];
				views[i].options.nextBlock = null;
			}

			// set prevChain (prevChain refers to the chain to the left, which
			// has a higher index)
			for (var i = 0; i < chains.length - 1; i++) {
				var b = chains[i].firstBlock;
				while (b) {
					b.options.prevChain = chains[i + 1]; 
					b = b.options.nextBlock;
				}
			}

			// set the chainIndex
			for (var i = 0; i < chains.length; i++) {
				var b = chains[i].firstBlock;
				while (b) {
					b.options.chainIndex = i;
					b.options.chain = chains[i];
					b = b.options.nextBlock;
				}
			}

			for (var i = 0; i < chains.length; i++) {
				var b = chains[i].firstBlock;
				var totalHeight = 0;
				var chainBlocks = []
				while (b) {
					totalHeight += b.textHeight();
					chainBlocks.push(b);
					b = b.options.nextBlock;
				}
				chainBlocks.sort(function (a,b) { return a.options.importance - b.options.importance; });
				var j = 0;
				var removedHeight = 0;
				while (removedHeight < totalHeight - C.TIMELINEHEIGHT) {
					chainBlocks[j].hide();
					removedHeight += chainBlocks[j].textHeight();
					j++;
				}
			}

			this.layoutViewChains(chains);

			// show all the elements
			_.each(views, function(v) { if (!v.options.hide) { v.show(); } })
		}
	});

	var TimelineView = Backbone.View.extend({
		el: $("#timeline-holder"),
		events: {
			"click #searchButton" : "search"
		},
		search: function(x) {
			$.get("/timelinedata/" + $("#query").val(), function(data) {
				var events = new Events(data);
				var timeline = new EventsView({collection: events});
				timeline.render();
			});
		}
	})

	var x = new TimelineView();
})