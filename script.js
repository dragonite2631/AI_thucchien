document.addEventListener('DOMContentLoaded', () => {

    // Sticky Navbar on Scroll
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // GSAP Animations
    if (typeof gsap !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        // Hero Section Animation
        gsap.from('#hero .container > *', {
            duration: 1,
            opacity: 0,
            y: 50,
            stagger: 0.2,
            ease: 'power3.out'
        });

        // General Section Animation
        const animateUp = (elem) => {
            gsap.from(elem, {
                scrollTrigger: {
                    trigger: elem,
                    start: 'top 85%',
                    toggleActions: 'play none none none'
                },
                duration: 0.8,
                opacity: 0,
                y: 50,
                ease: 'power3.out'
            });
        };
        
        animateUp('#tong-quan .row');
        animateUp('#ban-do .container');
        animateUp('#khoanh-khac .container');

        // Staggered Card Animation for Su Kien Section
        gsap.from('#su-kien .card', {
            scrollTrigger: {
                trigger: '#su-kien',
                start: 'top 80%',
                toggleActions: 'play none none none'
            },
            duration: 0.8,
            opacity: 0,
            y: 50,
            stagger: 0.2,
            ease: 'power3.out'
        });
    }

});
