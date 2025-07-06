# ZHI AI - 极客风格AI聊天界面

一个具有数码极客风格的AI聊天界面，采用黑绿配色方案，具有终端风格的视觉效果和动画。

## 特性

- 🎨 **极客风格设计** - 黑绿配色，终端风格界面
- ⚡ **实时通信** - WebSocket连接，支持实时音频和文本交互
- 🎵 **音频支持** - Opus音频编解码，支持语音合成和识别
- 🎭 **动画效果** - 扫描线、发光效果、打字机动画
- 📱 **响应式设计** - 适配不同屏幕尺寸
- 🔧 **状态监控** - 实时连接状态和系统信息显示

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite
- **样式**: Tailwind CSS + 自定义CSS动画
- **音频**: Opus Decoder
- **通信**: WebSocket
- **后端**: Python WebSocket代理服务器

## 快速开始

### 方法一：使用启动脚本（推荐）

```bash
# Windows
start.bat

# 或者手动启动
```

### 方法二：手动启动

1. **安装依赖**
```bash
npm install
```

2. **启动后端代理服务器**
```bash
python server.py
```

3. **启动前端开发服务器**
```bash
npm run dev
```

4. **访问应用**
打开浏览器访问 [http://localhost:5173](http://localhost:5173)

## 项目结构

```
Zhi-main/
├── src/
│   ├── components/
│   │   ├── Starter.vue      # 启动界面组件
│   │   └── Chat.vue         # 聊天界面组件
│   ├── App.vue              # 主应用组件
│   ├── main.ts              # 应用入口
│   └── style.css            # 全局样式
├── server.py                # WebSocket代理服务器
├── start.bat               # Windows启动脚本
└── package.json            # 项目配置
```

## 界面特性

### 启动界面
- 终端风格的初始化动画
- 系统状态指示器
- 打字机效果的系统信息
- 发光按钮和悬停效果

### 聊天界面
- 实时连接状态显示
- 消息类型图标和状态标签
- 音频播放状态指示
- 自动滚动消息列表
- 极客风格的输入框

### 视觉效果
- 扫描线动画
- 浮动粒子背景
- 发光边框和阴影
- 脉冲动画状态指示器
- 渐变背景和装饰元素

## 配置

### 环境变量
创建 `.env.local` 文件：
```
VITE_WS_URL=ws://localhost:8765
```

### WebSocket代理配置
在 `server.py` 中配置：
- `PROXY_PORT`: 代理服务器端口（默认8765）
- `SERVER_URL`: 目标服务器地址
- `SERVER_HEADERS`: 连接头信息

## 开发

### 构建生产版本
```bash
npm run build
```

### 预览生产版本
```bash
npm run preview
```

## 自定义

### 颜色主题
在 `src/style.css` 中修改CSS变量：
```css
:root {
  --neon-green: #00ff41;
  --dark-green: #0a0a0a;
  --medium-green: #1a472a;
  --light-green: #32cd32;
  --accent-green: #00d4aa;
  --glow-green: rgba(0, 255, 65, 0.3);
}
```

### 动画效果
- 扫描线：`.scanline` 类
- 发光效果：`.terminal-glow` 类
- 脉冲动画：`.status-indicator` 类

## 故障排除

### 常见问题

1. **WebSocket连接失败**
   - 检查后端服务器是否运行
   - 确认端口8765未被占用
   - 检查防火墙设置

2. **音频播放问题**
   - 确保浏览器支持Web Audio API
   - 检查音频权限设置

3. **样式显示异常**
   - 清除浏览器缓存
   - 检查CSS文件是否正确加载

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！
