// ===== AGENT EXO-SUIT V5.0 WEBSITE SCRIPT =====
// Where Dreams Become Code, and Code Becomes Legend

// ===== SMOOTH SCROLLING =====
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80; // Account for fixed navbar
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ===== SCROLL ANIMATIONS =====
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, observerOptions);

    // Observe all cards and sections for animation
    const animateElements = document.querySelectorAll('.feature-card, .capability-card, .architecture-layer, .start-card');
    animateElements.forEach(el => {
        observer.observe(el);
    });

    // ===== NAVBAR SCROLL EFFECT =====
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.style.background = 'rgba(15, 23, 42, 0.98)';
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(15, 23, 42, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });

    // ===== PARALLAX EFFECT FOR HERO BACKGROUND =====
    const heroBackground = document.querySelector('.hero-background');
    
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        if (heroBackground) {
            heroBackground.style.transform = `translateY(${rate}px)`;
        }
    });

    // ===== INTERACTIVE CODE WINDOWS =====
    const codeWindows = document.querySelectorAll('.code-window');
    
    codeWindows.forEach(window => {
        window.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
            this.style.boxShadow = '0 25px 50px rgba(0, 0, 0, 0.15)';
        });
        
        window.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)';
        });
    });

    // ===== STATS COUNTER ANIMATION =====
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const animateCounter = (element, target, duration = 2000) => {
        let start = 0;
        const increment = target / (duration / 16);
        
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(start);
            }
        }, 16);
    };

    // Animate stats when they come into view
    const statsObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statNumber = entry.target;
                const targetValue = statNumber.textContent;
                
                // Parse the target value
                let target = 0;
                if (targetValue.includes('+')) {
                    target = parseInt(targetValue.replace('+', ''));
                } else if (targetValue.includes('%')) {
                    target = parseFloat(targetValue.replace('%', ''));
                } else {
                    target = parseInt(targetValue);
                }
                
                if (!isNaN(target)) {
                    statNumber.textContent = '0';
                    animateCounter(statNumber, target);
                }
                
                statsObserver.unobserve(statNumber);
            }
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(stat => {
        statsObserver.observe(stat);
    });

    // ===== FEATURE CARD HOVER EFFECTS =====
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.feature-icon');
            if (icon) {
                icon.style.transform = 'scale(1.1) rotate(5deg)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.feature-icon');
            if (icon) {
                icon.style.transform = 'scale(1) rotate(0deg)';
            }
        });
    });

    // ===== ARCHITECTURE LAYER INTERACTIONS =====
    const architectureLayers = document.querySelectorAll('.architecture-layer');
    
    architectureLayers.forEach(layer => {
        layer.addEventListener('mouseenter', function() {
            const layerNumber = this.querySelector('.layer-number');
            if (layerNumber) {
                layerNumber.style.transform = 'scale(1.2)';
                layerNumber.style.color = '#8b5cf6';
            }
        });
        
        layer.addEventListener('mouseleave', function() {
            const layerNumber = this.querySelector('.layer-number');
            if (layerNumber) {
                layerNumber.style.transform = 'scale(1)';
                layerNumber.style.color = '#6366f1';
            }
        });
    });

    // ===== CTA BUTTON HOVER EFFECTS =====
    const ctaButtons = document.querySelectorAll('.cta-buttons .btn');
    
    ctaButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.05)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // ===== NEWSLETTER FORM INTERACTION =====
    const newsletterForm = document.querySelector('.newsletter-form');
    const emailInput = document.querySelector('.newsletter-form input[type="email"]');
    const subscribeBtn = document.querySelector('.newsletter-form button');
    
    if (newsletterForm && emailInput && subscribeBtn) {
        subscribeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const email = emailInput.value.trim();
            if (email && isValidEmail(email)) {
                // Show success message
                this.textContent = 'Subscribed!';
                this.style.background = 'var(--success-color)';
                emailInput.value = '';
                
                // Reset button after 3 seconds
                setTimeout(() => {
                    this.textContent = 'Subscribe';
                    this.style.background = 'var(--gradient-primary)';
                }, 3000);
            } else {
                // Show error state
                emailInput.style.borderColor = 'var(--danger-color)';
                emailInput.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
                
                setTimeout(() => {
                    emailInput.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                    emailInput.style.boxShadow = 'none';
                }, 3000);
            }
        });
    }

    // ===== EMAIL VALIDATION =====
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // ===== PERFORMANCE OPTIMIZATION =====
    // Throttle scroll events
    let ticking = false;
    
    function updateOnScroll() {
        // Update navbar background
        if (window.scrollY > 100) {
            navbar.style.background = 'rgba(15, 23, 42, 0.98)';
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(15, 23, 42, 0.95)';
            navbar.style.boxShadow = 'none';
        }
        
        // Update parallax effect
        if (heroBackground) {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            heroBackground.style.transform = `translateY(${rate}px)`;
        }
        
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateOnScroll);
            ticking = true;
        }
    });

    // ===== ACCESSIBILITY IMPROVEMENTS =====
    // Add focus indicators for keyboard navigation
    const focusableElements = document.querySelectorAll('a, button, input, textarea, select');
    
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '2px solid var(--accent-color)';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = 'none';
        });
    });

    // ===== LOADING ANIMATIONS =====
    // Add loading animation for the page
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
        
        // Animate hero elements sequentially
        const heroElements = document.querySelectorAll('.hero-badge, .hero-title, .hero-subtitle, .hero-description, .hero-buttons, .hero-stats');
        
        heroElements.forEach((element, index) => {
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * 200);
        });
    });

    // ===== MOBILE MENU ENHANCEMENTS =====
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            if (!isExpanded) {
                // Add slide-down animation
                navbarCollapse.style.display = 'block';
                navbarCollapse.style.height = '0';
                navbarCollapse.style.overflow = 'hidden';
                
                setTimeout(() => {
                    navbarCollapse.style.height = navbarCollapse.scrollHeight + 'px';
                }, 10);
            } else {
                // Add slide-up animation
                navbarCollapse.style.height = '0';
                
                setTimeout(() => {
                    navbarCollapse.style.display = 'none';
                }, 300);
            }
        });
    }
});

// ===== ADDITIONAL UTILITY FUNCTIONS =====
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ===== EXPORT FOR MODULE SYSTEMS =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        debounce,
        throttle
    };
}
