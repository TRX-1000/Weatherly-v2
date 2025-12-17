import json
import os
import platform


class WindowConfig:
    """Manages platform-specific window configurations"""
    
    def __init__(self, config_file="window_config.json"):
        self.config_file = config_file
        self.platform = platform.system()  # Returns 'Darwin' for Mac, 'Windows' for Windows
        self.config = self.load_config()
    
    def load_config(self):
        """Load window configuration from JSON file"""
        default_config = {
            "Darwin": {  # macOS
                "width": 1470,
                "height": 810,
                "min_width": 1470,
                "min_height": 810,
                "start_x": 0,
                "start_y": 0
            },
            "Windows": {
                "width": 1350,
                "height": 725,
                "min_width": 1350,
                "min_height": 725,
                "start_x": 100,
                "start_y": 100
            }
        }
        
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for platform_name in default_config:
                        if platform_name in loaded_config:
                            default_config[platform_name].update(loaded_config[platform_name])
                    return default_config
            except Exception as e:
                print(f"Error loading window config: {e}")
                return default_config
        else:
            # Create default config file
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Save window configuration to JSON file"""
        try:
            config_to_save = config if config else self.config
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
        except Exception as e:
            print(f"Error saving window config: {e}")
    
    def get_current_platform_config(self):
        """Get configuration for the current platform"""
        return self.config.get(self.platform, self.config["Darwin"])
    
    def get_width(self):
        """Get window width for current platform"""
        return self.get_current_platform_config()["width"]
    
    def get_height(self):
        """Get window height for current platform"""
        return self.get_current_platform_config()["height"]
    
    def get_min_width(self):
        """Get minimum window width for current platform"""
        return self.get_current_platform_config()["min_width"]
    
    def get_min_height(self):
        """Get minimum window height for current platform"""
        return self.get_current_platform_config()["min_height"]
    
    def get_start_x(self):
        """Get starting X position for window on current platform"""
        return self.get_current_platform_config().get("start_x", 0)
    
    def get_start_y(self):
        """Get starting Y position for window on current platform"""
        return self.get_current_platform_config().get("start_y", 0)
    
    def get_sidebar_opened(self):
        """Get the value of the sidebar when opened"""
        return self.get_current_platform_config().get("sidebar_opened", 0)
    
    def get_label_spacing(self):
        """Get the current value of label spacing"""
        return self.get_current_platform_config().get("label_spacing", 0)
    
    def get_platform_name(self):
        """Get current platform name"""
        platform_names = {
            "Darwin": "macOS",
            "Windows": "Windows",
            "Linux": "Linux"
        }
        return platform_names.get(self.platform, self.platform)