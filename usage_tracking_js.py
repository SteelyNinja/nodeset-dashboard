import streamlit as st

def inject_usage_tracking_js():
    """Inject JavaScript for comprehensive usage tracking"""
    
    tracking_js = """
    <script>
    // Usage tracking state
    window.dashboardUsageTracker = {
        currentTab: null,
        tabStartTime: null,
        sessionStartTime: Date.now(),
        interactions: 0,
        scrollEvents: 0,
        lastActivity: Date.now()
    };

    function trackTabSwitch(tabName) {
        // Track time spent on previous tab
        if (window.dashboardUsageTracker.currentTab && window.dashboardUsageTracker.tabStartTime) {
            const timeSpent = Date.now() - window.dashboardUsageTracker.tabStartTime;
            console.log('Tab', window.dashboardUsageTracker.currentTab, 'viewed for', Math.round(timeSpent/1000), 'seconds');
        }
        
        // Update current tab
        window.dashboardUsageTracker.currentTab = tabName;
        window.dashboardUsageTracker.tabStartTime = Date.now();
        window.dashboardUsageTracker.interactions++;
        
        // Log tab switch for debugging
        console.log('📑 Tab switched to:', tabName);
        
        // Note: Since we can't easily communicate back to Python from JavaScript in Streamlit,
        // we'll rely on the fact that this JavaScript tracking shows user engagement
        // The actual counting will happen when users trigger Streamlit reruns
    }

    function trackPageActivity() {
        window.dashboardUsageTracker.lastActivity = Date.now();
        window.dashboardUsageTracker.interactions++;
    }

    function trackScrollActivity() {
        window.dashboardUsageTracker.scrollEvents++;
        trackPageActivity();
    }

    // Track tab clicks using MutationObserver to detect Streamlit tab changes
    function observeTabChanges() {
        let tabClickTracker = {
            lastClickedTab: null,
            sessionId: Math.random().toString(36).substr(2, 9)
        };
        
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'aria-selected') {
                    const tab = mutation.target;
                    if (tab.getAttribute('aria-selected') === 'true') {
                        const tabText = tab.textContent || tab.innerText || 'Unknown';
                        const cleanTabText = tabText.trim().replace(/^[🔥📈🎯🏆⚡🤲📡🚪💰🔧📋]\s*/, '');
                        
                        // Only track if this is a different tab from what we last tracked
                        if (tabClickTracker.lastClickedTab !== cleanTabText) {
                            trackTabSwitch(cleanTabText);
                            tabClickTracker.lastClickedTab = cleanTabText;
                            
                            // Store tab click in localStorage to persist across reloads
                            try {
                                const tabClicks = JSON.parse(localStorage.getItem('dashboard_tab_clicks') || '{}');
                                tabClicks[cleanTabText] = (tabClicks[cleanTabText] || 0) + 1;
                                localStorage.setItem('dashboard_tab_clicks', JSON.stringify(tabClicks));
                                
                                // Send message to parent window if possible
                                if (window.parent && window.parent.postMessage) {
                                    window.parent.postMessage({
                                        type: 'tab-click',
                                        tabName: cleanTabText,
                                        timestamp: Date.now(),
                                        sessionId: tabClickTracker.sessionId
                                    }, '*');
                                }
                            } catch (e) {
                                console.log('Could not store tab click:', e);
                            }
                        }
                    }
                }
                
                // Also check for new tab elements and add direct click listeners
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            const tabs = node.querySelectorAll('[data-baseweb="tab"]');
                            tabs.forEach(function(tab) {
                                if (!tab.hasAttribute('data-tracked')) {
                                    tab.setAttribute('data-tracked', 'true');
                                    tab.addEventListener('click', function() {
                                        const tabText = tab.textContent || tab.innerText || 'Unknown';
                                        const cleanTabText = tabText.trim().replace(/^[🔥📈🎯🏆⚡🤲📡🚪💰🔧📋]\s*/, '');
                                        
                                        // Track the click immediately
                                        console.log('Direct tab click detected:', cleanTabText);
                                        
                                        // Only track if different from last clicked
                                        if (tabClickTracker.lastClickedTab !== cleanTabText) {
                                            trackTabSwitch(cleanTabText);
                                            tabClickTracker.lastClickedTab = cleanTabText;
                                            
                                            // Store in localStorage
                                            try {
                                                const tabClicks = JSON.parse(localStorage.getItem('dashboard_tab_clicks') || '{}');
                                                tabClicks[cleanTabText] = (tabClicks[cleanTabText] || 0) + 1;
                                                localStorage.setItem('dashboard_tab_clicks', JSON.stringify(tabClicks));
                                            } catch (e) {
                                                console.log('Could not store tab click:', e);
                                            }
                                        }
                                    });
                                }
                            });
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['aria-selected']
        });
        
        // Set initial tab as Distribution if no other tab has been clicked
        setTimeout(function() {
            if (!tabClickTracker.lastClickedTab) {
                tabClickTracker.lastClickedTab = 'Distribution';
                trackTabSwitch('Distribution');
                console.log('Initial tab set to Distribution');
            }
        }, 1000);
    }

    // Track general interactions
    function addInteractionListeners() {
        // Click tracking
        document.addEventListener('click', function(e) {
            trackPageActivity();
            
            // Special tracking for buttons
            if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                const button = e.target.tagName === 'BUTTON' ? e.target : e.target.closest('button');
                const buttonText = button.textContent || button.innerText || 'Unknown Button';
                console.log('Button clicked:', buttonText.trim());
                
                // Track refresh button specifically
                if (buttonText.includes('Refresh')) {
                    try {
                        if (window.parent && window.parent.postMessage) {
                            window.parent.postMessage({
                                type: 'refresh-action',
                                timestamp: Date.now()
                            }, '*');
                        }
                    } catch (e) {
                        console.log('Could not send refresh tracking message:', e);
                    }
                }
            }
        });

        // Scroll tracking (throttled)
        let scrollTimeout;
        document.addEventListener('scroll', function() {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(trackScrollActivity, 250);
        });

        // Mouse movement tracking (very throttled)
        let mouseTimeout;
        document.addEventListener('mousemove', function() {
            clearTimeout(mouseTimeout);
            mouseTimeout = setTimeout(trackPageActivity, 5000); // Only every 5 seconds
        });

        // Window focus/blur tracking
        window.addEventListener('focus', function() {
            console.log('Dashboard gained focus');
            trackPageActivity();
        });

        window.addEventListener('blur', function() {
            console.log('Dashboard lost focus');
        });

        // Track time on page before leaving
        window.addEventListener('beforeunload', function() {
            const sessionTime = Date.now() - window.dashboardUsageTracker.sessionStartTime;
            console.log('Session lasted', Math.round(sessionTime/1000), 'seconds with', 
                       window.dashboardUsageTracker.interactions, 'interactions');
        });
    }

    // Initialize tracking when DOM is ready
    function initializeTracking() {
        console.log('Dashboard usage tracking initialized');
        
        // Track initial page load
        trackTabSwitch('Dashboard Loaded');
        
        // Set up observers and listeners
        observeTabChanges();
        addInteractionListeners();
        
        // Send periodic activity updates
        setInterval(function() {
            const now = Date.now();
            const timeSinceLastActivity = now - window.dashboardUsageTracker.lastActivity;
            
            // If user has been active in last 30 seconds, send heartbeat
            if (timeSinceLastActivity < 30000) {
                try {
                    if (window.parent && window.parent.postMessage) {
                        window.parent.postMessage({
                            type: 'activity-heartbeat',
                            timestamp: now,
                            sessionTime: now - window.dashboardUsageTracker.sessionStartTime,
                            interactions: window.dashboardUsageTracker.interactions,
                            currentTab: window.dashboardUsageTracker.currentTab
                        }, '*');
                    }
                } catch (e) {
                    // Ignore postMessage errors
                }
            }
        }, 30000); // Every 30 seconds
    }

    // Start tracking
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeTracking);
    } else {
        initializeTracking();
    }

    // Also initialize after a short delay to catch dynamically loaded content
    setTimeout(initializeTracking, 1000);
    </script>
    """
    
    st.markdown(tracking_js, unsafe_allow_html=True)

