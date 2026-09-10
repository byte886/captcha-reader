---
name: captcha-reader
description: 验证码（CAPTCHA）图片识别辅助。在浏览器自动化（Playwright/Chrome MCP）中遇到图形验证码时，截取验证码元素图片并通过图像增强（放大、灰度、对比度、二值化）提升 AI 视觉识别率，然后填入验证码。适用于 Apple ID 重置、登录注册、表单提交等出现图形验证码的场景。
compatibility: "仅在 macOS(Darwin) 实测可用；Windows/Linux 未适配。执行前先判平台(uname -s 返回 Darwin)，非 macOS 停止并告知需另行适配、不硬跑；将来补齐 Windows 后仍按平台分流并分别标注验证状态"
---

# CAPTCHA 验证码识别辅助

## 平台适用（执行前先读）
- 本技能当前**仅在 macOS（Darwin）实测可用**，命令、路径、代理端口与系统原生能力均按 Mac。
- 动手前先判平台：`uname -s` 返回 `Darwin` 才走本技能流程；**Windows/Linux 未适配，遇到就停下告知用户“需先做该平台适配”，不要用想当然的等价命令硬跑**。
- 以后补齐 Windows 后也必须保留“先判平台 → 按平台分流”的结构：mac/Windows 的命令与路径分开写、各自标注是否已验证。

在浏览器自动化中遇到图形验证码时，截取验证码元素 → 图像增强 → AI 视觉读取 → 填入输入框。

## 前置依赖

- Python3 + Pillow：`pip3 install Pillow`
- 浏览器自动化工具（Playwright CLI 或 Chrome MCP）

## 工作流程

### 1. 定位验证码元素

通过 snapshot 获取验证码图片和输入框的 ref：

```bash
# Playwright CLI
npx playwright cli -s=<session> snapshot | grep -iE "captcha|challenge|characters|验证码"

# Chrome MCP: 使用 mcp__chrome__take_snapshot
```

验证码通常包含：
- 一个 `img` 元素（alt 含 "Image challenge" / "captcha" / "验证码"）
- 一个 `textbox`（placeholder 含 "Type the characters" / "验证码"）
- 可能有 "New Code" / "新代码" 按钮用于换一张

### 2. 截取验证码图片

```bash
# Playwright CLI — 截取验证码 img 元素
npx playwright cli -s=<session> screenshot <img_ref> --filename=/tmp/captcha_raw.png

# Chrome MCP — 使用 mcp__chrome__take_screenshot 传入 uid
```

### 3. 图像增强

运行增强脚本生成放大、高对比度版本：

```bash
# 基础增强（灰度 + 6x放大 + 对比度2.5 + 锐化）
python3 <skill_dir>/scripts/enhance_captcha.py /tmp/captcha_raw.png /tmp/captcha_enhanced.png

# 如果基础增强仍看不清，尝试二值化（黑白）
python3 <skill_dir>/scripts/enhance_captcha.py /tmp/captcha_raw.png /tmp/captcha_bw.png --threshold

# 更大放大倍数 + 更高对比度
python3 <skill_dir>/scripts/enhance_captcha.py /tmp/captcha_raw.png /tmp/captcha_big.png --scale 8 --contrast 3.0

# 反色（浅色背景深色文字时尝试）
python3 <skill_dir>/scripts/enhance_captcha.py /tmp/captcha_raw.png /tmp/captcha_inv.png --invert
```

### 4. AI 视觉读取

用 `Read` 工具查看增强后的图片（`thumbnail_size: "full"`），识别验证码字符。

**识别技巧：**
- 优先看基础增强版本；模糊时再看二值化版本交叉验证
- 注意区分易混淆字符：0/O、1/I/l、2/Z、5/S、8/B、G/6、Y/V
- 如果不确定，点击 "New Code" 换一张更清晰的验证码重试
- 验证码不区分大小写（除非页面明确说明）

### 5. 填入并提交

```bash
# Playwright CLI
npx playwright cli -s=<session> fill <textbox_ref> "<识别的验证码>"
# 等待提交按钮启用后点击
npx playwright cli -s=<session> snapshot | grep "Continue\|提交\|确认"
npx playwright cli -s=<session> click <button_ref>

# Chrome MCP: 使用 mcp__chrome__fill + mcp__chrome__click
```

### 6. 验证结果

提交后检查页面：
- 成功：页面跳转或进入下一步
- 失败：出现 "incorrect" / "错误" / "try again" 提示 → 换一张验证码重试（回到步骤 2）
- 网络错误：出现 "could not be completed because of an error" → 等待后重试

## 多版本对比策略

当验证码难以辨认时，一次性生成多个增强版本对比读取：

```bash
python3 <skill_dir>/scripts/enhance_captcha.py raw.png enhanced.png
python3 <skill_dir>/scripts/enhance_captcha.py raw.png bw.png --threshold
python3 <skill_dir>/scripts/enhance_captcha.py raw.png big.png --scale 8 --contrast 3.5
```

逐个 Read 三张图，取一致识别结果。

## 注意事项

- 验证码有时效性，截取后尽快识别填入（通常 2-5 分钟过期）
- 每次换验证码后 ref 可能变化，需重新 snapshot
- 部分验证码有背景干扰线/噪点，`--threshold` 二值化通常能有效去除
- 如果连续 3 次识别失败，建议换一张验证码或请用户人工输入
- 本 Skill 仅用于用户本人账户操作的验证码辅助，不得用于绕过他人账户安全措施
