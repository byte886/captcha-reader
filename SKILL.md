---
name: captcha-reader
description: 验证码（CAPTCHA）图片识别辅助。浏览器自动化（Playwright/Chrome MCP）中遇到图形验证码时，截取验证码元素图片，经图像增强（放大、灰度、对比度、二值化）提升 AI 视觉识别率后填入。适用于 Apple ID 重置、登录注册、表单提交等出现图形验证码的场景。
compatibility: 仅在 macOS(Darwin) 实测可用；Windows/Linux 未适配。执行前先判平台(uname -s 返回 Darwin)，非 macOS 停止并告知需另行适配、不硬跑；将来补齐 Windows 后仍按平台分流并分别标注验证状态
---

# CAPTCHA 验证码识别辅助

在浏览器自动化中遇到图形验证码时：截取验证码元素 → 图像增强 → AI 视觉读取 → 填入输入框。本技能只负责图像增强与识别；浏览器侧的打开页面、定位元素、截图、填值、点击交给浏览器控制能力（mac-system-toolkit，按其当前可用栈）。

## 平台适用（执行前先读）
- 本技能当前**仅在 macOS（Darwin）实测可用**，命令、路径与系统原生能力均按 Mac。
- 动手前先判平台：`uname -s` 返回 `Darwin` 才走本技能流程；**Windows/Linux 未适配，遇到就停下告知用户"需先做该平台适配"，不要用想当然的等价命令硬跑**。
- 以后补齐 Windows 后也必须保留"先判平台 → 按平台分流"的结构：mac/Windows 的命令与路径分开写、各自标注是否已验证。

## 前置依赖

- Python3 + Pillow：`pip3 install Pillow`
- 图像增强脚本：技能自带 `scripts/enhance_captcha.py`（见 SOP 步骤 3）。
- 浏览器侧动作（截图/填值）复用 mac-system-toolkit 的浏览器控制能力，不绑定具体 CLI 语法。

## 核心原则

- 截**验证码元素**而非整屏，避免背景噪声；存 `/tmp/captcha_raw.png`。
- 先基础增强读，模糊时用二值化/放大/反色多版本交叉验证。
- 验证码有时效（2–5 分钟），截后尽快识别填入；连续 3 次失败就换一张或请用户人工输入。

## 按需加载索引

| 你要做什么 | 读这篇 |
|---|---|
| 定位/截图/增强命令/AI 读取/填入验证全流程、多版本对比策略 | [references/sop.md](references/sop.md) |

## 硬红线

- 本 Skill 仅用于用户本人账户操作的验证码辅助，**不得用于绕过他人账户安全措施**。
