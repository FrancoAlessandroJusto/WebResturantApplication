/**
 * Animated List Component - Vanilla JS Implementation
 * Adapted from React Motion concept for our project
 */
class AnimatedList {
  constructor(options = {}) {
    this.items = options.items || [];
    this.onItemSelect = options.onItemSelect || (() => {});
    this.showGradients = options.showGradients !== false;
    this.enableArrowNavigation = options.enableArrowNavigation !== false;
    this.displayScrollbar = options.displayScrollbar !== false;
    this.initialSelectedIndex = options.initialSelectedIndex || -1;
    this.className = options.className || '';
    this.itemClassName = options.itemClassName || '';
    
    this.selectedIndex = this.initialSelectedIndex;
    this.keyboardNav = false;
    this.topGradientOpacity = 0;
    this.bottomGradientOpacity = 1;
    
    this.init();
  }
  
  init() {
    this.setupEventListeners();
  }
  
  setupEventListeners() {
    if (!this.enableArrowNavigation) return;
    
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowDown' || (e.key === 'Tab' && !e.shiftKey)) {
        e.preventDefault();
        this.keyboardNav = true;
        this.setSelectedIndex(Math.min(this.selectedIndex + 1, this.items.length - 1));
      } else if (e.key === 'ArrowUp' || (e.key === 'Tab' && e.shiftKey)) {
        e.preventDefault();
        this.keyboardNav = true;
        this.setSelectedIndex(Math.max(this.selectedIndex - 1, 0));
      } else if (e.key === 'Enter') {
        if (this.selectedIndex >= 0 && this.selectedIndex < this.items.length) {
          e.preventDefault();
          this.handleItemSelect(this.items[this.selectedIndex], this.selectedIndex);
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
  }
  
  handleItemMouseEnter(index) {
    this.setSelectedIndex(index);
  }
  
  handleItemClick(item, index) {
    this.setSelectedIndex(index);
    this.handleItemSelect(item, index);
  }
  
  handleItemSelect(item, index) {
    if (this.onItemSelect) {
      this.onItemSelect(item, index);
    }
  }
  
  setSelectedIndex(index) {
    this.selectedIndex = index;
    this.updateSelection();
    this.scrollToSelected();
  }
  
  updateSelection() {
    const container = document.querySelector('.scroll-list');
    if (!container) return;
    
    const items = container.querySelectorAll('.list-item');
    items.forEach((item, index) => {
      if (index === this.selectedIndex) {
        item.classList.add('selected');
      } else {
        item.classList.remove('selected');
      }
    });
  }
  
  scrollToSelected() {
    if (!this.keyboardNav || this.selectedIndex < 0) return;
    
    const container = document.querySelector('.scroll-list');
    if (!container) return;
    
    const selectedItem = container.querySelector(`[data-index="${this.selectedIndex}"]`);
    if (!selectedItem) return;
    
    const extraMargin = 50;
    const containerScrollTop = container.scrollTop;
    const containerHeight = container.clientHeight;
    const itemTop = selectedItem.offsetTop;
    const itemBottom = itemTop + selectedItem.offsetHeight;
    
    if (itemTop < containerScrollTop + extraMargin) {
      container.scrollTo({ top: itemTop - extraMargin, behavior: 'smooth' });
    } else if (itemBottom > containerScrollTop + containerHeight - extraMargin) {
      container.scrollTo({
        top: itemBottom - containerHeight + extraMargin,
        behavior: 'smooth'
      });
    }
    
    this.keyboardNav = false;
  }
  
  handleScroll(e) {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    this.topGradientOpacity = Math.min(scrollTop / 50, 1);
    const bottomDistance = scrollHeight - (scrollTop + clientHeight);
    this.bottomGradientOpacity = scrollHeight <= clientHeight ? 0 : Math.min(bottomDistance / 50, 1);
    
    this.updateGradients();
  }
  
  updateGradients() {
    const topGradient = document.querySelector('.top-gradient');
    const bottomGradient = document.querySelector('.bottom-gradient');
    
    if (topGradient) {
      topGradient.style.opacity = this.topGradientOpacity;
    }
    
    if (bottomGradient) {
      bottomGradient.style.opacity = this.bottomGradientOpacity;
    }
  }
  
  render(container) {
    const scrollbarClass = this.displayScrollbar ? '' : 'no-scrollbar';
    
    container.innerHTML = `
      <div class="scroll-list-container ${this.className}">
        <div class="scroll-list ${scrollbarClass}" onscroll="window.currentAnimatedList?.handleScroll(event)">
          ${this.items.map((item, index) => `
            <div class="list-item ${this.selectedIndex === index ? 'selected' : ''} ${this.itemClassName}" 
                 data-index="${index}"
                 onmouseenter="window.currentAnimatedList?.handleItemMouseEnter(${index})"
                 onclick="window.currentAnimatedList?.handleItemClick(${JSON.stringify(item)}, ${index})">
              <p class="list-item-text">${typeof item === 'string' ? item : item.name || item.text || JSON.stringify(item)}</p>
            </div>
          `).join('')}
        </div>
        ${this.showGradients ? `
          <div class="top-gradient" style="opacity: ${this.topGradientOpacity}"></div>
          <div class="bottom-gradient" style="opacity: ${this.bottomGradientOpacity}"></div>
        ` : ''}
      </div>
    `;
    
    window.currentAnimatedList = this;
  }
  
  updateItems(newItems) {
    this.items = newItems;
    this.selectedIndex = this.initialSelectedIndex;
    const container = document.querySelector('.scroll-list-container');
    if (container) {
      this.render(container.parentElement);
    }
  }
}

// Helper function to create animated list
function createAnimatedList(options) {
  return new AnimatedList(options);
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { AnimatedList, createAnimatedList };
}
