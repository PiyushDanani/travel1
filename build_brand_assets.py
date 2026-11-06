import cv2
import numpy as np
from PIL import Image

uploaded = r'C:/Users/Dell/.gemini/antigravity/brain/cdd5fc77-ec5b-4c4d-915b-6edb1a665ae5/.user_uploaded/media_1793970869428_d6f50fe9.jpg'
bgr = cv2.imread(uploaded)
h_img, w_img = bgr.shape[:2]

bg = bgr[5, 5].astype(float) # ~[242, 248, 243] BGR

# -------------------------------------------------------------
# 1. EMBLEM EXTRACTION
# -------------------------------------------------------------
# Emblem bounding box in source: Y in [74, 348], X in [363, 661]
diff = np.sqrt(np.sum((bgr.astype(float) - bg)**2, axis=2))
emblem_seed = (diff[74:348, 363:661] > 18).astype(np.uint8)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
emblem_closed = cv2.morphologyEx(emblem_seed, cv2.MORPH_CLOSE, kernel)
contours, _ = cv2.findContours(emblem_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
main_contour = max(contours, key=cv2.contourArea)

h_e, w_e = emblem_closed.shape
up_mask_e = np.zeros((h_e * 4, w_e * 4), dtype=np.uint8)
cv2.drawContours(up_mask_e, [(main_contour * 4).astype(np.int32)], -1, 255, -1)
smooth_emblem_alpha = cv2.resize(up_mask_e, (w_e, h_e), interpolation=cv2.INTER_AREA).astype(float) / 255.0

emblem_bgr = bgr[74:348, 363:661].copy().astype(np.float32)
# De-fringe emblem border pixels
for c in range(3):
    emblem_bgr[:, :, c] = np.clip((emblem_bgr[:, :, c] - (1.0 - smooth_emblem_alpha) * bg[c]) / np.maximum(smooth_emblem_alpha, 0.001), 0, 255)

emblem_rgba = np.zeros((h_e, w_e, 4), dtype=np.uint8)
emblem_rgba[:, :, :3] = emblem_bgr.astype(np.uint8)
emblem_rgba[:, :, 3] = (smooth_emblem_alpha * 255).astype(np.uint8)

# Crop emblem tightly
ey_nz, ex_nz = np.where(smooth_emblem_alpha > 0.05)
emblem_tight = emblem_rgba[ey_nz.min():ey_nz.max()+1, ex_nz.min():ex_nz.max()+1]
eth, etw = emblem_tight.shape[:2]

# -------------------------------------------------------------
# 2. TEXT EXTRACTION (DARK & LIGHT VERSIONS)
# -------------------------------------------------------------
# Text bounding box in source: Y in [354, 483], X in [316, 707]
text_crop = bgr[354:483, 316:707].copy().astype(np.float32)
text_diff = diff[354:483, 316:707]
text_alpha = np.clip((text_diff - 16) / (38 - 16), 0, 1)

for c in range(3):
    text_crop[:, :, c] = np.clip((text_crop[:, :, c] - (1.0 - text_alpha) * bg[c]) / np.maximum(text_alpha, 0.001), 0, 255)

text_orig_rgba = np.zeros((text_crop.shape[0], text_crop.shape[1], 4), dtype=np.uint8)
text_orig_rgba[:, :, :3] = text_crop.astype(np.uint8)
text_orig_rgba[:, :, 3] = (text_alpha * 255).astype(np.uint8)

# Crop text tightly
ty_nz, tx_nz = np.where(text_alpha > 0.05)
text_orig_tight = text_orig_rgba[ty_nz.min():ty_nz.max()+1, tx_nz.min():tx_nz.max()+1]

# Light text version (optimized for dark navy backgrounds)
text_light_tight = text_orig_tight.copy()
# TRAVELICIOUS is in the top 42% of text height
split_y = int(text_light_tight.shape[0] * 0.42)
text_light_tight[:split_y, :, 0] = 255  # Pure white B
text_light_tight[:split_y, :, 1] = 255  # Pure white G
text_light_tight[:split_y, :, 2] = 255  # Pure white R

# Bottom tagline (Your Journey, Our Passion) - boost brightness
split_tagline = int(text_light_tight.shape[0] * 0.82)
text_light_tight[split_tagline:, :, 0] = np.clip(text_light_tight[split_tagline:, :, 0].astype(float) * 1.8, 0, 255).astype(np.uint8)
text_light_tight[split_tagline:, :, 1] = np.clip(text_light_tight[split_tagline:, :, 1].astype(float) * 1.8, 0, 255).astype(np.uint8)
text_light_tight[split_tagline:, :, 2] = np.clip(text_light_tight[split_tagline:, :, 2].astype(float) * 1.5, 0, 255).astype(np.uint8)

tth, ttw = text_light_tight.shape[:2]

# -------------------------------------------------------------
# 3. GENERATE PRODUCTION ASSETS
# -------------------------------------------------------------

# A) logo_emblem.png and logo_emblem_transparent.png (512x512 square for favicon/app icon)
icon_size = 512
icon_canvas = np.zeros((icon_size, icon_size, 4), dtype=np.uint8)
target_inner = int(icon_size * 0.90)
scale_icon = target_inner / max(eth, etw)
nw = int(etw * scale_icon)
nh = int(eth * scale_icon)
resized_emblem = cv2.resize(emblem_tight, (nw, nh), interpolation=cv2.INTER_LANCZOS4)
ox = (icon_size - nw) // 2
oy = (icon_size - nh) // 2
icon_canvas[oy:oy+nh, ox:ox+nw] = resized_emblem

cv2.imwrite('logo_emblem.png', icon_canvas)
cv2.imwrite('logo_emblem_transparent.png', icon_canvas)

# Also generate favicon.ico (multi-resolution 16, 32, 48, 64)
pil_icon = Image.fromarray(cv2.cvtColor(icon_canvas, cv2.COLOR_BGRA2RGBA))
pil_icon.save('favicon.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

# B) logo_transparent.png (HORIZONTAL LOCKUP FOR NAVBAR & FOOTER)
# Height 160px, width auto
target_h = 160
scale_e = target_h / eth
new_ew = int(etw * scale_e)
emb_resized = cv2.resize(emblem_tight, (new_ew, target_h), interpolation=cv2.INTER_LANCZOS4)

# Scale text proportionally (text height ~ 100px)
target_th = int(target_h * 0.62)
scale_t = target_th / tth
new_tw = int(ttw * scale_t)
txt_light_resized = cv2.resize(text_light_tight, (new_tw, target_th), interpolation=cv2.INTER_LANCZOS4)

gap = int(target_h * 0.14) # ~22px
total_w = new_ew + gap + new_tw

canvas_h_dark = np.zeros((target_h, total_w, 4), dtype=np.uint8)
canvas_h_dark[:, :new_ew] = emb_resized
txt_oy = (target_h - target_th) // 2
canvas_h_dark[txt_oy:txt_oy+target_th, new_ew+gap:new_ew+gap+new_tw] = txt_light_resized

cv2.imwrite('logo_transparent.png', canvas_h_dark)
cv2.imwrite('logo_horizontal.png', canvas_h_dark)

# Also horizontal light-bg version
txt_orig_resized = cv2.resize(text_orig_tight, (new_tw, target_th), interpolation=cv2.INTER_LANCZOS4)
canvas_h_light = np.zeros((target_h, total_w, 4), dtype=np.uint8)
canvas_h_light[:, :new_ew] = emb_resized
canvas_h_light[txt_oy:txt_oy+target_th, new_ew+gap:new_ew+gap+new_tw] = txt_orig_resized
cv2.imwrite('logo_horizontal_light.png', canvas_h_light)

# C) STACKED LOGOS (Emblem on top, text below)
gap_v = 16
total_sw = max(etw, ttw)
total_sh = eth + gap_v + tth

stacked_dark = np.zeros((total_sh, total_sw, 4), dtype=np.uint8)
sox_e = (total_sw - etw) // 2
sox_t = (total_sw - ttw) // 2
stacked_dark[:eth, sox_e:sox_e+etw] = emblem_tight
stacked_dark[eth+gap_v:eth+gap_v+tth, sox_t:sox_t+ttw] = text_light_tight
cv2.imwrite('logo_stacked.png', stacked_dark)

stacked_orig = np.zeros((total_sh, total_sw, 4), dtype=np.uint8)
stacked_orig[:eth, sox_e:sox_e+etw] = emblem_tight
stacked_orig[eth+gap_v:eth+gap_v+tth, sox_t:sox_t+ttw] = text_orig_tight
cv2.imwrite('logo_stacked_light.png', stacked_orig)

# D) logo.png & logo_full.png (Clean official high-res logo with background for OpenGraph, Twitter, SEO)
cv2.imwrite('logo.png', bgr)
cv2.imwrite('logo_full.png', bgr)

print('All brand assets successfully generated!')
print(f'Emblem: {icon_size}x{icon_size}')
print(f'Horizontal Logo: {total_w}x{target_h}')
print(f'Stacked Logo: {total_sw}x{total_sh}')
print(f'Full Logo: {w_img}x{h_img}')
