# app.py
"""
SKAN Interactive Demo - Python Flask Application
Protected interactive elements with copyable Flutter code
"""

from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
from flask_compress import Compress
import secrets
import base64
import json
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)
Compress(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Obfuscated JavaScript code storage (to prevent easy copying)
class CodeProtector:
    @staticmethod
    def obfuscate(code):
        """Simple obfuscation for JavaScript code"""
        # Convert to base64 and reverse for basic protection
        encoded = base64.b64encode(code.encode()).decode()
        return encoded[::-1]  # Reverse the string
    
    @staticmethod
    def generate_runtime_key():
        """Generate a unique key for each session"""
        return secrets.token_urlsafe(16)

# Flutter code samples (these will be copyable)
FLUTTER_CODE_SAMPLES = {
    'consent_granted': '''
// Flutter Implementation - Consent Granted
import 'package:appsflyer_sdk/appsflyer_sdk.dart';

class AppsFlyerService {
  static final AppsflyerSdk _appsflyerSdk = AppsflyerSdk({
    'afDevKey': 'YOUR_DEV_KEY',
    'afAppId': 'YOUR_APP_ID',
    'isDebug': true,
  });

  static Future<void> initWithConsent() async {
    // Full tracking enabled
    await _appsflyerSdk.initSdk(
      registerConversionDataCallback: true,
      registerOnAppOpenAttributionCallback: true,
      registerOnDeepLinkingCallback: true,
    );
    
    // Enable conversion value tracking
    await _appsflyerSdk.enableSKAdNetwork(true);
    
    // Track custom events
    await trackEvent('user_signup', {
      'signup_method': 'email',
      'user_type': 'premium'
    });
  }
  
  static Future<void> trackEvent(String eventName, Map<String, dynamic> values) async {
    await _appsflyerSdk.logEvent(eventName, values);
  }
  
  static void updateConversionValue(int value) {
    // iOS only - Update SKAdNetwork conversion value
    if (Platform.isIOS) {
      _appsflyerSdk.updateServerUninstallToken(value.toString());
    }
  }
}
''',
    'consent_denied': '''
// Flutter Implementation - Consent Denied (SKAN Only)
import 'package:appsflyer_sdk/appsflyer_sdk.dart';

class AppsFlyerSKANOnly {
  static final AppsflyerSdk _appsflyerSdk = AppsflyerSdk({
    'afDevKey': 'YOUR_DEV_KEY',
    'afAppId': 'YOUR_APP_ID',
    'isDebug': false,
    'disableIDFACollection': true,  // Disable IDFA
    'disableAdvertisingIdentifier': true,  // No ad ID
  });

  static Future<void> initSKANOnly() async {
    // Initialize with limited tracking
    await _appsflyerSdk.initSdk(
      registerConversionDataCallback: false,
      registerOnAppOpenAttributionCallback: false,
      registerOnDeepLinkingCallback: false,
    );
    
    // Enable SKAN
    await _appsflyerSdk.enableSKAdNetwork(true);
    
    // Only update conversion values
    updateSKANConversionValue(1);
  }
  
  static void updateSKANConversionValue(int value) {
    if (Platform.isIOS && value >= 0 && value <= 63) {
      // Update conversion value for SKAN 4.0
      _appsflyerSdk.updateConversionValue(value);
    }
  }
  
  static Map<String, int> conversionSchema = {
    'install': 1,
    'registration': 2,
    'tutorial_complete': 3,
    'first_purchase': 10,
    'subscription': 20,
    // Add more events as needed
  };
}
''',
    'runtime_consent': '''
// Flutter Implementation - Runtime Consent Changes
import 'package:appsflyer_sdk/appsflyer_sdk.dart';
import 'package:shared_preferences/shared_preferences.dart';

class DynamicConsentManager {
  static AppsflyerSdk? _appsflyerSdk;
  static bool _isInitialized = false;
  static bool _hasConsent = false;

  static Future<void> checkAndInitialize() async {
    final prefs = await SharedPreferences.getInstance();
    _hasConsent = prefs.getBool('user_tracking_consent') ?? false;
    
    if (_hasConsent) {
      await _initializeWithFullTracking();
    } else {
      await _initializeSKANOnly();
    }
  }
  
  static Future<void> _initializeWithFullTracking() async {
    _appsflyerSdk = AppsflyerSdk({
      'afDevKey': 'YOUR_DEV_KEY',
      'afAppId': 'YOUR_APP_ID',
      'isDebug': true,
    });
    
    await _appsflyerSdk!.initSdk(
      registerConversionDataCallback: true,
      registerOnAppOpenAttributionCallback: true,
    );
    
    _isInitialized = true;
    print('AppsFlyer initialized with full tracking');
  }
  
  static Future<void> _initializeSKANOnly() async {
    _appsflyerSdk = AppsflyerSdk({
      'afDevKey': 'YOUR_DEV_KEY',
      'afAppId': 'YOUR_APP_ID',
      'disableIDFACollection': true,
      'disableAdvertisingIdentifier': true,
    });
    
    await _appsflyerSdk!.initSdk(
      registerConversionDataCallback: false,
    );
    
    _isInitialized = true;
    print('AppsFlyer initialized with SKAN only');
  }
  
  static Future<void> updateConsent(bool granted) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('user_tracking_consent', granted);
    
    if (granted != _hasConsent) {
      _hasConsent = granted;
      _isInitialized = false;
      
      // Re-initialize with new consent status
      if (granted) {
        await _initializeWithFullTracking();
      } else {
        await _initializeSKANOnly();
      }
    }
  }
  
  static void trackEvent(String name, Map<String, dynamic> params) {
    if (!_isInitialized) return;
    
    if (_hasConsent) {
      _appsflyerSdk?.logEvent(name, params);
    } else {
      // SKAN only - just update conversion value
      int conversionValue = _calculateConversionValue(name);
      if (Platform.isIOS) {
        _appsflyerSdk?.updateConversionValue(conversionValue);
      }
    }
  }
  
  static int _calculateConversionValue(String eventName) {
    // Map events to conversion values (0-63)
    final Map<String, int> eventValues = {
      'app_open': 1,
      'registration': 5,
      'purchase': 10,
      'subscription': 20,
      'level_complete': 15,
    };
    
    return eventValues[eventName] ?? 0;
  }
}
''',
    'conversion_studio_config': '''
// Conversion Studio Configuration
class ConversionStudioConfig {
  // 6-bit conversion value mapping (0-63)
  static const int MAX_CONVERSION_VALUE = 63;
  
  // Revenue ranges for conversion values
  static final Map<String, Map<String, dynamic>> revenueRanges = {
    'range_0': {'min': 0, 'max': 5, 'conversionValue': 1},
    'range_1': {'min': 5, 'max': 10, 'conversionValue': 2},
    'range_2': {'min': 10, 'max': 25, 'conversionValue': 3},
    'range_3': {'min': 25, 'max': 50, 'conversionValue': 4},
    'range_4': {'min': 50, 'max': 100, 'conversionValue': 5},
    'range_5': {'min': 100, 'max': 250, 'conversionValue': 10},
    'range_6': {'min': 250, 'max': 500, 'conversionValue': 15},
    'range_7': {'min': 500, 'max': 1000, 'conversionValue': 20},
    'range_8': {'min': 1000, 'max': double.infinity, 'conversionValue': 30},
  };
  
  // Event priority mapping
  static final Map<String, int> eventPriorities = {
    'install': 1,
    'registration': 2,
    'tutorial_start': 3,
    'tutorial_complete': 4,
    'first_purchase': 10,
    'repeat_purchase': 15,
    'subscription_trial': 20,
    'subscription_paid': 25,
    'high_value_action': 30,
  };
  
  static int calculateConversionValue({
    double? revenue,
    List<String>? events,
    int? engagementLevel,
  }) {
    int value = 0;
    
    // Add revenue component
    if (revenue != null) {
      for (var range in revenueRanges.values) {
        if (revenue >= range['min'] && revenue < range['max']) {
          value += range['conversionValue'] as int;
          break;
        }
      }
    }
    
    // Add event component
    if (events != null && events.isNotEmpty) {
      int maxEventValue = 0;
      for (String event in events) {
        int eventValue = eventPriorities[event] ?? 0;
        if (eventValue > maxEventValue) {
          maxEventValue = eventValue;
        }
      }
      value += maxEventValue;
    }
    
    // Add engagement component
    if (engagementLevel != null) {
      value += (engagementLevel * 5).clamp(0, 10);
    }
    
    // Ensure value is within SKAN limits
    return value.clamp(0, MAX_CONVERSION_VALUE);
  }
  
  static void updateConversionValue(int value) {
    if (Platform.isIOS) {
      // Update the SKAN conversion value
      SKAdNetwork.updateConversionValue(value);
      
      // Log for debugging
      debugPrint('SKAN Conversion Value Updated: $value');
    }
  }
}

// Usage Example
void trackUserAction(String action, double revenue) {
  int conversionValue = ConversionStudioConfig.calculateConversionValue(
    revenue: revenue,
    events: [action],
    engagementLevel: 3,
  );
  
  ConversionStudioConfig.updateConversionValue(conversionValue);
}
'''
}

# SKAN configuration and data
SKAN_CONFIG = {
    'overview': {
        'title': 'SKAdNetwork (SKAN) 4.0',
        'description': 'Apple\'s privacy-preserving attribution framework for iOS 14.5+',
        'key_features': [
            'Privacy-first attribution without IDFA',
            '6-bit conversion values (0-63)',
            'Multiple conversion windows',
            'Crowd anonymity thresholds',
            'Postback delays for privacy'
        ]
    },
    'appsflyer_features': {
        'title': 'AppsFlyer SKAN Solution',
        'features': [
            'Conversion Studio for value mapping',
            'Single Source of Truth (SSOT)',
            'Predictive analytics',
            'SKAN Dashboard',
            'Advanced conversion models'
        ]
    },
    'campaign_constraints': {
        'Google Ads': {'campaigns': 100, 'ad_groups': 'Unlimited'},
        'Meta (Facebook)': {'campaigns': 9, 'ad_groups': '5 per campaign'},
        'TikTok': {'campaigns': 11, 'ad_groups': 'Unlimited'},
        'Apple Search Ads': {'campaigns': 'Unlimited', 'ad_groups': 'Unlimited'},
        'Twitter': {'campaigns': 100, 'ad_groups': 'Unlimited'},
        'Snapchat': {'campaigns': 63, 'ad_groups': 'Unlimited'}
    }
}

@app.route('/')
def index():
    """Main application page"""
    # Generate session key for this user
    if 'session_key' not in session:
        session['session_key'] = CodeProtector.generate_runtime_key()
    
    return render_template('index.html', 
                         skan_config=SKAN_CONFIG,
                         session_key=session['session_key'])

@app.route('/api/get-flutter-code/<code_type>')
def get_flutter_code(code_type):
    """API endpoint to get Flutter code samples"""
    if code_type in FLUTTER_CODE_SAMPLES:
        return jsonify({
            'success': True,
            'code': FLUTTER_CODE_SAMPLES[code_type],
            'type': code_type
        })
    return jsonify({'success': False, 'error': 'Code sample not found'}), 404

@app.route('/api/protected-js')
def get_protected_js():
    """Serve obfuscated JavaScript code"""
    if 'session_key' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # This would contain your interactive JavaScript logic
    js_code = """
    // Protected interactive elements code
    (function() {
        'use strict';
        
        // Conversion value simulator
        window.ConversionSimulator = {
            currentValue: 0,
            events: [],
            
            addEvent: function(eventName, value) {
                this.events.push({name: eventName, value: value, time: Date.now()});
                this.updateConversionValue();
            },
            
            updateConversionValue: function() {
                let total = 0;
                this.events.forEach(e => total += e.value);
                this.currentValue = Math.min(63, total); // SKAN 4.0 limit
                this.updateDisplay();
            },
            
            updateDisplay: function() {
                const display = document.getElementById('conversion-value-display');
                if (display) {
                    display.textContent = this.currentValue;
                    display.className = 'conversion-value-' + Math.floor(this.currentValue / 10);
                }
            },
            
            reset: function() {
                this.currentValue = 0;
                this.events = [];
                this.updateDisplay();
            }
        };
        
        // Tab switching functionality
        window.TabManager = {
            init: function() {
                document.querySelectorAll('.tab-button').forEach(button => {
                    button.addEventListener('click', function() {
                        const tabId = this.dataset.tab;
                        TabManager.switchTab(tabId);
                    });
                });
            },
            
            switchTab: function(tabId) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.style.display = 'none';
                });
                
                // Remove active class from all buttons
                document.querySelectorAll('.tab-button').forEach(button => {
                    button.classList.remove('active');
                });
                
                // Show selected tab
                const selectedTab = document.getElementById(tabId);
                if (selectedTab) {
                    selectedTab.style.display = 'block';
                }
                
                // Add active class to selected button
                const selectedButton = document.querySelector(`[data-tab="${tabId}"]`);
                if (selectedButton) {
                    selectedButton.classList.add('active');
                }
            }
        };
        
        // Initialize on DOM ready
        document.addEventListener('DOMContentLoaded', function() {
            TabManager.init();
            ConversionSimulator.reset();
        });
    })();
    """
    
    # Return obfuscated code
    return jsonify({
        'code': CodeProtector.obfuscate(js_code),
        'key': session['session_key']
    })

@app.route('/api/simulate-conversion', methods=['POST'])
def simulate_conversion():
    """Simulate SKAN conversion value calculation"""
    data = request.json
    events = data.get('events', [])
    revenue = data.get('revenue', 0)
    
    # Calculate conversion value based on events and revenue
    conversion_value = 0
    
    # Event-based calculation
    event_values = {
        'install': 1,
        'registration': 2,
        'tutorial': 3,
        'first_purchase': 10,
        'subscription': 20
    }
    
    for event in events:
        conversion_value += event_values.get(event, 0)
    
    # Revenue-based calculation
    if revenue > 0:
        if revenue < 10:
            conversion_value += 5
        elif revenue < 50:
            conversion_value += 10
        elif revenue < 100:
            conversion_value += 15
        else:
            conversion_value += 20
    
    # Cap at SKAN maximum
    conversion_value = min(conversion_value, 63)
    
    return jsonify({
        'conversion_value': conversion_value,
        'events': events,
        'revenue': revenue,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/campaign-limits/<network>')
def get_campaign_limits(network):
    """Get campaign limitations for ad networks"""
    limits = SKAN_CONFIG['campaign_constraints'].get(network)
    if limits:
        return jsonify({'success': True, 'network': network, 'limits': limits})
    return jsonify({'success': False, 'error': 'Network not found'}), 404

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)