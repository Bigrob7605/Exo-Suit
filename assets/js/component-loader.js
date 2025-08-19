/**
 * Component Loader for Exo-Suit V5.0 Modular Webpage
 * Dynamically loads HTML components for maintainable architecture
 */

class ComponentLoader {
    constructor() {
        this.loadedComponents = new Set();
        this.componentCache = new Map();
    }

    /**
     * Load a component by name
     * @param {string} componentName - Name of the component to load
     * @param {string} containerId - ID of the container to load into
     * @param {boolean} cache - Whether to cache the component
     * @returns {Promise<void>}
     */
    async loadComponent(componentName, containerId, cache = true) {
        try {
            // Check if component is already loaded
            if (this.loadedComponents.has(componentName)) {
                console.log(`Component ${componentName} already loaded`);
                return;
            }

            // Check cache first
            if (cache && this.componentCache.has(componentName)) {
                this.insertComponent(componentName, containerId, this.componentCache.get(componentName));
                this.loadedComponents.add(componentName);
                return;
            }

            // Fetch component from server
            const response = await fetch(`components/${componentName}.html`);
            if (!response.ok) {
                throw new Error(`Failed to load component ${componentName}: ${response.status}`);
            }

            const html = await response.text();
            
            // Cache if requested
            if (cache) {
                this.componentCache.set(componentName, html);
            }

            // Insert component into DOM
            this.insertComponent(componentName, containerId, html);
            
            // Mark as loaded
            this.loadedComponents.add(componentName);
            
            console.log(`Component ${componentName} loaded successfully`);
            
            // Dispatch custom event for component loaded
            this.dispatchComponentEvent(componentName, 'loaded');
            
        } catch (error) {
            console.error(`Error loading component ${componentName}:`, error);
            this.dispatchComponentEvent(componentName, 'error', error);
        }
    }

    /**
     * Insert component HTML into container
     * @param {string} componentName - Name of the component
     * @param {string} containerId - ID of the container
     * @param {string} html - HTML content to insert
     */
    insertComponent(componentName, containerId, html) {
        const container = document.getElementById(containerId);
        if (!container) {
            throw new Error(`Container with ID '${containerId}' not found`);
        }

        // Insert HTML
        container.innerHTML = html;
        
        // Execute any scripts in the component
        this.executeComponentScripts(container);
        
        // Initialize component if it has an init function
        this.initializeComponent(componentName, container);
    }

    /**
     * Execute scripts found in component HTML
     * @param {HTMLElement} container - Container element
     */
    executeComponentScripts(container) {
        const scripts = container.querySelectorAll('script');
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            if (script.src) {
                newScript.src = script.src;
            } else {
                newScript.textContent = script.textContent;
            }
            document.head.appendChild(newScript);
        });
    }

    /**
     * Initialize component if it has initialization logic
     * @param {string} componentName - Name of the component
     * @param {HTMLElement} container - Container element
     */
    initializeComponent(componentName, container) {
        // Check if component has a global init function
        const initFunctionName = `${componentName}Init`;
        if (typeof window[initFunctionName] === 'function') {
            try {
                window[initFunctionName](container);
            } catch (error) {
                console.error(`Error initializing component ${componentName}:`, error);
            }
        }
    }

    /**
     * Load multiple components
     * @param {Array<{name: string, containerId: string}>} components - Array of component configs
     * @returns {Promise<void[]>}
     */
    async loadComponents(components) {
        const promises = components.map(comp => 
            this.loadComponent(comp.name, comp.containerId, comp.cache !== false)
        );
        return Promise.all(promises);
    }

    /**
     * Reload a component
     * @param {string} componentName - Name of the component to reload
     * @param {string} containerId - ID of the container
     * @returns {Promise<void>}
     */
    async reloadComponent(componentName, containerId) {
        // Remove from loaded components to force reload
        this.loadedComponents.delete(componentName);
        
        // Clear from cache
        this.componentCache.delete(componentName);
        
        // Reload
        await this.loadComponent(componentName, containerId);
    }

    /**
     * Dispatch custom component events
     * @param {string} componentName - Name of the component
     * @param {string} eventType - Type of event (loaded, error, etc.)
     * @param {*} data - Additional data for the event
     */
    dispatchComponentEvent(componentName, eventType, data = null) {
        const event = new CustomEvent(`component:${eventType}`, {
            detail: {
                component: componentName,
                type: eventType,
                data: data,
                timestamp: Date.now()
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Get loading status of components
     * @returns {Object} Status of all components
     */
    getStatus() {
        return {
            loaded: Array.from(this.loadedComponents),
            cached: Array.from(this.componentCache.keys()),
            totalLoaded: this.loadedComponents.size,
            totalCached: this.componentCache.size
        };
    }

    /**
     * Clear component cache
     */
    clearCache() {
        this.componentCache.clear();
        console.log('Component cache cleared');
    }
}

// Create global instance
window.componentLoader = new ComponentLoader();

// Auto-load components when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Component Loader initialized');
    
    // Auto-load components marked with data-component attribute
    const autoLoadContainers = document.querySelectorAll('[data-component]');
    autoLoadContainers.forEach(container => {
        const componentName = container.dataset.component;
        const containerId = container.id;
        
        if (componentName && containerId) {
            componentLoader.loadComponent(componentName, containerId);
        }
    });
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ComponentLoader;
}
