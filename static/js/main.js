document.addEventListener('DOMContentLoaded', function() {
    // 1. Mobile Sidebar Toggle
    const hamburger = document.querySelector('.hamburger');
    const sidebar = document.querySelector('.sidebar');
    if (hamburger && sidebar) {
        hamburger.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            const isClickInside = sidebar.contains(event.target) || hamburger.contains(event.target);
            if (!isClickInside && sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
            }
        });
    }

    // 2. Dynamic City Loading by State Selection
    const stateSelect = document.getElementById('state-select');
    const citySelect = document.getElementById('city-select');
    if (stateSelect && citySelect) {
        stateSelect.addEventListener('change', function() {
            const stateId = this.value;
            if (!stateId) {
                citySelect.innerHTML = '<option value="">Choose State First...</option>';
                return;
            }
            
            citySelect.innerHTML = '<option value="">Loading Cities...</option>';
            
            fetch(`/auth/api/cities/${stateId}`)
                .then(response => response.json())
                .then(data => {
                    citySelect.innerHTML = '<option value="">Select City</option>';
                    data.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city.id;
                        option.textContent = city.name;
                        citySelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching cities:', error);
                    citySelect.innerHTML = '<option value="">Error loading cities</option>';
                });
        });
    }

    // 3. Collapsible FAQ Accordion
    const faqTriggers = document.querySelectorAll('.faq-trigger');
    faqTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const icon = this.querySelector('svg');
            
            // Toggle visibility
            if (content.style.display === 'block') {
                content.style.display = 'none';
                if (icon) icon.style.transform = 'rotate(0deg)';
            } else {
                content.style.display = 'block';
                if (icon) icon.style.transform = 'rotate(180deg)';
            }
        });
    });

    // 4. Auto Fade-Out Flash Alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 1s ease-out, transform 1s ease-out';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 1000);
        }, 5000);
    });

    // 5. Image File Upload Preview (For Recruiter Logos)
    const logoInput = document.getElementById('logo-upload');
    const logoPreview = document.getElementById('logo-preview');
    if (logoInput && logoPreview) {
        logoInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    logoPreview.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // 6. Resume File Upload Name Display
    const resumeInput = document.getElementById('resume-upload');
    const resumeLabel = document.getElementById('resume-label');
    if (resumeInput && resumeLabel) {
        resumeInput.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : 'Choose PDF resume file...';
            resumeLabel.textContent = fileName;
        });
    }

    // 7. PlaceTrack AI Floating Chatbot Widget Interactivity
    const chatbotTrigger = document.getElementById('chatbot-trigger');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotMessages = document.getElementById('chatbot-messages');

    if (chatbotTrigger && chatbotWindow) {
        // Toggle chat window open/close
        chatbotTrigger.addEventListener('click', function() {
            chatbotWindow.classList.toggle('hidden');
            // Hide notification dot on first open
            const dot = chatbotTrigger.querySelector('.chatbot-notification-dot');
            if (dot) dot.style.display = 'none';
            // Scroll to bottom on open
            if (!chatbotWindow.classList.contains('hidden')) {
                chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                chatbotInput.focus();
            }
        });

        if (chatbotClose) {
            chatbotClose.addEventListener('click', function(e) {
                e.stopPropagation();
                chatbotWindow.classList.add('hidden');
            });
        }

        if (chatbotForm && chatbotInput && chatbotMessages) {
            chatbotForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const text = chatbotInput.value.trim();
                if (!text) return;

                // Clear input
                chatbotInput.value = '';

                // Append outgoing user message
                appendChatMessage(text, 'outgoing');

                // Append typing indicator
                const typingBubble = appendChatTypingIndicator();

                // Scroll messages list to bottom
                chatbotMessages.scrollTop = chatbotMessages.scrollHeight;

                // Send request to Flask API
                fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: text })
                })
                .then(response => response.json())
                .then(data => {
                    // Remove typing indicator
                    if (typingBubble) typingBubble.remove();
                    
                    // Append incoming chatbot reply
                    appendChatMessage(data.response || 'No reply received.', 'incoming');
                    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                })
                .catch(error => {
                    console.error('Chatbot error:', error);
                    if (typingBubble) typingBubble.remove();
                    appendChatMessage('Sorry, I encountered an issue connecting to the server. Please try again.', 'incoming');
                    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                });
            });
        }
    }

    function appendChatMessage(text, sender) {
        const bubble = document.createElement('div');
        bubble.className = `chatbot-message ${sender}`;
        bubble.textContent = text;
        chatbotMessages.appendChild(bubble);
    }

    function appendChatTypingIndicator() {
        const bubble = document.createElement('div');
        bubble.className = 'chatbot-message incoming typing-indicator';
        bubble.innerHTML = '<span></span><span></span><span></span>';
        chatbotMessages.appendChild(bubble);
        return bubble;
    }
});