def track_data_loading_operation(operation_name: str, success: bool = True, error_msg: str = None):
    """Track data loading operations throughout the dashboard"""
    try:
        from usage_tracker import usage_tracker
        
        if success:
            # Track successful data operations
            if 'data_operations' not in usage_tracker.stats:
                usage_tracker.stats['data_operations'] = {}
            
            if operation_name not in usage_tracker.stats['data_operations']:
                usage_tracker.stats['data_operations'][operation_name] = {
                    'success_count': 0,
                    'error_count': 0,
                    'last_success': None,
                    'last_error': None
                }
            
            usage_tracker.stats['data_operations'][operation_name]['success_count'] += 1
            usage_tracker.stats['data_operations'][operation_name]['last_success'] = st.session_state.get('current_time', 'unknown')
            
        else:
            # Track errors
            usage_tracker.track_error(f"data_loading_{operation_name}")
            
            if 'data_operations' not in usage_tracker.stats:
                usage_tracker.stats['data_operations'] = {}
            
            if operation_name not in usage_tracker.stats['data_operations']:
                usage_tracker.stats['data_operations'][operation_name] = {
                    'success_count': 0,
                    'error_count': 0,
                    'last_success': None,
                    'last_error': None
                }
            
            usage_tracker.stats['data_operations'][operation_name]['error_count'] += 1
            usage_tracker.stats['data_operations'][operation_name]['last_error'] = error_msg or 'Unknown error'
        
        usage_tracker._save_stats()
        
    except Exception as e:
        # Don't let tracking errors break the dashboard
        pass