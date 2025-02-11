document.addEventListener('DOMContentLoaded', function() {
    // YouTube URL handling
    const youtubeInput = document.getElementById('youtubeUrl');
    const loadButton = document.getElementById('loadVideo');
    const player = document.getElementById('youtubePlayer');

    function loadYouTubeVideo() {
        const url = youtubeInput.value.trim();
        const errorDiv = document.getElementById('videoError');

        if (!url) {
            showNotification('Vui lòng nhập link YouTube');
            return;
        }

        // Extract video ID from URL
        let videoId = extractVideoId(url);
        if (!videoId) {
            showNotification('Link YouTube không hợp lệ');
            return;
        }

        try {
            // Hide error message if visible
            errorDiv.style.display = 'none';
            errorDiv.classList.remove('show');

            // Create new iframe
            const newPlayer = document.createElement('iframe');
            newPlayer.width = '100%';
            newPlayer.height = '600';
            newPlayer.frameBorder = '0';
            newPlayer.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
            newPlayer.allowFullscreen = true;
            newPlayer.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
            
            // Add load event listener
            newPlayer.onload = () => {
                showNotification('Đã tải video thành công');
                youtubeInput.value = '';
            };

            // Add error event listener
            newPlayer.onerror = () => {
                errorDiv.style.display = 'block';
                errorDiv.classList.add('show');
                showNotification('Không thể tải video này');
            };

            // Replace old iframe
            player.parentNode.replaceChild(newPlayer, player);
        } catch (error) {
            errorDiv.style.display = 'block';
            errorDiv.classList.add('show');
            showNotification('Có lỗi khi tải video. Vui lòng thử lại.');
        }
    }

    // Handle button click
    loadButton.addEventListener('click', loadYouTubeVideo);

    // Handle Enter key
    youtubeInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            loadYouTubeVideo();
        }
    });

    // Extract YouTube video ID from various URL formats
    function extractVideoId(url) {
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
    }

    // Update time ago for all timestamps
    updateTimeAgo();
    
    // Handle sidebar navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!this.getAttribute('href').startsWith('/')) {
                e.preventDefault();
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });

    // Handle refresh button
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            this.classList.add('fa-spin');
            setTimeout(() => {
                this.classList.remove('fa-spin');
                // Here you would typically fetch new activity data
                showNotification('Activity list refreshed');
            }, 1000);
        });
    }

    // Notification system
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(notification);

        // Trigger animation
        setTimeout(() => notification.classList.add('show'), 10);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Update relative timestamps
    function updateTimeAgo() {
        const timestamps = document.querySelectorAll('.activity-table td:nth-child(3)');
        timestamps.forEach(timestamp => {
            // In a real application, you would convert actual timestamps
            // For now, we'll keep the demo times
            const time = timestamp.textContent;
            timestamp.textContent = time;
        });
    }

    // Add notification styles
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 10px;
            transform: translateX(120%);
            transition: transform 0.3s ease;
            z-index: 1000;
        }

        .notification.show {
            transform: translateX(0);
        }

        .notification i {
            color: var(--primary-color);
        }
    `;
    document.head.appendChild(style);

    // Handle user session
    function checkSession() {
        const lastActivity = localStorage.getItem('lastActivity');
        const now = new Date().getTime();
        
        // If no activity for 30 minutes, redirect to login
        if (lastActivity && (now - parseInt(lastActivity)) > 30 * 60 * 1000) {
            window.location.href = '/login';
        } else {
            localStorage.setItem('lastActivity', now);
        }
    }

    // Update last activity timestamp
    document.addEventListener('mousemove', () => {
        localStorage.setItem('lastActivity', new Date().getTime());
    });

    // Check session every minute
    setInterval(checkSession, 60000);

    // Initial session check
    checkSession();
});