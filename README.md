# 🌤️ Weatherly

A sleek, modern weather application built with PyQt5 featuring a beautiful dark UI and smooth animations.

## ✨ Features

- **Modern Dark Theme** - Eye-friendly dark interface with smooth gradients
- **Animated Sidebar** - Collapsible sidebar with fluid animations
- **Responsive Design** - Adapts to different window sizes
- **Search Functionality** - Quick location search with autocomplete
- **Real-time Updates** - Refresh button for latest weather data

## 🎨 UI Highlights

- Smooth 300ms cubic easing animations
- Glassmorphic design elements
- Rounded corners and modern spacing
- Hover effects on interactive elements
- Dynamic search bar that adjusts with sidebar state

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.7 or higher
PyQt5
```

### Installation

1. Clone the repository
```bash
git clone https://github.com/yTRX-1000/Weatherly-v2.git
cd weatherly-v2
```

2. Install dependencies
```bash
pip install PyQt5
```

3. Run the application
```bash
python weatherly-v2.py
```

## 🎯 Usage

- **Toggle Sidebar**: Click the menu button (☰) in the top-left corner
- **Search Location**: Type a city name or location in the search bar
- **Refresh Data**: Click the refresh button (↻) to update weather information

## 🛠️ Technical Details

### Architecture

The application uses PyQt5's animation framework for smooth UI transitions:

- `QPropertyAnimation` for sidebar expansion/collapse
- Dynamic width adjustment for responsive search bar
- Event-driven architecture for user interactions

### Key Components

- **Sidebar**: Collapsible navigation panel (0px → 250px)
- **Search Bar**: Adaptive width search input
- **Top Bar**: Fixed header with menu and refresh controls
- **Content Area**: Main display area with rounded frame

## 🎨 Customization

You can easily customize the colors by modifying the stylesheet values:

```python
# Sidebar background
background-color: #1a1a1a;

# Main content area
background-color: #111;

# Interactive elements
background: #262626;

# Hover states
background: #333;
```

## 📝 Roadmap

- [ ] Weather API integration
- [ ] Multiple location support
- [ ] Weather forecasts and graphs
- [ ] Temperature unit toggle (°C/°F)
- [ ] Dark/Light theme switcher
- [ ] Desktop notifications
- [ ] System tray integration

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PyQt5 documentation and community
- Modern UI design inspiration from contemporary weather apps
- Animation patterns from Material Design guidelines

## 📧 Contact

Project Link: [https://github.com/TRX-1000/Weatherly-v2](https://github.com/TRX-1000/Weatherly-v2)

---

⭐ Star this repo if you find it helpful!
