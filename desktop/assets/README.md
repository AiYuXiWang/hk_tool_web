# 桌面应用图标资源

此目录存放桌面应用的图标文件。

## 图标规格要求

### Windows (`icon.ico`)
- 格式: ICO
- 尺寸: 256x256 (推荐包含多个尺寸: 16x16, 32x32, 48x48, 128x128, 256x256)
- 用途: Windows 安装包和应用图标

### macOS (`icon.icns`)
- 格式: ICNS
- 尺寸: 512x512@2x (1024x1024)
- 用途: macOS 应用图标
- 工具: 使用 `iconutil` 或 https://cloudconvert.com/png-to-icns

### Linux (`icon.png`)
- 格式: PNG
- 尺寸: 512x512 (推荐)
- 用途: Linux 应用图标

## 创建图标的建议

1. 准备一张高分辨率的源图片（至少 1024x1024 PNG）
2. 使用在线工具生成各平台图标：
   - https://www.electron.build/icons
   - https://icoconvert.com/
   - https://cloudconvert.com/

3. 或使用命令行工具：
   ```bash
   # macOS
   iconutil -c icns icon.iconset
   
   # Windows (使用 ImageMagick)
   convert icon.png -define icon:auto-resize=256,128,96,64,48,32,16 icon.ico
   ```

## 默认图标

如果未提供自定义图标，Electron Builder 将使用默认图标。

为了最佳效果，请提供所有平台的图标文件。
