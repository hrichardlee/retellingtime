define(['jquery', 'underscore', 'simpleset', 'viewer/consts'], function ($, _, Set, C) {
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


	// hides the least important blocks in the dependentBlock chain of
	// block until height of the blocks removed equals or exceeds
	// verticalHeight. If the lowest (left-most then bottom-most) block is
	// not the original block passed in, that block will be returned.
	// Otherwise, null is returned.
	function hideDependentBlocks(block, verticalHeight) {
		var blocks = [];
		var origBlock = block;
		var i = 0;
		var lowestBlock = null;
		while (block) {
			blocks.push({block: block, i: i});
			block = block.dependentBlock;
			i++;
		}
		// should use a priority queue hahaha
		blocks.sort(function(a, b) { return a.block.importance - b.block.importance; });
		i = 0;
		var removedHeight = 0;
		var leftMostChain = null;
		var lowestBlock = null;
		while (removedHeight < verticalHeight) {
			blocks[i].block.hide();
			removedHeight += blocks[i].block.height;
			if (!lowestBlock || lowestBlock.i < blocks[i].i) {
				lowestBlock = blocks[i];
			}
			i++;
		}
		// relies on EventView.hide not removing the nextBlock pointer
		if (lowestBlock.block.id() != origBlock.id()) {
			if (lowestBlock.block.prevBlock) {
				layoutDependentChains(lowestBlock.block.prevBlock);
			} else {
				layoutDependentChainBlock(lowestBlock.block.chain.firstBlock)
			}
			
			if (origBlock.top > C.TIMELINEHEIGHT) {
				hideDependentBlocks(origBlock, origBlock.top - C.TIMELINEHEIGHT);
			}
		}
	}
	// Given a block, does not reposition it, and calls
	// layoutDependentChainBlock on the dependingBlocks. Each chain
	// coresponding to a dependingBlock is allowed to finish execution. If
	// all chains return true, then true is returned. If at least one
	// chain returns false, then false is returned.
	function layoutDependentChains(block) {	
		var nextBlocks = [];
		block.dependingBlocks.each(function (b) {
			nextBlocks.push(b);
		}, this);
		nextBlocks.sort(function (a, b) { return b.chainIndex - a.chainIndex; })
		var success = true;
		_.each(nextBlocks, function (b) {
			success = success && layoutDependentChainBlock(b);
		}, this);
		return success;
	}
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
	function layoutDependentChainBlock(block) {
		var prevBottom = block.bottom;
		// todo, be better at holding onto prevChainBlock
		placeBlock(block,
			block.prevChain
				? block.prevChain.firstBlock
				: null);

		if (block.bottom >= prevBottom
			|| block.top > C.TIMELINEHEIGHT) {
			return false;
		} else {
			return layoutDependentChains(block);
		}
	}


	// prevChainBlock may be null. returns prevChainBlock appropriately for
	// calling with the next block
	function placeBlock(block, prevChainBlock) {
		var bottom = block.prevBlock ? block.prevBlock.top : 0;

		if (block.dependentBlock) block.dependentBlock.dependingBlocks.remove(block);
		block.dependentBlock = block.prevBlock;
		if (block.dependentBlock) block.dependentBlock.dependingBlocks.add(block);

		// penultimatePrevChainBlock ends up being the block that the next block in the current chain needs to check for overlap
		var penultimatePrevChainBlock = prevChainBlock;
		// check for overlaps
		while (prevChainBlock
			&& prevChainBlock.bottom < bottom + block.height
			&& prevChainBlock.right > block.left) {
			// the while conditions plus this if condition guarantee overlap
			if (prevChainBlock.top > bottom) {
				bottom = prevChainBlock.top;
				// this case requires adding a new chain to the dependentChain
				if (block.dependentBlock) block.dependentBlock.dependingBlocks.remove(block);
				block.dependentBlock = prevChainBlock;
				block.dependentBlock.dependingBlocks.add(block);
			}

			// advance to the next block in the previous chain
			penultimatePrevChainBlock = prevChainBlock;
			prevChainBlock = prevChainBlock.nextBlock;
		}

		block.setBottom(bottom);

		return penultimatePrevChainBlock;
	}

	function layoutViewChains(chains) {
		var i = chains.length - 1;
		var reset = null;
		while (i >= 0 || reset) {
			var block = chains[i].firstBlock;
			var prevChainBlock = block.prevChain
				? block.prevChain.firstBlock
				: null;
			while (block) {
				prevChainBlock = placeBlock(block, prevChainBlock);

				// if vertical height is too high, remove blocks and relayout
				if (block.top > C.TIMELINEHEIGHT) {
					hideDependentBlocks(block, block.top - C.TIMELINEHEIGHT);
				}
				block = block.nextBlock;
			}
			i--;
		}
	}

	function makeViewChains (events) {
		// create view chains. Each chains[i] is a block that should be
		// rendered at the base of the timeline. The chain is doubly-
		// linked through chains[i].nextBlock and prevBlock
		var chains = [];
		var prevBlock = null;
		for (var i = 0; i < events.length; i++) {
			if (i == 0 ||
				events[i].right < chains[chains.length - 1].firstBlock.left) { // create a new chain
				chains.push({firstBlock: events[i]});
				events[i].prevBlock = null;
			} else { // add to the existing chain
				events[i].prevBlock = prevBlock;
				if (prevBlock) prevBlock.nextBlock = events[i];
			}
			
			prevBlock = events[i];
			events[i].nextBlock = null;
		}

		// set prevChain (prevChain refers to the chain to the left, which
		// has a higher index), chainIndex, and chain
		for (var i = 0; i < chains.length; i++) {
			var b = chains[i].firstBlock;
			while (b) {
				b.chainIndex = i;
				b.chain = chains[i];
				b.prevChain = i + 1 >= chains.length ? null : chains[i + 1]; 
				b = b.nextBlock;
			}
		}

		var hidden = false;

		// hide elements so that each chain is short enough to fit on the timeline
		for (var i = 0; i < chains.length; i++) {
			var b = chains[i].firstBlock;
			var totalHeight = 0;
			var chainBlocks = []
			while (b) {
				totalHeight += b.height;
				chainBlocks.push(b);
				b = b.nextBlock;
			}
			chainBlocks.sort(function (a,b) { return a.importance - b.importance; });
			var j = 0;
			var removedHeight = 0;
			while (removedHeight < totalHeight - C.TIMELINEHEIGHT) {
				chainBlocks[j].hide();
				hidden = true;
				removedHeight += chainBlocks[j].height;
				j++;
			}
		}

		if (hidden) {
			return makeViewChains(_.filter(events, function (e) { return !e.hidden; }));
		} else {
			return chains;
		}
	}


	var Event = (function() {
		var baseObject = {
			setBottom: function (b) { this.bottom = b; this.top = b + this.height; },
			setLeft: function (l) { this.left = l; this.right = l + C.EVENTWIDTH; },
			html: function () { return this.$el.html(); },
			id: function () { return this.date + this.content; },
			hide: function () {
				this.hidden = true;

				if (this.nextBlock)
					this.nextBlock.prevBlock = this.prevBlock;
				if (this.prevBlock)
					this.prevBlock.nextBlock = this.nextBlock;
				else
					this.chain.firstBlock = this.nextBlock;
				if (this.dependentBlock) {
					this.dependentBlock.dependingBlocks.remove(this);
					this.dependingBlocks.each(function (b) {
						this.dependentBlock.dependingBlocks.add(b);
					}, this);
				}
				this.dependingBlocks.each(function (b) {
					b.dependentBlock = this.dependentBlock;
				}, this)
			}
		}
		function Event(eventData, $containerEl, template) {
			this.date = eventData.date;
			this.content = eventData.content;
			this.importance = eventData.importance;
			this.hidden = false;
			this.dependingBlocks = new Set(function (e) { return e.id(); });

			this.$el = $('<div></div').html(template(eventData));
			$containerEl.append(this.$el);
			this.height = $('.event-text', this.$el).outerHeight(true); // true includes margins
		}
		Event.prototype = baseObject;
		return Event;
	})();

	// Takes a list of events that have had setLeft called. Returns a subset
	// of events that have had setBottom called
	function setBottoms(evs) {
		var chains = makeViewChains(evs)
		layoutViewChains(chains);
		return _.filter(evs, function (e) { return !e.hidden; });
	}

	return { Event: Event, setBottoms: setBottoms};
})