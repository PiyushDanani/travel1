/* ===================================================================
   TRAVELICIOUS TOURS AND TRAVELS - ULTRA-LUXURY JAVASCRIPT
   Director: Irfan Sheikh (+256 751 510 786 / 0751510786)
   Location: Obote Avenue Main Street, Lira City, Uganda
=================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  const DIRECTOR_WHATSAPP = '256751510786';

  // 1. Dynamic Year in Footer
  const yearElement = document.getElementById('currentYear');
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }

  // 2. Mobile Navigation Menu Toggle
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navMenu.classList.toggle('open');
      const icon = navToggle.querySelector('i');
      if (icon) {
        if (navMenu.classList.contains('open')) {
          icon.classList.remove('fa-bars');
          icon.classList.add('fa-xmark');
        } else {
          icon.classList.remove('fa-xmark');
          icon.classList.add('fa-bars');
        }
      }
    });

    // Close menu when clicking on a link
    const navLinks = navMenu.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('open');
        const icon = navToggle.querySelector('i');
        if (icon) {
          icon.classList.remove('fa-xmark');
          icon.classList.add('fa-bars');
        }
      });
    });
  }

  // 3. Navbar scroll effect
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.style.boxShadow = '0 12px 30px rgba(0, 0, 0, 0.6)';
      navbar.style.borderBottomColor = 'rgba(212, 175, 55, 0.45)';
    } else {
      navbar.style.boxShadow = 'none';
      navbar.style.borderBottomColor = 'rgba(212, 175, 55, 0.28)';
    }
  });

  // 4. Quick Inquiry Form (Hero Section) -> WhatsApp Redirect
  const quickForm = document.getElementById('quickInquiryForm');
  if (quickForm) {
    quickForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const dest = document.getElementById('quickDest').value;
      const service = document.getElementById('quickService').value;
      const travelers = document.getElementById('quickTravelers').value;

      const message = `*VIP TRAVEL INQUIRY - TRAVELICIOUS LIRA CITY*%0A------------------------------------------------%0A*Director:* Irfan Sheikh (+256 751 510 786)%0A*Destination:* ${encodeURIComponent(dest)}%0A*Service Required:* ${encodeURIComponent(service)}%0A*Travelers:* ${encodeURIComponent(travelers)}%0A*Branch:* Obote Avenue Main Street, Lira City%0A------------------------------------------------%0APlease provide luxury travel package options and competitive rates.`;

      const waUrl = `https://wa.me/${DIRECTOR_WHATSAPP}?text=${message}`;
      window.open(waUrl, '_blank');
    });
  }

  // 5. Contact / Inquiry Form -> WhatsApp & Feedback
  const contactForm = document.getElementById('contactForm');
  const successBanner = document.getElementById('formSuccessMessage');

  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const name = document.getElementById('userName').value.trim();
      const phone = document.getElementById('userPhone').value.trim();
      const dest = document.getElementById('userDest').value.trim() || 'Not specified';
      const service = document.getElementById('userService').value;
      const userMsg = document.getElementById('userMessage').value.trim() || 'No additional note';

      const message = `*NEW VIP CLIENT INQUIRY - LIRA HEADQUARTERS*%0A------------------------------------------------%0A*Name:* ${encodeURIComponent(name)}%0A*Phone:* ${encodeURIComponent(phone)}%0A*Service:* ${encodeURIComponent(service)}%0A*Preferred Destination:* ${encodeURIComponent(dest)}%0A*Client Notes:* ${encodeURIComponent(userMsg)}%0A------------------------------------------------%0A*Attn Managing Director:* Irfan Sheikh (+256 751 510 786)`;

      if (successBanner) {
        successBanner.style.display = 'flex';
      }

      setTimeout(() => {
        const waUrl = `https://wa.me/${DIRECTOR_WHATSAPP}?text=${message}`;
        window.open(waUrl, '_blank');
        contactForm.reset();
        if (successBanner) {
          setTimeout(() => {
            successBanner.style.display = 'none';
          }, 6000);
        }
      }, 600);
    });
  }

  // 6. Smooth Scroll on Anchor Click
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId && targetId !== '#') {
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
          e.preventDefault();
          const navHeight = navbar ? navbar.offsetHeight : 0;
          const elementPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
          const offsetPosition = elementPosition - navHeight;

          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });
        }
      }
    });
  });

  // 7. Stats Counter Animation
  const statNumbers = document.querySelectorAll('.stat-number[data-target]');
  if ('IntersectionObserver' in window && statNumbers.length > 0) {
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseFloat(el.getAttribute('data-target'));
          const isDecimal = target % 1 !== 0;
          const duration = 1800;
          const startTime = performance.now();

          const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentVal = target * easeOut;

            if (isDecimal) {
              el.textContent = currentVal.toFixed(1) + '%';
            } else if (target >= 1000) {
              el.textContent = Math.floor(currentVal).toLocaleString() + '+';
            } else {
              el.textContent = Math.floor(currentVal) + '+';
            }

            if (progress < 1) {
              requestAnimationFrame(updateCounter);
            }
          };

          requestAnimationFrame(updateCounter);
          obs.unobserve(el);
        }
      });
    }, { threshold: 0.5 });

    statNumbers.forEach(stat => observer.observe(stat));
  }
});
